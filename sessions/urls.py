from django.urls import path
from .views import SessionCompleteView, SessionHistoryView, SessionShareToggleView, DailySessionCreateView, StoryUploadView, GlobalStoriesView

urlpatterns = [
    path('complete/', SessionCompleteView.as_view(), name='session-complete'),
    path('daily/', DailySessionCreateView.as_view(), name='session-daily'),
    path('story/', StoryUploadView.as_view(), name='session-story'),
    path('history/', SessionHistoryView.as_view(), name='session-history'),
    path('stories/', GlobalStoriesView.as_view(), name='global-stories'),
    path('<int:pk>/share/', SessionShareToggleView.as_view(), name='session-share-toggle'),
]
