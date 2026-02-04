"""
Decorators for user management audit logging.
"""
from functools import wraps
from typing import Optional, Dict, Any
from django.http import JsonResponse
from rest_framework import status
from .services import UserManagementAuditService


def audit_user_group_assignment(action: str):
    """
    Decorator to audit user-group assignment operations.

    Args:
        action: The action being performed ('CREATE', 'UPDATE', 'DELETE')
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(self, request, *args, **kwargs):
            # Store original data for comparison (for updates/deletes)
            original_data = None
            if action in ['UPDATE', 'DELETE'] and hasattr(self, 'get_object'):
                try:
                    original_obj = await self.aget_object()
                    original_data = {
                        'user_id': original_obj.user.id,
                        'user_email': original_obj.user.email,
                        'group_id': original_obj.group.id,
                        'group_code': original_obj.group.code,
                        'group_name': original_obj.group.name,
                        'is_active': original_obj.is_active
                    }
                except Exception:
                    original_data = None

            # Execute the view function
            response = await view_func(self, request, *args, **kwargs)

            # Log the action if user is authenticated and operation was successful
            if (request.user and request.user.is_authenticated and
                hasattr(response, 'status_code') and response.status_code < 400):

                try:
                    # Get the user_group object from response or retrieve it
                    user_group = None
                    if hasattr(response, 'data') and isinstance(response.data, dict):
                        # For create operations, get the created object
                        if action == 'CREATE' and 'id' in response.data:
                            from user_app.models import UserGroup
                            user_group = await UserGroup.objects.select_related('user', 'group').aget(
                                id=response.data['id']
                            )
                        elif action in ['UPDATE', 'DELETE'] and hasattr(self, 'get_object'):
                            user_group = await self.aget_object()

                    if user_group:
                        # Prepare new values for audit
                        new_values = None
                        if action in ['CREATE', 'UPDATE']:
                            new_values = {
                                'user_id': user_group.user.id,
                                'user_email': user_group.user.email,
                                'group_id': user_group.group.id,
                                'group_code': user_group.group.code,
                                'group_name': user_group.group.name,
                                'is_active': user_group.is_active
                            }

                        # Log the audit event
                        await UserManagementAuditService.log_user_group_assignment(
                            user_group=user_group,
                            action=action,
                            performed_by=request.user,
                            ip_address=UserManagementAuditService.get_client_ip(request),
                            user_agent=UserManagementAuditService.get_user_agent(request),
                            old_values=original_data,
                            new_values=new_values
                        )

                except Exception:
                    # Don't fail the request if audit logging fails
                    pass

            return response
        return wrapper
    return decorator


def audit_group_permission_change(action: str):
    """
    Decorator to audit group permission changes.

    Args:
        action: The action being performed ('CREATE', 'UPDATE', 'DELETE')
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(self, request, *args, **kwargs):
            # Store original data for comparison (for updates/deletes)
            original_data = None
            if action in ['UPDATE', 'DELETE'] and hasattr(self, 'get_object'):
                try:
                    original_obj = await self.aget_object()
                    original_data = {
                        'group_id': original_obj.group.id,
                        'group_code': original_obj.group.code,
                        'group_name': original_obj.group.name,
                        'permission_id': original_obj.permission.id,
                        'permission_codename': original_obj.permission.codename,
                        'permission_name': original_obj.permission.name,
                        'permission_resource': original_obj.permission.resource,
                        'permission_action': original_obj.permission.action,
                        'granted': original_obj.granted
                    }
                except Exception:
                    original_data = None

            # Execute the view function
            response = await view_func(self, request, *args, **kwargs)

            # Log the action if user is authenticated and operation was successful
            if (request.user and request.user.is_authenticated and
                hasattr(response, 'status_code') and response.status_code < 400):

                try:
                    # Get the group_permission object from response or retrieve it
                    group_permission = None
                    if hasattr(response, 'data') and isinstance(response.data, dict):
                        # For create operations, get the created object
                        if action == 'CREATE' and 'id' in response.data:
                            from user_app.models import GroupPermission
                            group_permission = await GroupPermission.objects.select_related(
                                'group', 'permission'
                            ).aget(id=response.data['id'])
                        elif action in ['UPDATE', 'DELETE'] and hasattr(self, 'get_object'):
                            group_permission = await self.aget_object()

                    if group_permission:
                        # Prepare new values for audit
                        new_values = None
                        if action in ['CREATE', 'UPDATE']:
                            new_values = {
                                'group_id': group_permission.group.id,
                                'group_code': group_permission.group.code,
                                'group_name': group_permission.group.name,
                                'permission_id': group_permission.permission.id,
                                'permission_codename': group_permission.permission.codename,
                                'permission_name': group_permission.permission.name,
                                'permission_resource': group_permission.permission.resource,
                                'permission_action': group_permission.permission.action,
                                'granted': group_permission.granted
                            }

                        # Log the audit event
                        await UserManagementAuditService.log_group_permission_change(
                            group_permission=group_permission,
                            action=action,
                            performed_by=request.user,
                            ip_address=UserManagementAuditService.get_client_ip(request),
                            user_agent=UserManagementAuditService.get_user_agent(request),
                            old_values=original_data,
                            new_values=new_values
                        )

                except Exception:
                    # Don't fail the request if audit logging fails
                    pass

            return response
        return wrapper
    return decorator


def audit_bulk_operation(operation_type: str):
    """
    Decorator to audit bulk operations on user management entities.

    Args:
        operation_type: Type of operation ('user_group_assignment', 'group_permission')
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(self, request, *args, **kwargs):
            # Execute the view function
            response = await view_func(self, request, *args, **kwargs)

            # Log the action if user is authenticated and operation was successful
            if (request.user and request.user.is_authenticated and
                hasattr(response, 'status_code') and response.status_code < 400):

                try:
                    # Extract bulk operation details from response
                    if hasattr(response, 'data') and isinstance(response.data, dict):
                        # Log bulk operation summary
                        from user_app.models import audit_log

                        bulk_summary = {
                            'operation_type': operation_type,
                            'total_items': response.data.get('total', 0),
                            'successful_items': response.data.get('successful', 0),
                            'failed_items': response.data.get('failed', 0),
                            'details': response.data.get('details', [])
                        }

                        await audit_log.objects.acreate(
                            user_id=request.user,
                            action='BULK_OPERATION',
                            type_ressource=f'bulk_{operation_type}',
                            id_ressource='',
                            nouvelles_valeurs=bulk_summary,
                            adresse_ip=UserManagementAuditService.get_client_ip(request),
                            user_agent=UserManagementAuditService.get_user_agent(request)
                        )

                except Exception:
                    # Don't fail the request if audit logging fails
                    pass

            return response
        return wrapper
    return decorator
