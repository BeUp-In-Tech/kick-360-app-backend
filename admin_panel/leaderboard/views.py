from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin
from .serializers import AdminLeaderboardSerializer

class AdminLeaderboardViewSet(viewsets.ViewSet, AdminLoggerMixin):
    permission_classes = [IsAdminRole]
    serializer_class = AdminLeaderboardSerializer
    queryset = User.objects.all()

    def list(self, request):
        users = User.objects.all().order_by('-total_kicks')
        serializer = AdminLeaderboardSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def delete_entry(self, request, pk=None):
        try:
            user = User.objects.get(id=pk)
            user.total_kicks = 0
            user.points = 0
            user.save()
            self.log_action(request.user, "Reset User Ranking", "User", str(user.id))
            return Response({'status': 'success', 'message': 'User ranking reset.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'])
    def reset_all(self, request):
        User.objects.all().update(total_kicks=0, points=0, rank=0)
        self.log_action(request.user, "Reset Entire Leaderboard")
        return Response({'status': 'success', 'message': 'Leaderboard reset.'})
