# -*- coding: utf-8 -*-
"""Tests unitaires pour le module Employe avec ServiceGroup et UserGroup"""
import pytest
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from user_app.models import employe, service, Group, ServiceGroup, UserGroup

User = get_user_model()


def get_complete_employe_data(overrides=None):
    data = {
        'nom': 'Dupont',
        'prenom': 'Jean',
        'email_personnel': 'jean.dupont@example.com',
        'date_naissance': '1990-01-15',
        'sexe': 'M',
        'statut_matrimonial': 'S',
        'nationalite': 'Congolaise',
        'banque': 'Banque Test',
        'numero_compte': '123456789',
        'niveau_etude': 'Licence',
        'numero_inss': 'INSS123456',
        'telephone_personnel': '+243999999999',
        'adresse_ligne1': '123 Rue Test',
        'date_embauche': '2024-01-01',
        'nom_contact_urgence': 'Contact Test',
        'lien_contact_urgence': 'Frère',
        'telephone_contact_urgence': '+243888888888',
        'password': 'testpass123'
    }
    if overrides:
        data.update(overrides)
    return data


@pytest.mark.django_db
class TestEmployeWithServiceGroup(TestCase):
    """Tests pour Employe avec ServiceGroup"""

    def setUp(self):
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

    def test_create_employe_with_service_group(self):
        """Test création employé avec poste_id"""
        employe_data = get_complete_employe_data({
            'poste_id': self.service_group.id
        })
        response = self.client.post('/api/employees/', employe_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['poste_id'], self.service_group.id)

    def test_create_employe_with_group_id(self):
        """Test création employé avec group_id"""
        employe_data = get_complete_employe_data({
            'email_personnel': 'sophie.martin@example.com',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'poste_id': self.service_group.id,
            'group_id': self.group.id
        })
        response = self.client.post('/api/employees/', employe_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        # Vérifier que UserGroup a été créé
        created_user = User.objects.get(email=employe_data['email_personnel'])
        user_groups = UserGroup.objects.filter(user=created_user, group=self.group)
        self.assertEqual(user_groups.count(), 1)
        self.assertEqual(user_groups.first().assigned_by, self.user)

    def test_create_employe_without_group_id(self):
        """Test création employé sans group_id"""
        employe_data = get_complete_employe_data({
            'email_personnel': 'paul.bernard@example.com',
            'nom': 'Bernard',
            'prenom': 'Paul',
            'poste_id': self.service_group.id
        })
        response = self.client.post('/api/employees/', employe_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        # Vérifier qu'aucun UserGroup n'a été créé
        created_user = User.objects.get(email=employe_data['email_personnel'])
        user_groups = UserGroup.objects.filter(user=created_user)
        self.assertEqual(user_groups.count(), 0)

    def test_expand_poste_service_group(self):
        """Test expansion ?expand=poste_id.service,poste_id.group"""
        employe_data = get_complete_employe_data({
            'email_personnel': 'marie.durand@example.com',
            'nom': 'Durand',
            'prenom': 'Marie',
            'poste_id': self.service_group.id
        })
        response = self.client.post('/api/employees/', employe_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employe_id = response.data['id']

        # Test expansion
        response = self.client.get(f'/api/employees/{employe_id}/?expand=poste_id.service,poste_id.group')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('poste_id', response.data)
        self.assertIsInstance(response.data['poste_id'], dict)
        self.assertIn('service', response.data['poste_id'])
        self.assertIsInstance(response.data['poste_id']['service'], dict)
        self.assertEqual(response.data['poste_id']['service']['titre'], 'Service IT')
        self.assertIn('group', response.data['poste_id'])
        self.assertIsInstance(response.data['poste_id']['group'], dict)
        self.assertEqual(response.data['poste_id']['group']['code'], 'DEV')

    def test_expand_user_account_user_groups(self):
        """Test expansion ?expand=user_account.user_groups"""
        employe_data = get_complete_employe_data({
            'email_personnel': 'luc.petit@example.com',
            'nom': 'Petit',
            'prenom': 'Luc',
            'poste_id': self.service_group.id,
            'group_id': self.group.id
        })
        response = self.client.post('/api/employees/', employe_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employe_id = response.data['id']

        # Test expansion
        response = self.client.get(f'/api/employees/{employe_id}/?expand=user_account.user_groups')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_account', response.data)
        self.assertIsInstance(response.data['user_account'], dict)
        self.assertIn('user_groups', response.data['user_account'])
        self.assertIsInstance(response.data['user_account']['user_groups'], list)
        self.assertGreater(len(response.data['user_account']['user_groups']), 0)
