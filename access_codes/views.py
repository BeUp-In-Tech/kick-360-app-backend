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
            verify_response = ShopifyService.verify_access_code(code)
            
            if not verify_response['is_valid']:
                return APIResponse(
                    data={},
                    message=verify_response['meta'].get('error', 'Invalid access code.'),
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Retrieve the local object to return its data
            access_code = AccessCode.objects.get(code=code)
            
            return APIResponse(
                data=AccessCodeSerializer(access_code).data,
                message="Access code is valid."
            )
            
        except Exception as e:
            logger.error(f"Error verifying access code: {str(e)}")
            return APIResponse(
                data={},
                message="An error occurred while verifying the access code.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
