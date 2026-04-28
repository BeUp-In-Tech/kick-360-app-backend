from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TrainingSession, TrainingCompletion
from core.utils import generate_video_thumbnail
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TrainingSession)
def auto_generate_training_thumbnail(sender, instance, created, **kwargs):
    """
    Automatically generate a thumbnail when a TrainingSession is created or updated
    and has a video but no thumbnail.
    """
    if instance.video_file and not instance.thumbnail:
        logger.info(f"Triggering thumbnail generation for TrainingSession: {instance.title}")
        generate_video_thumbnail(instance.video_file, instance.thumbnail)
        # Use update() to avoid recursion with post_save
        TrainingSession.objects.filter(pk=instance.pk).update(thumbnail=instance.thumbnail)

@receiver(post_save, sender=TrainingCompletion)
def auto_generate_completion_thumbnail(sender, instance, created, **kwargs):
    """
    Automatically generate a thumbnail when a TrainingCompletion is created
    and has a video but no thumbnail.
    """
    if instance.video_file and not instance.thumbnail:
        logger.info(f"Triggering thumbnail generation for TrainingCompletion: {instance.id}")
        generate_video_thumbnail(instance.video_file, instance.thumbnail)
        # Use update() to avoid recursion with post_save
        TrainingCompletion.objects.filter(pk=instance.pk).update(thumbnail=instance.thumbnail)
