"""
Role-based permissions for the payroll system.
"""
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class IsHRAdmin(BasePermission):
    """
    Permission for HR administrators who can manage all payroll operations.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers have all permissions
        if request.user.is_superuser:
            return True

        # Check if user is staff (HR admin)
        return request.user.is_staff


class IsHRManager(BasePermission):
    """
    Permission for HR managers who can view and process payroll.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers and staff have manager permissions
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Check if user has an employee record with manager role
        if hasattr(request.user, 'employe_id') and request.user.employe_id:
            # For now, consider users with employee records as potential managers
            # This can be extended with specific role fields
            return True

        return False


class IsEmployee(BasePermission):
    """
    Permission for employees who can view their own payroll information.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # All authenticated users are considered employees
        return True

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to only allow employees to see their own data.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers and staff can access all objects
        if request.user.is_superuser or request.user.is_staff:
            return True

        # Employees can only access their own data
        if hasattr(obj, 'employe_id') and hasattr(request.user, 'employe_id'):
            return obj.employe_id == request.user.employe_id

        return False


class CanProcessPayroll(BasePermission):
    """
    Permission for users who can process payroll periods.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Only superusers and staff can process payroll
        return request.user.is_superuser or request.user.is_staff


class CanApprovePayroll(BasePermission):
    """
    Permission for users who can approve payroll periods.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Only superusers can approve payroll
        # This can be extended to include specific approval roles
        return request.user.is_superuser


class CanManageDeductions(BasePermission):
    """
    Permission for users who can manage employee deductions.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Only superusers and staff can manage deductions
        return request.user.is_superuser or request.user.is_staff


class CanViewAuditLogs(BasePermission):
    """
    Permission for users who can view audit logs.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Only superusers can view audit logs
        return request.user.is_superuser


class CanExportData(BasePermission):
    """
    Permission for users who can export payroll data.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers and staff can export data
        return request.user.is_superuser or request.user.is_staff


# Permission combinations for common use cases
class PayrollReadPermission(BasePermission):
    """
    Combined permission for reading payroll data.
    """
    def has_permission(self, request, view):
        # Allow read operations for HR managers and employees
        hr_manager = IsHRManager()
        employee = IsEmployee()

        return (hr_manager.has_permission(request, view) or
                employee.has_permission(request, view))


class PayrollWritePermission(BasePermission):
    """
    Combined permission for writing payroll data.
    """
    def has_permission(self, request, view):
        # Only HR admins can write payroll data
        hr_admin = IsHRAdmin()
        return hr_admin.has_permission(request, view)
