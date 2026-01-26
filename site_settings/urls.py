from django.urls import path
from site_settings.api.views import (
    SiteSettingsView,
    RecommendationListView,
    RecommendationDetailView,
    MilestoneListView,
    MilestoneDetailView,
)

app_name = 'site_settings'

urlpatterns = [
    # 网站设置
    path('settings/', SiteSettingsView.as_view(), name='site-settings'),

    # 推荐语 - 根路径（用于 /api/recommendation/）
    path('', RecommendationListView.as_view(), name='recommendation-root'),

    # 推荐语 - 详细路径
    path('recommendations/', RecommendationListView.as_view(), name='recommendation-list'),
    path('recommendations/<int:pk>/', RecommendationDetailView.as_view(), name='recommendation-detail'),

    # 里程碑
    path('milestones/', MilestoneListView.as_view(), name='milestone-list'),
    path('milestones/<int:pk>/', MilestoneDetailView.as_view(), name='milestone-detail'),
]