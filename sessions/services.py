from django.db import transaction
from django.utils import timezone
from .models import Session
from accounts.models import User
import logging

logger = logging.getLogger(__name__)

class SessionService:
    @staticmethod
    def recalculate_global_rank():
        users = User.objects.order_by('-total_kicks')
        for i, u in enumerate(users):
            if u.rank != i + 1:
                u.rank = i + 1
                u.save(update_fields=['rank'])

    @staticmethod
    @transaction.atomic
    def complete_session(user: User, data: dict, video_file=None, thumbnail=None) -> Session:
        """
        Creates a session and updates user statistics atomically.
        """
        total_kick = data.get('total_kick', 0)
        mode = data.get('mode', 'default')
        is_story = data.get('is_story', False)
        is_shared_to_leaderboard = data.get('is_shared_to_leaderboard', False)
        session_duration = data.get('session_duration', 5)
        
        # 1. Video Limit Check (Removed as per user request for unlimited uploads)
        pass

        # 2. Daily Streak Update
        today = timezone.localdate()
        if user.last_session_date == today:
            # Already completed a session today
            pass
        elif user.last_session_date == today - timezone.timedelta(days=1):
            # Consecutive day
            user.streak += 1
            user.last_session_date = today
        else:
            # Missed a day
            user.streak = 1
            user.last_session_date = today

        # 3. Update User Stats
        user.total_kicks += int(total_kick)
        user.points += 10 # Example rule: 10 points per session
        
        # 4. Save User Info Locally Before Finalizing Session
        user.save()

        # 5. Save the Session
        session = Session.objects.create(
            user=user,
            total_kick=total_kick,
            video_file=video_file,
            thumbnail=thumbnail,
            mode=mode,
            is_story=is_story,
            is_shared_to_leaderboard=is_shared_to_leaderboard,
            session_duration=session_duration
        )

        # 6. Log activity
        from core.models import UserActivityLog
        UserActivityLog.objects.create(
            user=user,
            activity_type='session_complete',
            description=f"Completed {mode} session: {total_kick} kicks"
        )

        # 7. Recalculate rank (can be expensive, might defer to Celery in prod, but doing synchronously per req)
        SessionService.recalculate_global_rank()

        # Re-fetch user rank
        user.refresh_from_db(fields=['rank'])

        return session

    @staticmethod
    def toggle_share(session: Session, share_type: str, state: bool) -> Session:
        if share_type == 'leaderboard':
            session.is_shared_to_leaderboard = state
        elif share_type == 'story':
            session.is_story = state
        else:
            raise ValueError("Invalid share type.")
            
        session.save(update_fields=['is_shared_to_leaderboard', 'is_story'])
        return session
