"""
Tests unitaires pour le module Group avec gestion ServiceGroups
"""
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from user_app.models import Group, service, ServiceGroup, UserGroup

User = get_user_model()


@pytest.mark.django_db
class TestGroupWithServiceGroups(TestCase):
    """Tests pour la création et suppression de Group avec ServiceGroups"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()

        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()

        # Authentifier le client
        self.client.force_authenticate(user=self.user)

        # Créer des services de test
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
        self.service3 = service.objects.create(
            titre='Service Finance',
            code='FIN',
            description='Service financier'
        )

    def test_create_group_with_valid_service_ids(self):
        """Test création Group avec service_ids valides"""
        data = {
            'code': 'ADM',
            'name': 'Administrateurs',
            'description': 'Groupe des administrateurs',
            'is_active': True,
            'service_ids': [self.service1.id, self.service2.id]
        }

        response = self.client.post('/api/groups/', data, format='json')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'ADM')
        self.assertIn('service_groups_created', response.data)
        self.assertEqual(response.data['service_groups_created'], 2)

        # Vérifier que les ServiceGroups ont été créés
        group = Group.objects.get(code='ADM')
        self.assertEqual(group.service_groups.count(), 2)

    def test_create_group_with_invalid_service_ids(self):
        """Test création Group avec service_ids invalides"""
        data = {
            'code': 'TEST',
            'name': 'Test Group',
            'description': 'Test',
            'is_active': True,
            'service_ids': [9999]  # ID qui n'existe pas
        }

        response = self.client.post('/api/groups/', data, format='json')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_group_without_service_ids(self):
        """Test création Group sans service_ids"""
        data = {
            'code': 'SIMPLE',
            'name': 'Simple Group',
            'description': 'Groupe sans services',
            'is_active': True
        }

        response = self.client.post('/api/groups/', data, format='json')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'SIMPLE')

        # Vérifier qu'aucun ServiceGroup n'a été créé
        group = Group.objects.get(code='SIMPLE')
        self.assertEqual(group.service_groups.count(), 0)

    def test_delete_group_without_users_cascade_service_groups(self):
        """Test suppression Group sans utilisateurs (cascade ServiceGroups)"""
        # Créer un groupe avec des ServiceGroups
        group = Group.objects.create(
            code='DEL',
            name='Group to Delete',
            description='Test deletion'
        )
        ServiceGroup.objects.create(service=self.service1, group=group)
        ServiceGroup.objects.create(service=self.service2, group=group)

        # Vérifier que les ServiceGroups existent
        self.assertEqual(group.service_groups.count(), 2)

        # Supprimer le groupe
        response = self.client.delete(f'/api/groups/{group.id}/')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['service_groups_deleted'], 2)

        # Vérifier que le groupe et les ServiceGroups ont été supprimés
        self.assertFalse(Group.objects.filter(code='DEL').exists())
        self.assertEqual(
            ServiceGroup.objects.filter(group__code='DEL').count(),
            0
        )

    def test_refuse_delete_group_with_active_users(self):
        """Test refus suppression Group avec utilisateurs actifs"""
        # Créer un groupe
        group = Group.objects.create(
            code='PROTECTED',
            name='Protected Group',
            description='Group with users'
        )

        # Créer un UserGroup actif
        UserGroup.objects.create(
            user=self.user,
            group=group,
            assigned_by=self.user,
            is_active=True
        )

        # Tenter de supprimer le groupe
        response = self.client.delete(f'/api/groups/{group.id}/')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('utilisateur(s) actif(s)', response.data['error'])

        # Vérifier que le groupe existe toujours
        self.assertTrue(Group.objects.filter(code='PROTECTED').exists())

    def test_expansion_service_groups(self):
        """Test expansion ?expand=service_groups"""
        # Créer un groupe avec des ServiceGroups
        group = Group.objects.create(
            code='EXP',
            name='Expandable Group',
            description='Test expansion'
        )
        ServiceGroup.objects.create(service=self.service1, group=group)
        ServiceGroup.objects.create(service=self.service2, group=group)

        # Récupérer le groupe avec expansion
        response = self.client.get(
            f'/api/groups/{group.id}/?expand=service_groups'
        )

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('service_groups', response.data)
        self.assertEqual(len(response.data['service_groups']), 2)

        # Vérifier que les service_groups sont des objets complets
        # (pas juste des IDs)
        first_sg = response.data['service_groups'][0]
        self.assertIn('service', first_sg)
        self.assertIn('group', first_sg)

    def test_create_group_with_duplicate_service_ids(self):
        """Test création Group avec service_ids en double (doit ignorer)"""
        data = {
            'code': 'DUP',
            'name': 'Duplicate Test',
            'description': 'Test duplicates',
            'is_active': True,
            'service_ids': [self.service1.id, self.service1.id]
        }

        response = self.client.post('/api/groups/', data, format='json')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Vérifier qu'un seul ServiceGroup a été créé
        group = Group.objects.get(code='DUP')
        self.assertEqual(group.service_groups.count(), 1)
        data = {
            'code': 'DUP',
            'name': 'Duplicate Test',
            'description': 'Test duplicates',
            'is_active': True,
            'service_ids': [self.service1.id, self.service1.id]
        }

        response = self.client.post('/api/groups/', data, format='json')

        # Vérifications
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Vérifier qu'un seul ServiceGroup a été créé
        group = Group.objects.get(code='DUP')
        self.assertEqual(group.service_groups.count(), 1)
