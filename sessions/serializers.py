from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Session

class SessionSerializer(serializers.ModelSerializer):
    video_file = serializers.SerializerMethodField()
    session_id = serializers.UUIDField(source='id', read_only=True)
    sessionId = serializers.UUIDField(source='id', read_only=True)

    class Meta:
        model = Session
        fields = ['id', 'session_id', 'sessionId', 'user', 'total_kick', 'video_file', 'mode', 'is_story', 'is_shared_to_leaderboard', 'session_duration', 'countdown_time', 'created_at']
        read_only_fields = ['id', 'session_id', 'sessionId', 'user', 'created_at']

    @extend_schema_field(OpenApiTypes.URI)
    def get_video_file(self, obj):
        request = self.context.get('request')
        if obj.video_file:
            url = obj.video_file.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

class SessionCompleteSerializer(serializers.Serializer):
    total_kick = serializers.IntegerField(required=True, min_value=0)
    video_file = serializers.FileField(required=False, allow_empty_file=False)
    mode = serializers.ChoiceField(choices=Session.MODE_CHOICES, default='default')
    is_story = serializers.BooleanField(default=False)
    is_shared_to_leaderboard = serializers.BooleanField(default=False)
    session_duration = serializers.IntegerField(default=5)
    countdown_time = serializers.IntegerField(default=3)

class SessionShareToggleSerializer(serializers.Serializer):
    share_type = serializers.ChoiceField(choices=['leaderboard', 'story'])
    state = serializers.BooleanField(required=True)
