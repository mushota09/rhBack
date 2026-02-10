"""
Audit logging services for user management events.
"""
import json
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from user_app.models import audit_log, UserGroup, GroupPermission, Group, Permission

User = get_user_model()


class UserManagementAuditService:
    """Service class for handling audit logging of user management operations."""

    @staticmethod
    async def log_user_group_assignment(
        user_group: UserGroup,
        action: str,
        performed_by: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> audit_log:
        """Log user-group assignment operations."""
        resource_id = f"user:{user_group.user.id}->group:{user_group.group.id}"

        if action == 'CREATE':
            audit_old_values = None
            audit_new_values = {
                'user_id': user_group.user.id,
                'user_email': user_group.user.email,
                'group_id': user_group.group.id,
                'group_code': user_group.group.code,
                'group_name': user_group.group.name,
                'assigned_by': user_group.assigned_by.id if user_group.assigned_by else None,
                'assigned_at': user_group.assigned_at.isoformat() if user_group.assigned_at else None,
                'is_active': user_group.is_active
            }
        elif action == 'UPDATE':
            audit_old_values = old_values or {}
            audit_new_values = new_values or {'is_active': user_group.is_active}
        elif action == 'DELETE':
            audit_old_values = old_values or {
                'user_id': user_group.user.id,
                'user_email': user_group.user.email,
                'group_id': user_group.group.id,
                'group_code': user_group.group.code,
                'group_name': user_group.group.name,
                'is_active': user_group.is_active
            }
            audit_new_values = None
        else:
            audit_old_values = old_values
            audit_new_values = new_values

        return await audit_log.objects.acreate(
            user_id=performed_by,
            action=action,
            type_ressource='UserGroup',
            id_ressource=resource_id,
            anciennes_valeurs=audit_old_values,
            nouvelles_valeurs=audit_new_values,
            adresse_ip=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    async def log_group_permission_change(
        group_permission: GroupPermission,
        action: str,
        performed_by: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> audit_log:
        """Log group permission changes."""
        resource_id = f"group:{group_permission.group.id}->permission:{group_permission.permission.id}"

        if action == 'CREATE':
            audit_old_values = None
            audit_new_values = {
                'group_id': group_permission.group.id,
                'group_code': group_permission.group.code,
                'group_name': group_permission.group.name,
                'permission_id': group_permission.permission.id,
                'permission_codename': group_permission.permission.codename,
                'permission_name': group_permission.permission.name,
                'permission_resource': group_permission.permission.resource,
                'permission_action': group_permission.permission.action,
                'granted': group_permission.granted,
                'created_by': group_permission.created_by.id if group_permission.created_by else None,
                'created_at': group_permission.created_at.isoformat() if group_permission.created_at else None
            }
        elif action == 'UPDATE':
            audit_old_values = old_values or {}
            audit_new_values = new_values or {'granted': group_permission.granted}
        elif action == 'DELETE':
            audit_old_values = old_values or {
                'group_id': group_permission.group.id,
                'group_code': group_permission.group.code,
                'permission_id': group_permission.permission.id,
                'permission_codename': group_permission.permission.codename,
                'granted': group_permission.granted
            }
            audit_new_values = None
        else:
            audit_old_values = old_values
            audit_new_values = new_values

        return await audit_log.objects.acreate(
            user_id=performed_by,
            action=action,
            type_ressource='GroupPermission',
            id_ressource=resource_id,
            anciennes_valeurs=audit_old_values,
            nouvelles_valeurs=audit_new_values,
            adresse_ip=ip_address,
            user_agent=user_agent
        )

    @staticmethod
    def get_client_ip(request) -> Optional[str]:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def get_user_agent(request) -> str:
        """Extract user agent from request."""
        return request.META.get('HTTP_USER_AGENT', '')
