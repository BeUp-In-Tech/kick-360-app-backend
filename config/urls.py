from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OpenAPI Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Apps URLs
    path('api/auth/', include('accounts.urls')),
    path('api/sessions/', include('sessions.urls')),
    path('api/tournaments/', include('tournaments.urls')),
    path('api/trainings/', include('training.urls')),
    path('api/leaderboard/', include('leaderboard.urls')),
    path('api/stats/', include('stats.urls')),
    path('api/follows/', include('follows.urls')),
    path('api/settings/', include('settings_app.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('core.urls')),
    path('api/admin/', include('admin_panel.urls')),
]
