from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import json

from ..models import SongRecordLike

HOURLY_LIKE_LIMIT = 100


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _get_like_counts(record_ids):
    counts = dict(
        SongRecordLike.objects.filter(song_record_id__in=record_ids)
        .values('song_record_id')
        .annotate(count=Count('id'))
        .values_list('song_record_id', 'count')
    )
    return {rid: counts.get(rid, 0) for rid in record_ids}


def _get_user_likes(record_ids, ip):
    return set(
        SongRecordLike.objects.filter(song_record_id__in=record_ids, ip_address=ip)
        .values_list('song_record_id', flat=True)
    )


def get_like_status(request):
    ids_param = request.GET.get('ids', '')
    if not ids_param:
        return JsonResponse({'error': '缺少 ids 参数'}, status=400)

    try:
        record_ids = [int(x.strip()) for x in ids_param.split(',') if x.strip()]
    except ValueError:
        return JsonResponse({'error': '无效的 ids 参数'}, status=400)

    ip = _get_client_ip(request)
    like_counts = _get_like_counts(record_ids)
    user_likes = _get_user_likes(record_ids, ip)

    result = {}
    for rid in record_ids:
        result[str(rid)] = {'like_count': like_counts.get(rid, 0), 'user_liked': rid in user_likes}

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

    ip = _get_client_ip(request)
    existing = SongRecordLike.objects.filter(
        song_record_id=song_record_id, ip_address=ip
    ).first()

    if existing:
        existing.delete()
        count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
        return JsonResponse({'success': True, 'liked': False, 'like_count': count, 'action': 'unlike'})

    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_count = SongRecordLike.objects.filter(
        song_record_id=song_record_id, created_at__gte=one_hour_ago
    ).count()

    if recent_count >= HOURLY_LIKE_LIMIT:
        count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
        return JsonResponse({
            'success': False,
            'error': '该记录短时间内点赞过多，请稍后再试',
            'like_count': count,
        }, status=429)

    try:
        SongRecordLike.objects.create(song_record_id=song_record_id, ip_address=ip)
    except IntegrityError:
        count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
        return JsonResponse({'success': True, 'liked': True, 'like_count': count, 'action': 'already_liked'})

    count = SongRecordLike.objects.filter(song_record_id=song_record_id).count()
    return JsonResponse({'success': True, 'liked': True, 'like_count': count, 'action': 'like'})
