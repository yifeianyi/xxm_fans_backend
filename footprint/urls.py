from django.urls import path
from . import views

app_name = 'footprint'

urlpatterns = [
    # 合集相关API
    path('collections/', views.collection_list_api, name='collection_list'),
    path('collections/<int:collection_id>/', views.collection_detail_api, name='collection_detail'),
    
    # 作品相关API
    path('works/', views.work_list_api, name='work_list'),
    path('works/<int:work_id>/', views.work_detail_api, name='work_detail'),
] 