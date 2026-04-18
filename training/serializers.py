from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import TrainingCategory, TrainingCompletion, TrainingSession
from accounts.serializers import UserSerializer

class TrainingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = ['id', 'title', 'description', 'is_active', 'created_at']

class TrainingSessionSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = ['id', 'category', 'title', 'subtitle', 'description', 'equipment_used', 'steps', 'video_file', 'video_url', 'duration_seconds', 'points', 'score_required', 'is_published', 'created_at']

    @extend_schema_field(OpenApiTypes.URI)
    def get_video_url(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None

class TrainingCompletionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    training_session = TrainingSessionSerializer(read_only=True)

    class Meta:
        model = TrainingCompletion
        fields = ['id', 'user', 'training_session', 'score_achieved', 'points_awarded', 'created_at']

class CompleteTrainingRequestSerializer(serializers.Serializer):
    score_achieved = serializers.IntegerField(default=0)
