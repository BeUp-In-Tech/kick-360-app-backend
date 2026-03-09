from django.urls import path
from .views import TrainingCompleteView, TrainingSessionListView

urlpatterns = [
    path('sessions/', TrainingSessionListView.as_view(), name='training-session-list'),
    path('<int:pk>/complete/', TrainingCompleteView.as_view(), name='training-complete'),
]
