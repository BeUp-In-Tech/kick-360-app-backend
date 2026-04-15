from rest_framework import serializers
from .models import User
from access_codes.models import AccessCode
from access_codes.services import ShopifyService

class UserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'profile_image', 'country', 'position', 'access_code', 'total_kicks', 'rank', 'points', 'streak']
        read_only_fields = ['id', 'access_code', 'total_kicks', 'rank', 'points', 'streak']

    def get_rank(self, obj):
        # Use dynamic_rank if annotated, otherwise fetch the static rank
        return getattr(obj, 'dynamic_rank', obj.rank)

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
