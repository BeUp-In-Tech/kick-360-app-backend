from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User
from .models import Session
from .services import SessionService
from unittest.mock import patch, MagicMock

class SessionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(access_code="SES_CODE", name="Session User", total_kicks=10, points=0, streak=0)
        self.client.force_authenticate(user=self.user)
        self.complete_url = reverse('session-complete')

    def test_session_complete_stats_update(self):
        data = {
            "total_kick": 15,
            "mode": "default",
            "session_duration": 5
        }
        
        response = self.client.post(self.complete_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify user stats updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.total_kicks, 25) # 10 + 15
        self.assertEqual(self.user.points, 10)
        self.assertEqual(self.user.streak, 1) # Missed previous day so streak is 1
        
        self.assertEqual(Session.objects.count(), 1)

    @patch('django.core.files.uploadedfile.SimpleUploadedFile')
    def test_session_complete_video_limit(self, mock_file):
        # Create 5 video sessions
        for i in range(5):
            Session.objects.create(
                user=self.user,
                total_kick=1,
                video_file=f"dummy_{i}.mp4"
            )
            
        data = {
            "total_kick": 5,
        }
        
        # Assuming we pass a file, but for test we can mock request.FILES by using mock form or passing dummy in test
        # Let's mock the service directly to test the ValueError for video limit
        with self.assertRaises(ValueError):
            SessionService.complete_session(self.user, data, video_file="new_dummy.mp4")

    def test_session_complete_limit_error_response(self):
        for i in range(5):
            Session.objects.create(
                user=self.user,
                total_kick=1,
                video_file=f"dummy_{i}.mp4"
            )
            
        # Passing mock file object in API test to hit the limit
        from django.core.files.uploadedfile import SimpleUploadedFile
        video = SimpleUploadedFile("file.mp4", b"file_content", content_type="video/mp4")
        
        data = {
            "total_kick": 5,
            "video_file": video
        }
        
        response = self.client.post(self.complete_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn("Video limit reached", response.data['message'])
