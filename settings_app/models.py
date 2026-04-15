from django.db import models
from core.models import BaseModel
from accounts.models import User
from sessions.models import Session

class SavedVideo(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_videos')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='saved_by')

    class Meta:
        unique_together = ('user', 'session')
        verbose_name = 'Saved Video'
        verbose_name_plural = 'Saved Videos'

    def __str__(self):
        return f"{self.user.name or 'User'} saved {self.session.id}"
