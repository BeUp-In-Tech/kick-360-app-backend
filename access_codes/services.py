import requests
import logging

logger = logging.getLogger(__name__)

class ShopifyService:
    @staticmethod
    def verify_access_code(code: str) -> dict:
        """
        Verifies if an access code is valid via Shopify API.
        Returns a dict: {'is_valid': bool, 'meta': dict}
        """
        try:
            response = requests.get('https://kick360-shopify-backend.onrender.com/api/access-codes/')
            if response.status_code == 200:
                codes = response.json()
                for c in codes:
                    if c.get('code') == code:
                        if c.get('status') == 'sent':
                            return {'is_valid': True, 'meta': c}
                        else:
                            return {
                                'is_valid': False, 
                                'meta': {'error': 'Access code is not activated (status: not_sent).'}
                            }
                return {
                    'is_valid': False, 
                    'meta': {'error': 'Invalid access code.'}
                }
            else:
                logger.error(f"Shopify API returned status {response.status_code}")
                return {
                    'is_valid': False, 
                    'meta': {'error': 'Could not reach Shopify service.'}
                }
        except Exception as e:
            logger.error(f"Error fetching from Shopify API: {str(e)}")
            return {
                'is_valid': False, 
                'meta': {'error': 'Error verifying access code.'}
            }

