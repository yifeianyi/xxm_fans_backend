from rest_framework import serializers
from .models import Songs, SongRecord, Style, SongStyle

class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Style
        fields = '__all__'

class SongRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongRecord
        fields = '__all__'
        read_only_fields = ('song',)  # song字段在创建时由URL中的song_id确定

class SongsSerializer(serializers.ModelSerializer):
    styles = serializers.SerializerMethodField()
    
    class Meta:
        model = Songs
        fields = '__all__'
    
    def get_styles(self, obj):
        # 获取歌曲关联的曲风名称列表
        return [song_style.style.name for song_style in obj.songstyle_set.all()]

class SongStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongStyle
        fields = '__all__'