from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import AccessCode
from .serializers import AccessCodeSerializer
from .services import ShopifyService
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)

class AccessCodeVerifyView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AccessCodeSerializer

    def create(self, request, *args, **kwargs):
        from django.utils import timezone
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        
        try:
            try:
                access_code = AccessCode.objects.get(code=code)
            except AccessCode.DoesNotExist:
                return APIResponse(
                    data={},
                    message="Invalid access code",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if access_code.status == 'not_sent':
                return APIResponse(
                    data={},
                    message="Access code is not activated (status: not_sent).",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if access_code.is_consumed:
                return APIResponse(
                    data={},
                    message="This access code has already been used.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Consume the code
            access_code.is_consumed = True
            access_code.user = request.user
            access_code.consumed_at = timezone.now()
            access_code.save()
            
            return APIResponse(
                data=AccessCodeSerializer(access_code).data,
                message="Access code verified and consumed successfully."
            )
            
        except Exception as e:
            logger.error(f"Error verifying access code: {str(e)}")
            return APIResponse(
                data={},
                message="An error occurred while verifying the access code.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
