from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

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
    path('api/access-codes/', include('access_codes.urls')),

    # Manual Media Serving (for Render Persistent Disk in production)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
