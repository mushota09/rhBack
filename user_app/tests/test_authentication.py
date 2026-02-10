"""
Tests pour le système d'authentification JWT unifié.
"""
import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from utilities.auth import JWT_AUTH
from utilities.jwt_utils import generate_token

User = get_user_model()


@pytest.mark.django_db
class TestJWTAuthentication(TestCase):
    """Tests pour la classe JWT_AUTH"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.factory = RequestFactory()
        self.auth = JWT_AUTH()

        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.save()

    def test_authenticate_with_valid_token(self):
        """Test d'authentification avec un token valide"""
        # Générer un token valide
        token = generate_token(self.user, 'access')

        # Créer une requête avec le token
        request = self.factory.get('/api/test/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # Authentifier
        result = self.auth.authenticate(request)

        # Vérifications
        self.assertIsNotNone(result)
        self.assertEqual(result[0].id, self.user.id)
        self.assertEqual(result[1], token)

    def test_authenticate_without_token(self):
        """Test d'authentification sans token"""
        request = self.factory.get('/api/test/')
        result = self.auth.authenticate(request)

        # Devrait retourner None (pas d'erreur)
        self.assertIsNone(result)

    def test_authenticate_with_invalid_token(self):
        """Test d'authentification avec un token invalide"""
        request = self.factory.get('/api/test/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token_here'

        # Devrait lever une exception
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_authenticate_with_inactive_user(self):
        """Test d'authentification avec un utilisateur inactif"""
        # Désactiver l'utilisateur
        self.user.is_active = False
        self.user.save()

        # Générer un token
        token = generate_token(self.user, 'access')

        # Créer une requête
        request = self.factory.get('/api/test/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # Devrait lever une exception
        with self.assertRaises(AuthenticationFailed) as context:
            self.auth.authenticate(request)

        self.assertIn('disabled', str(context.exception))

    def test_authenticate_with_malformed_header(self):
        """Test avec un header Authorization mal formé"""
        request = self.factory.get('/api/test/')
        request.META['HTTP_AUTHORIZATION'] = 'InvalidFormat token'

        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_logs_audit(self):
        """Test que l'authentification crée un log d'audit"""
        from user_app.models import audit_log

        # Compter les logs avant
        initial_count = audit_log.objects.count()

        # Générer un token et authentifier
        token = generate_token(self.user, 'access')
        request = self.factory.get('/api/test/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.META['HTTP_USER_AGENT'] = 'TestAgent/1.0'

        self.auth.authenticate(request)

        # Vérifier qu'un log a été créé
        final_count = audit_log.objects.count()
        self.assertEqual(final_count, initial_count + 1)

        # Vérifier le contenu du log
        log = audit_log.objects.latest('timestamp')
        self.assertEqual(log.action, 'LOGIN')
        self.assertEqual(log.user_id, self.user)
        self.assertEqual(log.type_ressource, 'authentication')
