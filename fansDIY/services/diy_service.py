from django.core.paginator import Paginator
from django.db import transaction

from core.cache import cache_result
from core.exceptions import CollectionNotFoundException, WorkNotFoundException, DatabaseException

from fansDIY.models import Collection, Work


class DIYService:
    """粉丝二创服务类"""
    
    @staticmethod
    @cache_result(timeout=300)
    def get_collections(page=1, page_size=20):
        """
        获取合集列表
        
        Args:
            page: 页码
            page_size: 每页数量
            
        Returns:
            dict: 包含分页信息和合集列表的字典
        """
        try:
            collections = Collection.objects.all().order_by('position', 'display_order', '-created_at')
            paginator = Paginator(collections, page_size)
            page = paginator.get_page(page)
            
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
            
            return {
                "total": paginator.count,
                "page": page.number,
                "page_size": paginator.per_page,
                "results": results
            }
        except Exception as e:
            raise DatabaseException(f"获取合集列表失败: {str(e)}")
    
    @staticmethod
    @cache_result(timeout=300)
    def get_collection_by_id(collection_id):
        """
        根据ID获取合集详情
        
        Args:
            collection_id: 合集ID
            
        Returns:
            dict: 合集详情
            
        Raises:
            CollectionNotFoundException: 合集不存在
        """
        try:
            collection = Collection.objects.get(id=collection_id)
            return {
                "id": collection.id,
                "name": collection.name,
                "works_count": collection.works_count,
                "position": collection.position,
                "display_order": collection.display_order,
                "created_at": collection.created_at,
                "updated_at": collection.updated_at,
            }
        except Collection.DoesNotExist:
            raise CollectionNotFoundException(f"合集ID {collection_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"获取合集详情失败: {str(e)}")
    
    @staticmethod
    @cache_result(timeout=300)
    def get_works(page=1, page_size=20, collection_id=None):
        """
        获取作品列表
        
        Args:
            page: 页码
            page_size: 每页数量
            collection_id: 合集ID（可选）
            
        Returns:
            dict: 包含分页信息和作品列表的字典
        """
        try:
            works = Work.objects.all().order_by('position', 'display_order', '-id')
            
            if collection_id:
                works = works.filter(collection_id=collection_id)
            
            paginator = Paginator(works, page_size)
            page = paginator.get_page(page)
            
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
            
            return {
                "total": paginator.count,
                "page": page.number,
                "page_size": paginator.per_page,
                "results": results
            }
        except Exception as e:
            raise DatabaseException(f"获取作品列表失败: {str(e)}")
    
    @staticmethod
    @cache_result(timeout=300)
    def get_work_by_id(work_id):
        """
        根据ID获取作品详情
        
        Args:
            work_id: 作品ID
            
        Returns:
            dict: 作品详情
            
        Raises:
            WorkNotFoundException: 作品不存在
        """
        try:
            work = Work.objects.get(id=work_id)
            return {
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
        except Work.DoesNotExist:
            raise WorkNotFoundException(f"作品ID {work_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"获取作品详情失败: {str(e)}")
    
    @staticmethod
    def create_collection(name, position=0, display_order=0):
        """
        创建合集
        
        Args:
            name: 合集名称
            position: 位置
            display_order: 显示顺序
            
        Returns:
            Collection: 创建的合集对象
        """
        try:
            collection = Collection.objects.create(
                name=name,
                position=position,
                display_order=display_order
            )
            return collection
        except Exception as e:
            raise DatabaseException(f"创建合集失败: {str(e)}")
    
    @staticmethod
    def update_collection(collection_id, **kwargs):
        """
        更新合集
        
        Args:
            collection_id: 合集ID
            **kwargs: 要更新的字段
            
        Returns:
            Collection: 更新后的合集对象
        """
        try:
            collection = Collection.objects.get(id=collection_id)
            for key, value in kwargs.items():
                setattr(collection, key, value)
            collection.save()
            return collection
        except Collection.DoesNotExist:
            raise CollectionNotFoundException(f"合集ID {collection_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"更新合集失败: {str(e)}")
    
    @staticmethod
    def delete_collection(collection_id):
        """
        删除合集
        
        Args:
            collection_id: 合集ID
            
        Returns:
            bool: 删除成功返回True
        """
        try:
            collection = Collection.objects.get(id=collection_id)
            collection.delete()
            return True
        except Collection.DoesNotExist:
            raise CollectionNotFoundException(f"合集ID {collection_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"删除合集失败: {str(e)}")
    
    @staticmethod
    def create_work(collection_id, title, author, **kwargs):
        """
        创建作品
        
        Args:
            collection_id: 合集ID
            title: 作品标题
            author: 作者
            **kwargs: 其他字段
            
        Returns:
            Work: 创建的作品对象
        """
        try:
            collection = Collection.objects.get(id=collection_id)
            work = Work.objects.create(
                collection=collection,
                title=title,
                author=author,
                **kwargs
            )
            return work
        except Collection.DoesNotExist:
            raise CollectionNotFoundException(f"合集ID {collection_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"创建作品失败: {str(e)}")
    
    @staticmethod
    def update_work(work_id, **kwargs):
        """
        更新作品
        
        Args:
            work_id: 作品ID
            **kwargs: 要更新的字段
            
        Returns:
            Work: 更新后的作品对象
        """
        try:
            work = Work.objects.get(id=work_id)
            for key, value in kwargs.items():
                setattr(work, key, value)
            work.save()
            return work
        except Work.DoesNotExist:
            raise WorkNotFoundException(f"作品ID {work_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"更新作品失败: {str(e)}")
    
    @staticmethod
    def delete_work(work_id):
        """
        删除作品
        
        Args:
            work_id: 作品ID
            
        Returns:
            bool: 删除成功返回True
        """
        try:
            work = Work.objects.get(id=work_id)
            work.delete()
            return True
        except Work.DoesNotExist:
            raise WorkNotFoundException(f"作品ID {work_id} 不存在")
        except Exception as e:
            raise DatabaseException(f"删除作品失败: {str(e)}")
