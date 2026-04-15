from django.urls import path
from .views import AccessCodeVerifyView

urlpatterns = [
    path('verify/', AccessCodeVerifyView.as_view(), name='access-code-verify'),
]
