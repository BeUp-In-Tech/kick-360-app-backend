from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminTournamentViewSet

router = DefaultRouter()
router.register(r'', AdminTournamentViewSet, basename='admin-tournaments')

urlpatterns = [
    path('', include(router.urls)),
]
