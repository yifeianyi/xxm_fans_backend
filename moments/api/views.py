from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.responses import success_response, error_response, paginated_response
from moments.models import Moment
from .serializers import MomentSerializer


@api_view(['GET'])
def moment_list_api(request):
    source = request.GET.get('source', '').strip()
    page_num = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('limit', 20))

    queryset = Moment.objects.all()
    if source in ('weibo', 'bilibili'):
        queryset = queryset.filter(source=source)

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_num)

    serializer = MomentSerializer(page.object_list, many=True)
    return paginated_response(
        data=serializer.data,
        total=paginator.count,
        page=page_num,
        page_size=page_size,
    )


@api_view(['GET'])
def moment_detail_api(request, moment_id):
    try:
        moment = Moment.objects.get(id=moment_id)
    except Moment.DoesNotExist:
        return error_response(message='动态不存在', code=404)

    serializer = MomentSerializer(moment)
    return success_response(data=serializer.data)
