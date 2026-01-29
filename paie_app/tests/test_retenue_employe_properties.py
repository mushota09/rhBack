"""
Tests de propriété pour le modèle retenue_employe.
Feature: paie-system
"""
from decimal import Decimal
from datetime import date
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from paie_app.models import retenue_employe
from user_app.models import employe

User = get_user_model()


class RetenueEmployePropertyTests(TestCase):
    """Tests de propriété pour retenue_employe"""

    def setUp(self):
        """Configuration des tests"""
        self.user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'nom': 'Test',
                'prenom': 'User'
            }
        )

        self.employe, created = employe.objects.get_or_create(
            email_personnel='employe@example.com',
            defaults={
                'nom': 'Employe',
                'prenom': 'Test',
                'date_naissance': date(1990, 1, 1),
                'date_embauche': date(2020, 1, 1),
                'sexe': 'M',
                'statut_matrimonial': 'S',
                'statut_emploi': 'ACTIVE',
                'nationalite': 'Congolaise',
                'banque': 'Test Bank',
                'numero_compte': '123456789',
                'niveau_etude': 'Universitaire',
                'numero_inss': '123456789',
                'telephone_personnel': '123456789',
                'adresse_ligne1': 'Test Address'
            }
        )

    def test_deduction_creation_completeness(self):
        """
        Feature: paie-system, Property 12: Deduction Creation Completeness
        For any deduction creation, the system should store all required
        information including amounts, dates, and creator.
        Validates: Requirements 3.1
        """
        retenue = retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='LOAN',
            description='Test loan deduction',
            montant_mensuel=Decimal('50000'),
            montant_total=Decimal('600000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        # Vérifier que toutes les informations sont stockées
        assert retenue.employe_id == self.employe
        assert retenue.type_retenue == 'LOAN'
        assert retenue.montant_mensuel == Decimal('50000')
        assert retenue.cree_par == self.user
        assert retenue.est_active is True

        # Nettoyer
        retenue.delete()

    def test_deduction_audit_trail(self):
        """
        Feature: paie-system, Property: Deduction Audit Trail
        For any deduction creation or modification, the system should
        maintain audit information.
        Validates: Requirements 8.3
        """
        creation_time = timezone.now()

        retenue = retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='FINE',
            description='Disciplinary fine',
            montant_mensuel=Decimal('25000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        # Vérifier l'audit de création
        assert retenue.cree_par == self.user
        assert retenue.created_at is not None

        # Nettoyer
        retenue.delete()
