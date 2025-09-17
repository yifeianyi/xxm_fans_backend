from rest_framework import serializers
from .models import Songs, SongRecord, Style, SongStyle, Recommendation

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
    styles = StyleSerializer(many=True, read_only=True)
    records = SongRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Songs
        fields = '__all__'

class SongStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongStyle
        fields = '__all__'

class RecommendationSerializer(serializers.ModelSerializer):
    recommended_songs = SongsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recommendation
        fields = '__all__'