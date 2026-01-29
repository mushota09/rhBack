"""
Tests pour les APIs de rapports d'audit.
"""
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from user_app.models import employe
from paie_app.models import periode_paie, entree_paie


User = get_user_model()


class AuditReportsAPITest(TestCase):
    """Tests pour les APIs de rapports d'audit"""

    def setUp(self):
        """Configuration des données de test"""
        self.client = APIClient()

        # Créer un utilisateur
        self.user = User.objects.create(
            email='test@example.com',
            nom='Test',
            prenom='User'
        )
        self.client.force_authenticate(user=self.user)

        # Créer un employé
        self.employe = employe.objects.create(
            nom='Doe',
            prenom='John',
            date_naissance='1990-01-01',
            sexe='M',
            statut_matrimonial='S',
            nationalite='Congolaise',
            banque='Test Bank',
            numero_compte='123456789',
            niveau_etude='Universitaire',
            numero_inss='INSS123456',
            email_personnel='john.doe@example.com',
            telephone_personnel='+243123456789',
            adresse_ligne1='123 Test Street',
            ville='Kinshasa',
            province='Kinshasa',
            pays='RDC',
            date_embauche='2020-01-01'
        )

        # Créer une période de paie
        self.periode = periode_paie.objects.create(
            annee=2024,
            mois=1,
            statut='COMPLETED',
            nombre_employes=1,
            masse_salariale_brute=Decimal('1000.00')
        )

        # Créer une entrée de paie
        self.entree = entree_paie.objects.create(
            employe_id=self.employe,
            periode_paie_id=self.periode,
            salaire_base=Decimal('800.00'),
            salaire_brut=Decimal('1000.00'),
            total_charge_salariale=Decimal('200.00'),
            base_imposable=Decimal('800.00'),
            salaire_net=Decimal('750.00')
        )

    def test_period_audit_report_api(self):
        """Test de l'API de rapport d'audit de période"""
        url = reverse('period-audit-report', kwargs={'periode_id': self.periode.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn('periode', data)
        self.assertIn('statistiques', data)
        self.assertEqual(data['periode']['id'], self.periode.id)

    def test_global_statistics_report_api(self):
        """Test de l'API de rapport de statistiques globales"""
        url = reverse('global-statistics-report')
        response = self.client.get(url, {'annee': 2024})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn('annee', data)
        self.assertIn('statistiques_mensuelles', data)
        self.assertEqual(data['annee'], 2024)
