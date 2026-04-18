from django.urls import path
from .views import TrainingCompleteView, TrainingSessionListView, TrainingSessionWatchView

urlpatterns = [
    path('sessions/', TrainingSessionListView.as_view(), name='training-session-list'),
    path('<uuid:id>/complete/', TrainingCompleteView.as_view(), name='training-complete'),
    path('<uuid:id>/watch/', TrainingSessionWatchView.as_view(), name='training-watch'),
]
