from rest_framework import generics, status, serializers
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

class TournamentDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = TournamentSerializer
    queryset = Tournament.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(data=serializer.data, message="Tournament retrieved.")

class TournamentJoinSerializer(serializers.Serializer):
    pass

class TournamentJoinView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    queryset = Tournament.objects.filter(is_active=True)
    serializer_class = TournamentJoinSerializer

    def post(self, request, *args, **kwargs):
        tournament = self.get_object()
        
        try:
            participation = TournamentService.join_tournament(user=request.user, tournament=tournament)
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

class TournamentLeaderboardView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = TournamentParticipationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TournamentParticipation.objects.none()
        tournament_id = self.kwargs['pk']
        return TournamentParticipation.objects.filter(tournament_id=tournament_id).order_by('-total_kicks')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Tournament leaderboard retrieved.")
