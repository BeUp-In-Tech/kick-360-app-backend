from rest_framework import serializers
from .models import AccessCode

class AccessCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessCode
        fields = ['id', 'code', 'duration_months', 'is_active', 'is_consumed', 'consumed_at', 'expires_at', 'created_at']
        read_only_fields = ['id', 'is_consumed', 'consumed_at', 'expires_at', 'created_at']
