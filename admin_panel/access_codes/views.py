from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from access_codes.models import AccessCode
from admin_panel.permissions import IsAdminRole, AdminLoggerMixin
from .serializers import AdminAccessCodeDetailSerializer

class AdminAccessCodeDetailViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = AccessCode.objects.all().order_by('-created_at')
    serializer_class = AdminAccessCodeDetailSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_consumed', 'is_active']
    search_fields = ['code', 'user__name']
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def perform_update(self, serializer):
        access_code = serializer.save()
        self.log_action(self.request.user, "Updated Access Code", "AccessCode", str(access_code.id))

    @action(detail=False, methods=['post'], url_path='fetch-shopify')
    def fetch_shopify(self, request):
        """
        Fetches all codes from Shopify and syncs with local database.
        """
        from access_codes.services import ShopifyService
        result = ShopifyService.sync_access_codes()
        
        if result['status'] == 'success':
            self.log_action(
                self.request.user, 
                f"Synced with Shopify: Created {result['created']}, Updated {result['updated']}", 
                "AccessCode", 
                "System"
            )
            return Response(result)
        else:
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)

    @action(detail=False, methods=['post'])
    def bulk_generate(self, request):
        count = request.data.get('count', 10)
        prefix = request.data.get('prefix', 'KICK')
        duration = request.data.get('duration_months', 1)
        
        codes = []
        import secrets
        import string
        
        for _ in range(int(count)):
            code_str = prefix + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            codes.append(AccessCode(code=code_str, duration_months=duration))
        
        AccessCode.objects.bulk_create(codes, ignore_conflicts=True)
        return Response({'status': 'success', 'message': f'{count} codes generated with {duration} month(s) validation.'})

from access_codes.models import VerificationPackage
from .serializers import AdminVerificationPackageSerializer

class AdminVerificationPackageViewSet(viewsets.ModelViewSet, AdminLoggerMixin):
    queryset = VerificationPackage.objects.all().order_by('-created_at')
    serializer_class = AdminVerificationPackageSerializer
    permission_classes = [IsAdminRole]
    
    def perform_create(self, serializer):
        package = serializer.save()
        self.log_action(self.request.user, "Created Verification Package", "VerificationPackage", str(package.id))

    def perform_update(self, serializer):
        package = serializer.save()
        self.log_action(self.request.user, "Updated Verification Package", "VerificationPackage", str(package.id))

    def perform_destroy(self, instance):
        package_id = str(instance.id)
        instance.delete()
        self.log_action(self.request.user, "Deleted Verification Package", "VerificationPackage", package_id)
