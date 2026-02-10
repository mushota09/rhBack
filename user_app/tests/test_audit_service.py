"""
Tests pour le service d'audit asynchrone.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from user_app.models import audit_log
from utilities.audit_service import AuditService, AuditContextManager

User = get_user_model()


@pytest.mark.django_db
class TestAuditService(TestCase):
    """Tests pour le service d'audit"""

    def setUp(self):
        """Configuration initiale"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='audit@example.com',
            password='testpass123'
        )

    def test_log_action_synchronous(self):
        """Test de création d'un log d'audit en mode synchrone"""
        # Compter les logs avant
        initial_count = audit_log.objects.count()

        # Créer un log en mode synchrone
        result = AuditService.log_action(
            user=self.user,
            action='CREATE',
            resource_type='test_resource',
            resource_id='123',
            old_values=None,
            new_values={'field': 'value'},
            async_mode=False
        )

        # Vérifier qu'un log a été créé
        self.assertEqual(audit_log.objects.count(), initial_count + 1)
        self.assertIsNotNone(result)
        self.assertEqual(result.action, 'CREATE')
        self.assertEqual(result.user_id, self.user)

    @patch('utilities.audit_service.CELERY_AVAILABLE', True)
    @patch('utilities.audit_service.create_audit_log_async')
    def test_log_action_asynchronous(self, mock_celery_task):
        """Test de création d'un log d'audit en mode asynchrone"""
        mock_celery_task.delay = MagicMock()

        # Créer un log en mode asynchrone
        result = AuditService.log_action(
            user=self.user,
            action='UPDATE',
            resource_type='test_resource',
            resource_id='456',
            old_values={'field': 'old'},
            new_values={'field': 'new'},
            async_mode=True
        )

        # Vérifier que la tâche Celery a été appelée
        mock_celery_task.delay.assert_called_once()

        # En mode async, retourne None
        self.assertIsNone(result)

    def test_sanitize_sensitive_data(self):
        """Test de la sanitisation des données sensibles"""
        sensitive_data = {
            'username': 'testuser',
            'password': 'secret123',
            'token': 'abc123',
            'api_key': 'key123',
            'normal_field': 'visible'
        }

        sanitized = AuditService._sanitize_data(sensitive_data)

        # Vérifier que les champs sensibles sont masqués
        self.assertEqual(sanitized['password'], '***MASKED***')
        self.assertEqual(sanitized['token'], '***MASKED***')
        self.assertEqual(sanitized['api_key'], '***MASKED***')

        # Vérifier que les champs normaux sont préservés
        self.assertEqual(sanitized['username'], 'testuser')
        self.assertEqual(sanitized['normal_field'], 'visible')

    def test_get_client_ip_with_forwarded(self):
        """Test d'extraction de l'IP avec X-Forwarded-For"""
        request = self.factory.get('/api/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        ip = AuditService._get_client_ip(request)

        # Devrait retourner la première IP de X-Forwarded-For
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_without_forwarded(self):
        """Test d'extraction de l'IP sans X-Forwarded-For"""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        ip = AuditService._get_client_ip(request)

        # Devrait retourner REMOTE_ADDR
        self.assertEqual(ip, '127.0.0.1')

    def test_log_login_success(self):
        """Test de log de connexion réussie"""
        request = self.factory.post('/api/login/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestBrowser/1.0'
        request.method = 'POST'
        request.path = '/api/login/'

        # Mock session
        request.session = MagicMock()
        request.session.session_key = 'test_session_key'

        # Devrait s'exécuter sans erreur
        try:
            AuditService.log_login(self.user, request, success=True)
            success = True
        except Exception:
            success = False

        self.assertTrue(success)

    def test_log_logout(self):
        """Test de log de déconnexion"""
        request = self.factory.post('/api/logout/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.method = 'POST'
        request.path = '/api/logout/'
        request.session = MagicMock()
        request.session.session_key = 'test_session_key'

        # Devrait s'exécuter sans erreur
        try:
            AuditService.log_logout(self.user, request)
            success = True
        except Exception:
            success = False

        self.assertTrue(success)

    def test_audit_never_crashes_app(self):
        """Test que l'audit ne fait jamais planter l'application"""
        # Tenter de créer un log avec des données invalides
        try:
            AuditService.log_action(
                user=None,
                action=None,
                resource_type=None,
                async_mode=False
            )
            # Ne devrait pas lever d'exception
            success = True
        except Exception:
            success = False

        self.assertTrue(success)


@pytest.mark.django_db
class TestAuditContextManager(TestCase):
    """Tests pour le gestionnaire de contexte d'audit"""

    def setUp(self):
        """Configuration initiale"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email='context@example.com',
            password='testpass123'
        )

    def test_context_manager_success(self):
        """Test du context manager avec succès"""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.method = 'GET'
        request.path = '/api/test/'
        request.session = MagicMock()
        request.session.session_key = 'test_key'

        # Devrait s'exécuter sans erreur
        try:
            with AuditContextManager(
                user=self.user,
                action='VIEW',
                resource_type='test',
                resource_id='123',
                request=request
            ):
                # Simuler une opération
                pass
            success = True
        except Exception:
            success = False

        self.assertTrue(success)

    def test_context_manager_with_exception(self):
        """Test du context manager avec exception"""
        request = self.factory.get('/api/test/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.method = 'GET'
        request.path = '/api/test/'
        request.session = MagicMock()
        request.session.session_key = 'test_key'

        # Le context manager devrait gérer l'exception
        exception_handled = False
        try:
            with AuditContextManager(
                user=self.user,
                action='DELETE',
                resource_type='test',
                resource_id='456',
                request=request
            ):
                # Simuler une erreur
                raise ValueError("Test error")
        except ValueError:
            exception_handled = True

        # L'exception devrait avoir été propagée
        self.assertTrue(exception_handled)
