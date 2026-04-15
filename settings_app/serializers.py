from rest_framework import serializers
from .models import SavedVideo
from sessions.serializers import SessionSerializer

class SavedVideoSerializer(serializers.ModelSerializer):
    session = SessionSerializer(read_only=True)

    class Meta:
        model = SavedVideo
        fields = ['id', 'session', 'created_at']

class SavedVideoToggleSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=True)
