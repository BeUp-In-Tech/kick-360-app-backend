from rest_framework import viewsets, status, parsers
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from training.models import TrainingCategory, TrainingSession
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin

from .serializers import (
    AdminTrainingSessionSerializer,
    AdminTrainingCategorySerializer
)

class AdminTrainingCategoryViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = TrainingCategory.objects.all().order_by('title')
    serializer_class = AdminTrainingCategorySerializer
    permission_classes = [IsAdminRole]

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
    request=AdminTrainingSessionSerializer,
    responses=AdminTrainingSessionSerializer
)
class AdminTrainingSessionViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = TrainingSession.objects.select_related('category').all().order_by('-created_at')
    serializer_class = AdminTrainingSessionSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def perform_create(self, serializer):
        session = serializer.save()
        self.log_action(
            self.request.user,
            "Created Training Session",
            "TrainingSession",
            str(session.id)
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
    def publish(self, request, pk=None):
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