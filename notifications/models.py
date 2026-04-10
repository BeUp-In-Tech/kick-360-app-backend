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
