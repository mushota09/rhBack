"""
Tests unitaires pour le service de rapports d'audit.
"""
from decimal import Decimal
from datetime import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model

from user_app.models import employe
from paie_app.models import periode_paie, entree_paie
from paie_app.services.audit_reports_service import AuditReportsService


User = get_user_model()


class AuditReportsServiceTest(TestCase):
    """Tests pour AuditReportsService"""

    def setUp(self):
        """Configuration des données de test"""
        self.service = AuditReportsService()

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

    def test_generate_period_report(self):
        """Test de génération de rapport de période"""
        report = self.service.generate_period_report(self.periode.id)

        self.assertIn('periode', report)
        self.assertIn('statistiques', report)
        self.assertIn('generated_at', report)

        # Vérifier les données de la période
        periode_data = report['periode']
        self.assertEqual(periode_data['id'], self.periode.id)
        self.assertEqual(periode_data['annee'], 2024)
        self.assertEqual(periode_data['mois'], 1)
        self.assertEqual(periode_data['statut'], 'COMPLETED')

    def test_generate_period_report_not_found(self):
        """Test avec période inexistante"""
        with self.assertRaises(ValueError) as context:
            self.service.generate_period_report(999)

        self.assertIn('Periode 999 non trouvee', str(context.exception))

    def test_generate_employee_history_report(self):
        """Test de génération de rapport d'historique employé"""
        report = self.service.generate_employee_history_report(self.employe.id)

        self.assertIn('employe', report)
        self.assertIn('statistiques', report)
        self.assertIn('generated_at', report)

    def test_generate_global_statistics_report(self):
        """Test de génération de rapport de statistiques globales"""
        report = self.service.generate_global_statistics_report(2024)

        self.assertIn('annee', report)
        self.assertIn('statistiques_mensuelles', report)
        self.assertIn('generated_at', report)

        self.assertEqual(report['annee'], 2024)
