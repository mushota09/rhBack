"""
Decorators for role-based access control and audit logging.
"""
from functools import wraps
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from user_app.models import audit_log

User = get_user_model()


def require_role(required_roles):
    """
    Decorator to require specific roles for view access.

    Args:
        required_roles: List of required roles ['hr_admin', 'hr_manager', 'employee']
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user_roles = get_user_roles(request.user)

            # Check if user has any of the required roles
            if not any(role in user_roles for role in required_roles):
                return JsonResponse(
                    {'error': 'Insufficient permissions'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return await view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def audit_action(action_type, resource_type):
    """
    Decorator to automatically log actions for audit purposes.

    Args:
        action_type: Type of action ('CREATE', 'UPDATE', 'DELETE', 'VIEW', 'PROCESS')
        resource_type: Type of resource being acted upon
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(request, *args, **kwargs):
            # Execute the view function
            response = await view_func(request, *args, **kwargs)

            # Log the action if user is authenticated and operation was successful
            if (request.user and request.user.is_authenticated and
                hasattr(response, 'status_code') and response.status_code < 400):

                try:
                    # Extract resource ID from kwargs or response
                    resource_id = kwargs.get('pk', kwargs.get('id', ''))

                    # Create audit log entry
                    await audit_log.objects.acreate(
                        user_id=request.user,
                        action=action_type,
                        type_ressource=resource_type,
                        id_ressource=str(resource_id),
                        adresse_ip=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    )
                except Exception:
                    # Don't fail the request if audit logging fails
                    pass

            return response
        return wrapper
    return decorator


def require_payroll_permission(permission_type):
    """
    Decorator to require specific payroll permissions.

    Args:
        permission_type: Type of permission ('read', 'write', 'process', 'approve')
    """
    def decorator(view_func):
        @wraps(view_func)
        async def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            has_permission = check_payroll_permission(request.user, permission_type)

            if not has_permission:
                return JsonResponse(
                    {'error': f'Insufficient permissions for {permission_type} operations'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return await view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_roles(user):
    """
    Get the roles for a user based on their attributes.

    Args:
        user: User instance

    Returns:
        List of role strings
    """
    roles = []

    if user.is_superuser:
        roles.extend(['hr_admin', 'hr_manager', 'employee'])
    elif user.is_staff:
        roles.extend(['hr_manager', 'employee'])
    else:
        roles.append('employee')

    return roles


def check_payroll_permission(user, permission_type):
    """
    Check if user has specific payroll permission.

    Args:
        user: User instance
        permission_type: Type of permission to check

    Returns:
        Boolean indicating if user has permission
    """
    if not user or not user.is_authenticated:
        return False

    permission_map = {
        'read': user.is_authenticated,  # All authenticated users can read
        'write': user.is_staff or user.is_superuser,  # Only staff can write
        'process': user.is_staff or user.is_superuser,  # Only staff can process
        'approve': user.is_superuser,  # Only superusers can approve
        'export': user.is_staff or user.is_superuser,  # Only staff can export
        'audit': user.is_superuser,  # Only superusers can view audit logs
    }

    return permission_map.get(permission_type, False)


def get_client_ip(request):
    """
    Get the client IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
