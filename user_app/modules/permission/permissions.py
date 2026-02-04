"""
Custom permission classes for the user management system.
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from .services import PermissionService


class HasGroupPermission(BasePermission):
    """
    Permission class that checks if the user has the required group-based permission
    for the requested action on the resource.
    """

    # Mapping of HTTP methods to permission actions
    METHOD_ACTION_MAP = {
        'GET': 'READ',
        'HEAD': 'READ',
        'OPTIONS': 'READ',
        'POST': 'CREATE',
        'PUT': 'UPDATE',
        'PATCH': 'UPDATE',
        'DELETE': 'DELETE',
    }

    async def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if the user has permission to perform the requested action."""
        # Allow unauthenticated users to be handled by other permission classes
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have all permissions
        if request.user.is_superuser:
            return True

        # Determine the resource name from the view
        resource = self._get_resource_name(view)
        if not resource:
            return False

        # Determine the action from the HTTP method
        action = self._get_action_from_method(request.method)
        if not action:
            return False

        # Check if user has the required permission
        return await PermissionService.check_permission(request.user, resource, action)

    def _get_resource_name(self, view: APIView) -> str:
        """Extract the resource name from the view."""
        # Try to get resource name from view attribute
        if hasattr(view, 'resource_name'):
            return view.resource_name

        # Try to get from model
        if hasattr(view, 'queryset') and view.queryset is not None:
            return view.queryset.model._meta.model_name

        if hasattr(view, 'model') and view.model is not None:
            return view.model._meta.model_name

        return ""

    def _get_action_from_method(self, method: str) -> str:
        """Map HTTP method to permission action."""
        return self.METHOD_ACTION_MAP.get(method.upper(), "")


class CanManageUserGroups(BasePermission):
    """
    Permission class specifically for managing user-group assignments.
    """

    async def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if the user can manage user-group assignments."""
        # Allow unauthenticated users to be handled by other permission classes
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers can always manage user groups
        if request.user.is_superuser:
            return True

        # For read operations, check if user has read permission
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return await PermissionService.check_permission(
                request.user, 'user_group', 'READ'
            )

        # For write operations, check if user has update permission
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return await PermissionService.check_permission(
                request.user, 'user_group', 'UPDATE'
            )

        return False


class HasSpecificPermission(BasePermission):
    """
    Permission class that checks for a specific permission.
    """

    async def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if the user has the specific permission defined in the view."""
        # Allow unauthenticated users to be handled by other permission classes
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have all permissions
        if request.user.is_superuser:
            return True

        # Get required permission from view
        if not hasattr(view, 'required_permission'):
            return False

        required_permission = view.required_permission
        if not isinstance(required_permission, (tuple, list)) or len(required_permission) != 2:
            return False

        resource, action = required_permission
        return await PermissionService.check_permission(request.user, resource, action)


class IsGroupMember(BasePermission):
    """
    Permission class that checks if the user belongs to specific groups.
    """

    async def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if the user belongs to any of the required groups."""
        # Allow unauthenticated users to be handled by other permission classes
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers bypass group checks
        if request.user.is_superuser:
            return True

        # Get required groups from view
        if not hasattr(view, 'required_groups'):
            return False

        required_groups = view.required_groups
        if not isinstance(required_groups, (list, tuple)):
            return False

        return await PermissionService.has_any_group(request.user, required_groups)


class CanManagePermissions(BasePermission):
    """
    Permission class for managing group permissions.
    """

    async def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if the user can manage group permissions."""
        # Allow unauthenticated users to be handled by other permission classes
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers can always manage permissions
        if request.user.is_superuser:
            return True

        # For read operations, check if user has read permission
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return await PermissionService.check_permission(
                request.user, 'group_permission', 'READ'
            )

        # For write operations, check if user has update permission
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return await PermissionService.check_permission(
                request.user, 'group_permission', 'UPDATE'
            )

        return False
