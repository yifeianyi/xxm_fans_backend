from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.responses import success_response, error_response
from .models import Gallery


@api_view(['GET'])
def gallery_tree(request):
    """获取图集树结构"""
    try:
        # 获取所有根图集（level=0）
        root_galleries = Gallery.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('sort_order', 'id')

        # 构建树结构
        def build_tree(gallery):
            data = {
                'id': gallery.id,
                'title': gallery.title,
                'description': gallery.description,
                'cover_url': gallery.cover_url,
                'level': gallery.level,
                'image_count': gallery.image_count,
                'folder_path': gallery.folder_path,
                'tags': gallery.tags,
                'created_at': gallery.created_at.isoformat() if gallery.created_at else None,
            }

            # 递归获取子图集
            children = Gallery.objects.filter(
                parent=gallery,
                is_active=True
            ).order_by('sort_order', 'id')

            if children.exists():
                data['children'] = [build_tree(child) for child in children]

            return data

        tree = [build_tree(gallery) for gallery in root_galleries]

        return success_response(tree, '获取图集树成功')
    except Exception as e:
        return error_response(str(e))


@api_view(['GET'])
def gallery_detail(request, gallery_id):
    """获取图集详情"""
    try:
        gallery = Gallery.objects.get(id=gallery_id, is_active=True)

        data = {
            'id': gallery.id,
            'title': gallery.title,
            'description': gallery.description,
            'cover_url': gallery.cover_url,
            'level': gallery.level,
            'image_count': gallery.image_count,
            'folder_path': gallery.folder_path,
            'tags': gallery.tags,
            'is_leaf': gallery.is_leaf(),
            'breadcrumbs': gallery.get_breadcrumbs(),
            'created_at': gallery.created_at.isoformat() if gallery.created_at else None,
        }

        # 获取子图集
        children = Gallery.objects.filter(
            parent=gallery,
            is_active=True
        ).order_by('sort_order', 'id')

        if children.exists():
            data['children'] = [{
                'id': child.id,
                'title': child.title,
                'description': child.description,
                'cover_url': child.cover_url,
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
        return error_response(str(e))


@api_view(['GET'])
def gallery_images(request, gallery_id):
    """获取图集图片列表"""
    try:
        gallery = Gallery.objects.get(id=gallery_id, is_active=True)
        images = gallery.get_images()

        # 构建图片列表
        image_list = []
        for img in images:
            image_list.append({
                'url': img['url'],
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
        return error_response(str(e))


@api_view(['GET'])
def gallery_children_images(request, gallery_id):
    """获取父图集下所有子图集的图片，按子图集分组返回"""
    try:
        gallery = Gallery.objects.get(id=gallery_id, is_active=True)

        # 如果是叶子节点，返回自己的图片
        if gallery.is_leaf():
            images = gallery.get_images()
            return success_response({
                'gallery': {
                    'id': gallery.id,
                    'title': gallery.title,
                    'description': gallery.description,
                    'cover_url': gallery.cover_url,
                    'image_count': gallery.image_count,
                    'folder_path': gallery.folder_path,
                    'tags': gallery.tags,
                },
                'images': images,
                'total': len(images)
            }, '获取图片列表成功')

        # 如果是父节点，返回所有子图集的图片
        children_images = gallery.get_all_children_images()
        total_images = sum(len(item['images']) for item in children_images)

        return success_response({
            'children': children_images,
            'total_galleries': len(children_images),
            'total_images': total_images
        }, '获取子图集图片成功')
    except Gallery.DoesNotExist:
        return error_response('图集不存在', status_code=404)
    except Exception as e:
        return error_response(str(e))