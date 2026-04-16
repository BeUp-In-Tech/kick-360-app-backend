import uuid
from django.db import models
from accounts.models import User
from core.models import BaseModel

class FCMDevice(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_devices', null=True, blank=True)
    registration_id = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., ios, android, web")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email if self.user else 'Anonymous'} - {self.device_type} - Active: {self.is_active}"

class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('NEW_TOURNAMENT', 'New Tournament'),
        ('NEW_TRAINING', 'New Training Session'),
        ('NEW_FOLLOW', 'New Follow'),
        ('NEW_USER', 'New User Registered'),
        ('USER_ATTEND_TOURNAMENT', 'User Attend Tournament'),
        ('USER_DELETED', 'User Deleted Account'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    is_for_admin = models.BooleanField(default=False)
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_item_id = models.CharField(max_length=255, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.title}"
