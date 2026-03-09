from rest_framework import serializers
from core.models import AdminActionLog

class AdminActivityLogSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='admin.name', read_only=True)
    
    class Meta:
        model = AdminActionLog
        fields = ['id', 'admin_name', 'action', 'target_model', 'target_id', 'details', 'created_at']

class CombinedActivitySerializer(serializers.Serializer):
    type = serializers.CharField() # 'admin' or 'user'
    user = serializers.CharField()
    action = serializers.CharField()
    details = serializers.CharField()
    created_at = serializers.DateTimeField()

class AdminAnalyticsStatsSerializer(serializers.Serializer):
    daily_active_users = serializers.IntegerField()
    training_sessions = serializers.IntegerField()
    video_uploads = serializers.IntegerField()
    tournament_participation = serializers.IntegerField()
    new_users_today = serializers.IntegerField()

class AdminOverviewSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_tournaments = serializers.IntegerField()
    total_sessions = serializers.IntegerField()
    total_videos = serializers.IntegerField()
    analytics = AdminAnalyticsStatsSerializer()
    recent_activity = CombinedActivitySerializer(many=True)
    registration_trend = serializers.ListField(child=serializers.DictField())
