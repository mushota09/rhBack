"""
Permission module for user management system.

This module provides services and permission classes for group-based access control.
"""

from .services import PermissionService
from .permissions import (
    HasGroupPermission,
    CanManageUserGroups,
    HasSpecificPermission,
    IsGroupMember,
    CanManagePermissions
)
from .views import GroupPermissionViewSet, PermissionViewSet
from .serializers import (
    PermissionSerializer,
    GroupPermissionReadSerializer,
    GroupPermissionWriteSerializer,
    BulkGroupPermissionSerializer,
    GroupPermissionSummarySerializer
)

__all__ = [
    'PermissionService',
    'HasGroupPermission',
    'CanManageUserGroups',
    'HasSpecificPermission',
    'IsGroupMember',
    'CanManagePermissions',
    'GroupPermissionViewSet',
    'PermissionViewSet',
    'PermissionSerializer',
    'GroupPermissionReadSerializer',
    'GroupPermissionWriteSerializer',
    'BulkGroupPermissionSerializer',
    'GroupPermissionSummarySerializer'
]
