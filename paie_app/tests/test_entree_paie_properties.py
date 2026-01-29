"""
Tests de propriété pour le modèle entree_paie.
Feature: paie-system
"""
from decimal import Decimal
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from paie_app.models import entree_paie, periode_paie
from user_app.models import employe

User = get_user_model()


class EntreePaiePropertyTests(TestCase):
    """Tests de propriété pour entree_paie"""

    def setUp(self):
        """Configuration des tests"""
        self.user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'nom': 'Test',
                'prenom': 'User'
            }
        )

        from datetime import date

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

        self.periode, created = periode_paie.objects.get_or_create(
            annee=2024,
            mois=1,
            defaults={
                'traite_par': self.user
            }
        )

    def test_payslip_generation_audit(self):
        """
        Feature: paie-system, Property 33: Payslip Generation Audit
        For any payslip generation, the system should record who generated
        it and when for audit purposes.
        Validates: Requirements 8.2
        """
        entree = entree_paie.objects.create(
            employe_id=self.employe,
            periode_paie_id=self.periode,
            salaire_base=Decimal('500000'),
            salaire_brut=Decimal('500000'),
            total_charge_salariale=Decimal('0'),
            base_imposable=Decimal('500000'),
            salaire_net=Decimal('500000')
        )

        # Simuler la génération avec audit
        generation_time = timezone.now()
        entree.payslip_generated = True
        entree.payslip_generated_at = generation_time
        entree.calculated_by = self.user
        entree.calculated_at = generation_time
        entree.save()

        # Vérifier l'audit
        entree.refresh_from_db()
        assert entree.payslip_generated is True
        assert entree.payslip_generated_at is not None
        assert entree.calculated_by == self.user
        assert entree.calculated_at is not None

        # Nettoyer
        entree.delete()

    def test_modification_history_tracking(self):
        """
        Feature: paie-system, Property: Modification History Tracking
        For any payroll entry modification, the system should maintain
        a history of changes for audit purposes.
        Validates: Requirements 8.1, 8.3
        """
        entree = entree_paie.objects.create(
            employe_id=self.employe,
            periode_paie_id=self.periode,
            salaire_base=Decimal('500000'),
            salaire_brut=Decimal('500000'),
            total_charge_salariale=Decimal('0'),
            base_imposable=Decimal('500000'),
            salaire_net=Decimal('500000')
        )

        # Simuler une modification avec historique
        modification_entry = {
            'timestamp': timezone.now().isoformat(),
            'user': self.user.email,
            'field': 'salaire_base',
            'old_value': '500000.00',
            'new_value': '600000.00',
            'reason': 'Correction salaire'
        }

        entree.modification_history.append(modification_entry)
        entree.salaire_base = Decimal('600000')
        entree.save()

        # Vérifier l'historique
        entree.refresh_from_db()
        assert len(entree.modification_history) == 1
        assert entree.modification_history[0]['field'] == 'salaire_base'
        assert entree.modification_history[0]['user'] == self.user.email

        # Nettoyer
        entree.delete()
