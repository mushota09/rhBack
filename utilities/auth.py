from random import random
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .jwt_utils import verify_token


User = get_user_model()


class JWT_AUTH(BaseAuthentication):
    """
    Custom JWT authentication class for async views.
    """
    async def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header[7:]

        try:
            payload = verify_token(token, 'access')
            user = await User.objects.aget(id=payload['user_id'])

            # Check if user is active
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled')

            return (user, token)
        except (ValueError, User.DoesNotExist):
            raise AuthenticationFailed('Token invalide')


class PayrollJWTAuthentication(JWTAuthentication):
    """
    Enhanced JWT authentication with payroll-specific validation.
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # Additional validation for payroll system
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')

        # Log authentication attempt for audit
        self._log_authentication(request, user)

        return user, validated_token

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
