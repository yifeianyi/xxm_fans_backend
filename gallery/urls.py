from django.urls import path
from .views import gallery_tree, gallery_detail, gallery_images, gallery_children_images, get_thumbnail
from .admin import get_gallery_images

app_name = 'gallery'

urlpatterns = [
    # API 路由
    path('tree/', gallery_tree, name='tree'),
    path('thumbnail/', get_thumbnail, name='thumbnail'),  # 缩略图接口（放在前面，避免被<str:gallery_id>匹配）
    path('<str:gallery_id>/', gallery_detail, name='detail'),
    path('<str:gallery_id>/images/', gallery_images, name='images'),
    path('<str:gallery_id>/children-images/', gallery_children_images, name='children_images'),
    # Admin 路由
    path('admin/<str:gallery_id>/images/', get_gallery_images, name='gallery_images_admin'),
]