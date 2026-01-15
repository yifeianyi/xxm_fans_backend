"""
API 序列化器
"""
from rest_framework import serializers
from ..models import Song, SongRecord, Style, SongStyle, Tag, SongTag


class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class SongRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongRecord
        fields = '__all__'
        read_only_fields = ('song',)  # song字段在创建时由URL中的song_id确定


class SongSerializer(serializers.ModelSerializer):
    styles = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = '__all__'

    def get_styles(self, obj):
        """获取歌曲的曲风名称列表"""
        return obj.styles

    def get_tags(self, obj):
        """获取歌曲的标签名称列表"""
        return obj.tags


class SongStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongStyle
        fields = '__all__'


class SongTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongTag
        fields = '__all__'
