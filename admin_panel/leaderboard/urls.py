from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminLeaderboardViewSet

router = DefaultRouter()
router.register(r'', AdminLeaderboardViewSet, basename='admin-leaderboard')

urlpatterns = [
    path('', include(router.urls)),
]
