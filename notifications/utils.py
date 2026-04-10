import firebase_admin
from firebase_admin import messaging
from .models import FCMDevice
import logging

logger = logging.getLogger(__name__)

def send_push_notification(users, title, body, data_payload=None):
    """
    Sends a push notification to specific users using their registered FCM devices.
    
    Args:
        users: A QuerySet of users or a single User instance to send the notification to.
        title (str): The notification title.
        body (str): The notification body.
        data_payload (dict): Optional custom data to send along with the notification.
    """
    if data_payload is None:
        data_payload = {}
        
    # Ensure all values in data payload are strings (FCM requirement)
    clean_data_payload = {str(k): str(v) for k, v in data_payload.items()}
        
    try:
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            logger.warning("Firebase Admin SDK not initialized. Mocking push notification:")
            logger.warning(f"Title: {title} | Body: {body} | Users: {users}")
            return False, "Mocked - Firebase not initialized"

        devices = FCMDevice.objects.filter(user__in=users, is_active=True).values_list('registration_id', flat=True)
        tokens = list(devices)

        if not tokens:
            logger.info(f"No active tokens found for the targeted users to send: {title}")
            return False, "No active tokens found"

        # Split tokens into batches of 500 (FCM API limit)
        success_count = 0
        failure_count = 0
        
        for i in range(0, len(tokens), 500):
            batch_tokens = tokens[i:i + 500]
            
            message = messaging.MulticastMessage(
                tokens=batch_tokens,
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=clean_data_payload,
                # Set Android configuration (optional prioritization)
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                    ),
                ),
                # Set APNS for iOS
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound='default'),
                    ),
                ),
            )
            
            response = messaging.send_each_for_multicast(message)
            success_count += response.success_count
            failure_count += response.failure_count
            
            # Clean up unregistered tokens
            if response.failure_count > 0:
                responses = response.responses
                for idx, resp in enumerate(responses):
                    if not resp.success:
                        if resp.exception.code in ('messaging/invalid-registration-token', 'messaging/registration-token-not-registered'):
                            # The token is no longer valid; mark it inactive or delete it
                            token_to_remove = batch_tokens[idx]
                            FCMDevice.objects.filter(registration_id=token_to_remove).update(is_active=False)
                            logger.info(f"Deactivated invalid token: {token_to_remove}")

        logger.info(f"FCM Multicast sent: {success_count} success, {failure_count} failure")
        return True, f"Success: {success_count}, Failure: {failure_count}"
        
    except Exception as e:
        logger.error(f"Error sending FCM notification: {str(e)}")
        return False, str(e)
