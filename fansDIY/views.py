from django.shortcuts import render
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from core.responses import success_response, error_response, paginated_response
from core.exceptions import CollectionNotFoundException, WorkNotFoundException
from .models import Collection, Work

# Create your views here.

@api_view(['GET'])
def collection_list_api(request):
    """获取合集列表"""
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("limit", 20)

    # 按照 position 升序排列，再按 display_order 升序排列，最后按创建时间降序排列
    collections = Collection.objects.all().order_by('position', 'display_order', '-created_at')
    paginator = Paginator(collections, page_size)
    page = paginator.get_page(page_num)

    results = []
    for collection in page.object_list:
        results.append({
            "id": collection.id,
            "name": collection.name,
            "works_count": collection.works_count,
            "position": collection.position,
            "display_order": collection.display_order,
            "created_at": collection.created_at,
            "updated_at": collection.updated_at,
        })

    return paginated_response(
        data=results,
        total=paginator.count,
        page=page.number,
        page_size=page_size,
        message="获取合集列表成功"
    )


@api_view(['GET'])
def collection_detail_api(request, collection_id):
    """获取合集详情"""
    try:
        collection = Collection.objects.get(id=collection_id)
        data = {
            "id": collection.id,
            "name": collection.name,
            "works_count": collection.works_count,
            "position": collection.position,
            "display_order": collection.display_order,
            "created_at": collection.created_at,
            "updated_at": collection.updated_at,
        }
        return success_response(data=data, message="获取合集详情成功")
    except Collection.DoesNotExist:
        raise CollectionNotFoundException(f"合集不存在: {collection_id}")


@api_view(['GET'])
def work_list_api(request):
    """获取作品列表"""
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("limit", 20)
    collection_id = request.GET.get("collection")

    # 按照 position 升序排列，再按 display_order 升序排列，最后按ID降序排列
    works = Work.objects.all().order_by('position', 'display_order', '-id')

    if collection_id:
        works = works.filter(collection_id=collection_id)

    paginator = Paginator(works, page_size)
    page = paginator.get_page(page_num)

    results = []
    for work in page.object_list:
        results.append({
            "id": work.id,
            "title": work.title,
            "cover_url": work.cover_url,
            "view_url": work.view_url,
            "author": work.author,
            "notes": work.notes,
            "position": work.position,
            "display_order": work.display_order,
            "collection": {
                "id": work.collection.id,
                "name": work.collection.name,
            },
        })

    return paginated_response(
        data=results,
        total=paginator.count,
        page=page.number,
        page_size=page_size,
        message="获取作品列表成功"
    )


@api_view(['GET'])
def work_detail_api(request, work_id):
    """获取作品详情"""
    try:
        work = Work.objects.get(id=work_id)
        data = {
            "id": work.id,
            "title": work.title,
            "cover_url": work.cover_url,
            "view_url": work.view_url,
            "author": work.author,
            "notes": work.notes,
            "position": work.position,
            "display_order": work.display_order,
            "collection": {
                "id": work.collection.id,
                "name": work.collection.name,
            },
        }
        return success_response(data=data, message="获取作品详情成功")
    except Work.DoesNotExist:
        raise WorkNotFoundException(f"作品不存在: {work_id}")