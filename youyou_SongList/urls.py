from django.urls import path, include
from . import views

app_name = 'youyou_SongList'
urlpatterns = [
    path('songs/', views.song_list, name='song_list'),
    path('site-settings/', views.site_settings, name='site_settings'),
    path('favicon.ico', views.favicon, name='favicon'),
]