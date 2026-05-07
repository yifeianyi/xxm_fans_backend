from rest_framework import serializers
from moments.models import Moment


class MomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moment
        fields = [
            'id', 'source', 'source_id', 'content', 'images',
            'publish_time', 'like_count', 'comment_count', 'share_count',
            'source_url', 'video_bvid', 'video_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
