from django.db import models
from core.models import BaseModel
from accounts.models import User

class PerformanceTrack(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_tracks')
    session = models.ForeignKey('training.TrainingSession', on_delete=models.SET_NULL, null=True, blank=True)
    
    # AI Analysis Data
    pac = models.IntegerField(default=0)
    sho = models.IntegerField(default=0)
    pas = models.IntegerField(default=0)
    dri = models.IntegerField(default=0)
    _def = models.IntegerField(default=0) # 'def' is a keyword
    phy = models.IntegerField(default=0)
    
    # Metadata
    filename = models.CharField(max_length=255, blank=True)
    total_duration_sec = models.FloatField(default=0.0)
    fps = models.FloatField(default=0.0)
    total_players_detected = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Performance for {self.user.name} at {self.created_at}"
