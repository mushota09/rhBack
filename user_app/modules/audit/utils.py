"""
Utility functions for manual audit logging.
These can be used directly in views when decorators are not suitable.
"""
from typing import Optional, Dict, Any
from django.contrib.auth import get_user_model
from user_app.models import audit_log, UserGroup, GroupPermission
from .services import UserManagementAuditService

User = get_user_model()


async def log_user_group_assignment_manual(
    user_group: UserGroup,
    action: str,
    request,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None
) -> Optional[audit_log]:
    """
    Manually log user-group assignment operations.

    Args:
        user_group: The UserGroup instance being modified
        action: The action being performed ('CREATE', 'UPDATE', 'DELETE')
        request: Django request object
        old_values: Previous values (for updates/deletes)
        new_values: New values (for creates/updates)

    Returns:
        audit_log: The created audit log entry or None if failed
    """
    try:
        return await UserManagementAuditService.log_user_group_assignment(
            user_group=user_group,
            action=action,
            performed_by=request.user,
            ip_address=UserManagementAuditService.get_client_ip(request),
            user_agent=UserManagementAuditService.get_user_agent(request),
            old_values=old_values,
            new_values=new_values
        )
    except Exception:
        # Don't fail the request if audit logging fails
        return None


async def log_group_permission_change_manual(
    group_permission: GroupPermission,
    action: str,
    request,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None
) -> Optional[audit_log]:
    """
    Manually log group permission changes.

    Args:
        group_permission: The GroupPermission instance being modified
        action: The action being performed ('CREATE', 'UPDATE', 'DELETE')
        request: Django request object
        old_values: Previous values (for updates/deletes)
        new_values: New values (for creates/updates)

    Returns:
        audit_log: The created audit log entry or None if failed
    """
    try:
        return await UserManagementAuditService.log_group_permission_change(
            group_permission=group_permission,
            action=action,
            performed_by=request.user,
            ip_address=UserManagementAuditService.get_client_ip(request),
            user_agent=UserManagementAuditService.get_user_agent(request),
            old_values=old_values,
            new_values=new_values
        )
    except Exception:
        # Don't fail the request if audit logging fails
        return None


async def log_bulk_operation_manual(
    operation_type: str,
    request,
    summary_data: Dict[str, Any]
) -> Optional[audit_log]:
    """
    Manually log bulk operations.

    Args:
        operation_type: Type of operation ('user_group_assignment', 'group_permission')
        request: Django request object
        summary_data: Summary data about the bulk operation

    Returns:
        audit_log: The created audit log entry or None if failed
    """
    try:
        return await audit_log.objects.acreate(
            user_id=request.user,
            action='BULK_OPERATION',
            type_ressource=f'bulk_{operation_type}',
            id_ressource='',
            nouvelles_valeurs=summary_data,
            adresse_ip=UserManagementAuditService.get_client_ip(request),
            user_agent=UserManagementAuditService.get_user_agent(request)
        )
    except Exception:
        # Don't fail the request if audit logging fails
        return None
