from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import FCMDevice
from .serializers import FCMDeviceSerializer

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
