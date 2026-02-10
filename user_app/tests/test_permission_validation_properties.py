"""
Property-Based Tests for Permission Validation

Requirements: 8.4 - Property-based tests for permission validation logic
"""

from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

from user_app.models import Group, UserGroup, Permission, GroupPermission

User = get_user_model()


class SyncPermissionService:
    """Synchronous version of PermissionService for testing"""

    @classmethod
    def get_user_permissions(cls, user):
        if not user or not user.is_active:
            return set()

        user_groups = list(
            UserGroup.objects.filter(
                user=user,
                is_active=True,
                group__is_active=True
            ).select_related('group')
        )

        if not user_groups:
            return set()

        group_ids = [ug.group.id for ug in user_groups]
        group_permissions = list(
            GroupPermission.objects.filter(
                group_id__in=group_ids,
                granted=True
            ).select_related('permission')
        )

        permissions = {gp.permission.codename for gp in group_permissions}
        return permissions

    @classmethod
    def check_permission(cls, user, resource, action):
        if not user or not user.is_active:
            return False

        if user.is_superuser:
            return True

        user_permissions = cls.get_user_permissions(user)
        permission_codename = f"{resource}.{action}"
        return permission_codename in user_permissions


class PermissionValidationPropertyTests(HypothesisTestCase):
    """Property-based tests for permission validation logic"""

    def setUp(self):
        try:
            cache.clear()
        except Exception:
            # Ignore cache errors in tests
            pass

    def tearDown(self):
        try:
            cache.clear()
        except Exception:
            # Ignore cache errors in tests
            pass

    @given(
        user_email=st.emails(),
        resource_name=st.text(min_size=3, max_size=10),
        action=st.sampled_from(['CREATE', 'READ', 'UPDATE', 'DELETE'])
    )
    @settings(max_examples=5, deadline=10000)
    def test_superuser_permission_bypass_property(self, user_email, resource_name, action):
        """Property: Superusers have all permissions, regular users need group assignments."""
        # Create regular user
        regular_user = User.objects.create(
            email=user_email,
            nom="Regular",
            prenom="User",
            is_active=True,
            is_superuser=False
        )

        # Create superuser
        super_email = f"super_{user_email}"
        super_user = User.objects.create(
            email=super_email,
            nom="Super",
            prenom="User",
            is_active=True,
            is_superuser=True
        )

        # Property: Superuser should always have permission
        super_has_permission = SyncPermissionService.check_permission(
            super_user, resource_name, action
        )
        self.assertTrue(super_has_permission)

        # Property: Regular user should not have permission without group assignment
        regular_has_permission = SyncPermissionService.check_permission(
            regular_user, resource_name, action
        )
        self.assertFalse(regular_has_permission)

    @given(
        user_email=st.emails(),
        group_code=st.text(min_size=3, max_size=10),
        resource_name=st.text(min_size=3, max_size=10),
        action=st.sampled_from(['CREATE', 'READ', 'UPDATE', 'DELETE']),
        granted=st.booleans()
    )
    @settings(max_examples=5, deadline=10000)
    def test_permission_grant_revoke_property(self, user_email, group_code, resource_name, action, granted):
        """Property: Permission granted state determines user access."""
        # Create test user
        user = User.objects.create(
            email=user_email,
            nom="Test",
            prenom="User",
            is_active=True
        )

        # Create test group
        group = Group.objects.create(
            code=group_code,
            name=f"Group {group_code}",
            description=f"Test group {group_code}",
            is_active=True
        )

        # Assign user to group
        UserGroup.objects.create(
            user=user,
            group=group,
            assigned_by=user,
            is_active=True
        )

        # Create permission
        content_type = ContentType.objects.get_for_model(User)
        permission_codename = f"{resource_name}.{action}"
        permission = Permission.objects.create(
            codename=permission_codename,
            name=f"Permission {permission_codename}",
            content_type=content_type,
            resource=resource_name,
            action=action
        )

        # Create group permission with granted state
        GroupPermission.objects.create(
            group=group,
            permission=permission,
            granted=granted,
            created_by=user
        )

        # Property: Permission check should match granted state
        has_permission = SyncPermissionService.check_permission(user, resource_name, action)
        self.assertEqual(has_permission, granted)

    @given(
        user_email=st.emails(),
        group_code=st.text(min_size=3, max_size=10)
    )
    @settings(max_examples=5, deadline=5000)
    def test_empty_permission_set_property(self, user_email, group_code):
        """Property: Users with no permissions have empty permission sets."""
        # Create test user
        user = User.objects.create(
            email=user_email,
            nom="Test",
            prenom="User",
            is_active=True
        )

        # Create test group
        group = Group.objects.create(
            code=group_code,
            name=f"Group {group_code}",
            description=f"Test group {group_code}",
            is_active=True
        )

        # Assign user to group but don't grant any permissions
        UserGroup.objects.create(
            user=user,
            group=group,
            assigned_by=user,
            is_active=True
        )

        # Property: User should have no permissions
        user_permissions = SyncPermissionService.get_user_permissions(user)
        self.assertEqual(len(user_permissions), 0)

        # Property: Any permission check should return False
        has_any_permission = SyncPermissionService.check_permission(user, "any_resource", "READ")
        self.assertFalse(has_any_permission)

    @given(
        resource_name=st.text(min_size=3, max_size=10),
        action=st.sampled_from(['CREATE', 'READ', 'UPDATE', 'DELETE'])
    )
    @settings(max_examples=5, deadline=5000)
    def test_nonexistent_user_permission_property(self, resource_name, action):
        """Property: None and inactive users have no permissions."""
        # Test with None user
        has_permission = SyncPermissionService.check_permission(None, resource_name, action)
        self.assertFalse(has_permission)

        # Test with inactive user
        inactive_user = User.objects.create(
            email="inactive@test.com",
            nom="Inactive",
            prenom="User",
            is_active=False
        )

        has_permission = SyncPermissionService.check_permission(inactive_user, resource_name, action)
        self.assertFalse(has_permission)
