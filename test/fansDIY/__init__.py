"""
FansDIY 应用测试
"""
from .test_diy_service import DIYServiceTest
from .test_views import FansDIYViewTest
from .test_admin import CollectionAdminTest, WorkAdminTest, AdminIntegrationTest

__all__ = [
    'DIYServiceTest',
    'FansDIYViewTest',
    'CollectionAdminTest',
    'WorkAdminTest',
    'AdminIntegrationTest',
]
