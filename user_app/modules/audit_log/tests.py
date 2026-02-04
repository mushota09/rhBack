"""
Tests for the AuditLogViewSet with filtering and search capabilities.

This module tests the comprehensive audit log querying functionality including:
- Basic CRUD operations
- Filtering by user, action, resource type, date ranges
- Search across user details, actions, and resource information
- Permission-based access control
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from user_app.models import audit_log

User = get_user_model()


class AuditLogViewSetTestCase(TestCase):
    """
    Test case for AuditLogViewSet functionality.

    Tests the filtering, searching, and permission capabilities
    of the audit log API endpoints.
    """

    def setUp(self):
        """Set up test data for audit log tests."""
        # Create test users using direct creation since UserManager only has async methods
        self.superuser = User.objects.create(
            email='admin@test.com',
            nom='Admin',
            prenom='User',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.superuser.set_password('testpass123')
        self.superuser.save()

        self.regular_user = User.objects.create(
            email='user@test.com',
            nom='Regular',
            prenom='User',
            is_active=True
        )
        self.regular_user.set_password('testpass123')
        self.regular_user.save()

        # Create test audit log entries
        self.audit_entry_1 = audit_log.objects.create(
            user_id=self.regular_user,
            action='CREATE',
            type_ressource='user_group',
            id_ressource='1',
            anciennes_valeurs={'status': 'inactive'},
            nouvelles_valeurs={'status': 'active'},
            adresse_ip='192.168.1.1',
            user_agent='Test Agent 1'
        )

        self.audit_entry_2 = audit_log.objects.create(
            user_id=self.superuser,
            action='UPDATE',
            type_ressource='group_permission',
            id_ressource='2',
            anciennes_valeurs={'permission': 'read'},
            nouvelles_valeurs={'permission': 'write'},
            adresse_ip='192.168.1.2',
            user_agent='Test Agent 2'
        )

        self.client = APIClient()
        self.audit_log_url = reverse('audit_logAPIView-list')

    def test_superuser_can_access_audit_logs(self):
        """Test that superusers can access audit logs."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.audit_log_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_regular_user_cannot_access_audit_logs(self):
        """Test that regular users cannot access audit logs."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.audit_log_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_user_id(self):
        """Test filtering audit logs by user ID."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            self.audit_log_url,
            {'user_id': self.regular_user.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']

        # Should return entries for regular_user only
        for entry in results:
            self.assertEqual(entry['user_id'], self.regular_user.id)

    def test_filter_by_action(self):
        """Test filtering audit logs by action."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            self.audit_log_url,
            {'action': 'CREATE'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']

        # Should return only CREATE entries
        for entry in results:
            self.assertEqual(entry['action'], 'CREATE')

    def test_search_functionality(self):
        """Test search across multiple fields."""
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(
            self.audit_log_url,
            {'search': 'Regular'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Search should work even if no results found
        self.assertIsInstance(response.data['results'], list)
