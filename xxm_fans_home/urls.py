"""
URL configuration for xxm_fans_home project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from rest_framework import permissions
from site_settings.api.views import SitemapView, RobotsTxtView

urlpatterns = [
    # SEO 相关 - 根路径访问（直接引入视图，不通过 site_settings.urls）
    path('sitemap.xml', SitemapView.as_view(), name='sitemap'),
    path('robots.txt', RobotsTxtView.as_view(), name='robots-txt'),
    # API 路由
    path('api/', include('song_management.urls')),  # song_management 应用路由（替代main）
    path('api/data-analytics/', include('data_analytics.urls')),  # data_analytics 应用路由
    path('api/site-settings/', include('site_settings.urls')),  # site_settings 应用路由
    path('api/fansDIY/', include('fansDIY.urls')),
    path('api/gallery/', include('gallery.urls')),  # gallery 应用路由
    path('api/', include('livestream.api.urls')),  # livestream 应用路由
    # 保持API兼容性：冰洁和乐游API都指向songlist应用
    path('api/youyou/', include('songlist.urls')),
    path('api/bingjie/', include('songlist.urls')),
    # 新增：songlist独立路由
    path('api/songlist/', include('songlist.urls')),
    path('admin/', admin.site.urls),
    # 为youyou_SongList_frontend/photos目录提供静态文件服务
    re_path(r'^youyou_SongList_frontend/photos/(?P<path>.*)$', serve, {
        'document_root': settings.BASE_DIR / 'youyou_SongList_frontend' / 'photos',
    }),
    # 为bingjie_SongList_frontend/photos目录提供静态文件服务
    re_path(r'^bingjie_SongList_frontend/photos/(?P<path>.*)$', serve, {
        'document_root': settings.BASE_DIR / 'bingjie_SongList_frontend' / 'photos',
    }),
    # 为songlist_frontend/photos目录提供静态文件服务
    re_path(r'^songlist_frontend/photos/(?P<path>.*)$', serve, {
        'document_root': settings.BASE_DIR / 'songlist_frontend' / 'photos',
    }),
    # 为gallery目录提供静态文件服务
    re_path(r'^gallery/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT / 'gallery',
    }),
]

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
