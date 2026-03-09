from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminAccessCodeDetailViewSet

router = DefaultRouter()
router.register(r'', AdminAccessCodeDetailViewSet, basename='admin-access-codes')

urlpatterns = [
    path('', include(router.urls)),
]
