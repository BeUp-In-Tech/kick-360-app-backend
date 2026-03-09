from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminTrainingSessionViewSet, AdminTrainingCategoryViewSet

router = DefaultRouter()
router.register(r'categories', AdminTrainingCategoryViewSet, basename='admin-training-categories')
router.register(r'', AdminTrainingSessionViewSet, basename='admin-training-sessions')

urlpatterns = [
    path('', include(router.urls)),
]
