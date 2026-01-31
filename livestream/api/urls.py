from django.urls import path
from .views import LivestreamListView, LivestreamDetailView

urlpatterns = [
    path('livestreams/', LivestreamListView.as_view(), name='livestream-list'),
    path('livestreams/<str:date_str>/', LivestreamDetailView.as_view(), name='livestream-detail'),
]