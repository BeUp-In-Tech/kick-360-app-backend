from django.urls import path
from .views import AccessCodeVerifyView, VerificationPackageListView

urlpatterns = [
    path('verify/', AccessCodeVerifyView.as_view(), name='access-code-verify'),
    path('packages/', VerificationPackageListView.as_view(), name='verification-packages'),
]
