from django.urls import path
from .views import gallery_tree, gallery_detail, gallery_images, gallery_children_images
from .admin import get_gallery_images

app_name = 'gallery'

urlpatterns = [
    # API 路由
    path('tree/', gallery_tree, name='tree'),
    path('<str:gallery_id>/', gallery_detail, name='detail'),
    path('<str:gallery_id>/images/', gallery_images, name='images'),
    path('<str:gallery_id>/children-images/', gallery_children_images, name='children_images'),
    # Admin 路由
    path('admin/<str:gallery_id>/images/', get_gallery_images, name='gallery_images_admin'),
]