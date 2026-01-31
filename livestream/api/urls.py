from django.urls import path
from .views import LivestreamListView, LivestreamDetailView, LivestreamConfigView

urlpatterns = [
    path('livestreams/config/', LivestreamConfigView.as_view(), name='livestream-config'),
    path('livestreams/', LivestreamListView.as_view(), name='livestream-list'),
    path('livestreams/<str:date_str>/', LivestreamDetailView.as_view(), name='livestream-detail'),
]