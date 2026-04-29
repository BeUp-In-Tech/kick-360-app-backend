import firebase_admin
from firebase_admin import messaging
from .models import FCMDevice
import logging

logger = logging.getLogger(__name__)

def send_push_notification(users, title, body, data_payload=None):
    """
    Sends a push notification to specific users using their registered FCM devices.
    Uses the single message send method for better background delivery reliability.
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

        success_count = 0
        failure_count = 0
        
        for token in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=clean_data_payload,
                    token=token,
                    # Set Android configuration (optional prioritization)
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                        ),
                    ),
                    # Set APNS for iOS background delivery
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                content_available=True,
                            ),
                        ),
                    ),
                )
                
                response = messaging.send(message)
                logger.info(f"Successfully sent push notification to {token}: {response}")
                success_count += 1
            except Exception as send_error:
                logger.error(f"Failed to send push notification to {token}: {str(send_error)}")
                failure_count += 1
                
                # Clean up unregistered tokens if possible
                if 'registration-token-not-registered' in str(send_error).lower() or 'invalid-registration-token' in str(send_error).lower():
                    FCMDevice.objects.filter(registration_id=token).update(is_active=False)
                    logger.info(f"Deactivated invalid token: {token}")

        logger.info(f"FCM Sending complete: {success_count} success, {failure_count} failure")
        return True, f"Success: {success_count}, Failure: {failure_count}"
        
    except Exception as e:
        logger.error(f"Error in push notification loop: {str(e)}")
        return False, str(e)

def create_user_notification(user, title, message, notification_type, related_item_id=None):
    from .models import Notification
    notification = Notification.objects.create(
        recipient=user,
        is_for_admin=False,
        title=title,
        message=message,
        notification_type=notification_type,
        related_item_id=related_item_id
    )
    send_push_notification([user], title, message, data_payload={
        'notification_type': notification_type,
        'related_item_id': str(related_item_id) if related_item_id else ''
    })
    return notification

def create_admin_notification(title, message, notification_type, related_item_id=None):
    from .models import Notification
    from accounts.models import User
    
    # Broadcast to all staff members
    admins = User.objects.filter(is_staff=True, is_active=True)
    notifications_to_create = []
    
    for admin in admins:
        notifications_to_create.append(
            Notification(
                recipient=admin,
                is_for_admin=True,
                title=title,
                message=message,
                notification_type=notification_type,
                related_item_id=related_item_id
            )
        )
    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        send_push_notification(admins, title, message, data_payload={
            'notification_type': notification_type,
            'related_item_id': str(related_item_id) if related_item_id else ''
        })

