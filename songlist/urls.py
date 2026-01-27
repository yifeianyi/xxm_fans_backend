from django.urls import path
from . import views

urlpatterns = [
    # 统一的API路由
    path('songs/', views.song_list, name='song-list'),
    path('languages/', views.language_list, name='language-list'),
    path('styles/', views.style_list, name='style-list'),
    path('random-song/', views.random_song, name='random-song'),
    path('site-settings/', views.site_settings, name='site-settings'),
    path('artist-info/', views.get_artist_info, name='artist-info'),
    path('favicon/', views.favicon, name='favicon'),
]