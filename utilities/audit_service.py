"""
Service d'audit global ASYNCHRONE pour capturer toutes les actions du système.
Utilise Celery pour l'exécution en arrière-plan sans bloquer le serveur.
"""
import time
from django.contrib.auth import get_user_model
from user_app.models import audit_log
import logging

User = get_user_model()
logger = logging.getLogger('paie_app.audit')

# Import Celery pour les tâches asynchrones
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    logger.warning("Celery not available, audit logs will be synchronous")


# ============================================================================
# TÂCHE CELERY ASYNCHRONE POUR L'AUDIT
# ============================================================================

if CELERY_AVAILABLE:
    @shared_task(bind=True, max_retries=3, default_retry_delay=60)
    def create_audit_log_async(
        self,
        user_id=None,
        action=None,
        resource_type=None,
        resource_id=None,
        old_values=None,
        new_values=None,
        ip_address=None,
        user_agent=None,
        request_method=None,
        request_path=None,
        response_status=None,
        execution_time=None,
        session_key=None
    ):
        """
        Tâche Celery asynchrone pour créer un log d'audit en arrière-plan.
        Ne bloque JAMAIS le serveur principal.
        """
        try:
            # Récupérer l'utilisateur si user_id est fourni
            user = None
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    logger.warning(f"User {user_id} not found for audit log")

            # Créer l'entrée d'audit
            audit_entry = audit_log.objects.create(
                user_id=user,
                action=action,
                type_ressource=resource_type or 'unknown',
                id_ressource=str(resource_id) if resource_id else '',
                anciennes_valeurs=old_values,
                nouvelles_valeurs=new_values,
                adresse_ip=ip_address,
                user_agent=user_agent or '',
                session_key=session_key or '',
                request_method=request_method or '',
                request_path=request_path or '',
                response_status=response_status,
                execution_time=execution_time
            )

            logger.info(f"✅ Audit log created asynchronously: {audit_entry.id}")
            return audit_entry.id

        except Exception as exc:
            logger.error(f"❌ Failed to create audit log asynchronously: {str(exc)}")
            # Retry la tâche en cas d'erreur
            raise self.retry(exc=exc)


class AuditService:
    """
    Service centralisé pour l'audit ASYNCHRONE de toutes les actions du système.
    Par défaut, toutes les opérations sont exécutées en arrière-plan via Celery.
    """

    @staticmethod
    def log_action(
        user=None,
        action=None,
        resource_type=None,
        resource_id=None,
        old_values=None,
        new_values=None,
        ip_address=None,
        user_agent=None,
        request_method=None,
        request_path=None,
        response_status=None,
        execution_time=None,
        session_key=None,
        async_mode=True  # Par défaut ASYNCHRONE
    ):
        """
        Enregistre une action dans le système d'audit EN ARRIÈRE-PLAN.

        ⚡ Par défaut, l'audit est ASYNCHRONE (async_mode=True) pour ne JAMAIS bloquer le serveur.

        Args:
            user: Instance User ou None pour les actions anonymes
            action: Type d'action (CREATE, UPDATE, DELETE, etc.)
            resource_type: Type de ressource affectée
            resource_id: ID de la ressource (optionnel)
            old_values: Valeurs avant modification (dict)
            new_values: Valeurs après modification (dict)
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur
            request_method: Méthode HTTP (GET, POST, etc.)
            request_path: Chemin de la requête
            response_status: Code de statut HTTP
            execution_time: Temps d'exécution en secondes
            session_key: Clé de session
            async_mode: Si True, utilise Celery (recommandé)
        """
        try:
            # Sanitiser les données sensibles
            old_values = AuditService._sanitize_data(old_values)
            new_values = AuditService._sanitize_data(new_values)

            # Préparer les données pour l'audit
            audit_data = {
                'user_id': user.id if user else None,
                'action': action,
                'resource_type': resource_type,
                'resource_id': resource_id,
                'old_values': old_values,
                'new_values': new_values,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'request_method': request_method,
                'request_path': request_path,
                'response_status': response_status,
                'execution_time': execution_time,
                'session_key': session_key
            }

            # ⚡ Mode asynchrone avec Celery (RECOMMANDÉ - ne bloque pas le serveur)
            if async_mode and CELERY_AVAILABLE:
                # Envoyer la tâche à Celery en arrière-plan
                create_audit_log_async.delay(**audit_data)
                logger.debug(f"📤 Audit log queued: {action} on {resource_type}")
                return None  # Retourne None car l'audit est asynchrone

            # Mode synchrone (fallback si Celery n'est pas disponible)
            else:
                if not CELERY_AVAILABLE:
                    logger.warning("⚠️  Celery not available, using synchronous audit")

                audit_entry = audit_log.objects.create(
                    user_id=user,
                    action=action,
                    type_ressource=resource_type or 'unknown',
                    id_ressource=str(resource_id) if resource_id else '',
                    anciennes_valeurs=old_values,
                    nouvelles_valeurs=new_values,
                    adresse_ip=ip_address,
                    user_agent=user_agent or '',
                    session_key=session_key or '',
                    request_method=request_method or '',
                    request_path=request_path or '',
                    response_status=response_status,
                    execution_time=execution_time
                )

                logger.info(f"✅ Audit log created synchronously: {audit_entry}")
                return audit_entry

        except Exception as e:
            # ⚠️ Ne JAMAIS faire planter l'application à cause de l'audit
            logger.error(f"❌ Failed to queue/create audit log: {str(e)}")
            return None

    @staticmethod
    def log_login(user, request, success=True):
        """
        Enregistre une tentative de connexion EN ARRIÈRE-PLAN.
        """
        action = 'LOGIN' if success else 'LOGIN_FAILED'

        return AuditService.log_action(
            user=user if success else None,
            action=action,
            resource_type='authentication',
            resource_id=str(user.id) if user else None,
            ip_address=AuditService._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_method=request.method,
            request_path=request.path,
            session_key=request.session.session_key if hasattr(request, 'session') else None,
            async_mode=True  # Toujours asynchrone
        )

    @staticmethod
    def log_logout(user, request):
        """
        Enregistre une déconnexion EN ARRIÈRE-PLAN.
        """
        return AuditService.log_action(
            user=user,
            action='LOGOUT',
            resource_type='authentication',
            resource_id=str(user.id),
            ip_address=AuditService._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request_method=request.method,
            request_path=request.path,
            session_key=request.session.session_key if hasattr(request, 'session') else None,
            async_mode=True  # Toujours asynchrone
        )

    @staticmethod
    def log_model_change(user, instance, action, old_values=None, request=None):
        """
        Enregistre les modifications sur les modèles Django EN ARRIÈRE-PLAN.
        """
        # Extraire les nouvelles valeurs de l'instance
        new_values = None
        if hasattr(instance, '__dict__'):
            new_values = {
                field.name: getattr(instance, field.name, None)
                for field in instance._meta.fields
                if not field.name.endswith('_ptr')
            }

        return AuditService.log_action(
            user=user,
            action=action,
            resource_type=instance._meta.model_name,
            resource_id=str(instance.pk) if instance.pk else None,
            old_values=old_values,
            new_values=new_values,
            ip_address=AuditService._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
            request_method=request.method if request else None,
            request_path=request.path if request else None,
            session_key=request.session.session_key if request and hasattr(request, 'session') else None,
            async_mode=True  # Toujours asynchrone
        )

    @staticmethod
    def log_bulk_operation(user, resource_type, count, action='BULK_OPERATION', request=None):
        """
        Enregistre les opérations en lot EN ARRIÈRE-PLAN.
        """
        return AuditService.log_action(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=f"bulk_{count}_items",
            new_values={'affected_count': count},
            ip_address=AuditService._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
            request_method=request.method if request else None,
            request_path=request.path if request else None,
            session_key=request.session.session_key if request and hasattr(request, 'session') else None,
            async_mode=True  # Toujours asynchrone
        )

    @staticmethod
    def log_export(user, resource_type, format_type='excel', count=None, request=None):
        """
        Enregistre les exports de données EN ARRIÈRE-PLAN.
        """
        export_data = {
            'format': format_type,
            'exported_count': count
        }

        return AuditService.log_action(
            user=user,
            action='EXPORT',
            resource_type=resource_type,
            resource_id=f"export_{format_type}",
            new_values=export_data,
            ip_address=AuditService._get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None,
            request_method=request.method if request else None,
            request_path=request.path if request else None,
            session_key=request.session.session_key if request and hasattr(request, 'session') else None,
            async_mode=True  # Toujours asynchrone
        )

    @staticmethod
    def _get_client_ip(request):
        """
        Extrait l'adresse IP réelle du client.
        """
        if not request:
            return None

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def _sanitize_data(data):
        """
        Supprime ou masque les données sensibles.
        """
        if not data:
            return data

        if isinstance(data, dict):
            sanitized = data.copy()
            sensitive_fields = [
                'password', 'token', 'secret', 'key', 'authorization',
                'csrf_token', 'session_key', 'api_key', 'refresh_token',
                'access_token', 'private_key', 'secret_key'
            ]

            for field in sensitive_fields:
                if field in sanitized:
                    sanitized[field] = '***MASKED***'

            return sanitized

        return data


# ============================================================================
# GESTIONNAIRE DE CONTEXTE (optionnel, pour usage avancé)
# ============================================================================

class AuditContextManager:
    """
    Gestionnaire de contexte pour l'audit avec mesure du temps d'exécution.
    L'audit est toujours ASYNCHRONE.
    """

    def __init__(self, user, action, resource_type, resource_id=None, request=None):
        self.user = user
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.request = request
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time

        # Déterminer le statut basé sur les exceptions
        if exc_type is not None:
            action = f"{self.action}_FAILED"
            response_status = 500
        else:
            action = self.action
            response_status = 200

        # Audit asynchrone
        AuditService.log_action(
            user=self.user,
            action=action,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            execution_time=execution_time,
            response_status=response_status,
            ip_address=AuditService._get_client_ip(self.request) if self.request else None,
            user_agent=self.request.META.get('HTTP_USER_AGENT', '') if self.request else None,
            request_method=self.request.method if self.request else None,
            request_path=self.request.path if self.request else None,
            session_key=self.request.session.session_key if self.request and hasattr(self.request, 'session') else None,
            async_mode=True  # Toujours asynchrone
        )
