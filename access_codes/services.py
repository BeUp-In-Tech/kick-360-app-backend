import requests
import logging

logger = logging.getLogger(__name__)

class ShopifyService:
    @staticmethod
    def fetch_all_codes() -> list:
        """
        Fetches all access codes from Shopify API.
        """
        try:
            response = requests.get('https://kick360-shopify-backend.onrender.com/api/access-codes/', timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Shopify API returned status {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching from Shopify API: {str(e)}")
            return []

    @staticmethod
    def sync_access_codes() -> dict:
        """
        Synchronizes external Shopify codes with local database.
        """
        from access_codes.models import AccessCode
        
        codes_data = ShopifyService.fetch_all_codes()
        if not codes_data:
            return {'status': 'error', 'message': 'No data fetched from Shopify.'}
        
        created_count = 0
        updated_count = 0
        
        for item in codes_data:
            code_str = item.get('code')
            if not code_str:
                continue
                
            status = item.get('status', 'not_sent')
            order_id = item.get('order_id')
            email = item.get('email')
            
            access_code, created = AccessCode.objects.update_or_create(
                code=code_str,
                defaults={
                    'status': status,
                    'shopify_order_id': order_id,
                    'shopify_email': email,
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
                
        return {
            'status': 'success', 
            'created': created_count, 
            'updated': updated_count,
            'total': len(codes_data)
        }

    @staticmethod
    def verify_access_code(code: str) -> dict:
        """
        Verifies if an access code is valid via Shopify API.
        Returns a dict: {'is_valid': bool, 'meta': dict}
        """
        codes = ShopifyService.fetch_all_codes()
        if not codes:
            return {
                'is_valid': False, 
                'meta': {'error': 'Could not reach Shopify service.'}
            }
            
        for c in codes:
            if c.get('code') == code:
                if c.get('status') == 'sent':
                    return {'is_valid': True, 'meta': c}
                else:
                    return {
                        'is_valid': False, 
                        'meta': {'error': f'Access code is not activated (status: {c.get("status")}).'}
                    }
        return {
            'is_valid': False, 
            'meta': {'error': 'Invalid access code.'}
        }

