from rest_framework import serializers

from fansDIY.models import Collection, Work


class CollectionSerializer(serializers.ModelSerializer):
    """合集序列化器"""
    
    class Meta:
        model = Collection
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkSerializer(serializers.ModelSerializer):
    """作品序列化器"""
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    
    class Meta:
        model = Work
        fields = '__all__'
        read_only_fields = ['id']
