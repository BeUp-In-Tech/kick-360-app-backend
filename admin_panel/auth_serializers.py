from rest_framework import serializers
from accounts.models import User, PasswordResetToken
from django.conf import settings

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = User.objects.get(email=email, is_staff=True)
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Admin account not found.")
            
        data['user'] = user
        return data

class AdminPasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect current password.")
        return value

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value, is_staff=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Admin account with this email not found.")
        return value

class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        token_uuid = data.get('token')
        try:
            reset_token = PasswordResetToken.objects.get(token=token_uuid)
            if not reset_token.is_valid(timeout_minutes=settings.PASSWORD_RESET_TIMEOUT_MINUTES):
                raise serializers.ValidationError("Token has expired or already been used.")
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")
        
        data['reset_token'] = reset_token
        return data

class AdminLogoutSerializer(serializers.Serializer):
    pass
