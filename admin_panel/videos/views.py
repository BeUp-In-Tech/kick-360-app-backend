from rest_framework import viewsets, status, parsers
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from training.models import TrainingCategory, TrainingSession
from accounts.models import User
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin
from notifications.utils import send_push_notification

from .serializers import (
    AdminTrainingSessionSerializer,
    AdminTrainingCategorySerializer
)

class AdminTrainingCategoryViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = TrainingCategory.objects.all().order_by('title')
    serializer_class = AdminTrainingCategorySerializer
    permission_classes = [IsAdminRole]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def perform_create(self, serializer):
        category = serializer.save()
        self.log_action(
            self.request.user,
            "Created Training Category",
            "TrainingCategory",
            str(category.id)
        )

    def perform_update(self, serializer):
        category = serializer.save()
        self.log_action(
            self.request.user,
            "Updated Training Category",
            "TrainingCategory",
            str(category.id)
        )

    def perform_destroy(self, instance):
        category_id = str(instance.id)
        instance.delete()
        self.log_action(
            self.request.user,
            "Deleted Training Category",
            "TrainingCategory",
            category_id
        )

@extend_schema(
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'Select_category': {'type': 'string'},
                'Title': {'type': 'string'},
                'Subtitle': {'type': 'string'},
                'Equipment_used': {'type': 'string'},
                'Steps': {'type': 'string'},
                'Time': {'type': 'string'},
                'Points': {'type': 'integer'},
                'video': {'type': 'string', 'format': 'binary'},
                'is_pulished': {'type': 'boolean'},
            },
            'required': ['Select_category', 'Title', 'Time'],
        }
    },
    responses=AdminTrainingSessionSerializer
)
class AdminTrainingSessionViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = TrainingSession.objects.select_related('category').all().order_by('-created_at')
    serializer_class = AdminTrainingSessionSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def perform_create(self, serializer):
        session = serializer.save()
        self.log_action(
            self.request.user,
            "Created Training Session",
            "TrainingSession",
            str(session.id)
        )
        
        # Broadcast to all active users
        users = User.objects.filter(is_active=True)
        send_push_notification(
            users=users,
            title="New Training Video Available!",
            body=f"Check out our new training video: {session.title}.",
            data_payload={'type': 'new_training', 'training_id': str(session.id)}
        )

    def perform_update(self, serializer):
        session = serializer.save()
        self.log_action(
            self.request.user,
            "Updated Training Session",
            "TrainingSession",
            str(session.id)
        )

    def perform_destroy(self, instance):
        instance_id = str(instance.id)
        instance.delete()
        self.log_action(
            self.request.user,
            "Deleted Training Session",
            "TrainingSession",
            instance_id
        )

    @action(detail=True, methods=['patch'])
    def publish(self, request, id=None):
        session = self.get_object()
        session.is_published = True
        session.save()
        self.log_action(
            request.user,
            "Published Training Session",
            "TrainingSession",
            str(session.id)
        )
        return Response({
            'status': 'success',
            'message': 'Session published.'
        })