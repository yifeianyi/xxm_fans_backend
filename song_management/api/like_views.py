import hmac
import json
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from core.cache import clear_cache_pattern
from ..models import SongRecord, SongRecordLike

HOURLY_LIKE_LIMIT = 100
MAX_STATUS_IDS = 100


def _get_client_ip(request):
    """Return the best-effort client IP address for anonymous like identity."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def get_client_like_identifier(request):
    """
    Return a stable, non-reversible identifier for the anonymous client.

    The like system only needs to know whether the same anonymous client has
    already liked a song record.  Persisting an HMAC instead of the raw IP
    reduces the amount of personal data stored in the database while keeping
    the existing uniqueness semantics.
    """
    ip_address = _get_client_ip(request)
    secret = settings.SECRET_KEY.encode('utf-8')
    return hmac.new(secret, ip_address.encode('utf-8'), 'sha256').hexdigest()


def _get_client_identifier_candidates(request):
    """
    Return current and legacy identifiers for read/delete compatibility.

    Older rows stored the raw IP address in SongRecordLike.ip_address.  Reads
    and toggles check both the new HMAC identifier and the legacy raw IP so
    existing likes are not orphaned after the privacy hardening change.
    """
    identifier = get_client_like_identifier(request)
    legacy_ip = _get_client_ip(request)
    return [value for value in (identifier, legacy_ip) if value]


def _get_like_counts(record_ids):
    counts = dict(
        SongRecordLike.objects.filter(song_record_id__in=record_ids)
        .values('song_record_id')
        .annotate(count=Count('id'))
        .values_list('song_record_id', 'count')
    )
    return {rid: counts.get(rid, 0) for rid in record_ids}


def _get_user_likes(record_ids, request):
    return set(
        SongRecordLike.objects.filter(
            song_record_id__in=record_ids,
            ip_address__in=_get_client_identifier_candidates(request),
        ).values_list('song_record_id', flat=True)
    )


def _parse_record_ids(ids_param):
    if not ids_param:
        raise ValidationError('缺少 ids 参数')

    try:
        record_ids = [int(x.strip()) for x in ids_param.split(',') if x.strip()]
    except (TypeError, ValueError):
        raise ValidationError('无效的 ids 参数')

    if not record_ids:
        raise ValidationError('缺少 ids 参数')
    if any(record_id <= 0 for record_id in record_ids):
        raise ValidationError('无效的 ids 参数')
    if len(record_ids) > MAX_STATUS_IDS:
        raise ValidationError(f'一次最多查询 {MAX_STATUS_IDS} 条记录')

    # De-duplicate while preserving input order so the response remains stable.
    return list(dict.fromkeys(record_ids))


@require_GET
def get_like_status(request):
    try:
        record_ids = _parse_record_ids(request.GET.get('ids', ''))
    except ValidationError as exc:
        return JsonResponse({'error': exc.messages[0]}, status=400)

    like_counts = _get_like_counts(record_ids)
    user_likes = _get_user_likes(record_ids, request)

    result = {}
    for rid in record_ids:
        result[str(rid)] = {
            'like_count': like_counts.get(rid, 0),
            'user_liked': rid in user_likes,
        }

    return JsonResponse({'success': True, 'data': result})


@csrf_exempt
@require_http_methods(["POST"])
def toggle_like(request):
    try:
        body = json.loads(request.body)
        song_record_id = int(body.get('song_record_id', 0))
        if song_record_id <= 0:
            return JsonResponse({'error': '缺少 song_record_id'}, status=400)
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'error': '无效的请求参数'}, status=400)

    try:
        song_record = SongRecord.objects.only('id', 'song_id').get(id=song_record_id)
    except SongRecord.DoesNotExist:
        return JsonResponse({'error': '演唱记录不存在'}, status=404)

    identifier = get_client_like_identifier(request)
    identifier_candidates = _get_client_identifier_candidates(request)

    with transaction.atomic():
        existing = SongRecordLike.objects.filter(
            song_record_id=song_record_id,
            ip_address__in=identifier_candidates,
        ).first()

        if existing:
            existing.delete()
            count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
            clear_cache_pattern(f'song_records:{song_record.song_id}')
            return JsonResponse({
                'success': True,
                'liked': False,
                'like_count': count,
                'action': 'unlike',
            })

        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_count = SongRecordLike.objects.filter(
            song_record_id=song_record_id,
            created_at__gte=one_hour_ago,
        ).count()

        if recent_count >= HOURLY_LIKE_LIMIT:
            count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
            return JsonResponse({
                'success': False,
                'error': '该记录短时间内点赞过多，请稍后再试',
                'like_count': count,
            }, status=429)

        try:
            SongRecordLike.objects.create(
                song_record_id=song_record_id,
                ip_address=identifier,
            )
        except IntegrityError:
            count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
            clear_cache_pattern(f'song_records:{song_record.song_id}')
            return JsonResponse({
                'success': True,
                'liked': True,
                'like_count': count,
                'action': 'already_liked',
            })

        count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
        clear_cache_pattern(f'song_records:{song_record.song_id}')
        return JsonResponse({
            'success': True,
            'liked': True,
            'like_count': count,
            'action': 'like',
        })
