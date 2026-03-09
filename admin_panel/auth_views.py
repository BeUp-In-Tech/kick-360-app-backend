from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .auth_serializers import AdminLoginSerializer, AdminPasswordResetSerializer
from core.exceptions import APIResponse
from .permissions import IsAdminRole, AdminLoggerMixin

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class AdminLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return APIResponse(
            data={
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                },
                "tokens": tokens
            },
            message="Admin login successful."
        )

class AdminPasswordResetView(generics.GenericAPIView, AdminLoggerMixin):
    permission_classes = [IsAdminRole]
    serializer_class = AdminPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        self.log_action(user, "Changed Admin Password", "User", str(user.id))
        return APIResponse(message="Password changed successfully.")
