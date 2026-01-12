from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view

from core.responses import success_response, error_response, paginated_response
from core.exceptions import CollectionNotFoundException, WorkNotFoundException
from fansDIY.services import DIYService


class CollectionListView(APIView):
    """合集列表视图"""
    
    def get(self, request):
        """获取合集列表"""
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('limit', 20))
            result = DIYService.get_collections(page=page, page_size=page_size)
            return success_response(data=result, message="获取合集列表成功")
        except Exception as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CollectionDetailView(APIView):
    """合集详情视图"""
    
    def get(self, request, collection_id):
        """获取合集详情"""
        try:
            result = DIYService.get_collection_by_id(collection_id)
            return success_response(data=result, message="获取合集详情成功")
        except CollectionNotFoundException as e:
            return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkListView(APIView):
    """作品列表视图"""
    
    def get(self, request):
        """获取作品列表"""
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('limit', 20))
            collection_id = request.GET.get('collection')
            
            if collection_id:
                collection_id = int(collection_id)
            
            result = DIYService.get_works(page=page, page_size=page_size, collection_id=collection_id)
            return success_response(data=result, message="获取作品列表成功")
        except Exception as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkDetailView(APIView):
    """作品详情视图"""
    
    def get(self, request, work_id):
        """获取作品详情"""
        try:
            result = DIYService.get_work_by_id(work_id)
            return success_response(data=result, message="获取作品详情成功")
        except WorkNotFoundException as e:
            return error_response(message=str(e), status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
