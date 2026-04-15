from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status 
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            "success": False,
            "error": {
                "code": exc.__getattribute__('default_code') if hasattr(exc, 'default_code') else exc.__class__.__name__,
                "message": exc.default_detail if hasattr(exc, 'default_detail') else str(exc),
                "details": response.data
            }
        }
        response.data = custom_response
    else:
        logger.error(f"Unexpected error: {str(exc)}")
        
    return response

class APIResponse(Response):
    def __init__(self, data=None, message="Success", **kwargs):
        formatted_data = {
            "success": True,
            "message": message,
            "data": data
        }
        super().__init__(formatted_data, **kwargs)
