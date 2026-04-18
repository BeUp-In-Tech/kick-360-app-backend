from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminAccessCodeDetailViewSet, AdminVerificationPackageViewSet

router = DefaultRouter()
router.register(r'packages', AdminVerificationPackageViewSet, basename='admin-verification-packages')
router.register(r'', AdminAccessCodeDetailViewSet, basename='admin-access-codes')

urlpatterns = [
    path('', include(router.urls)),
]
