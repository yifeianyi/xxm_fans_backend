from django.urls import path, include
from . import views

app_name = 'bingjie_SongList'
urlpatterns = [
    path('songs/', views.song_list, name='song_list'),
    path('languages/', views.get_languages, name='get_languages'),
    path('styles/', views.get_styles, name='get_styles'),
    path('random-song/', views.get_random_song, name='get_random_song'),
    path('site-settings/', views.site_settings, name='site_settings'),
    path('favicon.ico', views.favicon, name='favicon'),
]