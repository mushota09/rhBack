"""
Authentication and audit middleware for the payroll system.
"""
import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from user_app.models import audit_log

User = get_user_model()


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to log API access and operations for audit purposes.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """
        Process incoming request and prepare audit data.
        """
        # Store request data for audit logging
        request._audit_data = {
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
        }

        return None

    def process_response(self, request, response):
        """
        Process response and log audit information.
        """
        # Only log API endpoints (not static files, admin, etc.)
        if not request.path.startswith('/api/'):
            return response

        # Only log for authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response

        # Determine action based on HTTP method and response status
        action = self.determine_action(request.method, response.status_code)
        if not action:
            return response

        # Extract resource information from path
        resource_type, resource_id = self.extract_resource_info(request.path)

        # Create audit log entry
        try:
            audit_log.objects.create(
                user_id=request.user,
                action=action,
                type_ressource=resource_type,
                id_ressource=resource_id,
                adresse_ip=request._audit_data.get('ip_address'),
                user_agent=request._audit_data.get('user_agent'),
                # Note: We don't log request/response data for security reasons
                # but this could be extended for specific endpoints
            )
        except Exception:
            # Don't fail the request if audit logging fails
            pass

        return response

    def get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def determine_action(self, method, status_code):
        """
        Determine the audit action based on HTTP method and status code.
        """
        # Only log successful operations
        if status_code >= 400:
            return None

        action_map = {
            'GET': 'VIEW',
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }

        return action_map.get(method)

    def extract_resource_info(self, path):
        """
        Extract resource type and ID from the API path.
        """
        # Remove /api/ prefix and split path
        path_parts = path.replace('/api/', '').strip('/').split('/')

        if not path_parts:
            return 'unknown', ''

        resource_type = path_parts[0]
        resource_id = ''

        # Try to extract resource ID (usually the second part if it's numeric)
        if len(path_parts) > 1:
            try:
                resource_id = str(int(path_parts[1]))
            except ValueError:
                # Not a numeric ID, might be an action like 'process', 'approve'
                if len(path_parts) > 2:
                    try:
                        resource_id = str(int(path_parts[2]))
                    except ValueError:
                        pass

        return resource_type, resource_id


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT authentication for async views.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """
        Process JWT token from request headers.
        """
        # This middleware works in conjunction with the JWT_AUTH authentication class
        # It ensures that JWT tokens are properly processed for async views

        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            # Store the token for later use by authentication classes
            request._jwt_token = auth_header[7:]

        return None
