from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status

from core.responses import success_response, error_response, created_response, updated_response
from core.exceptions import ValidationException, DatabaseException

from site_settings.models import SiteSettings, Recommendation, Milestone
from site_settings.services import SettingsService, RecommendationService, MilestoneService
from site_settings.api.serializers import SiteSettingsSerializer, RecommendationSerializer, MilestoneSerializer


class SiteSettingsView(APIView):
    """网站设置视图"""

    def get(self, request):
        """
        获取网站设置
        """
        try:
            settings = SettingsService.get_site_settings()
            if not settings:
                return success_response(data=None, message="暂无网站设置")
            serializer = SiteSettingsSerializer(settings)
            return success_response(data=serializer.data, message="获取网站设置成功")
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        创建网站设置
        """
        try:
            serializer = SiteSettingsSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

            settings = SettingsService.create_site_settings(
                favicon=request.data.get('favicon')
            )
            serializer = SiteSettingsSerializer(settings)
            return created_response(data=serializer.data, message="创建网站设置成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        """
        更新网站设置
        """
        try:
            settings = SettingsService.get_site_settings()
            if not settings:
                return error_response(message="网站设置不存在", status_code=status.HTTP_404_NOT_FOUND)

            serializer = SiteSettingsSerializer(settings, data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

            updated_settings = SettingsService.update_site_settings(
                settings_id=settings.id,
                favicon=request.data.get('favicon')
            )
            serializer = SiteSettingsSerializer(updated_settings)
            return updated_response(data=serializer.data, message="更新网站设置成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecommendationListView(APIView):
    """推荐语列表视图"""

    def get(self, request):
        """
        获取推荐语列表
        """
        try:
            # 获取查询参数
            is_active = request.query_params.get('is_active')
            all_recommendations = request.query_params.get('all', 'false').lower() == 'true'

            if all_recommendations:
                # 获取所有推荐语
                recommendations = RecommendationService.get_all_recommendations()
            else:
                # 只获取激活的推荐语
                recommendations = RecommendationService.get_active_recommendations()

            serializer = RecommendationSerializer(recommendations, many=True)
            return success_response(data=serializer.data, message="获取推荐语列表成功")
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        创建推荐语
        """
        try:
            serializer = RecommendationSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

            recommendation = RecommendationService.create_recommendation(
                content=request.data.get('content'),
                recommended_songs=request.data.get('recommended_songs')
            )
            serializer = RecommendationSerializer(recommendation)
            return created_response(data=serializer.data, message="创建推荐语成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecommendationDetailView(APIView):
    """推荐语详情视图"""

    def get(self, request, pk):
        """
        获取推荐语详情
        """
        try:
            recommendation = RecommendationService.get_recommendation_by_id(pk)
            if not recommendation:
                return error_response(message="推荐语不存在", status_code=status.HTTP_404_NOT_FOUND)

            serializer = RecommendationSerializer(recommendation)
            return success_response(data=serializer.data, message="获取推荐语详情成功")
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """
        更新推荐语
        """
        try:
            serializer = RecommendationSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

            recommendation = RecommendationService.update_recommendation(
                recommendation_id=pk,
                content=request.data.get('content'),
                is_active=request.data.get('is_active'),
                recommended_songs=request.data.get('recommended_songs')
            )
            serializer = RecommendationSerializer(recommendation)
            return updated_response(data=serializer.data, message="更新推荐语成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """
        删除推荐语
        """
        try:
            RecommendationService.delete_recommendation(pk)
            return success_response(data=None, message="删除推荐语成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MilestoneListView(APIView):
    """里程碑列表视图"""

    def get(self, request):
        """
        获取里程碑列表
        """
        try:
            milestones = MilestoneService.get_all_milestones()
            serializer = MilestoneSerializer(milestones, many=True)
            return success_response(data=serializer.data, message="获取里程碑列表成功")
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        创建里程碑
        """
        try:
            serializer = MilestoneSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

            milestone = MilestoneService.create_milestone(
                date=request.data.get('date'),
                title=request.data.get('title'),
                description=request.data.get('description'),
                display_order=request.data.get('display_order', 0)
            )
            serializer = MilestoneSerializer(milestone)
            return created_response(data=serializer.data, message="创建里程碑成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MilestoneDetailView(APIView):
    """里程碑详情视图"""

    def get(self, request, pk):
        """
        获取里程碑详情
        """
        try:
            milestone = MilestoneService.get_milestone_by_id(pk)
            if not milestone:
                return error_response(message="里程碑不存在", status_code=status.HTTP_404_NOT_FOUND)

            serializer = MilestoneSerializer(milestone)
            return success_response(data=serializer.data, message="获取里程碑详情成功")
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        """
        更新里程碑
        """
        try:
            milestone = MilestoneService.update_milestone(
                milestone_id=pk,
                date=request.data.get('date'),
                title=request.data.get('title'),
                description=request.data.get('description'),
                display_order=request.data.get('display_order')
            )
            serializer = MilestoneSerializer(milestone)
            return updated_response(data=serializer.data, message="更新里程碑成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """
        删除里程碑
        """
        try:
            MilestoneService.delete_milestone(pk)
            return success_response(data=None, message="删除里程碑成功")
        except ValidationException as e:
            return error_response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        except DatabaseException as e:
            return error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.http import HttpResponse
from django.template.loader import render_to_string
from song_management.models import Song
from gallery.models import Gallery


class SitemapView(APIView):
    """动态 Sitemap 视图"""

    def get(self, request):
        """生成 sitemap.xml"""
        try:
            # 基础 URL 列表
            base_urls = [
                {
                    'loc': 'https://www.xxm8777.cn/',
                    'lastmod': '2026-01-26',
                    'changefreq': 'daily',
                    'priority': '1.0'
                },
                {
                    'loc': 'https://www.xxm8777.cn/about',
                    'lastmod': '2026-01-26',
                    'changefreq': 'weekly',
                    'priority': '0.8'
                },
                {
                    'loc': 'https://www.xxm8777.cn/songs',
                    'lastmod': '2026-01-26',
                    'changefreq': 'daily',
                    'priority': '0.9'
                },
                {
                    'loc': 'https://www.xxm8777.cn/gallery',
                    'lastmod': '2026-01-26',
                    'changefreq': 'daily',
                    'priority': '0.8'
                },
                {
                    'loc': 'https://www.xxm8777.cn/fansDIY',
                    'lastmod': '2026-01-26',
                    'changefreq': 'weekly',
                    'priority': '0.7'
                },
                {
                    'loc': 'https://www.xxm8777.cn/live',
                    'lastmod': '2026-01-26',
                    'changefreq': 'weekly',
                    'priority': '0.7'
                },
                {
                    'loc': 'https://www.xxm8777.cn/data',
                    'lastmod': '2026-01-26',
                    'changefreq': 'weekly',
                    'priority': '0.6'
                },
            ]

            # 添加歌曲页面
            songs = Song.objects.all()
            for song in songs:
                base_urls.append({
                    'loc': f'https://www.xxm8777.cn/songs/{song.id}',
                    'lastmod': song.updated_at.strftime('%Y-%m-%d') if hasattr(song, 'updated_at') else '2026-01-26',
                    'changefreq': 'monthly',
                    'priority': '0.7'
                })

            # 添加图集页面
            galleries = Gallery.objects.all()
            for gallery in galleries:
                base_urls.append({
                    'loc': f'https://www.xxm8777.cn/gallery/{gallery.id}',
                    'lastmod': gallery.updated_at.strftime('%Y-%m-%d') if hasattr(gallery, 'updated_at') else '2026-01-26',
                    'changefreq': 'weekly',
                    'priority': '0.6'
                })

            # 生成 XML
            xml_content = render_to_string('sitemap.xml', {'urls': base_urls})
            return HttpResponse(xml_content, content_type='application/xml')
        except Exception as e:
            # 返回基本的 sitemap
            basic_urls = [
                {'loc': 'https://www.xxm8777.cn/', 'priority': '1.0'},
                {'loc': 'https://www.xxm8777.cn/about', 'priority': '0.8'},
                {'loc': 'https://www.xxm8777.cn/songs', 'priority': '0.9'},
            ]
            xml_content = render_to_string('sitemap.xml', {'urls': basic_urls})
            return HttpResponse(xml_content, content_type='application/xml')


class RobotsTxtView(APIView):
    """Robots.txt 视图"""

    def get(self, request):
        """生成 robots.txt"""
        content = """User-agent: *
Allow: /

Disallow: /admin/
Disallow: /api/

Sitemap: https://www.xxm8777.cn/sitemap.xml
"""
        return HttpResponse(content, content_type='text/plain')