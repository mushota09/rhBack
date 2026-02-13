"""
Tests for ServiceGroup module

This module tests the ServiceGroup functionality including:
- Basic CRUD operations
- Unique constraint validation (service, group)
- Dynamic field expansion (?expand=service,group)
- Filtering by service and group
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from user_app.models import ServiceGroup, Group, service

User = get_user_model()


class ServiceGroupTestCase(TestCase):
    """
    Test case for ServiceGroup functionality.

    Tests CRUD operations, validation, expansion, and filtering.
    """

    def setUp(self):
        """Set up test data for ServiceGroup tests."""
        # Create test user
        self.user = User.objects.create(
            email='test@test.com',
            nom='Test',
            prenom='User',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.user.set_password('testpass123')
        self.user.save()

        # Create test services
        self.service1 = service.objects.create(
            titre='Service IT',
            code='IT',
            description='Service informatique'
        )
        self.service2 = service.objects.create(
            titre='Service RH',
            code='RH',
            description='Service ressources humaines'
        )

        # Create test groups
        self.group1 = Group.objects.create(
            code='ADM',
            name='Administrateur',
            description='Groupe administrateur',
            is_active=True
        )
        self.group2 = Group.objects.create(
            code='RRH',
            name='Responsable RH',
            description='Groupe responsable RH',
            is_active=True
        )

        # Create test ServiceGroup
        self.service_group1 = ServiceGroup.objects.create(
            service=self.service1,
            group=self.group1
        )

        self.client = APIClient()
        self.service_group_url = reverse('ServiceGroupViewSet-list')

    def test_create_service_group_valid(self):
        """Test creating a valid ServiceGroup."""
        self.client.force_authenticate(user=self.user)
        data = {
            'service': self.service2.id,
            'group': self.group2.id
        }
        response = self.client.post(self.service_group_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['service'], self.service2.id)
        self.assertEqual(response.data['group'], self.group2.id)

    def test_create_service_group_duplicate(self):
        """Test that duplicate ServiceGroup is rejected."""
        self.client.force_authenticate(user=self.user)
        data = {
            'service': self.service1.id,
            'group': self.group1.id
        }
        response = self.client.post(self.service_group_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Django's unique constraint validation message
        self.assertIn('unique', str(response.data).lower())

    def test_list_service_groups(self):
        """Test listing ServiceGroups."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.service_group_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_expand_service_and_group(self):
        """Test expanding service and group fields."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.service_group_url,
            {'expand': 'service,group'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        if len(results) > 0:
            first_result = results[0]
            # Check that service is expanded (should be dict, not int)
            self.assertIsInstance(first_result['service'], dict)
            self.assertIn('titre', first_result['service'])
            # Check that group is expanded (should be dict, not int)
            self.assertIsInstance(first_result['group'], dict)
            self.assertIn('code', first_result['group'])

    def test_filter_by_service(self):
        """Test filtering ServiceGroups by service."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.service_group_url,
            {'service': self.service1.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        for entry in results:
            self.assertEqual(entry['service'], self.service1.id)

    def test_filter_by_group(self):
        """Test filtering ServiceGroups by group."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            self.service_group_url,
            {'group': self.group1.id}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        for entry in results:
            self.assertEqual(entry['group'], self.group1.id)

    def test_delete_service_group(self):
        """Test deleting a ServiceGroup."""
        self.client.force_authenticate(user=self.user)
        detail_url = reverse(
            'ServiceGroupViewSet-detail',
            kwargs={'pk': self.service_group1.id}
        )
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ServiceGroup.objects.filter(id=self.service_group1.id).exists()
        )

    def test_delete_service_group_keeps_group_with_other_service_groups(self):
        """
        Test suppression ServiceGroup (Group garde autres ServiceGroups).

        Requirements: 4.1, 4.2, 4.3
        """
        self.client.force_authenticate(user=self.user)

        # Create a second ServiceGroup for the same group
        service_group2 = ServiceGroup.objects.create(
            service=self.service2,
            group=self.group1
        )

        # Delete the first ServiceGroup
        detail_url = reverse(
            'ServiceGroupViewSet-detail',
            kwargs={'pk': self.service_group1.id}
        )
        response = self.client.delete(detail_url)

        # Should succeed
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # First ServiceGroup should be deleted
        self.assertFalse(
            ServiceGroup.objects.filter(id=self.service_group1.id).exists()
        )

        # Group should still exist (has other ServiceGroups)
        self.assertTrue(
            Group.objects.filter(id=self.group1.id).exists()
        )

        # Second ServiceGroup should still exist
        self.assertTrue(
            ServiceGroup.objects.filter(id=service_group2.id).exists()
        )

    def test_delete_last_service_group_deletes_group_without_users(self):
        """
        Test suppression dernier ServiceGroup (Group supprimé si pas d'utilisateurs).

        Requirements: 4.1, 4.2, 4.3
        """
        self.client.force_authenticate(user=self.user)

        # Ensure group1 has no active users
        from user_app.models import UserGroup
        UserGroup.objects.filter(group=self.group1, is_active=True).delete()

        # Verify this is the only ServiceGroup for group1
        service_group_count = ServiceGroup.objects.filter(group=self.group1).count()
        self.assertEqual(service_group_count, 1)

        # Delete the last ServiceGroup
        detail_url = reverse(
            'ServiceGroupViewSet-detail',
            kwargs={'pk': self.service_group1.id}
        )
        response = self.client.delete(detail_url)

        # Should succeed
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # ServiceGroup should be deleted
        self.assertFalse(
            ServiceGroup.objects.filter(id=self.service_group1.id).exists()
        )

        # Group should also be deleted (no users, no other ServiceGroups)
        self.assertFalse(
            Group.objects.filter(id=self.group1.id).exists()
        )

    def test_delete_last_service_group_prevents_deletion_with_active_users(self):
        """
        Test refus suppression dernier ServiceGroup (Group a utilisateurs actifs).

        Requirements: 4.1, 4.2, 4.3
        """
        self.client.force_authenticate(user=self.user)

        # Create an active user assigned to group1
        from user_app.models import UserGroup
        test_user2 = User.objects.create(
            email='user2@test.com',
            nom='User2',
            prenom='Test',
            is_active=True
        )
        UserGroup.objects.create(
            user=test_user2,
            group=self.group1,
            assigned_by=self.user,
            is_active=True
        )

        # Verify this is the only ServiceGroup for group1
        service_group_count = ServiceGroup.objects.filter(group=self.group1).count()
        self.assertEqual(service_group_count, 1)

        # Attempt to delete the last ServiceGroup
        detail_url = reverse(
            'ServiceGroupViewSet-detail',
            kwargs={'pk': self.service_group1.id}
        )
        response = self.client.delete(detail_url)

        # Should fail with 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('utilisateur(s) actif(s)', str(response.data))

        # ServiceGroup should still exist
        self.assertTrue(
            ServiceGroup.objects.filter(id=self.service_group1.id).exists()
        )

        # Group should still exist
        self.assertTrue(
            Group.objects.filter(id=self.group1.id).exists()
        )

