from django.urls import path
from .views import SessionCompleteView, SessionHistoryView, SessionShareToggleView, DailySessionCreateView, StoryUploadView, GlobalStoriesView, SessionDetailView

urlpatterns = [
    path('complete/', SessionCompleteView.as_view(), name='session-complete'),
    path('daily/', DailySessionCreateView.as_view(), name='session-daily'),
    path('story/', StoryUploadView.as_view(), name='session-story'),
    path('history/', SessionHistoryView.as_view(), name='session-history'),
    path('stories/', GlobalStoriesView.as_view(), name='global-stories'),
    path('<uuid:pk>/', SessionDetailView.as_view(), name='session-detail'),
    path('<int:pk>/share/', SessionShareToggleView.as_view(), name='session-share-toggle'),
]
