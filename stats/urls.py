from django.urls import path
from .views import StatsLeaderboardView, PerformanceRecordView

urlpatterns = [
    path('leaderboard/', StatsLeaderboardView.as_view(), name='stats-leaderboard'),
    path('record/', PerformanceRecordView.as_view(), name='performance-record'),
    path('performance/', PerformanceRecordView.as_view(), name='performance-stats'),
]
