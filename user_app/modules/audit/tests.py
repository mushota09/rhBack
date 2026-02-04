"""
Tests for user management audit logging functionality.
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from user_app.models import Group, UserGroup, Permission, GroupPermission, audit_log
from user_app.modules.audit.services import UserManagementAuditService

User = get_user_model()


class UserManagementAuditServiceTest(TestCase):
    """Test cases for UserManagementAuditService."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            nom='Admin',
            prenom='Test',
            password='testpass123'
        )
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            nom='User',
            prenom='Test',
            password='testpass123'
        )

        # Create test group
        self.test_group = Group.objects.create(
            code='TEST',
            name='Test Group',
            description='Test group for audit logging'
        )

        # Create test permission
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(User)
        self.test_permission = Permission.objects.create(
            codename='test_permission',
            name='Test Permission',
            content_type=content_type,
            resource='user',
            action='READ',
            description='Test permission for audit logging'
        )

    @pytest.mark.asyncio
    async def test_log_user_group_assignment_create(self):
        """Test logging user-group assignment creation."""
        # Create user-group assignment
        user_group = await sync_to_async(UserGroup.objects.create)(
            user=self.regular_user,
            group=self.test_group,
            assigned_by=self.admin_user
        )

        # Log the assignment
        audit_entry = await UserManagementAuditService.log_user_group_assignment(
            user_group=user_group,
            action='CREATE',
            performed_by=self.admin_user,
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )

        # Verify audit log entry
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.action, 'CREATE')
        self.assertEqual(audit_entry.type_ressource, 'user_group_assignment')
        self.assertEqual(audit_entry.user_id, self.admin_user)
        self.assertEqual(audit_entry.adresse_ip, '127.0.0.1')
        self.assertEqual(audit_entry.user_agent, 'Test Agent')

        # Verify audit data
        self.assertIsNone(audit_entry.anciennes_valeurs)
        self.assertIsNotNone(audit_entry.nouvelles_valeurs)
        self.assertEqual(audit_entry.nouvelles_valeurs['user_id'], self.regular_user.id)
        self.assertEqual(audit_entry.nouvelles_valeurs['group_id'], self.test_group.id)
        self.assertEqual(audit_entry.nouvelles_valeurs['group_code'], 'TEST')

    @pytest.mark.asyncio
    async def test_log_group_permission_change_create(self):
        """Test logging group permission change creation."""
        # Create group permission
        group_permission = await sync_to_async(GroupPermission.objects.create)(
            group=self.test_group,
            permission=self.test_permission,
            granted=True,
            created_by=self.admin_user
        )

        # Log the permission change
        audit_entry = await UserManagementAuditService.log_group_permission_change(
            group_permission=group_permission,
            action='CREATE',
            performed_by=self.admin_user,
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )

        # Verify audit log entry
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.action, 'CREATE')
        self.assertEqual(audit_entry.type_ressource, 'group_permission')
        self.assertEqual(audit_entry.user_id, self.admin_user
er-group assignment update."""
        # Create user-group assignment
        user_group = await sync_to_async(UserGroup.objects.create)(
            user=self.regular_user,
            group=self.test_group,
            assigned_by=self.admin_user,
            is_active=True
        )

        old_values = {'is_active': True}
        new_values = {'is_active': False}

        # Update the assignment
        user_group.is_active = False
        await sync_to_async(user_group.save)()

        # Log the update
        audit_entry = await UserManagementAuditService.log_user_group_assignment(
            user_group=user_group,
            action='UPDATE',
            performed_by=self.admin_user,
            old_values=old_values,
            new_values=new_values
        )

        # Verify audit log entry
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.action, 'UPDATE')
        self.assertEqual(audit_entry.anciennes_valeurs, old_values)
        self.assertEqual(audit_entry.nouvelles_valeurs, new_values)

    @pytest.mark.asyncio
    async def test_log_user_group_assignment_delete(self):
        """Test logging user-group assignment deletion."""
        # Create user-group assignment
        user_group = await sync_to_async(UserGroup.objects.create)(
            user=self.regular_user,
            group=self.test_group,
            assigned_by=self.admin_user
        )

        old_values = {
            'user_id': self.regular_user.id,
            'group_id': self.test_group.id,
            'is_active': True
        }

        # Log the deletion
        audit_entry = await UserManagementAuditService.log_user_group_assignment(
            user_group=user_group,
            action='DELETE',
            performed_by=self.admin_user,
            old_values=old_values
        )

        # Verify audit log entry
        self.assertIsNotNone(audit_entry)
        self.assertEqual(audit_entry.action, 'DELETE')
        self.assertEqual(audit_entry.anciennes_valeurs, old_values)
        self.assertIsNone(audit_entry.nouvelles_valeurs)

    def test_get_client_ip(self):
        """Test client IP extraction."""
        from django.test import RequestFactory

        factory = RequestFactory()

        # Test with X-Forwarded-For header
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        ip = UserManagementAuditService.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

        # Test with REMOTE_ADDR
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        ip = UserManagementAuditService.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

    def test_get_user_agent(self):
        """Test user agent extraction."""
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 Test Browser'

        user_agent = UserManagementAuditService.get_user_agent(request)
        self.assertEqual(user_agent, 'Mozilla/5.0 Test Browser')

        # Test with missing user agent
        request = factory.get('/')
        user_agent = UserManagementAuditService.get_user_agent(request)
        self.assertEqual(user_agent, '')
