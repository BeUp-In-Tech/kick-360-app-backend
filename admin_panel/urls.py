from django.urls import path, include

from .auth_views import (
    AdminLoginView, 
    AdminPasswordResetView,
    ForgotPasswordView,
    SetNewPasswordView,
    AdminLogoutView
)

urlpatterns = [
    path('auth/login/', AdminLoginView.as_view(), name='admin-login'),
    path('auth/logout/', AdminLogoutView.as_view(), name='admin-logout'),
    path('auth/reset-password/', AdminPasswordResetView.as_view(), name='admin-reset-password'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='admin-forgot-password'),
    path('auth/set-new-password/', SetNewPasswordView.as_view(), name='admin-set-new-password'),
    path('overview/', include('admin_panel.analytics.urls')),
    path('analytics/export-pdf/', include('admin_panel.analytics.urls')), # Supporting both paths
    path('users/', include('admin_panel.users.urls')),
    path('tournaments/', include('admin_panel.tournaments.urls')),
    path('videos/', include('admin_panel.videos.urls')),
    path('access-codes/', include('admin_panel.access_codes.urls')),
    path('leaderboard/', include('admin_panel.leaderboard.urls')),
]
