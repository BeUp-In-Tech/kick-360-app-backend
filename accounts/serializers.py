from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import User
from access_codes.models import AccessCode
from access_codes.services import ShopifyService

class UserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()
    latest_session = serializers.SerializerMethodField()
    active_story = serializers.SerializerMethodField()
    performance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'profile_image', 'country', 'position', 
                  'access_code', 'total_kicks', 'rank', 'points', 'streak', 'last_session_date',
                  'expires_at', 'latest_session', 'active_story', 'performance']
        read_only_fields = ['id', 'access_code', 'total_kicks', 'rank', 'points', 'streak']

    @extend_schema_field(OpenApiTypes.STR)
    def get_expires_at(self, obj):
        from access_codes.models import AccessCode
        from django.utils import timezone
        code = AccessCode.objects.filter(user=obj, is_consumed=True).order_by('-expires_at').first()
        return code.expires_at.isoformat() if code and code.expires_at else None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_latest_session(self, obj):
        from sessions.serializers import SessionSerializer
        session = obj.sessions.order_by('-created_at').first()
        if session:
            return SessionSerializer(session, context=self.context).data
        return None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_active_story(self, obj):
        from sessions.serializers import SessionSerializer
        from django.utils import timezone
        import datetime
        twenty_four_hours_ago = timezone.now() - datetime.timedelta(hours=24)
        story = obj.sessions.filter(is_story=True, created_at__gte=twenty_four_hours_ago).order_by('-created_at').first()
        if story:
            return SessionSerializer(story, context=self.context).data
        return None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_performance(self, obj):
        from stats.models import PerformanceTrack
        from stats.serializers import PerformanceTrackSerializer
        perf = PerformanceTrack.objects.filter(user=obj).order_by('-created_at').first()
        if perf:
            return PerformanceTrackSerializer(perf, context=self.context).data
        return None

    @extend_schema_field(OpenApiTypes.INT)
    def get_rank(self, obj):
        # Use dynamic_rank if annotated, otherwise fetch the static rank
        return getattr(obj, 'dynamic_rank', obj.rank)

    @extend_schema_field(OpenApiTypes.URI)
    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.profile_image:
            # ensure the URL starts with /media/ if it doesn't already
            url = obj.profile_image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

class RegisterSerializer(serializers.ModelSerializer):
    access_code = serializers.CharField(required=True)
    profile_image = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['name', 'profile_image', 'country', 'position', 'access_code']
        extra_kwargs = {
            'name': {'required': True},
            'country': {'required': True},
            'position': {'required': True},
        }

    def validate_access_code(self, value):
        # 1. Verify via local database (previously external)
        verify_response = ShopifyService.verify_access_code(value)
        if not verify_response['is_valid']:
            raise serializers.ValidationError(verify_response['meta'].get('error', 'Invalid access code.'))
            
        # 2. Check if already linked to a user account (safety check)
        if User.objects.filter(access_code=value).exists():
            raise serializers.ValidationError("Access code is already registered.")
            
        return value

class LoginSerializer(serializers.Serializer):
    access_code = serializers.CharField(required=True)
    
    def validate_access_code(self, value):
        if not User.objects.filter(access_code=value, is_active=True).exists():
            raise serializers.ValidationError("No active account found with this access code.")
        return value

class ProfileUpdateSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['name', 'country', 'position', 'profile_image']

from core.models import UserActivityLog

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = ['id', 'activity_type', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']
