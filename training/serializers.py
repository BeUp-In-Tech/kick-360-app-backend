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
    category = serializers.SlugRelatedField(slug_field='title', read_only=True)
    video_url = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = ['id', 'category', 'title', 'subtitle', 'description', 'equipment_used', 'steps', 'video_file', 'video_url', 'thumbnail', 'duration_seconds', 'points', 'score_required', 'is_published', 'created_at']

    @extend_schema_field(OpenApiTypes.URI)
    def get_thumbnail(self, obj):
        if obj.thumbnail:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None

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
    video_file = serializers.SerializerMethodField()

    class Meta:
        model = TrainingCompletion
        fields = ['id', 'user', 'training_session', 'score_achieved', 'points_awarded', 'video_file', 'thumbnail', 'created_at']

    @extend_schema_field(OpenApiTypes.URI)
    def get_video_file(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None

class CompleteTrainingRequestSerializer(serializers.Serializer):
    score_achieved = serializers.IntegerField(default=0)
    video_file = serializers.FileField(required=False, allow_null=True)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
