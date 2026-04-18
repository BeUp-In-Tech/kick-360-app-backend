from django.db import models
from core.models import BaseModel
from accounts.models import User

class TrainingCategory(BaseModel):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class TrainingSession(BaseModel):
    category = models.ForeignKey(TrainingCategory, on_delete=models.CASCADE, related_name='sessions', null=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    equipment_used = models.TextField(blank=True)
    steps = models.TextField(blank=True)
    video_file = models.FileField(upload_to='training/videos/', blank=True, null=True)
    duration_seconds = models.IntegerField(default=60)
    points = models.IntegerField(default=0)
    score_required = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    reattempt = models.BooleanField(default=False)
    participate_count = models.IntegerField(default=0)
    video_watched_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class TrainingCompletion(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='training_completions')
    training_session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='completions')
    score_achieved = models.IntegerField(default=0)
    points_awarded = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.name} completed {self.training_session.title}"
