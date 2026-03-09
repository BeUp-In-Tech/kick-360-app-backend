import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AdminActionLog(BaseModel):
    admin = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='admin_actions')
    action = models.CharField(max_length=255)
    target_model = models.CharField(max_length=100, null=True, blank=True)
    target_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.admin.name} - {self.action} on {self.target_model}:{self.target_id}"

class UserActivityLog(BaseModel):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=100) # 'sign_in', 'register', 'session_complete', etc.
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.name or 'User'} - {self.activity_type} at {self.created_at}"
