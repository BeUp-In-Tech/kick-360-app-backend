from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminUserViewSet

router = DefaultRouter()
router.register(r'', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('', include(router.urls)),
]
