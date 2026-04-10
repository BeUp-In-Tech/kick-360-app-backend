from rest_framework import serializers
from .models import User
from access_codes.models import AccessCode
from access_codes.services import ShopifyService

class UserSerializer(serializers.ModelSerializer):
    rank = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'profile_image', 'country', 'position', 'access_code', 'total_kicks', 'rank', 'points', 'streak']
        read_only_fields = ['id', 'access_code', 'total_kicks', 'rank', 'points', 'streak']

    def get_rank(self, obj):
        # Use dynamic_rank if annotated, otherwise fetch the static rank
        return getattr(obj, 'dynamic_rank', obj.rank)

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
        # 1. Verify via external Shopify Service
        verify_response = ShopifyService.verify_access_code(value)
        if not verify_response['is_valid']:
            raise serializers.ValidationError(verify_response['meta'].get('error', 'Invalid access code.'))
            
        # 2. Check if already consumed locally
        access_code_obj = AccessCode.objects.filter(code=value).first()
        if access_code_obj and access_code_obj.is_consumed:
            raise serializers.ValidationError("Access code has already been used.")
            
        # 3. Check if already linked to a user account
        if User.objects.filter(access_code=value).exists():
            raise serializers.ValidationError("Access code is already linked to an account.")
            
        return value

class LoginSerializer(serializers.Serializer):
    access_code = serializers.CharField(required=True)
    
    def validate_access_code(self, value):
        if not User.objects.filter(access_code=value, is_active=True).exists():
            raise serializers.ValidationError("No active account found with this access code.")
        return value
