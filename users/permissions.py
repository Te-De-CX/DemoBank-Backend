from rest_framework.permissions import BasePermission

class IsVerified(BasePermission):
    message = 'User email not verified.'
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_verified

class IsAccountOwner(BasePermission):
    """Ensure the user owns the account they are trying to access."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user