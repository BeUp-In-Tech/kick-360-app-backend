from rest_framework import generics, status, serializers, parsers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from access_codes.models import AccessCode
from core.exceptions import APIResponse
from notifications.utils import send_push_notification

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = []
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the access code string from validated data
        code_str = serializer.validated_data['access_code']
        
        # Ensure the code is not already used by another user locally
        if User.objects.filter(access_code=code_str).exists():
            return APIResponse(message="This access code is already registered.", status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        
        # Mark code as consumed in the AccessCode model
        from django.utils import timezone
        from core.models import UserActivityLog
        
        # Sync with AccessCode model if it doesn't exist locally
        access_code_obj, created = AccessCode.objects.get_or_create(
            code=code_str,
            defaults={'status': 'sent'}
        )
        access_code_obj.user = user
        from dateutil.relativedelta import relativedelta
        access_code_obj.is_consumed = True
        access_code_obj.consumed_at = timezone.now()
        access_code_obj.expires_at = access_code_obj.consumed_at + relativedelta(months=access_code_obj.duration_months or 1)
        access_code_obj.save()

        # Log Activity
        UserActivityLog.objects.create(
            user=user,
            activity_type='register',
            description=f"User registered with code {code_str}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Notify admins
        admins = User.objects.filter(is_staff=True)
        send_push_notification(
            users=admins,
            title="New User Registered",
            body=f"A new user has registered with code: {code_str}",
            data_payload={'type': 'new_user', 'user_id': str(user.id)}
        )
        
        tokens = get_tokens_for_user(user)
        return APIResponse(
            data={
                "user": UserSerializer(user, context={'request': request}).data,
                "tokens": tokens
            },
            message="User registered successfully."
        )

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_code = serializer.validated_data['access_code']
        try:
            user = User.objects.get(access_code=access_code)
        except User.DoesNotExist:
            return APIResponse(message="Invalid access code.", status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_subscription_active:
             return APIResponse(message="Your access code has expired. Please purchase a new one.", status=status.HTTP_403_FORBIDDEN)

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
                "user": UserSerializer(user, context={'request': request}).data,
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

class DeleteAccountView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer # Dummy serializer for schema

    def delete(self, request, *args, **kwargs):
        user = request.user
        # Log this somehow, or notify admins based on previous pattern
        admins = User.objects.filter(is_staff=True)
        send_push_notification(
            users=admins,
            title="User Deleted Account",
            body=f"User {user.name or user.email or user.access_code} has deleted their account.",
            data_payload={'type': 'user_deleted', 'user_id': str(user.id)}
        )
        user.delete()
        return APIResponse(message="Account deleted successfully.")


from core.models import UserActivityLog
from .serializers import UserActivityLogSerializer

class UserActivityLogView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserActivityLogSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserActivityLog.objects.none()
        return UserActivityLog.objects.filter(user=self.request.user).order_by('-created_at')
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data, message="Activity logs retrieved.")

class PublicProfileView(generics.RetrieveAPIView):
    """
    Allows viewing any user's public profile data including rank and active story.
    """
    queryset = User.objects.filter(is_active=True)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return APIResponse(data=serializer.data, message="User profile retrieved.")
