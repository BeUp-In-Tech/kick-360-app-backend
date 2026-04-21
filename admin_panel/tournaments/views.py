from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from tournaments.models import Tournament, TournamentParticipation
from accounts.models import User
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin
from notifications.utils import send_push_notification
from .serializers import AdminTournamentSerializer, AdminTournamentParticipationSerializer

class AdminTournamentViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = Tournament.objects.prefetch_related('participations').all().order_by('-created_at')
    serializer_class = AdminTournamentSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'id'
    lookup_url_kwarg = 'id'


    def perform_create(self, serializer):
        is_free = serializer.validated_data.get('is_free', False)
        if is_free:
            if Tournament.objects.filter(is_free=True, is_active=True).exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Only one free tournament can be active at a time.")
        
        tournament = serializer.save()
        self.log_action(self.request.user, "Created Tournament", "Tournament", str(tournament.id))
        
        # Broadcast to all active users
        users = User.objects.filter(is_active=True)
        send_push_notification(
            users=users,
            title="New Tournament Available!",
            body=f"{tournament.title} is now open.",
            data_payload={'type': 'new_tournament', 'tournament_id': str(tournament.id)}
        )

    def perform_update(self, serializer):
        is_free = serializer.validated_data.get('is_free', False)
        if is_free:
            # Check if another free tournament is active
            if Tournament.objects.filter(is_free=True, is_active=True).exclude(id=serializer.instance.id).exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Only one free tournament can be active at a time.")
        
        tournament = serializer.save()
        self.log_action(self.request.user, "Updated Tournament", "Tournament", str(tournament.id))

    def perform_destroy(self, instance):
        tournament_id = str(instance.id)
        instance.delete()
        self.log_action(self.request.user, "Deleted Tournament", "Tournament", tournament_id)

    @action(detail=True, methods=['patch'])
    def publish(self, request, id=None):
        tournament = self.get_object()
        tournament.is_active = True
        tournament.save()
        self.log_action(request.user, "Published Tournament", "Tournament", str(tournament.id))
        return Response({'status': 'success', 'message': 'Tournament published.'})

    @action(detail=True, methods=['patch'])
    def pause(self, request, id=None):
        tournament = self.get_object()
        tournament.is_active = False
        tournament.save()
        self.log_action(request.user, "Paused Tournament", "Tournament", str(tournament.id))
        return Response({'status': 'success', 'message': 'Tournament paused.'})

    @action(detail=True, methods=['delete'])
    def delete(self, request, id=None):
        tournament = self.get_object()
        tournament_id = str(tournament.id)
        tournament.delete()
        self.log_action(request.user, "Deleted Tournament", "Tournament", tournament_id)
        return Response({'status': 'success', 'message': 'Tournament deleted.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def participants(self, request, id=None):
        tournament = self.get_object()
        participants = tournament.participations.all().order_by('-score', '-total_kicks')
        serializer = AdminTournamentParticipationSerializer(participants, many=True)
        return Response(serializer.data)
