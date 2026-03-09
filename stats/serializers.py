from rest_framework import serializers
from .models import PerformanceTrack

class PerformanceTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceTrack
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at']

class PerformanceAIRequestSerializer(serializers.Serializer):
    """
    Matches the AI model response format provided by the user.
    """
    status = serializers.CharField()
    response_code = serializers.IntegerField()
    video_info = serializers.DictField()
    data = serializers.DictField()
    session_id = serializers.UUIDField(required=False)
