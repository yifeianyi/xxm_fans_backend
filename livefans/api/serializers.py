from rest_framework import serializers
from ..models import FanProfile, LiveAttendance


class FanProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanProfile
        fields = [
            'id', 'platform', 'bilibili_uid', 'username',
            'avatar_url', 'first_seen_at', 'created_at'
        ]


class LiveAttendanceSerializer(serializers.ModelSerializer):
    fan_username = serializers.CharField(source='fan.username', read_only=True)
    fan_uid = serializers.CharField(source='fan.bilibili_uid', read_only=True)
    fan_avatar = serializers.CharField(source='fan.avatar_url', read_only=True)
    livestream_date = serializers.DateField(source='livestream.date', read_only=True)
    livestream_title = serializers.CharField(source='livestream.title', read_only=True)

    class Meta:
        model = LiveAttendance
        fields = [
            'id', 'fan', 'fan_username', 'fan_uid', 'fan_avatar',
            'livestream', 'livestream_date', 'livestream_title',
            'has_danmaku', 'danmaku_count', 'has_gift',
            'has_sc', 'has_guard', 'watch_duration_minutes',
            'is_attended', 'first_seen', 'last_seen', 'created_at'
        ]
