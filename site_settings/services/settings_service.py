from typing import List, Optional, Dict, Any
from core.cache import cache_result
from core.exceptions import ValidationException, DatabaseException
from django.core.exceptions import ObjectDoesNotExist

from site_settings.models import SiteSettings, Recommendation


class SettingsService:
    """网站设置服务类"""

    @staticmethod
    @cache_result(timeout=3600)
    def get_site_settings() -> Optional[SiteSettings]:
        """
        获取网站设置

        Returns:
            SiteSettings: 网站设置对象，如果不存在则返回None
        """
        try:
            settings = SiteSettings.objects.first()
            return settings
        except Exception as e:
            raise DatabaseException(f"获取网站设置失败: {str(e)}")

    @staticmethod
    def create_site_settings(favicon: Optional[str] = None) -> SiteSettings:
        """
        创建网站设置

        Args:
            favicon: favicon文件路径

        Returns:
            SiteSettings: 创建的网站设置对象

        Raises:
            DatabaseException: 创建失败时抛出
        """
        try:
            settings = SiteSettings.objects.create(favicon=favicon)
            # 清除缓存
            SettingsService.get_site_settings.cache_clear()
            return settings
        except Exception as e:
            raise DatabaseException(f"创建网站设置失败: {str(e)}")

    @staticmethod
    def update_site_settings(settings_id: int, favicon: Optional[str] = None) -> SiteSettings:
        """
        更新网站设置

        Args:
            settings_id: 设置ID
            favicon: favicon文件路径

        Returns:
            SiteSettings: 更新后的网站设置对象

        Raises:
            ValidationException: 设置不存在时抛出
            DatabaseException: 更新失败时抛出
        """
        try:
            settings = SiteSettings.objects.get(id=settings_id)
            if favicon is not None:
                settings.favicon = favicon
            settings.save()
            # 清除缓存
            SettingsService.get_site_settings.cache_clear()
            return settings
        except ObjectDoesNotExist:
            raise ValidationException("网站设置不存在")
        except Exception as e:
            raise DatabaseException(f"更新网站设置失败: {str(e)}")


class RecommendationService:
    """推荐语服务类"""

    @staticmethod
    @cache_result(timeout=1800)
    def get_active_recommendations() -> List[Recommendation]:
        """
        获取所有激活的推荐语

        Returns:
            List[Recommendation]: 推荐语列表
        """
        try:
            recommendations = Recommendation.objects.filter(is_active=True).order_by('-created_at')
            return list(recommendations)
        except Exception as e:
            raise DatabaseException(f"获取推荐语失败: {str(e)}")

    @staticmethod
    @cache_result(timeout=1800)
    def get_recommendation_by_id(recommendation_id: int) -> Optional[Recommendation]:
        """
        根据ID获取推荐语

        Args:
            recommendation_id: 推荐语ID

        Returns:
            Recommendation: 推荐语对象，如果不存在则返回None
        """
        try:
            recommendation = Recommendation.objects.get(id=recommendation_id)
            return recommendation
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            raise DatabaseException(f"获取推荐语失败: {str(e)}")

    @staticmethod
    def create_recommendation(content: str, recommended_songs: Optional[List[int]] = None) -> Recommendation:
        """
        创建推荐语

        Args:
            content: 推荐语内容
            recommended_songs: 推荐的歌曲ID列表

        Returns:
            Recommendation: 创建的推荐语对象

        Raises:
            ValidationException: 内容为空时抛出
            DatabaseException: 创建失败时抛出
        """
        if not content or not content.strip():
            raise ValidationException("推荐语内容不能为空")

        try:
            recommendation = Recommendation.objects.create(content=content)
            if recommended_songs:
                # 导入Song模型以避免循环导入
                from song_management.models import Song
                songs = Song.objects.filter(id__in=recommended_songs)
                recommendation.recommended_songs.set(songs)
            # 清除缓存
            RecommendationService.get_active_recommendations.cache_clear()
            RecommendationService.get_recommendation_by_id.cache_clear()
            return recommendation
        except Exception as e:
            raise DatabaseException(f"创建推荐语失败: {str(e)}")

    @staticmethod
    def update_recommendation(
        recommendation_id: int,
        content: Optional[str] = None,
        is_active: Optional[bool] = None,
        recommended_songs: Optional[List[int]] = None
    ) -> Recommendation:
        """
        更新推荐语

        Args:
            recommendation_id: 推荐语ID
            content: 推荐语内容
            is_active: 是否激活
            recommended_songs: 推荐的歌曲ID列表

        Returns:
            Recommendation: 更新后的推荐语对象

        Raises:
            ValidationException: 推荐语不存在或内容为空时抛出
            DatabaseException: 更新失败时抛出
        """
        try:
            recommendation = Recommendation.objects.get(id=recommendation_id)
            if content is not None:
                if not content or not content.strip():
                    raise ValidationException("推荐语内容不能为空")
                recommendation.content = content
            if is_active is not None:
                recommendation.is_active = is_active
            if recommended_songs is not None:
                from song_management.models import Song
                songs = Song.objects.filter(id__in=recommended_songs)
                recommendation.recommended_songs.set(songs)
            recommendation.save()
            # 清除缓存
            RecommendationService.get_active_recommendations.cache_clear()
            RecommendationService.get_recommendation_by_id.cache_clear()
            return recommendation
        except ObjectDoesNotExist:
            raise ValidationException("推荐语不存在")
        except Exception as e:
            raise DatabaseException(f"更新推荐语失败: {str(e)}")

    @staticmethod
    def delete_recommendation(recommendation_id: int) -> bool:
        """
        删除推荐语

        Args:
            recommendation_id: 推荐语ID

        Returns:
            bool: 删除成功返回True

        Raises:
            ValidationException: 推荐语不存在时抛出
            DatabaseException: 删除失败时抛出
        """
        try:
            recommendation = Recommendation.objects.get(id=recommendation_id)
            recommendation.delete()
            # 清除缓存
            RecommendationService.get_active_recommendations.cache_clear()
            RecommendationService.get_recommendation_by_id.cache_clear()
            return True
        except ObjectDoesNotExist:
            raise ValidationException("推荐语不存在")
        except Exception as e:
            raise DatabaseException(f"删除推荐语失败: {str(e)}")

    @staticmethod
    def get_all_recommendations() -> List[Recommendation]:
        """
        获取所有推荐语（包括未激活的）

        Returns:
            List[Recommendation]: 推荐语列表
        """
        try:
            recommendations = Recommendation.objects.all().order_by('-created_at')
            return list(recommendations)
        except Exception as e:
            raise DatabaseException(f"获取推荐语失败: {str(e)}")