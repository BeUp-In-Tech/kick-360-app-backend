from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to users with staff status or a specific 'Admin' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)

class AdminLoggerMixin:
    """
    Mixin to log admin actions.
    """
    def log_action(self, admin, action, target_model=None, target_id=None, details=None):
        from core.models import AdminActionLog
        AdminActionLog.objects.create(
            admin=admin,
            action=action,
            target_model=target_model,
            target_id=target_id,
            details=details
        )
