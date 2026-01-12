"""
API 序列化器
"""
from rest_framework import serializers
from ..models import Song, SongRecord, Style, Tag


class SongSerializer(serializers.ModelSerializer):
    """歌曲序列化器"""
    styles = serializers.ListField(read_only=True)
    tags = serializers.ListField(read_only=True)

    class Meta:
        model = Song
        fields = [
            'id',
            'song_name',
            'singer',
            'last_performed',
            'perform_count',
            'language',
            'styles',
            'tags',
        ]


class SongRecordSerializer(serializers.ModelSerializer):
    """演唱记录序列化器"""
    song_name = serializers.CharField(source='song.song_name', read_only=True)

    class Meta:
        model = SongRecord
        fields = [
            'id',
            'song',
            'song_name',
            'performed_at',
            'url',
            'notes',
            'cover_url',
        ]


class StyleSerializer(serializers.ModelSerializer):
    """曲风序列化器"""
    song_count = serializers.SerializerMethodField()

    class Meta:
        model = Style
        fields = ['id', 'name', 'description', 'song_count']

    def get_song_count(self, obj):
        return obj.style_songs.count()


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""
    song_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'song_count']

    def get_song_count(self, obj):
        return obj.tag_songs.count()