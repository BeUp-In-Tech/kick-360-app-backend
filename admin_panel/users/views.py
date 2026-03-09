from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import User
from access_codes.models import AccessCode
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin
from .serializers import AdminUserSerializer

class AdminUserViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'position', 'is_active', 'is_staff']
    search_fields = ['name', 'username', 'email']
    ordering_fields = ['total_kicks', 'points', 'rank', 'date_joined']

    def perform_create(self, serializer):
        user = serializer.save()
        self.log_action(self.request.user, "Created User", "User", str(user.id))

    def perform_update(self, serializer):
        user = serializer.save()
        self.log_action(self.request.user, "Updated User", "User", str(user.id))

    def perform_destroy(self, instance):
        user_id = str(instance.id)
        instance.delete()
        self.log_action(self.request.user, "Deleted User", "User", user_id)

    @action(detail=True, methods=['patch'])
    def suspend(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        self.log_action(request.user, "Suspended User", "User", str(user.id))
        return Response({'status': 'success', 'message': 'User suspended.'})

    @action(detail=True, methods=['delete'])
    def delete(self, request, pk=None):
        user = self.get_object()
        user_id = str(user.id)
        user.delete()
        self.log_action(request.user, "Deleted User", "User", user_id)
        return Response({'status': 'success', 'message': 'User deleted.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'status': 'success', 'is_active': user.is_active})
