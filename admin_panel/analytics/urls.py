from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminOverviewViewSet

router = DefaultRouter()
router.register(r'', AdminOverviewViewSet, basename='admin-overview')

urlpatterns = [
    path('', include(router.urls)),
]
