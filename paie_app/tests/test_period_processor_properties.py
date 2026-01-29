"""
Tests de propriété pour PeriodProcessorService.
Feature: paie-system
"""
from decimal import Decimal
from datetime import date
from calendar import monthrange
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import asyncio

from paie_app.services import PeriodProcessorService
from paie_app.models import periode_paie, entree_paie
from user_app.models import employe, contrat

User = get_user_model()


class PeriodProcessorPropertyTests(TestCase):
    """Tests de propriété pour PeriodProcessorService"""

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

        self.service = PeriodProcessorService()

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=10, deadline=None)
    def test_property_5_automatic_period_date_calculation(self, annee, mois):
        """
        Feature: paie-system, Property 5: Automatic Period Date Calculation
        For any period with year and month, the system should automatically
        calculate correct start and end dates.
        Validates: Requirements 1.5
        """
        # Créer une période de façon synchrone pour éviter les problèmes de DB
        from django.db import transaction

        with transaction.atomic():
            # Utiliser la méthode synchrone pour créer la période
            periode = periode_paie.objects.create(
                annee=annee,
                mois=mois,
                statut='DRAFT',
                traite_par=self.user
            )

            # Vérifier les dates calculées automatiquement
            expected_date_debut = date(annee, mois, 1)
            _, last_day = monthrange(annee, mois)
            expected_date_fin = date(annee, mois, last_day)

            assert periode.date_debut == expected_date_debut
            assert periode.date_fin == expected_date_fin
            assert periode.annee == annee
            assert periode.mois == mois
            assert periode.statut == 'DRAFT'

    def test_property_22_batch_processing_coverage(self):
        """
        Feature: paie-system, Property 22: Batch Processing Coverage
        For any period processing, the system should calculate salaries
        for all employees with active contracts.
        Validates: Requirements 5.1
        """
        # Créer une période
        periode = periode_paie.objects.create(
            annee=2024,
            mois=1,
            statut='DRAFT',
            traite_par=self.user
        )

        # Créer un contrat actif pour l'employé
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=Decimal('500000'),
            devise='USD',
            statut='en_cours'
        )

        # Traiter la période de façon asynchrone
        async def run_process():
            return await self.service.process_period(periode.id)

        results = asyncio.run(run_process())

        # Vérifier que l'employé actif a été traité
        assert results['employes_traites'] >= 1
        assert results['total_salaire_brut'] > Decimal('0')
        assert results['total_salaire_net'] > Decimal('0')

        # Vérifier qu'une entrée de paie a été créée
        entree_exists = entree_paie.objects.filter(
            employe_id=self.employe,
            periode_paie_id=periode
        ).exists()
        assert entree_exists is True

    def test_property_23_payroll_entry_creation(self):
        """
        Feature: paie-system, Property 23: Payroll Entry Creation
        For any period processing, the system should create a payroll
        entry for each eligible employee.
        Validates: Requirements 5.2
        """
        # Créer une période
        periode = periode_paie.objects.create(
            annee=2024,
            mois=2,
            statut='DRAFT',
            traite_par=self.user
        )

        # Créer un contrat actif
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=Decimal('600000'),
            devise='USD',
            statut='en_cours'
        )

        # Traiter la période
        async def run_process():
            return await self.service.process_period(periode.id)

        results = asyncio.run(run_process())

        # Vérifier qu'une entrée de paie a été créée
        entree = entree_paie.objects.filter(
            employe_id=self.employe,
            periode_paie_id=periode
        ).first()

        assert entree is not None
        assert entree.salaire_base == Decimal('600000')
        assert entree.salaire_brut > Decimal('0')
        assert entree.salaire_net > Decimal('0')
        assert entree.calculated_at is not None
        assert entree.calculated_by_id == self.user.id
