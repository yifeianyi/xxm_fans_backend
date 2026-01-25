from rest_framework import serializers
from site_settings.models import SiteSettings, Recommendation, Milestone


class SiteSettingsSerializer(serializers.ModelSerializer):
    """网站设置序列化器"""
    favicon_url = serializers.SerializerMethodField()
    artist_avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = [
            'id',
            'favicon',
            'favicon_url',
            'artist_name',
            'artist_avatar',
            'artist_avatar_url',
            'artist_birthday',
            'artist_constellation',
            'artist_location',
            'artist_profession',
            'artist_voice_features',
            'bilibili_url',
            'weibo_url',
            'netease_music_url',
            'youtube_url',
            'qq_music_url',
            'xiaohongshu_url',
            'douyin_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_favicon_url(self, obj):
        """获取favicon URL"""
        return obj.favicon_url()

    def get_artist_avatar_url(self, obj):
        """获取艺人头像URL"""
        return obj.artist_avatar_url()


class MilestoneSerializer(serializers.ModelSerializer):
    """里程碑序列化器"""

    class Meta:
        model = Milestone
        fields = ['id', 'date', 'title', 'description', 'display_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class RecommendationSerializer(serializers.ModelSerializer):
    """推荐语序列化器"""
    recommended_songs_details = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = [
            'id', 'content', 'recommended_songs', 'recommended_songs_details',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_recommended_songs_details(self, obj):
        """获取推荐歌曲的详细信息"""
        songs = obj.recommended_songs.all()
        return [
            {
                'id': song.id,
                'song_name': song.song_name,
                'singer': song.singer,
                'language': song.language
            }
            for song in songs
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 动态设置recommended_songs的queryset
        from song_management.models import Song
        self.fields['recommended_songs'] = serializers.PrimaryKeyRelatedField(
            many=True,
            read_only=False,
            required=False,
            queryset=Song.objects.all()
        )