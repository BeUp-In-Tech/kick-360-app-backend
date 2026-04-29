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
        
        # Fallback to the JSON file in the firebase directory if env var is missing
        if not firebase_cred_path or not os.path.exists(firebase_cred_path):
            fallback_path = os.path.join(settings.BASE_DIR, 'firebase', 'kick360-ed2da-firebase-adminsdk-fbsvc-577c2f5cc3.json')
            if os.path.exists(fallback_path):
                firebase_cred_path = fallback_path
                print(f"Using fallback Firebase credentials: {firebase_cred_path}")
        
        if firebase_cred_path and os.path.exists(firebase_cred_path):
            try:
                cred = credentials.Certificate(firebase_cred_path)
                # Check if already initialized to avoid errors during reloads
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                    print("Firebase Admin SDK initialized successfully.")
            except Exception as e:
                print(f"Failed to initialize Firebase: {e}")
        else:
            print("FIREBASE_CREDENTIALS not set and fallback file not found. Push notifications will be mocked.")
        
        # Import signals to register them
        import notifications.signals
