from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import SavedVideo
from .serializers import SavedVideoSerializer, SavedVideoToggleSerializer
from accounts.models import User
from accounts.serializers import UserSerializer, ProfileUpdateSerializer
from sessions.models import Session
from core.exceptions import APIResponse

class ProfileViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    queryset = User.objects.none()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ProfileUpdateSerializer
        if self.action == 'toggle_save':
            return SavedVideoToggleSerializer
        return UserSerializer

    def list(self, request):
        """Get current user profile."""
        serializer = UserSerializer(request.user, context={'request': request})
        return APIResponse(data=serializer.data, message="Profile retrieved.")

    def partial_update(self, request, *args, **kwargs):
        """Update current user profile."""
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full user data
        full_serializer = UserSerializer(request.user, context={'request': request})
        return APIResponse(data=full_serializer.data, message="Profile updated successfully.")

    @action(detail=False, methods=['get'], url_path='saved-videos')
    def saved_videos(self, request):
        """Get list of user's saved videos."""
        saved = SavedVideo.objects.filter(user=request.user).select_related('session')
        serializer = SavedVideoSerializer(saved, many=True, context={'request': request})
        return APIResponse(data=serializer.data, message="Saved videos retrieved.")

    @action(detail=False, methods=['post'], url_path='toggle-save')
    def toggle_save(self, request):
        """Toggle save/unsave for a video."""
        serializer = SavedVideoToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        session_id = serializer.validated_data['session_id']
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return APIResponse(message="Session not found.", status=status.HTTP_404_NOT_FOUND)

        saved_video, created = SavedVideo.objects.get_or_create(
            user=request.user,
            session=session
        )

        if not created:
            saved_video.delete()
            return APIResponse(data={'is_saved': False}, message="Video removed from saved.")
        
        return APIResponse(data={'is_saved': True}, message="Video saved successfully.")
