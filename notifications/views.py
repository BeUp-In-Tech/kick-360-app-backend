from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import FCMDevice, Notification
from .serializers import FCMDeviceSerializer, NotificationSerializer

@extend_schema(
    tags=['Notifications'],
    summary="Register FCM Device Token",
    description="Register a Firebase Cloud Messaging device token to allow the backend to send push notifications. The token can be associated with an authenticated user or anonymous. If a token already exists, it will be updated."
)
class RegisterDeviceView(generics.CreateAPIView):
    """
    Register FCM token for the device
    """
    serializer_class = FCMDeviceSerializer
    # Allow anonymous users to register device tokens for general notifications
    permission_classes = [AllowAny] 
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        device = serializer.save()
        
        return Response(
            {"message": "Device token registered successfully", "registration_id": device.registration_id},
            status=status.HTTP_201_CREATED
        )

class BaseNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Must be overridden
        pass
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
            
        # Add summary stats
        unread_count = queryset.filter(is_read=False).count()
        total_count = queryset.count()
        response.data['unread_count'] = unread_count
        response.data['total_count'] = total_count
        return response

class UserNotificationListView(BaseNotificationListView):
    """
    List user notifications
    """
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user, is_for_admin=False)

class AdminNotificationListView(BaseNotificationListView):
    """
    List admin notifications
    """
    def get_queryset(self):
        if not self.request.user.is_staff:
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user, is_for_admin=True)

class NotificationDetailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Allows retrieving if user is recipient
        # No distinction between admin/user notifications needed at this level since per-user isolation exists
        return Notification.objects.filter(recipient=self.request.user)
        
    def post(self, request, pk, *args, **kwargs):
        """Mark as read"""
        try:
            notification = self.get_queryset().get(pk=pk)
            notification.is_read = True
            notification.save()
            return Response({"message": "Marked as read"})
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
            
    def delete(self, request, pk, *args, **kwargs):
        """Delete notification"""
        try:
            notification = self.get_queryset().get(pk=pk)
            notification.delete()
            return Response({"message": "Notification deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

