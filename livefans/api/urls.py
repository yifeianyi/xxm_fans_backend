from django.urls import path
from . import views

urlpatterns = [
    path('ranking/attendance/', views.AttendanceRankingView.as_view(), name='fans-attendance-ranking'),
    path('ranking/danmaku/', views.DanmakuRankingView.as_view(), name='fans-danmaku-ranking'),
    path('search/', views.FanSearchView.as_view(), name='fans-search'),
    path('profile/<str:uid>/', views.FanProfileView.as_view(), name='fans-profile'),
    path('stats/', views.FansStatsView.as_view(), name='fans-stats'),
]
