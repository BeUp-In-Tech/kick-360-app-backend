from rest_framework import generics, status, serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from rest_framework.permissions import IsAuthenticated
from core.permissions import HasActiveSubscription
from .models import Tournament, TournamentParticipation
from .serializers import TournamentSerializer, TournamentParticipationSerializer
from .services import TournamentService
from core.exceptions import APIResponse

class TournamentListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.filter(is_active=True).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Active tournaments retrieved.")

@extend_schema(
    responses=TournamentSerializer
)
class TournamentDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(data=serializer.data, message="Tournament retrieved.")

class TournamentJoinSerializer(serializers.Serializer):
    total_kicks = serializers.IntegerField(required=False, default=0)
    hours_played = serializers.FloatField(required=False, default=0.0)
    score = serializers.IntegerField(required=False, default=0)

@extend_schema(
    responses={200: TournamentParticipationSerializer}
)
class TournamentJoinView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    queryset = Tournament.objects.filter(is_active=True)
    serializer_class = TournamentJoinSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def post(self, request, *args, **kwargs):
        tournament = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            participation = TournamentService.join_tournament(
                user=request.user, 
                tournament=tournament,
                total_kicks=serializer.validated_data.get('total_kicks', 0),
                hours_played=serializer.validated_data.get('hours_played', 0.0),
                score=serializer.validated_data.get('score', 0)
            )
            return APIResponse(
                data=TournamentParticipationSerializer(participation).data,
                message=f"Successfully joined tournament: {tournament.title}"
            )
        except ValueError as e:
            return APIResponse(
                data={},
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema(
    responses=TournamentParticipationSerializer(many=True)
)
class TournamentLeaderboardView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = TournamentParticipationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TournamentParticipation.objects.none()
        tournament_id = self.kwargs['id']
        return TournamentParticipation.objects.filter(tournament_id=tournament_id).order_by('-score', '-total_kicks')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Tournament leaderboard retrieved.")
