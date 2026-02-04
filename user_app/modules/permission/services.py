"""
Permission service for user management system.

This module provides services for calculating and checking user permissions
based on their group assignments and the permissions granted to those groups.
"""

from typing import List, Set, Dict, Any
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from user_app.models import UserGroup, GroupPermission

User = get_user_model()


class PermissionService:
    """
    Service class for managing user permissions and group-based access control.
    """

    CACHE_TIMEOUT = 300  # 5 minutes cache timeout
    CACHE_PREFIX = "user_permissions"

    @classmethod
    async def get_user_permissions(cls, user: User) -> Set[str]:
        """
        Get all permissions for a user based on their group memberships.
        """
        if not user or not user.is_active:
            return set()

        # Check cache first
        cache_key = f"{cls.CACHE_PREFIX}:{user.id}"
        cached_permissions = cache.get(cache_key)
        if cached_permissions is not None:
            return cached_permissions

        # Get user's active groups
        user_groups = await sync_to_async(list)(
            UserGroup.objects.filter(
                user=user,
                is_active=True,
                group__is_active=True
            ).select_related('group')
        )

        if not user_groups:
            return set()

        # Get all permissions for these groups
        group_ids = [ug.group.id for ug in user_groups]
        group_permissions = await sync_to_async(list)(
            GroupPermission.objects.filter(
                group_id__in=group_ids,
                granted=True
            ).select_related('permission')
        )

        # Extract permission codenames
        permissions = {gp.permission.codename for gp in group_permissions}

        # Cache the result
        cache.set(cache_key, permissions, cls.CACHE_TIMEOUT)

        return permissions

    @classmethod
    async def check_permission(cls, user: User, resource: str, action: str) -> bool:
        """
        Check if a user has a specific permission.
        """
        if not user or not user.is_active:
            return False

        # Superusers have all permissions
        if user.is_superuser:
            return True

        # Get user permissions
        user_permissions = await cls.get_user_permissions(user)

        # Check for specific permission
        permission_codename = f"{resource}.{action}"
        return permission_codename in user_permissions

    @classmethod
    async def get_effective_permissions(cls, user: User) -> Dict[str, Any]:
        """
        Get detailed information about user's effective permissions.
        """
        if not user or not user.is_active:
            return {
                'groups': [],
                'permissions': [],
                'permission_count': 0,
                'group_count': 0
            }

        # Get user's active groups with details
        user_groups = await sync_to_async(list)(
            UserGroup.objects.filter(
                user=user,
                is_active=True,
                group__is_active=True
            ).select_related('group').order_by('group__code')
        )

        groups_data = []
        for ug in user_groups:
            groups_data.append({
                'id': ug.group.id,
                'code': ug.group.code,
                'name': ug.group.name,
                'description': ug.group.description,
                'assigned_at': ug.assigned_at
            })

        # Get all permissions for these groups
        if user_groups:
            group_ids = [ug.group.id for ug in user_groups]
            group_permissions = await sync_to_async(list)(
                GroupPermission.objects.filter(
                    group_id__in=group_ids,
                    granted=True
                ).select_related('permission', 'group').order_by(
                    'permission__resource', 'permission__action'
                )
            )

            permissions_data = []
            for gp in group_permissions:
                permissions_data.append({
                    'id': gp.permission.id,
                    'codename': gp.permission.codename,
                    'name': gp.permission.name,
                    'resource': gp.permission.resource,
                    'action': gp.permission.action,
                    'description': gp.permission.description,
                    'granted_by_group': gp.group.code
                })
        else:
            permissions_data = []

        return {
            'groups': groups_data,
            'permissions': permissions_data,
            'permission_count': len(permissions_data),
            'group_count': len(groups_data)
        }

    @classmethod
    async def has_any_group(cls, user: User, group_codes: List[str]) -> bool:
        """
        Check if user belongs to any of the specified groups.
        """
        if not user or not user.is_active or not group_codes:
            return False

        user_group_codes = await sync_to_async(list)(
            UserGroup.objects.filter(
                user=user,
                is_active=True,
                group__is_active=True,
                group__code__in=group_codes
            ).values_list('group__code', flat=True)
        )

        return len(user_group_codes) > 0

    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> None:
        """
        Invalidate cached permissions for a specific user.
        """
        cache_key = f"{cls.CACHE_PREFIX}:{user_id}"
        cache.delete(cache_key)

    @classmethod
    def invalidate_all_cache(cls) -> None:
        """
        Invalidate all cached permissions.
        """
        cache.clear()

    @classmethod
    async def can_manage_user_groups(cls, user: User, target_user: User) -> bool:
        """
        Check if a user can manage group assignments for another user.
        """
        if not user or not user.is_active:
            return False

        # Superusers can manage anyone
        if user.is_superuser:
            return True

        # Check for specific user management permission
        has_permission = await cls.check_permission(user, 'user_management', 'UPDATE')
        if not has_permission:
            return False

        # Additional business rules can be added here based on target_user
        # For example: users can only manage users in their department

        return True
