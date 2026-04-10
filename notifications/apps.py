from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import os

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        # Initialize Firebase Admin SDK
        firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS')
        
        if firebase_cred_path and os.path.exists(firebase_cred_path):
            try:
                cred = credentials.Certificate(firebase_cred_path)
                # Check if already initialized to avoid errors during reloads
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
            except Exception as e:
                print(f"Failed to initialize Firebase: {e}")
        else:
            print("FIREBASE_CREDENTIALS not set or file not found. Push notifications will be mocked.")
