from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from core.permissions import HasActiveSubscription
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import TrainingCategory, TrainingSession, TrainingCompletion
from .services import TrainingService
from core.exceptions import APIResponse
from .serializers import (
    TrainingCategorySerializer, 
    CompleteTrainingRequestSerializer, 
    TrainingCompletionSerializer,
    TrainingSessionSerializer
)

class TrainingSessionListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = TrainingSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']

    def get_queryset(self):
        return TrainingSession.objects.filter(is_published=True).order_by('-created_at')


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Training sessions retrieved.")


class TrainingCompleteView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = CompleteTrainingRequestSerializer
    lookup_url_kwarg = 'id'

    @extend_schema(
        responses={200: TrainingCompletionSerializer}
    )
    def post(self, request, id, *args, **kwargs):
        training_session = get_object_or_404(TrainingSession, id=id, is_published=True)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        score_achieved = serializer.validated_data.get('score_achieved', 0)
        
        completion = TrainingService.complete_training(
            user=request.user,
            training_session=training_session,
            score_achieved=score_achieved
        )
        
        return APIResponse(
            data=TrainingCompletionSerializer(completion).data,
            message="Training completed successfully."
        )

class TrainingSessionWatchView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = None
    lookup_url_kwarg = 'id'

    def post(self, request, id, *args, **kwargs):
        training_session = get_object_or_404(TrainingSession, id=id, is_published=True)
        TrainingService.watch_video(training_session)
        return APIResponse(message="Video watch count incremented.")
