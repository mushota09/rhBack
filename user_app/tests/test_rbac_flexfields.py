# -*- coding: utf-8 -*-
"""
Tests unitaires pour les modules RBAC avec FlexFields
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from user_app.models import Group, service, ServiceGroup, UserGroup, Permission, GroupPermission
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


@pytest.mark.django_db
class TestUserGroupFlexFields(TestCase):
    """Tests pour UserGroup avec expansion dynamique"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            nom='Admin',
            prenom='Test'
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.service1 = service.objects.create(
            titre='Service IT',
            code='IT',
            description='Service informatique'
        )
        self.group = Group.objects.create(
            code='DEV',
            name='Developpeurs',
            description='Groupe des developpeurs'
        )
        self.service_group = ServiceGroup.objects.create(
            service=self.service1,
            group=self.group
        )
        self.user_group = UserGroup.objects.create(
            user=self.user,
            group=self.group,
            assigned_by=self.user,
            is_active=True
        )

    def test_expansion_user_group_basic(self):
        """Test expansion UserGroup avec expand=user,group"""
        response = self.client.get(
            f'/api/user-group/{self.user_group.id}/?expand=user,group'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIsInstance(response.data['user'], dict)
        self.assertIn('email', response.data['user'])
        self.assertEqual(response.data['user']['email'], 'admin@example.com')
        self.assertIn('group', response.data)
        self.assertIsInstance(response.data['group'], dict)
        self.assertIn('code', response.data['group'])
        self.assertEqual(response.data['group']['code'], 'DEV')

    def test_expansion_user_group_nested(self):
        """Test expansion imbriquee avec expand=group.service_groups"""
        response = self.client.get(
            f'/api/user-group/{self.user_group.id}/?expand=group.service_groups'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('group', response.data)
        self.assertIsInstance(response.data['group'], dict)
        self.assertIn('service_groups', response.data['group'])
        self.assertIsInstance(response.data['group']['service_groups'], list)
        self.assertEqual(len(response.data['group']['service_groups']), 1)

    def test_sparse_fields_user_group(self):
        """Test champs sparse avec fields=id,user,group"""
        response = self.client.get(
            f'/api/user-group/{self.user_group.id}/?fields=id,user,group'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('user', response.data)
        self.assertIn('group', response.data)
        self.assertNotIn('assigned_at', response.data)
        self.assertNotIn('is_active', response.data)

    def test_omit_fields_user_group(self):
        """Test omission avec omit=assigned_at"""
        response = self.client.get(
            f'/api/user-group/{self.user_group.id}/?omit=assigned_at'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('assigned_at', response.data)
        self.assertIn('id', response.data)
        self.assertIn('user', response.data)
        self.assertIn('group', response.data)


@pytest.mark.django_db
class TestGroupPermissionFlexFields(TestCase):
    """Tests pour GroupPermission avec expansion dynamique"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.group = Group.objects.create(
            code='ADM',
            name='Administrateurs',
            description='Groupe des administrateurs'
        )
        content_type = ContentType.objects.get_for_model(User)
        self.permission = Permission.objects.create(
            codename='can_manage_users',
            name='Can manage users',
            content_type=content_type,
            resource='user',
            action='manage'
        )
        self.group_permission = GroupPermission.objects.create(
            group=self.group,
            permission=self.permission,
            granted=True,
            created_by=self.user
        )

    def test_expansion_group_permission_basic(self):
        """Test expansion GroupPermission avec expand=group,permission"""
        response = self.client.get(
            f'/api/group-permission/{self.group_permission.id}/?expand=group,permission'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('group', response.data)
        self.assertIsInstance(response.data['group'], dict)
        self.assertIn('code', response.data['group'])
        self.assertEqual(response.data['group']['code'], 'ADM')
        self.assertIn('permission', response.data)
        self.assertIsInstance(response.data['permission'], dict)
        self.assertIn('codename', response.data['permission'])
        self.assertEqual(response.data['permission']['codename'], 'can_manage_users')

    def test_expansion_group_permission_created_by(self):
        """Test expansion GroupPermission avec expand=created_by"""
        response = self.client.get(
            f'/api/group-permission/{self.group_permission.id}/?expand=created_by'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('created_by', response.data)
        self.assertIsInstance(response.data['created_by'], dict)
        self.assertIn('email', response.data['created_by'])
        self.assertEqual(response.data['created_by']['email'], 'admin@example.com')

    def test_sparse_fields_group_permission(self):
        """Test champs sparse avec fields=id,group,permission"""
        response = self.client.get(
            f'/api/group-permission/{self.group_permission.id}/?fields=id,group,permission'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('group', response.data)
        self.assertIn('permission', response.data)
        self.assertNotIn('granted', response.data)
        self.assertNotIn('created_at', response.data)


@pytest.mark.django_db
class TestPermissionFlexFields(TestCase):
    """Tests pour Permission avec FlexFields"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

        content_type = ContentType.objects.get_for_model(User)
        self.permission = Permission.objects.create(
            codename='can_view_users',
            name='Can view users',
            content_type=content_type,
            resource='user',
            action='view'
        )

    def test_list_permissions(self):
        """Test liste des permissions"""
        response = self.client.get('/api/permission/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)

    def test_retrieve_permission(self):
        """Test recuperation d une permission"""
        response = self.client.get(f'/api/permission/{self.permission.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codename'], 'can_view_users')
        self.assertIn('content_type_name', response.data)


@pytest.mark.django_db
class TestServiceFlexFields(TestCase):
    """Tests pour Service avec FlexFields"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

        self.service1 = service.objects.create(
            titre='Service IT',
            code='IT',
            description='Service informatique'
        )

    def test_list_services(self):
        """Test liste des services"""
        response = self.client.get('/api/service/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)

    def test_retrieve_service(self):
        """Test recuperation d un service"""
        response = self.client.get(f'/api/service/{self.service1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titre'], 'Service IT')
        self.assertEqual(response.data['code'], 'IT')

    def test_search_service(self):
        """Test recherche de service"""
        response = self.client.get('/api/service/?search=IT')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
