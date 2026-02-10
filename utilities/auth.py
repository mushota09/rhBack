from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_utils import verify_token


User = get_user_model()


class JWT_AUTH(BaseAuthentication):
    """
    Custom JWT authentication class for both sync and async views.
    Supports both synchronous and asynchronous authentication automatically.
    """

    def authenticate(self, request):
        """
        Synchronous authentication for regular views.
        """
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]

        try:
            payload = verify_token(token, 'access')
            user = User.objects.get(id=payload['user_id'])

            # Check if user is active
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled')

            # Log authentication for audit
            self._log_authentication(request, user)

            return (user, token)
        except ValueError as exc:
            raise AuthenticationFailed('Token invalide') from exc
        except User.DoesNotExist as exc:
            raise AuthenticationFailed('Token invalide') from exc

    def _log_authentication(self, request, user):
        """
        Log authentication attempt for audit purposes.
        """
        try:
            from user_app.models import audit_log

            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            # Create audit log entry
            audit_log.objects.create(
                user_id=user,
                action='LOGIN',
                type_ressource='authentication',
                id_ressource=str(user.id),
                adresse_ip=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        except Exception:
            # Don't fail authentication if audit logging fails
            pass
