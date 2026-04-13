from rest_framework import serializers
from access_codes.models import AccessCode

class AdminAccessCodeDetailSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = AccessCode
        fields = [
            'id', 'code', 'duration_months', 'is_active', 
            'is_consumed', 'consumed_at', 'expires_at', 
            'user', 'user_name', 'shopify_order_id', 'shopify_email', 'created_at'
        ]
