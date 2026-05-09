from rest_framework import serializers
from site_settings.models import SiteSettings, Recommendation, Milestone, EmailConfig


class SiteSettingsSerializer(serializers.ModelSerializer):
    """网站设置序列化器"""
    favicon_url = serializers.SerializerMethodField()
    artist_avatar_url = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

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
            'background_image',
            'background_image_url',
            'background_active',
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

    def get_background_image_url(self, obj):
        """获取背景图URL"""
        return obj.background_image_url()


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


class EmailConfigSerializer(serializers.ModelSerializer):
    smtp_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = EmailConfig
        fields = [
            'id', 'smtp_host', 'smtp_port', 'smtp_use_tls',
            'smtp_username', 'smtp_password', 'admin_email',
            'from_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_smtp_port(self, value):
        if not 1 <= value <= 65535:
            raise serializers.ValidationError('端口号必须在 1-65535 之间')
        return value

    def validate_admin_email(self, value):
        if value and '@' not in value:
            raise serializers.ValidationError('请输入有效的邮箱地址')
        return value

    def update(self, instance, validated_data):
        raw_password = validated_data.pop('smtp_password', None)
        if raw_password:
            instance.set_password(raw_password)
        return super().update(instance, validated_data)