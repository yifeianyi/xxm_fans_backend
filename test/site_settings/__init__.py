"""
Site Settings 应用测试
"""
from .test_settings_service import SettingsServiceTest
from .test_recommendation_service import RecommendationServiceTest
from .test_views import SiteSettingsViewTest
from .test_admin import SiteSettingsAdminTest, RecommendationAdminTest

__all__ = [
    'SettingsServiceTest',
    'RecommendationServiceTest',
    'SiteSettingsViewTest',
    'SiteSettingsAdminTest',
    'RecommendationAdminTest',
]