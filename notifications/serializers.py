from rest_framework import serializers
from .models import FCMDevice, Notification

class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['registration_id', 'device_type', 'is_active']
        
    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            user = None
            
        registration_id = validated_data.get('registration_id')
        
        # Update or create the device
        device, created = FCMDevice.objects.update_or_create(
            registration_id=registration_id,
            defaults={
                'user': user,
                'device_type': validated_data.get('device_type', ''),
                'is_active': validated_data.get('is_active', True)
            }
        )
        return device

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'related_item_id', 'is_read', 'created_at']

