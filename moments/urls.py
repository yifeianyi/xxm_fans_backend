from django.urls import path
from .api import views

urlpatterns = [
    path('moments/', views.moment_list_api, name='moment_list'),
    path('moments/<int:moment_id>/', views.moment_detail_api, name='moment_detail'),
]
