"""
Tests basiques pour les services de paie.
Feature: paie-system
"""
from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from paie_app.models import periode_paie, retenue_employe
from user_app.models import employe, contrat

User = get_user_model()


class BasicServicesTests(TestCase):
    """Tests basiques pour vérifier le fonctionnement des services"""

    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create(
            email='test@example.com',
            nom='Test',
            prenom='User'
        )

        self.employe = employe.objects.create(
            email_personnel='employe@example.com',
            nom='Employe',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            date_embauche=date(2020, 1, 1),
            sexe='M',
            statut_matrimonial='S',
            statut_emploi='ACTIVE',
            nationalite='Congolaise',
            banque='Test Bank',
            numero_compte='123456789',
            niveau_etude='Universitaire',
            numero_inss='123456789',
            telephone_personnel='123456789',
            adresse_ligne1='Test Address',
            nombre_enfants=2
        )

    def test_periode_paie_creation(self):
        """Test de création d'une période de paie"""
        periode = periode_paie.objects.create(
            annee=2024,
            mois=1,
            statut='DRAFT',
            traite_par=self.user
        )

        # Vérifier que les dates sont calculées automatiquement
        self.assertEqual(periode.date_debut, date(2024, 1, 1))
        self.assertEqual(periode.date_fin, date(2024, 1, 31))
        self.assertEqual(periode.annee, 2024)
        self.assertEqual(periode.mois, 1)
        self.assertEqual(periode.statut, 'DRAFT')

    def test_retenue_employe_creation(self):
        """Test de création d'une retenue employé"""
        retenue = retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='LOAN',
            description='Test loan',
            montant_mensuel=Decimal('50000'),
            montant_total=Decimal('200000'),
            date_debut=date(2024, 1, 1),
            est_active=True,
            est_recurrente=True,
            cree_par=self.user
        )

        self.assertEqual(retenue.employe_id, self.employe)
        self.assertEqual(retenue.type_retenue, 'LOAN')
        self.assertEqual(retenue.montant_mensuel, Decimal('50000'))
        self.assertEqual(retenue.montant_total, Decimal('200000'))
        self.assertTrue(retenue.est_active)
        self.assertTrue(retenue.est_recurrente)

    def test_contrat_creation(self):
        """Test de création d'un contrat"""
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=Decimal('500000'),
            devise='USD',
            statut='en_cours'
        )

        self.assertEqual(contrat_obj.employe_id, self.employe)
        self.assertEqual(contrat_obj.type_contrat, 'PERMANENT')
        self.assertEqual(contrat_obj.salaire_base, Decimal('500000'))
        self.assertEqual(contrat_obj.statut, 'en_cours')
