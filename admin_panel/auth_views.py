from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .auth_serializers import (
    AdminLoginSerializer, 
    AdminPasswordResetSerializer,
    ForgotPasswordSerializer,
    SetNewPasswordSerializer
)
from core.exceptions import APIResponse
from .permissions import IsAdminRole, AdminLoggerMixin
from django.conf import settings
from accounts.models import User, PasswordResetToken
from django.core.mail import send_mail
import os

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

class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Generate token
        reset_token = PasswordResetToken.objects.create(user=user)

        # Send email
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
        subject = "Reset your password"
        html_content = f"""
            <h2>Password Reset</h2>
            <p>Click the link below to reset your password</p>
            <a href="{reset_link}">Reset Password</a>
            <p>This link will expire in {settings.PASSWORD_RESET_TIMEOUT_MINUTES} minutes</p>
        """
        
        try:
            send_mail(
                subject=subject,
                message=f"Please use this link to reset your password: {reset_link}\nThis link will expire in {settings.PASSWORD_RESET_TIMEOUT_MINUTES} minutes.",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@kick360.com'),
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False,
            )
        except Exception as e:
            return Response({"success": False, "message": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return APIResponse(message="Password reset link sent to your email.")

class SetNewPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        reset_token.is_used = True
        reset_token.save()
        
        return APIResponse(message="Password has been reset successfully. You can now login.")
