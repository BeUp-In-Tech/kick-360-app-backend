from django.db import transaction
from .models import TrainingSession, TrainingCompletion
from core.models import UserActivityLog
from accounts.models import User
from notifications.utils import send_push_notification

class TrainingService:
    @staticmethod
    @transaction.atomic
    def complete_training(user: User, training_session: TrainingSession, score_achieved: int, video_file=None) -> TrainingCompletion:
        """
        """
        points_to_award = training_session.points
        
        # Determine if we should create a new completion or update an existing one
        existing_completion = TrainingCompletion.objects.filter(user=user, training_session=training_session).first()
        
        if existing_completion:
            if training_session.reattempt:
                existing_completion.score_achieved = score_achieved
                if video_file:
                    existing_completion.video_file = video_file
                existing_completion.save(update_fields=['score_achieved', 'video_file'] if video_file else ['score_achieved'])
                completion = existing_completion
                # Do not award points again, or award delta? Let's just update score.
            else:
                raise ValueError("Reattempting this training session is not allowed.")
        else:
            completion = TrainingCompletion.objects.create(
                user=user,
                training_session=training_session,
                score_achieved=score_achieved,
                points_awarded=points_to_award,
                video_file=video_file
            )
            # Award points and increment participation only on first attempt
            user.points += points_to_award
            user.save(update_fields=['points'])
            
            training_session.participate_count += 1
            training_session.save(update_fields=['participate_count'])

        # Log activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='session_complete',
            description=f"Completed {training_session.title} (+{points_to_award} points)"
        )
        
        # Notify admins
        admins = User.objects.filter(is_staff=True)
        send_push_notification(
            users=admins,
            title="Training Completed Alert",
            body=f"{user.name or user.email} just completed training: {training_session.title}.",
            data_payload={'type': 'training_complete', 'training_id': str(training_session.id), 'user_id': str(user.id)}
        )
        
        return completion
        
    @staticmethod
    def watch_video(training_session: TrainingSession) -> None:
        training_session.video_watched_count += 1
        training_session.save(update_fields=['video_watched_count'])
