from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, FileResponse
from django.core.files.storage import default_storage
from core.responses import success_response, error_response
from .models import Gallery
from .utils import ThumbnailGenerator


def to_media_url(path):
    """将 /gallery/ 路径转换为 /media/gallery/ 路径"""
    if path and path.startswith('/gallery/'):
        return path.replace('/gallery/', '/media/gallery/', 1)
    return path


import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def gallery_tree(request):
    """获取图集树结构"""
    try:
        # 优化: 一次性获取所有活跃图集，避免递归查询数据库
        all_galleries = list(
            Gallery.objects.filter(is_active=True).order_by('sort_order', 'id')
        )
        
        # 构建父子关系映射
        children_map = {}
        for gallery in all_galleries:
            if gallery.parent_id:
                children_map.setdefault(gallery.parent_id, []).append(gallery)

        def build_tree(gallery):
            data = {
                'id': gallery.id,
                'title': gallery.title,
                'description': gallery.description,
                'cover_url': gallery.cover_url,
                'cover_thumbnail_url': gallery.get_cover_thumbnail_url(),
                'level': gallery.level,
                'image_count': gallery.image_count,
                'folder_path': gallery.folder_path,
                'tags': gallery.tags,
                'created_at': gallery.created_at.isoformat() if gallery.created_at else None,
            }

            # 从内存映射中获取子图集，避免数据库查询
            children = children_map.get(gallery.id, [])
            if children:
                data['children'] = [build_tree(child) for child in children]

            return data

        # 仅获取根图集进行遍历
        root_galleries = [g for g in all_galleries if g.parent_id is None]
        tree = [build_tree(gallery) for gallery in root_galleries]

        return success_response(tree, '获取图集树成功')
    except Exception as e:
        logger.error(f"获取图集树失败: {e}", exc_info=True)
        return error_response(f"获取图集树失败: {str(e)}")


@api_view(['GET'])
def gallery_detail(request, gallery_id):
    """获取图集详情"""
    try:
        # 优化: 使用 prefetch_related 预取子图集
        gallery = Gallery.objects.prefetch_related('children').get(id=gallery_id, is_active=True)

        data = {
            'id': gallery.id,
            'title': gallery.title,
            'description': gallery.description,
            'cover_url': gallery.cover_url,
            'cover_thumbnail_url': gallery.get_cover_thumbnail_url(),
            'level': gallery.level,
            'image_count': gallery.image_count,
            'folder_path': gallery.folder_path,
            'tags': gallery.tags,
            'is_leaf': gallery.is_leaf(),
            'breadcrumbs': gallery.get_breadcrumbs(),
            'created_at': gallery.created_at.isoformat() if gallery.created_at else None,
        }

        # 获取子图集（已从 prefetch_related 缓存中获取）
        children = gallery.children.filter(is_active=True).order_by('sort_order', 'id')

        if children.exists():
            data['children'] = [{
                'id': child.id,
                'title': child.title,
                'description': child.description,
                'cover_url': child.cover_url,
                'cover_thumbnail_url': child.get_cover_thumbnail_url(),
                'level': child.level,
                'image_count': child.image_count,
                'folder_path': child.folder_path,
                'tags': child.tags,
                'is_leaf': child.is_leaf(),
            } for child in children]

        return success_response(data, '获取图集详情成功')
    except Gallery.DoesNotExist:
        return error_response('图集不存在', status_code=404)
    except Exception as e:
        logger.error(f"获取图集详情失败: {e}", exc_info=True)
        return error_response(f"获取图集详情失败: {str(e)}")


@api_view(['GET'])
def gallery_images(request, gallery_id):
    """获取图集图片列表"""
    try:
        gallery = Gallery.objects.get(id=gallery_id, is_active=True)
        images = gallery.get_images()

        # 构建图片列表
        image_list = []
        for img in images:
            # 使用核心缩略图生成器获取缩略图 URL
            thumbnail_url = ThumbnailGenerator.get_thumbnail_url(img['url'])
            image_list.append({
                'url': img['url'],
                'thumbnail_url': thumbnail_url,
                'title': img['title'],
                'filename': img['filename'],
            })

        return success_response({
            'images': image_list,
            'total': len(image_list)
        }, '获取图片列表成功')
    except Gallery.DoesNotExist:
        return error_response('图集不存在', status_code=404)
    except Exception as e:
        logger.error(f"获取图片列表失败: {e}", exc_info=True)
        return error_response(f"获取图片列表失败: {str(e)}")


@api_view(['GET'])
def gallery_children_images(request, gallery_id):
    """获取父图集下所有子图集的图片，按子图集分组返回"""
    try:
        gallery = Gallery.objects.get(id=gallery_id, is_active=True)

        # 如果是叶子节点，返回自己的图片
        if gallery.is_leaf():
            images = gallery.get_images()
            # 为每张图片添加缩略图 URL
            for img in images:
                img['thumbnail_url'] = ThumbnailGenerator.get_thumbnail_url(img['url'])
            return success_response({
                'gallery': {
                    'id': gallery.id,
                    'title': gallery.title,
                    'description': gallery.description,
                    'cover_url': gallery.cover_url,
                    'cover_thumbnail_url': gallery.get_cover_thumbnail_url(),
                    'image_count': gallery.image_count,
                    'folder_path': gallery.folder_path,
                    'tags': gallery.tags,
                },
                'images': images,
                'total': len(images)
            }, '获取图片列表成功')

        # 如果是父节点，返回所有子图集的图片
        children_images = gallery.get_all_children_images()
        # 为每张图片添加缩略图 URL
        for item in children_images:
            item['gallery']['cover_thumbnail_url'] = ThumbnailGenerator.get_thumbnail_url(
                item['gallery']['cover_url']
            )
            for img in item['images']:
                img['thumbnail_url'] = ThumbnailGenerator.get_thumbnail_url(img['url'])
        total_images = sum(len(item['images']) for item in children_images)

        return success_response({
            'children': children_images,
            'total_galleries': len(children_images),
            'total_images': total_images
        }, '获取子图集图片成功')
    except Gallery.DoesNotExist:
        return error_response('图集不存在', status_code=404)
    except Exception as e:
        logger.error(f"获取子图集图片失败: {e}", exc_info=True)
        return error_response(f"获取子图集图片失败: {str(e)}")


@api_view(['GET'])
def get_thumbnail(request):
    """获取图片缩略图"""
    image_path = request.GET.get('path')

    if not image_path:
        return HttpResponse('Missing path parameter', status=400)

    # 生成缩略图
    thumbnail_path = ThumbnailGenerator.generate_thumbnail(image_path)

    # 返回缩略图
    try:
        if default_storage.exists(thumbnail_path):
            file = default_storage.open(thumbnail_path, 'rb')
            response = FileResponse(file)
            response['Cache-Control'] = 'public, max-age=31536000'
            response['Content-Type'] = 'image/webp'
            return response
        else:
            # 降级到原图
            if default_storage.exists(image_path):
                file = default_storage.open(image_path, 'rb')
                response = FileResponse(file)
                response['Cache-Control'] = 'public, max-age=86400'
                return response
            else:
                return HttpResponse('Image not found', status=404)
    except Exception as e:
        logger.error(f"生成缩略图失败: {e}", exc_info=True)
        return HttpResponse(f'Error: {str(e)}', status=500)