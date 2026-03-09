from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from access_codes.models import AccessCode
from core.exceptions import APIResponse

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the access code string from validated data
        code_str = serializer.validated_data['access_code']
        
        # Strictly accept any 8-character alphanumeric string as valid for now
        import re
        if not re.match(r'^[a-zA-Z0-9]{8}$', code_str):
             return APIResponse(message="Access code must be exactly 8 characters long (letters and numbers).", status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure the code is not already used by another user (if we want to enforce uniqueness)
        if User.objects.filter(access_code=code_str).exists():
            return APIResponse(message="This access code is already registered.", status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        
        # Mark code as consumed in the AccessCode model if it exists, or just rely on User.access_code
        from django.utils import timezone
        from core.models import UserActivityLog
        
        # Sync with AccessCode model if it exists
        AccessCode.objects.get_or_create(
            code=code_str,
            defaults={
                'user': user,
                'is_consumed': True,
                'consumed_at': timezone.now()
            }
        )

        # Log Activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='register',
            description=f"User registered with code {code_str}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        tokens = get_tokens_for_user(user)
        return APIResponse(
            data={
                "user": UserSerializer(user).data,
                "tokens": tokens
            },
            message="User registered successfully."
        )

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_code = serializer.validated_data['access_code']
        try:
            user = User.objects.get(access_code=access_code)
        except User.DoesNotExist:
            return APIResponse(message="Invalid access code.", status=status.HTTP_401_UNAUTHORIZED)
        
        # TEMPORARY: Allow login even if subscription is "expired" for testing
        # if not user.is_subscription_active:
        #     return APIResponse(message="Your access code has expired. Please purchase a new one.", status=status.HTTP_403_FORBIDDEN)

        # Log Activity
        from core.models import UserActivityLog
        UserActivityLog.objects.create(
            user=user,
            activity_type='sign_in',
            description="User signed in via access code",
            ip_address=request.META.get('REMOTE_ADDR')
        )

        tokens = get_tokens_for_user(user)
        return APIResponse(
            data={
                "user": UserSerializer(user).data,
                "tokens": tokens
            },
            message="Login successful."
        )

class LogoutSerializer(serializers.Serializer):
    pass

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        return APIResponse(message="Logout successful.")

