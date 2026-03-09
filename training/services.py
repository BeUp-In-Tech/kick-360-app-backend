from django.db import transaction
from .models import TrainingSession, TrainingCompletion
from core.models import UserActivityLog
from accounts.models import User

class TrainingService:
    @staticmethod
    @transaction.atomic
    def complete_training(user: User, training_session: TrainingSession, score_achieved: int) -> TrainingCompletion:
        """
        User completes a training session, recording the score and updating user points.
        """
        points_to_award = training_session.points
        
        completion = TrainingCompletion.objects.create(
            user=user,
            training_session=training_session,
            score_achieved=score_achieved,
            points_awarded=points_to_award
        )
        
        user.points += points_to_award
        user.save(update_fields=['points'])
        
        # Log activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='session_complete',
            description=f"Completed {training_session.title} (+{points_to_award} points)"
        )
        
        return completion
