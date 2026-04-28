from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Session
from core.utils import generate_video_thumbnail
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Session)
def auto_generate_session_thumbnail(sender, instance, created, **kwargs):
    """
    Automatically generate a thumbnail when a Session is created or updated
    and has a video but no thumbnail.
    """
    if instance.video_file and not instance.thumbnail:
        logger.info(f"Triggering thumbnail generation for Session: {instance.id}")
        generate_video_thumbnail(instance.video_file, instance.thumbnail)
        # Use update() to avoid recursion with post_save
        Session.objects.filter(pk=instance.pk).update(thumbnail=instance.thumbnail)
