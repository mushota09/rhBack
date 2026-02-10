"""
Enhanced audit middleware for comprehensive system activity logging.
"""
import json
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from utilities.audit_service import AuditService

User = get_user_model()


class AuditMiddleware(MiddlewareMixin):
    """
    Enhanced middleware to log ALL system activities for comprehensive audit trail.

    Captures:
    - All API operations (CRUD)
    - Authentication events
    - Data changes (before/after states)
    - User context (IP, User-Agent)
    - System-wide activities
    - Performance metrics
    """

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """
        Process incoming request and prepare comprehensive audit data.
        """
        # Marquer le début de la requête pour mesurer le temps d'exécution
        request._audit_start_time = time.time()

        # Store request data for audit logging
        request._audit_data = {
            'ip_address': AuditService._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'content_type': request.content_type,
        }

        # Store request body for POST/PUT/PATCH operations (for before/after comparison)
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
            try:
                if request.content_type == 'application/json':
                    request._audit_data['request_data'] = json.loads(request.body.decode('utf-8'))
                elif request.content_type == 'application/x-www-form-urlencoded':
                    request._audit_data['request_data'] = dict(request.POST)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If we can't parse the body, just note that data was sent
                request._audit_data['request_data'] = {'_note': 'Binary or unparseable data'}

        return None

    def process_response(self, request, response):
        """
        Process response and create comprehensive audit log entries.
        """
        # Skip non-auditable requests
        if not self._should_audit_request(request):
            return response

        # Calculer le temps d'exécution
        execution_time = None
        if hasattr(request, '_audit_start_time'):
            execution_time = time.time() - request._audit_start_time

        # Determine action based on HTTP method and response status
        action = self.determine_action(request.method, response.status_code)
        if not action:
            return response

        # Get user from request
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None

        # Extract resource info from path
        resource_type, resource_id = self.extract_resource_info(request.path)

        # Extract response data for audit trail
        response_data = self._extract_response_data(response)

        # Determine old and new values for UPDATE operations
        old_values, new_values = self._determine_data_changes(request, response_data, action)

        # Use AuditService to log the action asynchronously
        AuditService.log_action(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request._audit_data.get('ip_address'),
            user_agent=request._audit_data.get('user_agent'),
            request_method=request.method,
            request_path=request.path,
            response_status=response.status_code,
            execution_time=execution_time,
            session_key=request.session.session_key if hasattr(request, 'session') else None
        )

        return response

    def _should_audit_request(self, request):
        """
        Determine if the request should be audited.
        """
        path = request.path

        # Audit all API endpoints
        if path.startswith('/api/'):
            return True

        # Audit admin actions
        if path.startswith('/admin/'):
            return True

        # Skip static files, media files, and other non-business endpoints
        skip_patterns = [
            '/static/', '/media/', '/favicon.ico', '/robots.txt',
            '/health/', '/ping/', '/metrics/', '/api/schema/', '/api/docs/', '/api/redoc/'
        ]

        for pattern in skip_patterns:
            if path.startswith(pattern):
                return False

        return False

    def determine_action(self, method, status_code):
        """
        Determine the audit action based on HTTP method and status code.
        """
        # Map HTTP methods to audit actions
        action_map = {
            'GET': 'VIEW',
            'POST': 'CREATE',
            'PUT': 'UPDATE',
            'PATCH': 'UPDATE',
            'DELETE': 'DELETE',
        }

        base_action = action_map.get(method)
        if not base_action:
            return None

        # Add failure suffix for failed operations
        if status_code >= 400:
            return f"{base_action}_FAILED"

        return base_action

    def extract_resource_info(self, path):
        """
        Extract resource type and ID from the API path.
        """
        # Remove /api/ prefix and split path
        path_parts = path.replace('/api/', '').strip('/').split('/')

        if not path_parts or path_parts == ['']:
            return 'unknown', ''

        resource_type = path_parts[0]
        resource_id = ''

        # Try to extract resource ID
        if len(path_parts) > 1:
            # Check if second part is numeric (resource ID)
            try:
                resource_id = str(int(path_parts[1]))
            except ValueError:
                # Not a numeric ID, might be an action or sub-resource
                if len(path_parts) > 2:
                    try:
                        # Check if third part is numeric
                        resource_id = str(int(path_parts[2]))
                    except ValueError:
                        # Use the action/sub-resource as identifier
                        resource_id = path_parts[1]

        return resource_type, resource_id

    def _extract_response_data(self, response):
        """
        Extract relevant data from response for audit logging.
        """
        try:
            if hasattr(response, 'data'):
                # DRF Response object
                return response.data
            elif hasattr(response, 'content'):
                # Try to parse JSON content
                content_type = response.get('Content-Type', '')
                if 'application/json' in content_type:
                    return json.loads(response.content.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            pass

        return None

    def _determine_data_changes(self, request, response_data, action):
        """
        Determine old and new values for data change tracking.
        """
        old_values = None
        new_values = None

        if action == 'CREATE':
            # For creation, new values are the created data
            new_values = response_data

        elif action == 'UPDATE':
            # For updates, old values are from request, new values from response
            old_values = request._audit_data.get('request_data')
            new_values = response_data

        elif action == 'DELETE':
            # For deletion, old values are what was deleted
            old_values = response_data

        return old_values, new_values


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
