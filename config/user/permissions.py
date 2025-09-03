from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
        Object-level permission to only allow owners of an object to view and edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `uco_user`.
        return obj.uco_user == request.user