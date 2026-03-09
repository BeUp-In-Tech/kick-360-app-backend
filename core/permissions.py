from rest_framework import permissions

class HasActiveSubscription(permissions.BasePermission):
    """
    Allows access only to users with an active (unexpired) access code.
    Staff members bypass this check.
    """
    message = "Your access code has expired. Please purchase a new one to continue."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_subscription_active
