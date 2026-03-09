from rest_framework import generics, serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from core.permissions import HasActiveSubscription
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User
from accounts.serializers import UserSerializer
from core.exceptions import APIResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from .services import LeaderboardService

class LeaderboardPlayerSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    name = serializers.CharField(allow_null=True)
    profile_image = serializers.URLField(allow_null=True)
    total_kicks = serializers.IntegerField()
    points = serializers.IntegerField()
    streak = serializers.IntegerField()

class LeaderboardResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = LeaderboardPlayerSerializer(many=True)
    message = serializers.CharField()

from django.utils import timezone
from .models import PerformanceTrack
from .serializers import PerformanceTrackSerializer, PerformanceAIRequestSerializer

class PerformanceRecordView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = PerformanceAIRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        video_info = data.get('video_info', {})
        analysis_data = data.get('data', {}).get('analysis', {})
        total_players = data.get('data', {}).get('total_players_detected', 0)
        session_id = data.get('session_id')
        
        # Pick the first analysis entry or specific player id if provided
        # For now, let's assume we take the first key in analysis
        player_analysis = {}
        if analysis_data:
            first_key = list(analysis_data.keys())[0]
            player_analysis = analysis_data[first_key]
            
        track = PerformanceTrack.objects.create(
            user=request.user,
            session_id=session_id,
            pac=player_analysis.get('PAC', 0),
            sho=player_analysis.get('SHO', 0),
            pas=player_analysis.get('PAS', 0),
            dri=player_analysis.get('DRI', 0),
            _def=player_analysis.get('DEF', 0),
            phy=player_analysis.get('PHY', 0),
            filename=video_info.get('filename', ''),
            total_duration_sec=video_info.get('total_duration_sec', 0.0),
            fps=video_info.get('fps', 0.0),
            total_players_detected=total_players
        )
        
        # Update User Streak and Points
        user = request.user
        today = timezone.now().date()
        
        if user.last_session_date != today:
            if user.last_session_date == today - timezone.timedelta(days=1):
                user.streak += 1
            else:
                user.streak = 1
            user.last_session_date = today
            
        # Give some points for the session
        user.points += 10 # Default points for attempt
        user.save()
        
        return APIResponse(
            data=PerformanceTrackSerializer(track).data,
            message="Performance tracked and user stats updated."
        )

class StatsLeaderboardView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='filter', description='Filter type (everyone, germany, following)', required=False, type=str),
            OpenApiParameter(name='month', description='Month (1-12)', required=False, type=int),
            OpenApiParameter(name='year', description='Year', required=False, type=int),
        ],
        responses={200: LeaderboardResponseSerializer}
    )
    def get(self, request):
        filter_type = request.query_params.get('filter', 'everyone')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if month: month = int(month)
        if year: year = int(year)
        
        user = request.user
        leaderboard_data = LeaderboardService.get_top_players(user, filter_type, month, year)
        
        response_data = [
            {
                "rank": i + 1,
                "user_id": player['user'],
                "name": player['name'],
                "profile_image": player['profile_image'], # Already absolute URL or placeholder in profile_image field
                "total_score": player['monthly_score'],
                "streak": player['streak'],
                "total_kicks": player['total_kicks'],
                "points": player['points']
            }
            for i, player in enumerate(leaderboard_data)
        ]
        
        return Response({
            "success": True,
            "data": response_data,
            "message": f"Top 11 players ({filter_type.capitalize()}) for {month or 'current'}/{year or 'current'}"
        })
