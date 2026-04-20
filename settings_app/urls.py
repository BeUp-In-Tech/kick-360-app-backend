from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, SavedVideoViewSet

router = DefaultRouter()
router.register(r'saved-videos', SavedVideoViewSet, basename='saved-videos')
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
