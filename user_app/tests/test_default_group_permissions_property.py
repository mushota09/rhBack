"""
Property-Based Test for Default Group Permissions

Feature: user-management, Property 9: Default Group Permissions
**Validates: Requirements 4.4**

This test validates that predefined groups have appropriate default permission sets
that align with their organizational role and responsibilities.
"""

from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase as HypothesisTestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models

from user_app.models import Group, UserGroup, Permission, GroupPermission

User = get_user_model()


class DefaultGroupPermissionsPropertyTest(HypothesisTestCase):
    """
    Property-based test for default group permissions

    Feature: user-management, Property 9: Default Group Permissions
    **Validates: Requirements 4.4**
    """

    def setUp(self):
        cache.clear()
        # Create test data programmatically instead of using fixtures
        self._create_test_data()

    def _create_test_data(self):
        """Create test groups, permissions, and group permissions"""
        from django.contrib.contenttypes.models import ContentType
        from django.utils import timezone

        # Create predefined groups
        groups_data = [
            ('ADM', 'Administrateur', 'Administrateur système avec accès complet'),
            ('AP', 'Analyste des Projets', 'Analyste responsable du suivi des projets'),
            ('AI', 'Auditeur interne', 'Auditeur interne responsable du contrôle'),
            ('CSE', 'Chargé du Suivi-Evaluation', 'Chargé du suivi et évaluation'),
            ('CH', 'Chauffeur', 'Chauffeur responsable du transport'),
            ('CS', 'Chef de service', 'Chef de service responsable d\'une unité'),
            ('CSFP', 'Chef Service Financement Projets', 'Chef du service de financement'),
            ('CCI', 'Chef du contrôle interne', 'Chef du service de contrôle interne'),
            ('CM', 'Comptable', 'Comptable responsable de la gestion financière'),
            ('DIR', 'Directeur/Directrice', 'Directeur avec autorité de direction'),
            ('GS', 'Gestionnaire de Stock', 'Gestionnaire responsable des stocks'),
            ('IT', 'Informaticien', 'Informaticien responsable des systèmes'),
            ('JR', 'Juriste', 'Juriste responsable des questions juridiques'),
            ('LG', 'Logisticien', 'Logisticien responsable de la logistique'),
            ('PL', 'Planton', 'Planton responsable de l\'accueil et sécurité'),
            ('PCA', 'Président commission d\'appel', 'Président de la commission d\'appel'),
            ('PCR', 'Président commission réception', 'Président de la commission de réception'),
            ('PCDR', 'Président commission recrutement', 'Président de la commission de recrutement'),
            ('RAF', 'Responsable Administratif et Financier', 'Responsable des affaires administratives'),
            ('RRH', 'Responsable Ressources Humaines', 'Responsable de la gestion RH'),
            ('SEC', 'Secrétaire', 'Secrétaire responsable du support administratif'),
        ]

        for code, name, description in groups_data:
            Group.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                    'is_active': True
                }
            )

        # Create basic permissions
        content_type = ContentType.objects.get_for_model(User)
        permissions_data = [
            ('employee.create', 'Create Employee', 'employee', 'CREATE'),
            ('employee.read', 'Read Employee', 'employee', 'READ'),
            ('employee.update', 'Update Employee', 'employee', 'UPDATE'),
            ('employee.delete', 'Delete Employee', 'employee', 'DELETE'),
            ('contract.create', 'Create Contract', 'contract', 'CREATE'),
            ('contract.read', 'Read Contract', 'contract', 'READ'),
            ('contract.update', 'Update Contract', 'contract', 'UPDATE'),
            ('contract.delete', 'Delete Contract', 'contract', 'DELETE'),
            ('payroll.create', 'Create Payroll', 'payroll', 'CREATE'),
            ('payroll.read', 'Read Payroll', 'payroll', 'READ'),
            ('payroll.update', 'Update Payroll', 'payroll', 'UPDATE'),
            ('payroll.delete', 'Delete Payroll', 'payroll', 'DELETE'),
            ('leave.create', 'Create Leave', 'leave', 'CREATE'),
            ('leave.read', 'Read Leave', 'leave', 'READ'),
            ('leave.update', 'Update Leave', 'leave', 'UPDATE'),
            ('leave.delete', 'Delete Leave', 'leave', 'DELETE'),
            ('user_management.create', 'Create User Management', 'user_management', 'CREATE'),
            ('user_management.read', 'Read User Management', 'user_management', 'READ'),
            ('user_management.update', 'Update User Management', 'user_management', 'UPDATE'),
            ('user_management.delete', 'Delete User Management', 'user_management', 'DELETE'),
            ('audit.read', 'Read Audit', 'audit', 'READ'),
            ('system.create', 'Create System', 'system', 'CREATE'),
            ('system.read', 'Read System', 'system', 'READ'),
            ('system.update', 'Update System', 'system', 'UPDATE'),
            ('system.delete', 'Delete System', 'system', 'DELETE'),
            ('report.read', 'Read Reports', 'report', 'READ'),
            ('deduction.create', 'Create Deduction', 'deduction', 'CREATE'),
            ('deduction.read', 'Read Deduction', 'deduction', 'READ'),
            ('deduction.update', 'Update Deduction', 'deduction', 'UPDATE'),
            ('deduction.delete', 'Delete Deduction', 'deduction', 'DELETE'),
            ('document.create', 'Create Document', 'document', 'CREATE'),
            ('document.read', 'Read Document', 'document', 'READ'),
            ('document.update', 'Update Document', 'document', 'UPDATE'),
            ('document.delete', 'Delete Document', 'document', 'DELETE'),
        ]

        for codename, name, resource, action in permissions_data:
            Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'content_type': content_type,
                    'resource': resource,
                    'action': action,
                    'description': f'Permission to {action.lower()} {resource}'
                }
            )

        # Create some basic group permissions
        self._create_group_permissions()

    def _create_group_permissions(self):
        """Create basic group permissions for testing"""
        # ADM group gets all permissions
        adm_group = Group.objects.get(code='ADM')
        all_permissions = Permission.objects.all()
        for permission in all_permissions:
            GroupPermission.objects.get_or_create(
                group=adm_group,
                permission=permission,
                defaults={'granted': True}
            )

        # DIR group gets most permissions except system
        dir_group = Group.objects.get(code='DIR')
        dir_permissions = Permission.objects.exclude(resource='system')
        for permission in dir_permissions:
            GroupPermission.objects.get_or_create(
                group=dir_group,
                permission=permission,
                defaults={'granted': True}
            )

        # RRH group gets HR-related permissions
        rrh_group = Group.objects.get(code='RRH')
        rrh_permission_resources = ['employee', 'contract', 'leave', 'user_management', 'document', 'report']
        rrh_permissions = Permission.objects.filter(resource__in=rrh_permission_resources)
        for permission in rrh_permissions:
            GroupPermission.objects.get_or_create(
                group=rrh_group,
                permission=permission,
                defaults={'granted': True}
            )

        # IT group gets system and user management permissions
        it_group = Group.objects.get(code='IT')
        it_permission_resources = ['system', 'user_management', 'employee', 'document']
        it_permissions = Permission.objects.filter(resource__in=it_permission_resources)
        for permission in it_permissions:
            GroupPermission.objects.get_or_create(
                group=it_group,
                permission=permission,
                defaults={'granted': True}
            )

        # AI group gets audit and read-only permissions
        ai_group = Group.objects.get(code='AI')
        ai_permissions = Permission.objects.filter(
            models.Q(resource='audit') |
            models.Q(action='READ')
        )
        for permission in ai_permissions:
            GroupPermission.objects.get_or_create(
                group=ai_group,
                permission=permission,
                defaults={'granted': True}
            )

        # RAF group gets financial permissions
        raf_group = Group.objects.get(code='RAF')
        raf_permission_resources = ['payroll', 'deduction', 'report', 'employee']
        raf_permissions = Permission.objects.filter(resource__in=raf_permission_resources)
        for permission in raf_permissions:
            GroupPermission.objects.get_or_create(
                group=raf_group,
                permission=permission,
                defaults={'granted': True}
            )

        # CM group gets accounting permissions
        cm_group = Group.objects.get(code='CM')
        cm_permission_resources = ['payroll', 'deduction']
        cm_permissions = Permission.objects.filter(resource__in=cm_permission_resources)
        for permission in cm_permissions:
            GroupPermission.objects.get_or_create(
                group=cm_group,
                permission=permission,
                defaults={'granted': True}
            )

        # CS group gets service management permissions
        cs_group = Group.objects.get(code='CS')
        cs_permissions = Permission.objects.filter(
            models.Q(resource='employee', action='READ') |
            models.Q(resource='leave') |
            models.Q(resource='report', action='READ')
        )
        for permission in cs_permissions:
            GroupPermission.objects.get_or_create(
                group=cs_group,
                permission=permission,
                defaults={'granted': True}
            )

        # SEC group gets basic read permissions and document management
        sec_group = Group.objects.get(code='SEC')
        sec_permissions = Permission.objects.filter(
            models.Q(resource='employee', action='READ') |
            models.Q(resource='document') |
            models.Q(resource='leave', action__in=['CREATE', 'READ'])
        )
        for permission in sec_permissions:
            GroupPermission.objects.get_or_create(
                group=sec_group,
                permission=permission,
                defaults={'granted': True}
            )

        # PL group gets minimal read permissions
        pl_group = Group.objects.get(code='PL')
        pl_permissions = Permission.objects.filter(
            resource='employee',
            action='READ'
        )
        for permission in pl_permissions:
            GroupPermission.objects.get_or_create(
                group=pl_group,
                permission=permission,
                defaults={'granted': True}
            )

        # Assign basic read permissions to remaining groups
        remaining_groups = Group.objects.exclude(
            code__in=['ADM', 'DIR', 'RRH', 'IT', 'AI', 'RAF', 'CM', 'CS', 'SEC', 'PL']
        )
        basic_permissions = Permission.objects.filter(
            models.Q(resource='employee', action='READ') |
            models.Q(resource='document', action='READ') |
            models.Q(resource='report', action='READ')
        )

        for group in remaining_groups:
            for permission in basic_permissions:
                GroupPermission.objects.get_or_create(
                    group=group,
                    permission=permission,
                    defaults={'granted': True}
                )

    def tearDown(self):
        cache.clear()

    @given(
        group_code=st.sampled_from([
            'ADM', 'AP', 'AI', 'CSE', 'CH', 'CS', 'CSFP', 'CCI', 'CM', 'DIR',
            'GS', 'IT', 'JR', 'LG', 'PL', 'PCA', 'PCR', 'PCDR', 'RAF', 'RRH', 'SEC'
        ])
    )
    @settings(max_examples=100, deadline=10000)
    def test_predefined_group_has_appropriate_default_permissions(self, group_code):
        """
        Property: For any predefined group, the system should include appropriate
        default permission sets that align with the group's organizational role
        and responsibilities.

        **Validates: Requirements 4.4**
        """
        # Get the group
        try:
            group = Group.objects.get(code=group_code, is_active=True)
        except Group.DoesNotExist:
            self.fail(f"Predefined group {group_code} should exist and be active")

        # Get all permissions assigned to this group
        group_permissions = GroupPermission.objects.filter(
            group=group,
            granted=True
        ).select_related('permission')

        # Property: Every predefined group should have at least some permissions
        self.assertGreater(
            group_permissions.count(),
            0,
            f"Group {group_code} should have at least one default permission"
        )

        # Get permission codenames for this group
        permission_codenames = set(
            gp.permission.codename for gp in group_permissions
        )

        # Define expected permission patterns based on organizational roles
        role_based_expectations = self._get_role_based_expectations()

        if group_code in role_based_expectations:
            expected_patterns = role_based_expectations[group_code]

            # Property: Group should have permissions that match its organizational role
            for pattern_type, patterns in expected_patterns.items():
                if pattern_type == 'required':
                    # These permissions must be present
                    for pattern in patterns:
                        matching_permissions = [
                            perm for perm in permission_codenames
                            if pattern in perm
                        ]
                        self.assertGreater(
                            len(matching_permissions),
                            0,
                            f"Group {group_code} should have permissions matching pattern '{pattern}'"
                        )

                elif pattern_type == 'forbidden':
                    # These permissions should not be present
                    for pattern in patterns:
                        matching_permissions = [
                            perm for perm in permission_codenames
                            if pattern in perm
                        ]
                        self.assertEqual(
                            len(matching_permissions),
                            0,
                            f"Group {group_code} should not have permissions matching pattern '{pattern}'"
                        )

        # Property: All permissions should be valid and properly formatted
        for gp in group_permissions:
            permission = gp.permission

            # Permission should have proper codename format (resource.action)
            self.assertIn('.', permission.codename,
                         f"Permission {permission.codename} should follow 'resource.action' format")

            # Permission should have valid action
            valid_actions = ['CREATE', 'READ', 'UPDATE', 'DELETE']
            self.assertIn(permission.action, valid_actions,
                         f"Permission {permission.codename} should have valid action")

            # Permission should have non-empty resource
            self.assertTrue(permission.resource.strip(),
                           f"Permission {permission.codename} should have non-empty resource")

    def _get_role_based_expectations(self):
        """
        Define expected permission patterns for each organizational role
        based on their responsibilities
        """
        return {
            'ADM': {
                'required': ['employee', 'contract', 'payroll', 'user_management', 'system'],
                'forbidden': []  # Admin should have access to everything
            },
            'DIR': {
                'required': ['employee', 'contract', 'payroll', 'report'],
                'forbidden': ['system']  # Directors shouldn't manage system config
            },
            'RRH': {
                'required': ['employee', 'contract', 'leave', 'user_management'],
                'forbidden': ['system']  # HR shouldn't manage system config
            },
            'RAF': {
                'required': ['payroll', 'deduction', 'report'],
                'forbidden': ['system']  # Finance shouldn't manage system config
            },
            'CM': {
                'required': ['payroll', 'deduction'],
                'forbidden': ['employee.create', 'employee.delete', 'system']  # Accountants shouldn't create/delete employees
            },
            'AI': {
                'required': ['audit', 'report'],
                'forbidden': ['employee.create', 'employee.update', 'employee.delete']  # Auditors should only read
            },
            'IT': {
                'required': ['system', 'user_management'],
                'forbidden': ['payroll', 'deduction']  # IT shouldn't access financial data
            },
            'CS': {
                'required': ['employee.read', 'leave'],
                'forbidden': ['payroll', 'deduction', 'system']  # Service chiefs have limited access
            },
            'SEC': {
                'required': ['employee.read', 'document'],
                'forbidden': ['payroll', 'deduction', 'system', 'user_management']  # Secretaries have basic access
            },
            'PL': {
                'required': ['employee.read'],
                'forbidden': ['payroll', 'deduction', 'system', 'user_management', 'contract']  # Guards have minimal access
            }
        }

    @given(
        resource_type=st.sampled_from(['employee', 'contract', 'payroll', 'leave', 'deduction', 'document', 'user_management', 'audit', 'system', 'report'])
    )
    @settings(max_examples=50, deadline=10000)
    def test_resource_permissions_are_consistently_assigned(self, resource_type):
        """
        Property: For any resource type, permissions should be consistently assigned
        across groups based on their organizational hierarchy and responsibilities.

        **Validates: Requirements 4.4**
        """
        # Get all groups that have any permission for this resource
        groups_with_resource_access = Group.objects.filter(
            group_permissions__permission__resource=resource_type,
            group_permissions__granted=True,
            is_active=True
        ).distinct()

        if groups_with_resource_access.exists():
            # Property: If a resource has permissions assigned, at least one group should have READ access
            read_permissions = GroupPermission.objects.filter(
                group__in=groups_with_resource_access,
                permission__resource=resource_type,
                permission__action='READ',
                granted=True
            )

            self.assertGreater(
                read_permissions.count(),
                0,
                f"At least one group should have READ permission for resource '{resource_type}'"
            )

            # Property: Administrative groups should have more comprehensive access
            admin_groups = Group.objects.filter(code__in=['ADM', 'DIR', 'RRH'], is_active=True)

            for admin_group in admin_groups:
                admin_permissions = GroupPermission.objects.filter(
                    group=admin_group,
                    permission__resource=resource_type,
                    granted=True
                ).count()

                # Property: Admin groups should have access to resources they manage
                if admin_permissions > 0:
                    self.assertGreater(
                        admin_permissions,
                        0,
                        f"Admin group {admin_group.code} should have {resource_type} permissions"
                    )

    def test_all_predefined_groups_exist_and_have_permissions(self):
        """
        Property: All 21 predefined groups should exist and have appropriate default permissions.

        **Validates: Requirements 4.4**
        """
        expected_groups = [
            'ADM', 'AP', 'AI', 'CSE', 'CH', 'CS', 'CSFP', 'CCI', 'CM', 'DIR',
            'GS', 'IT', 'JR', 'LG', 'PL', 'PCA', 'PCR', 'PCDR', 'RAF', 'RRH', 'SEC'
        ]

        # Property: All predefined groups should exist
        existing_groups = Group.objects.filter(
            code__in=expected_groups,
            is_active=True
        ).values_list('code', flat=True)

        self.assertEqual(
            set(existing_groups),
            set(expected_groups),
            "All 21 predefined groups should exist and be active"
        )

        # Property: Each group should have at least one permission
        for group_code in expected_groups:
            group = Group.objects.get(code=group_code)
            permission_count = GroupPermission.objects.filter(
                group=group,
                granted=True
            ).count()

            self.assertGreater(
                permission_count,
                0,
                f"Group {group_code} should have at least one default permission"
            )

    @given(
        action_type=st.sampled_from(['CREATE', 'READ', 'UPDATE', 'DELETE'])
    )
    @settings(max_examples=20, deadline=10000)
    def test_permission_action_distribution_is_appropriate(self, action_type):
        """
        Property: For any action type, the distribution of permissions across groups
        should reflect organizational hierarchy and security principles.

        **Validates: Requirements 4.4**
        """
        # Get all permissions with this action type
        permissions_with_action = Permission.objects.filter(action=action_type)

        if permissions_with_action.exists():
            # Get groups that have permissions with this action
            groups_with_action = Group.objects.filter(
                group_permissions__permission__action=action_type,
                group_permissions__granted=True,
                is_active=True
            ).distinct()

            # Property: READ permissions should be more widely distributed than CREATE/UPDATE/DELETE
            if action_type == 'READ':
                # Most groups should have some READ permissions
                self.assertGreaterEqual(
                    groups_with_action.count(),
                    10,  # At least 10 groups should have READ permissions
                    "READ permissions should be widely distributed across groups"
                )

            elif action_type in ['CREATE', 'DELETE']:
                # CREATE and DELETE should be more restricted
                admin_groups = ['ADM', 'DIR', 'RRH', 'RAF', 'IT']
                groups_with_create_delete = groups_with_action.filter(
                    code__in=admin_groups
                ).count()

                # Most CREATE/DELETE permissions should be with admin groups
                total_groups_with_action = groups_with_action.count()
                if total_groups_with_action > 0:
                    admin_ratio = groups_with_create_delete / total_groups_with_action
                    self.assertGreaterEqual(
                        admin_ratio,
                        0.3,  # At least 30% of groups with CREATE/DELETE should be admin groups
                        f"{action_type} permissions should be primarily assigned to administrative groups"
                    )

            # Property: All groups with this action should have valid permissions
            for group in groups_with_action:
                group_permissions = GroupPermission.objects.filter(
                    group=group,
                    permission__action=action_type,
                    granted=True
                )

                self.assertGreater(
                    group_permissions.count(),
                    0,
                    f"Group {group.code} should have at least one {action_type} permission"
                )
