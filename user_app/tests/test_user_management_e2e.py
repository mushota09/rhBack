"""
End-to-End Tests for User Management Critical Flows (Backend)

This test suite covers the critical user management workflows from the backend perspective:
- User authentication and permission loading
- User-group assignment API workflows
- Permission management API workflows

Requirements: 8.5 - End-to-end tests for critical user management flows
"""

import json
import asyncio
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from asgiref.sync import sync_to_async
from user_app.models import Group, UserGroup, Permission, GroupPermission, audit_log
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class UserManagementE2ETestCase(APITestCase):
    """
    End-to-end tests for user management critical flows
    """

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            nom='Admin',
            prenom='User',
            is_staff=True,
            is_superuser=True
        )

        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            nom='Regular',
            prenom='User'
        )

        # Create test groups
        self.admin_group = Group.objects.create(
            code='ADM',
            name='Administrateur',
            description='Groupe administrateur avec tous les droits'
        )

        self.rrh_group = Group.objects.create(
            code='RRH',
            name='Responsable Ressources Humaines',
            description='Responsable des ressources humaines'
        )

        self.dir_group = Group.objects.create(
            code='DIR',
            name='Directeur',
            description='Directeur général'
        )

        # Create test permissions
        user_content_type = ContentType.objects.get_for_model(User)
        group_content_type = ContentType.objects.get_for_model(Group)

        self.manage_users_permission = Permission.objects.create(
            codename='manage_users',
            name='Manage Users',
            content_type=user_content_type,
            resource='user',
            action='CREATE'
        )

        self.view_users_permission = Permission.objects.create(
            codename='view_users',
            name='View Users',
            content_type=user_content_type,
            resource='user',
            action='READ'
        )

        self.manage_groups_permission = Permission.objects.create(
            codename='manage_groups',
            name='Manage Groups',
            content_type=group_content_type,
            resource='group',
            action='UPDATE'
        )

        # Assign admin user to admin group
        UserGroup.objects.create(
            user=self.admin_user,
            group=self.admin_group,
            assigned_by=self.admin_user
        )

        # Assign permissions to admin group
        GroupPermission.objects.create(
            group=self.admin_group,
            permission=self.manage_users_permission,
            granted=True,
            created_by=self.admin_user
        )

        GroupPermission.objects.create(
            group=self.admin_group,
            permission=self.view_users_permission,
            granted=True,
            created_by=self.admin_user
        )

        GroupPermission.objects.create(
            group=self.admin_group,
            permission=self.manage_groups_permission,
            granted=True,
            created_by=self.admin_user
        )

    def test_user_login_and_permission_loading_flow(self):
        """
        Test complete user login flow and permission loading
        """
        # Step 1: Login user
        login_url = reverse('login')
        login_data = {
            'email': 'admin@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        # Extract tokens
        access_token = response.data['access']
        user_data = response.data['user']

        # Verify user data
        self.assertEqual(user_data['email'], 'admin@example.com')
        self.assertEqual(user_data['nom'], 'Admin')
        self.assertEqual(user_data['prenom'], 'User')

        # Step 2: Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Step 3: Load user groups
        groups_url = reverse('GroupViewSet-list')
        response = self.client.get(groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)

        # Verify groups are returned
        group_codes = [group['code'] for group in response.data['results']]
        self.assertIn('ADM', group_codes)
        self.assertIn('RRH', group_codes)
        self.assertIn('DIR', group_codes)

        # Step 4: Load user permissions
        user_groups_url = reverse('UserGroupViewSet-list')
        response = self.client.get(f"{user_groups_url}?user={self.admin_user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify user is assigned to admin group
        user_groups = response.data['results']
        self.assertEqual(len(user_groups), 1)
        self.assertEqual(user_groups[0]['group'], self.admin_group.id)
        self.assertEqual(user_groups[0]['user'], self.admin_user.id)

        # Step 5: Verify permissions are accessible
        permissions_url = reverse('PermissionViewSet-list')
        response = self.client.get(permissions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)

    def test_user_login_failure_handling(self):
        """
        Test login failure scenarios
        """
        login_url = reverse('login')

        # Test with invalid credentials
        invalid_login_data = {
            'email': 'invalid@example.com',
            'password': 'wrongpassword'
        }

        response = self.client.post(login_url, invalid_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)

        # Test with missing fields
        incomplete_data = {'email': 'admin@example.com'}
        response = self.client.post(login_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_group_assignment_workflow(self):
        """
        Test complete user-group assignment workflow
        """
        # Login as admin
        self.client.force_authenticate(user=self.admin_user)

        # Step 1: Verify initial state - regular user has no groups
        user_groups_url = reverse('UserGroupViewSet-list')
        response = self.client.get(f"{user_groups_url}?user={self.regular_user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        # Step 2: Assign user to RRH group
        assignment_data = {
            'user': self.regular_user.id,
            'group': self.rrh_group.id,
            'assigned_by': self.admin_user.id
        }

        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify assignment was created
        self.assertEqual(response.data['user'], self.regular_user.id)
        self.assertEqual(response.data['group'], self.rrh_group.id)
        self.assertEqual(response.data['assigned_by'], self.admin_user.id)
        self.assertTrue(response.data['is_active'])

        # Step 3: Verify user now has the group
        response = self.client.get(f"{user_groups_url}?user={self.regular_user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Step 4: Assign user to another group (DIR)
        assignment_data['group'] = self.dir_group.id
        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 5: Verify user now has both groups
        response = self.client.get(f"{user_groups_url}?user={self.regular_user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        group_ids = [ug['group'] for ug in response.data['results']]
        self.assertIn(self.rrh_group.id, group_ids)
        self.assertIn(self.dir_group.id, group_ids)

    def test_user_group_assignment_failure_scenarios(self):
        """
        Test user-group assignment failure scenarios
        """
        self.client.force_authenticate(user=self.admin_user)
        user_groups_url = reverse('UserGroupViewSet-list')

        # Test duplicate assignment
        UserGroup.objects.create(
            user=self.regular_user,
            group=self.rrh_group,
            assigned_by=self.admin_user
        )

        assignment_data = {
            'user': self.regular_user.id,
            'group': self.rrh_group.id,
            'assigned_by': self.admin_user.id
        }

        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test assignment to non-existent group
        assignment_data['group'] = 99999
        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test assignment of non-existent user
        assignment_data = {
            'user': 99999,
            'group': self.rrh_group.id,
            'assigned_by': self.admin_user.id
        }
        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_group_removal_workflow(self):
        """
        Test removing user from group workflow
        """
        self.client.force_authenticate(user=self.admin_user)

        # Step 1: Create user-group assignment
        user_group = UserGroup.objects.create(
            user=self.regular_user,
            group=self.rrh_group,
            assigned_by=self.admin_user
        )

        # Step 2: Verify assignment exists
        user_groups_url = reverse('UserGroupViewSet-list')
        response = self.client.get(f"{user_groups_url}?user={self.regular_user.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Step 3: Remove user from group (soft delete)
        detail_url = reverse('UserGroupViewSet-detail', kwargs={'pk': user_group.id})
        update_data = {'is_active': False}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])

        # Step 4: Verify assignment is removed (filtered by is_active=True)
        response = self.client.get(f"{user_groups_url}?user={self.regular_user.id}")
        self.assertEqual(len(response.data['results']), 0)

    def test_permission_management_workflow(self):
        """
        Test complete permission management workflow
        """
        self.client.force_authenticate(user=self.admin_user)

        # Step 1: Get current group permissions
        group_permissions_url = reverse('GroupPermissionViewSet-list')
        response = self.client.get(f"{group_permissions_url}?group={self.rrh_group.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        initial_count = len(response.data['results'])

        # Step 2: Add permission to RRH group
        permission_data = {
            'group': self.rrh_group.id,
            'permission': self.view_users_permission.id,
            'granted': True,
            'created_by': self.admin_user.id
        }

        response = self.client.post(group_permissions_url, permission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 3: Verify group has the permission
        response = self.client.get(f"{group_permissions_url}?group={self.rrh_group.id}")
        self.assertEqual(len(response.data['results']), initial_count + 1)

        # Step 4: Update permission (revoke it)
        group_permission_id = response.data['results'][-1]['id']
        detail_url = reverse('GroupPermissionViewSet-detail', kwargs={'pk': group_permission_id})

        update_data = {'granted': False}
        response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['granted'])

        # Step 5: Add another permission with different action
        permission_data['permission'] = self.manage_users_permission.id
        response = self.client.post(group_permissions_url, permission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 6: Verify group has multiple permissions
        response = self.client.get(f"{group_permissions_url}?group={self.rrh_group.id}")
        self.assertEqual(len(response.data['results']), initial_count + 2)

    def test_permission_management_failure_scenarios(self):
        """
        Test permission management failure scenarios
        """
        self.client.force_authenticate(user=self.admin_user)
        group_permissions_url = reverse('GroupPermissionViewSet-list')

        # Test duplicate permission assignment
        GroupPermission.objects.create(
            group=self.rrh_group,
            permission=self.view_users_permission,
            granted=True,
            created_by=self.admin_user
        )

        permission_data = {
            'group': self.rrh_group.id,
            'permission': self.view_users_permission.id,
            'granted': True,
            'created_by': self.admin_user.id
        }

        response = self.client.post(group_permissions_url, permission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test permission assignment to non-existent group
        permission_data['group'] = 99999
        response = self.client.post(group_permissions_url, permission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_audit_logging_integration(self):
        """
        Test that user management operations are properly audited
        """
        self.client.force_authenticate(user=self.admin_user)

        # Clear existing audit logs
        audit_log.objects.all().delete()

        # Step 1: Perform user-group assignment
        user_groups_url = reverse('UserGroupViewSet-list')
        assignment_data = {
            'user': self.regular_user.id,
            'group': self.rrh_group.id,
            'assigned_by': self.admin_user.id
        }

        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 2: Verify audit log was created
        audit_logs = audit_log.objects.filter(
            user_id=self.admin_user,
            action='CREATE',
            type_ressource='UserGroup'
        )
        self.assertEqual(audit_logs.count(), 1)

        audit_entry = audit_logs.first()
        self.assertEqual(audit_entry.user_id, self.admin_user)
        self.assertEqual(audit_entry.action, 'CREATE')
        self.assertEqual(audit_entry.type_ressource, 'UserGroup')

        # Step 3: Perform permission update
        group_permission = GroupPermission.objects.create(
            group=self.rrh_group,
            permission=self.view_users_permission,
            granted=True,
            created_by=self.admin_user
        )

        group_permissions_url = reverse('GroupPermissionViewSet-detail', kwargs={'pk': group_permission.id})
        update_data = {'granted': False}
        response = self.client.patch(group_permissions_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Step 4: Verify permission update was audited
        audit_logs = audit_log.objects.filter(
            user_id=self.admin_user,
            action='UPDATE',
            type_ressource='GroupPermission'
        )
        self.assertGreaterEqual(audit_logs.count(), 1)

    def test_unauthorized_access_scenarios(self):
        """
        Test unauthorized access scenarios
        """
        # Test without authentication
        user_groups_url = reverse('UserGroupViewSet-list')
        response = self.client.get(user_groups_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test with regular user (insufficient permissions)
        self.client.force_authenticate(user=self.regular_user)

        user_groups_url = reverse('UserGroupViewSet-list')
        assignment_data = {
            'user': self.admin_user.id,
            'group': self.rrh_group.id,
            'assigned_by': self.regular_user.id
        }

        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_complete_user_management_integration_workflow(self):
        """
        Test complete user management integration workflow
        """
        # Step 1: Login as admin
        login_url = reverse('login')
        login_data = {
            'email': 'admin@example.com',
            'password': 'testpass123'
        }

        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']

        # Step 2: Set authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        # Step 3: Create a new user
        users_url = reverse('userAPIView-list')
        new_user_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'nom': 'New',
            'prenom': 'User'
        }

        response = self.client.post(users_url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user_id = response.data['id']

        # Step 4: Assign new user to a group
        user_groups_url = reverse('UserGroupViewSet-list')
        assignment_data = {
            'user': new_user_id,
            'group': self.rrh_group.id,
            'assigned_by': self.admin_user.id
        }

        response = self.client.post(user_groups_url, assignment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 5: Add permissions to the group
        group_permissions_url = reverse('GroupPermissionViewSet-list')
        permission_data = {
            'group': self.rrh_group.id,
            'permission': self.view_users_permission.id,
            'granted': True,
            'created_by': self.admin_user.id
        }

        response = self.client.post(group_permissions_url, permission_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Step 6: Verify the complete setup
        # Check user exists
        response = self.client.get(f"{users_url}{new_user_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newuser@example.com')

        # Check user-group assignment
        response = self.client.get(f"{user_groups_url}?user={new_user_id}")
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['group'], self.rrh_group.id)

        # Check group permissions
        response = self.client.get(f"{group_permissions_url}?group={self.rrh_group.id}")
        permission_ids = [gp['permission'] for gp in response.data['results']]
        self.assertIn(self.view_users_permission.id, permission_ids)

        # Step 7: Test new user login and permission verification
        new_user_login_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }

        response = self.client.post(login_url, new_user_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user_token = response.data['access']

        # Step 8: Verify new user can access appropriate resources
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_user_token}')

        # Should be able to view users (has view_users permission through RRH group)
        response = self.client.get(users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should not be able to create users (doesn't have manage_users permission)
        response = self.client.post(users_url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_pagination_and_filtering(self):
        """
        Test API pagination and filtering functionality
        """
        self.client.force_authenticate(user=self.admin_user)

        # Create additional test data
        for i in range(15):
            Group.objects.create(
                code=f'TST{i:02d}',
                name=f'Test Group {i}',
                description=f'Test group number {i}'
            )

        # Test pagination
        groups_url = reverse('GroupViewSet-list')
        response = self.client.get(f"{groups_url}?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNotNone(response.data['next'])

        # Test filtering
        response = self.client.get(f"{groups_url}?search=ADM")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

        # Verify ADM group is in results
        group_codes = [group['code'] for group in response.data['results']]
        self.assertIn('ADM', group_codes)

        # Test ordering
        response = self.client.get(f"{groups_url}?ordering=code")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify results are ordered by code
        codes = [group['code'] for group in response.data['results']]
        self.assertEqual(codes, sorted(codes))

    def tearDown(self):
        """Clean up after tests"""
        # Clean up is handled automatically by Django's test framework
        pass
