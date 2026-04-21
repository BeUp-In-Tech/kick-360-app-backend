from django.db import models
from core.models import BaseModel
from accounts.models import User

class Session(BaseModel):
    MODE_CHOICES = (
        ('default', 'Default'),
        ('live', 'Live'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    total_kick = models.IntegerField(default=0)
    video_file = models.FileField(upload_to='sessions/videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='sessions/thumbnails/', null=True, blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='default')
    is_story = models.BooleanField(default=False)
    is_shared_to_leaderboard = models.BooleanField(default=False)
    session_duration = models.IntegerField(default=5)  # seconds
    countdown_time = models.IntegerField(default=3)    # seconds

    def __str__(self):
        return f"Session {self.id} - {self.user.name} ({self.total_kick} kicks)"
