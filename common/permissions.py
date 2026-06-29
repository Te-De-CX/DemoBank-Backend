# common/permissions.py
from rest_framework.permissions import BasePermission

class IsAccountOwner(BasePermission):
    """Allow only the owner of the account to access it."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user