from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from training.models import TrainingCategory, TrainingSession

class AdminTrainingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = [
            'id',
            'title',
            'description',
            'is_active',
            'created_at'
        ]

class AdminTrainingSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/managing Training Sessions with simplified 
    field names as requested by the user.
    """
    Select_category = serializers.SlugRelatedField(
        slug_field='title',
        queryset=TrainingCategory.objects.all(),
        source='category'
    )
    Title = serializers.CharField(source='title')
    Subtitle = serializers.CharField(source='subtitle', required=False, allow_blank=True)
    Equipment_used = serializers.CharField(source='equipment_used', required=False, allow_blank=True)
    Steps = serializers.CharField(source='steps', required=False, allow_blank=True)
    Time = serializers.CharField(source='duration_seconds', help_text="Duration (e.g., '10:00')")
    Points = serializers.IntegerField(source='points', default=0)
    video = serializers.FileField(source='video_file', required=False, allow_null=True)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
    is_pulished = serializers.BooleanField(source='is_published', default=False)
    reattempt = serializers.BooleanField(default=False)
    participate_count = serializers.IntegerField(read_only=True)
    video_watched_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TrainingSession
        fields = [
            'id',
            'Select_category',
            'Title',
            'Subtitle',
            'Equipment_used',
            'Steps',
            'Time',
            'Points',
            'video',
            'thumbnail',
            'is_pulished',
            'reattempt',
            'participate_count',
            'video_watched_count',
            'created_at'
        ]

    def to_representation(self, instance):
        """
        Include category name in the output.
        """
        data = super().to_representation(instance)
        data['category_name'] = instance.category.title if instance.category else None
        return data