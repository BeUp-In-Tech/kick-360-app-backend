from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User
from access_codes.models import AccessCode
from unittest.mock import patch

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
    def test_successful_registration(self):
        AccessCode.objects.create(code="VALID123", status="sent")
        
        data = {
            "name": "Test User",
            "country": "Germany",
            "position": "Forward",
            "access_code": "VALID123"
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(AccessCode.objects.filter(code="VALID123", is_consumed=True).exists())

    def test_registration_invalid_code(self):
        data = {
            "name": "Test User",
            "country": "Germany",
            "position": "Forward",
            "access_code": "INVALID1"
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertEqual(User.objects.count(), 0)

    def test_registration_already_consumed_code(self):
        AccessCode.objects.create(code="CONS1234", status="sent", is_consumed=True) # Already consumed locally
        
        data = {
            "name": "Test User",
            "country": "Germany",
            "position": "Forward",
            "access_code": "CONS1234"
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_registration_not_sent_code(self):
        AccessCode.objects.create(code="NOTSN123", status="not_sent")
        
        data = {
            "name": "Test User",
            "country": "Germany",
            "position": "Forward",
            "access_code": "NOTSN123"
        }
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


    def test_successful_login(self):
        # Create active user
        User.objects.create_user(access_code="LOGIN_CODE", name="Log User")
        
        data = {
            "access_code": "LOGIN_CODE"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data']['tokens'])

    def test_login_invalid_code(self):
        data = {
            "access_code": "UNKNOWN_CODE"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
