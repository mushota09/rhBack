"""
Tests de propriété pour DeductionManagerService.
Feature: paie-system
"""
import asyncio
from decimal import Decimal
from datetime import date, timedelta
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model

from paie_app.services import DeductionManagerService
from paie_app.models import periode_paie, retenue_employe
from user_app.models import employe

User = get_user_model()


class DeductionManagerPropertyTests(TestCase):
    """Tests de propriété pour DeductionManagerService"""

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
                'adresse_ligne1': 'Test Address',
                'nombre_enfants': 2
            }
        )

        self.periode, created = periode_paie.objects.get_or_create(
            annee=2024,
            mois=1,
            defaults={
                'traite_par': self.user
            }
        )

        self.service = DeductionManagerService()
    @given(
        montant_mensuel=st.decimals(min_value=1000, max_value=100000, places=2),
        montant_total=st.decimals(min_value=5000, max_value=500000, places=2)
    )
    @settings(max_examples=100)
    def test_property_13_recurring_deduction_application(self, montant_mensuel, montant_total):
        """
        Feature: paie-system, Property 13: Recurring Deduction Application
        For any recurring deduction, the system should apply it automatically
        each month until the end date.
        Validates: Requirements 3.2
        """
        # S'assurer que le montant total est supérieur au montant mensuel
        if montant_total <= montant_mensuel:
            montant_total = montant_mensuel * 3

        # Créer une retenue récurrente
        retenue_data = {
            'employe_id': self.employe.id,
            'type_retenue': 'PRET',
            'description': 'Test recurring deduction',
            'montant_mensuel': montant_mensuel,
            'montant_total': montant_total,
            'date_debut': date(2024, 1, 1),
            'est_recurrente': True,
            'cree_par': self.user.id
        }

        # Créer la retenue
        retenue = asyncio.run(self.service.create_deduction(retenue_data))

        # Vérifier que la retenue est créée comme récurrente
        assert retenue.est_recurrente is True
        assert retenue.est_active is True
        assert retenue.montant_mensuel == montant_mensuel
        assert retenue.montant_total == montant_total

        # Appliquer la retenue pour plusieurs périodes
        montant_applique = asyncio.run(self.service.apply_deduction(retenue, self.periode))

        # Le montant appliqué doit être le montant mensuel (ou le restant si moins)
        expected_montant = min(montant_mensuel, montant_total)
        assert montant_applique == expected_montant

        # Nettoyer
        asyncio.run(retenue.adelete())
    @given(
        montant_mensuel=st.decimals(min_value=1000, max_value=50000, places=2),
        jours_avant_periode=st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100)
    def test_property_15_active_deductions_inclusion(self, montant_mensuel, jours_avant_periode):
        """
        Feature: paie-system, Property 15: Active Deductions Inclusion
        For any salary calculation, the system should include all active
        deductions for the period.
        Validates: Requirements 3.4
        """
        # Créer une date de début avant la période
        date_debut = date(2024, 1, 1) - timedelta(days=jours_avant_periode)

        # Créer une retenue active
        retenue_data = {
            'employe_id': self.employe.id,
            'type_retenue': 'AVANCE',
            'description': 'Test active deduction',
            'montant_mensuel': montant_mensuel,
            'date_debut': date_debut,
            'est_active': True,
            'cree_par': self.user.id
        }

        # Créer la retenue
        retenue = asyncio.run(self.service.create_deduction(retenue_data))

        # Récupérer les retenues actives pour la période
        retenues_actives = asyncio.run(
            self.service.get_active_deductions(self.employe.id, self.periode)
        )

        # Vérifier que la retenue est incluse
        retenue_ids = [r.id for r in retenues_actives]
        assert retenue.id in retenue_ids

        # Vérifier que toutes les retenues retournées sont actives
        for r in retenues_actives:
            assert r.est_active is True
            assert r.date_debut <= date(self.periode.annee, self.periode.mois, 1)

        # Nettoyer
        asyncio.run(retenue.adelete())
    @given(
        montant_mensuel=st.decimals(min_value=1000, max_value=50000, places=2),
        montant_total=st.decimals(min_value=5000, max_value=200000, places=2)
    )
    @settings(max_examples=100)
    def test_property_28_deduction_validity_verification(self, montant_mensuel, montant_total):
        """
        Feature: paie-system, Property 28: Deduction Validity Verification
        For any deduction application, the system should verify the deduction
        is active and within its validity period.
        Validates: Requirements 7.2
        """
        # S'assurer que le montant total est supérieur au montant mensuel
        if montant_total <= montant_mensuel:
            montant_total = montant_mensuel * 3

        # Créer une retenue avec une date de fin
        date_fin = date(2024, 12, 31)
        retenue_data = {
            'employe_id': self.employe.id,
            'type_retenue': 'COTISATION',
            'description': 'Test validity verification',
            'montant_mensuel': montant_mensuel,
            'montant_total': montant_total,
            'date_debut': date(2024, 1, 1),
            'date_fin': date_fin,
            'est_active': True,
            'cree_par': self.user.id
        }

        # Créer la retenue
        retenue = asyncio.run(self.service.create_deduction(retenue_data))

        # Vérifier que la retenue est valide pour la période
        retenues_actives = asyncio.run(
            self.service.get_active_deductions(self.employe.id, self.periode)
        )

        retenue_ids = [r.id for r in retenues_actives]
        assert retenue.id in retenue_ids

        # Désactiver la retenue
        retenue.est_active = False
        asyncio.run(retenue.asave())

        # Vérifier que la retenue désactivée n'est plus incluse
        retenues_actives_apres = asyncio.run(
            self.service.get_active_deductions(self.employe.id, self.periode)
        )

        retenue_ids_apres = [r.id for r in retenues_actives_apres]
        assert retenue.id not in retenue_ids_apres

        # Nettoyer
        asyncio.run(retenue.adelete())
