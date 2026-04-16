from django.urls import path
from .views import (
    RegisterDeviceView,
    UserNotificationListView,
    AdminNotificationListView,
    NotificationDetailView
)

urlpatterns = [
    path('register-device/', RegisterDeviceView.as_view(), name='register-device'),
    
    # User endpoints
    path('', UserNotificationListView.as_view(), name='user-notifications-list'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    
    # Admin endpoints
    path('admin/', AdminNotificationListView.as_view(), name='admin-notifications-list'),
    path('admin/<uuid:pk>/', NotificationDetailView.as_view(), name='admin-notification-detail'),
]
