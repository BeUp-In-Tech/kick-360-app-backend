from django.db.models import Sum, F
from django.utils import timezone
from .models import PerformanceTrack
from accounts.models import User

class LeaderboardService:
    @staticmethod
    def get_top_players(user, filter_type, month=None, year=None):
        """
        Return the top 11 players based on the filter type and optional month/year.
        Sorted by total score (PAC+SHO+PAS+DRI+DEF+PHY) and streak.
        """
        now = timezone.now()
        month = month or now.month
        year = year or now.year
        
        # Base queryset: users who have performance tracks in the given month
        tracks = PerformanceTrack.objects.filter(
            created_at__month=month,
            created_at__year=year
        )
        
        if filter_type == 'germany':
            tracks = tracks.filter(user__country__iexact='Germany')
        elif filter_type == 'following' and user:
            following_user_ids = user.following.values_list('following_id', flat=True)
            tracks = tracks.filter(user_id__in=following_user_ids)
            
        # Aggregate scores per user
        user_stats = tracks.values('user').annotate(
            monthly_score=(
                Sum('pac') + Sum('sho') + Sum('pas') + 
                Sum('dri') + Sum('_def') + Sum('phy')
            ),
            streak=F('user__streak'),
            name=F('user__name'),
            profile_image=F('user__profile_image'),
            total_kicks=F('user__total_kicks'), # Keep for reference
            points=F('user__points')
        ).order_by('-monthly_score', '-streak')[:11]
        
        return user_stats
