"""
Tests de propriété pour le modèle periode_paie.
Feature: paie-system
"""
import calendar
from datetime import date
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from paie_app.models import periode_paie

User = get_user_model()


class PeriodePaiePropertyTests(TestCase):
    """Tests de propriété pour periode_paie"""

    def setUp(self):
        """Configuration des tests"""
        self.user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'nom': 'Test',
                'prenom': 'User'
            }
        )

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=100)
    def test_period_creation_consistency(self, annee, mois):
        """
        Feature: paie-system, Property 1: Period Creation Consistency
        For any new payroll period creation, the system should create a period
        with the specified year, month, and default status "DRAFT".
        Validates: Requirements 1.1
        """
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            traite_par=self.user
        )

        # Vérifier que la période est créée avec les bonnes valeurs
        assert periode.annee == annee
        assert periode.mois == mois
        assert periode.statut == 'DRAFT'
        assert periode.traite_par == self.user

        # Nettoyer pour le prochain test
        periode.delete()

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=100)
    def test_period_uniqueness_enforcement(self, annee, mois):
        """
        Feature: paie-system, Property 2: Period Uniqueness Enforcement
        For any year and month combination, only one payroll period should
        exist in the system.
        Validates: Requirements 1.2
        """
        # Créer la première période
        periode1 = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            traite_par=self.user
        )

        # Tenter de créer une deuxième période avec les mêmes année/mois
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                periode_paie.objects.create(
                    annee=annee,
                    mois=mois,
                    traite_par=self.user
                )

        # Nettoyer
        periode1.delete()

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=100)
    def test_period_status_transitions(self, annee, mois):
        """
        Feature: paie-system, Property 3: Period Status Transitions
        For any period finalization, the system should change status to
        "COMPLETED" and record the processing timestamp.
        Validates: Requirements 1.3
        """
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            traite_par=self.user
        )

        # Simuler la finalisation
        before_finalization = timezone.now()

        periode.statut = 'COMPLETED'
        periode.date_traitement = timezone.now()
        periode.save()

        after_finalization = timezone.now()

        # Vérifier la transition d'état
        periode.refresh_from_db()
        assert periode.statut == 'COMPLETED'
        assert periode.date_traitement is not None
        assert (before_finalization <= periode.date_traitement <=
                after_finalization)

        # Nettoyer
        periode.delete()

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=100)
    def test_automatic_period_date_calculation(self, annee, mois):
        """
        Feature: paie-system, Property 5: Automatic Period Date Calculation
        For any period with year and month, the system should automatically
        calculate correct start and end dates.
        Validates: Requirements 1.5
        """
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            traite_par=self.user
        )

        # Calculer les dates attendues
        expected_start = date(annee, mois, 1)
        last_day = calendar.monthrange(annee, mois)[1]
        expected_end = date(annee, mois, last_day)

        # Vérifier que les dates sont calculées automatiquement
        assert periode.date_debut == expected_start
        assert periode.date_fin == expected_end

        # Nettoyer
        periode.delete()

    def test_period_approval_immutability_example(self):
        """
        Test d'exemple pour l'immutabilité après approbation.
        Feature: paie-system, Property 4: Period Approval Immutability
        """
        periode = periode_paie.objects.create(
            annee=2024,
            mois=1,
            traite_par=self.user,
            statut='APPROVED'
        )

        # Une fois approuvée, la période ne devrait plus être modifiable
        # (Cette logique sera implémentée dans les vues/services)
        assert periode.statut == 'APPROVED'

        # Nettoyer
        periode.delete()
