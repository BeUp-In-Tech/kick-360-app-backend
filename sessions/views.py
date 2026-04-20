from rest_framework import generics, status, parsers
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from core.permissions import HasActiveSubscription
from .models import Session
from .serializers import SessionSerializer, SessionCompleteSerializer, SessionShareToggleSerializer
from .services import SessionService
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)

class SessionCompleteView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, HasActiveSubscription)
    serializer_class = SessionCompleteSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        video_file = serializer.validated_data.get('video_file')
        
        try:
            session = SessionService.complete_session(
                user=request.user,
                data=serializer.validated_data,
                video_file=video_file
            )
            return APIResponse(
                data=SessionSerializer(session).data,
                message="Session completed successfully."
            )
        except ValueError as e:
            # Catch internal service validation errors like video limit
            return APIResponse(
                data={},
                message=str(e),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error completing session: {str(e)}")
            return APIResponse(
                data={},
                message="An error occurred while completing the session.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DailySessionCreateView(SessionCompleteView):
    """Alias for backwards compatibility or explicit naming for daily sessions."""
    pass

class StoryUploadView(SessionCompleteView):
    """Endpoint specifically for uploading story videos."""
    def create(self, request, *args, **kwargs):
        # Handle QueryDict (from multipart) vs standard dict
        if hasattr(request.data, '_mutable'):
            request.data._mutable = True
            request.data['is_story'] = True
            request.data._mutable = False
        else:
            # It's a standard dict or similar
            try:
                request.data['is_story'] = True
            except TypeError:
                # If immutable dict, work on a copy
                request.data = request.data.copy()
                request.data['is_story'] = True
        return super().create(request, *args, **kwargs)

class SessionHistoryView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SessionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Session.objects.none()
        return Session.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Session history retrieved.")

class SessionShareToggleView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SessionShareToggleSerializer
    queryset = Session.objects.all()

    def update(self, request, *args, **kwargs):
        session = self.get_object()
        
        # Ensure user owns the session
        if session.user != request.user:
            return APIResponse(message="Forbidden", status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_session = SessionService.toggle_share(
            session=session,
            share_type=serializer.validated_data['share_type'],
            state=serializer.validated_data['state']
        )
        
        return APIResponse(
            data=SessionSerializer(updated_session).data,
            message=f"Session share settings updated successfully."
        )

class GlobalStoriesView(generics.ListAPIView):
    """
    Returns a list of all active stories (from the last 24 hours) from all users.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = SessionSerializer

    def get_queryset(self):
        from django.utils import timezone
        import datetime
        twenty_four_hours_ago = timezone.now() - datetime.timedelta(hours=24)
        return Session.objects.filter(
            is_story=True, 
            created_at__gte=twenty_four_hours_ago
        ).select_related('user').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_resp = self.get_paginated_response(serializer.data)
            return APIResponse(
                data=paginated_resp.data,
                message="Global stories retrieved."
            )

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Global stories retrieved.")
