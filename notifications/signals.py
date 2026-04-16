from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from accounts.models import User
from tournaments.models import Tournament, TournamentParticipation
from training.models import TrainingSession
from follows.models import Follow
from .utils import create_user_notification, create_admin_notification
import logging

logger = logging.getLogger(__name__)

# --- ADMIN NOTIFICATIONS ---

@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        # Prevent tracking anonymous temp users if they don't have enough data
        # Assuming all users matter for this demo
        create_admin_notification(
            title="New User Registered",
            message=f"A new user with email/access code {instance.email or instance.access_code} has registered.",
            notification_type='NEW_USER',
            related_item_id=instance.id
        )

@receiver(post_save, sender=TournamentParticipation)
def notify_admin_tournament_attendance(sender, instance, created, **kwargs):
    if created:
        create_admin_notification(
            title="User Attended Tournament",
            message=f"{instance.user.name or 'A user'} has joined the tournament '{instance.tournament.title}'.",
            notification_type='USER_ATTEND_TOURNAMENT',
            related_item_id=instance.id
        )

@receiver(pre_delete, sender=User)
def notify_admin_user_deleted(sender, instance, **kwargs):
    if not instance.is_staff:
        create_admin_notification(
            title="User Account Deleted",
            message=f"The account for {instance.email or instance.access_code} has been deleted.",
            notification_type='USER_DELETED',
            related_item_id=instance.id
        )

# --- USER NOTIFICATIONS ---

@receiver(post_save, sender=Tournament)
def notify_users_new_tournament(sender, instance, created, **kwargs):
    if created and instance.is_active:
        # Notify all active users
        users = User.objects.filter(is_active=True, is_staff=False)
        # Note: Depending on the app size, bulk notification in signal can be heavy.
        # But this fits the requirement.
        for user in users:
            create_user_notification(
                user=user,
                title="New Tournament Available",
                message=f"A new tournament '{instance.title}' has been posted!",
                notification_type='NEW_TOURNAMENT',
                related_item_id=instance.id
            )

@receiver(post_save, sender=TrainingSession)
def notify_users_new_training_session(sender, instance, created, **kwargs):
    if created and instance.is_published:
        # Notify all active users
        users = User.objects.filter(is_active=True, is_staff=False)
        for user in users:
            create_user_notification(
                user=user,
                title="New Training Session",
                message=f"A new training session '{instance.title}' is available!",
                notification_type='NEW_TRAINING',
                related_item_id=instance.id
            )

@receiver(post_save, sender=Follow)
def notify_user_new_follow(sender, instance, created, **kwargs):
    if created:
        create_user_notification(
            user=instance.following,
            title="New Follower",
            message=f"{instance.follower.name or 'Someone'} has started following you.",
            notification_type='NEW_FOLLOW',
            related_item_id=instance.follower.id
        )
