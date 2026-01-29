"""
Tests de propriété pour SalaryCalculatorService.
Feature: paie-system
"""
import asyncio
from decimal import Decimal
from datetime import date
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model

from paie_app.services import SalaryCalculatorService
from paie_app.models import periode_paie
from user_app.models import employe, contrat

User = get_user_model()


class SalaryCalculatorPropertyTests(TestCase):
    """Tests de propriété pour SalaryCalculatorService"""

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

        self.service = SalaryCalculatorService()

    @given(salaire_base=st.decimals(min_value=100000, max_value=2000000, places=2))
    @settings(max_examples=100)
    def test_property_6_base_salary_usage(self, salaire_base):
        """
        Feature: paie-system, Property 6: Base Salary Usage
        For any salary calculation, the system should use the base salary
        from the employee's active contract.
        Validates: Requirements 2.1
        """
        # Créer un contrat avec le salaire de base donné
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=salaire_base,
            devise='USD',
            statut='en_cours'
        )

        # Calculer le salaire brut
        salaire_brut = asyncio.run(
            self.service.calculate_gross_salary(contrat_obj, self.periode)
        )

        # Vérifier que le salaire de base est utilisé dans le calcul
        assert salaire_brut >= salaire_base

        # Le salaire brut doit contenir le salaire de base
        # (plus les indemnités et allocations)
        assert salaire_brut > Decimal('0')

        # Nettoyer
        contrat_obj.delete()

    @given(
        indemnite_logement=st.decimals(min_value=0, max_value=50, places=2),
        indemnite_deplacement=st.decimals(min_value=0, max_value=50, places=2),
        prime_fonction=st.decimals(min_value=0, max_value=50, places=2)
    )
    @settings(max_examples=100)
    def test_property_7_allowance_percentage_application(self, indemnite_logement, indemnite_deplacement, prime_fonction):
        """
        Feature: paie-system, Property 7: Allowance Percentage Application
        For any salary calculation, allowances should be calculated using
        the percentages defined in the employee's contract.
        Validates: Requirements 2.2
        """
        salaire_base = Decimal('500000')

        # Créer un contrat avec les pourcentages donnés
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=salaire_base,
            indemnite_logement=indemnite_logement,
            indemnite_deplacement=indemnite_deplacement,
            prime_fonction=prime_fonction,
            devise='USD',
            statut='en_cours'
        )

        # Calculer le salaire brut
        salaire_brut = asyncio.run(
            self.service.calculate_gross_salary(contrat_obj, self.periode)
        )

        # Calculer les indemnités attendues
        expected_logement = salaire_base * (indemnite_logement / 100)
        expected_deplacement = salaire_base * (indemnite_deplacement / 100)
        expected_fonction = salaire_base * (prime_fonction / 100)

        # Vérifier que les pourcentages sont appliqués correctement
        # Le salaire brut doit inclure ces indemnités
        minimum_expected = salaire_base + expected_logement + expected_deplacement + expected_fonction
        assert salaire_brut >= minimum_expected

        # Nettoyer
        contrat_obj.delete()
    @given(nombre_enfants=st.integers(min_value=0, max_value=10))
    @settings(max_examples=100)
    def test_property_8_family_allowance_progressive_scale(self, nombre_enfants):
        """
        Feature: paie-system, Property 8: Family Allowance Progressive Scale
        For any employee, family allowance should follow the progressive
        scale based on number of children.
        Validates: Requirements 2.3
        """
        # Calculer l'allocation familiale
        allocation = asyncio.run(
            self.service.calculate_family_allowance(nombre_enfants)
        )

        # Vérifier le barème progressif
        if nombre_enfants == 0:
            assert allocation == Decimal('0')
        elif nombre_enfants == 1:
            assert allocation == Decimal('5000')
        elif nombre_enfants == 2:
            assert allocation == Decimal('10000')
        elif nombre_enfants == 3:
            assert allocation == Decimal('15000')
        else:
            # 15000 pour 3 enfants + 3000 par enfant supplémentaire
            expected = Decimal('15000') + (Decimal('3000') * (nombre_enfants - 3))
            assert allocation == expected

        # L'allocation doit toujours être positive ou nulle
        assert allocation >= Decimal('0')
    @given(salaire_brut=st.decimals(min_value=100000, max_value=5000000, places=2))
    @settings(max_examples=100)
    def test_property_9_inss_contribution_caps(self, salaire_brut):
        """
        Feature: paie-system, Property 9: INSS Contribution Caps
        For any salary calculation, INSS contributions should respect
        regulatory caps (pension: 6% max 27000, risk: 6% max 2400).
        Validates: Requirements 2.4
        """
        # Créer un contrat minimal
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=salaire_brut,
            devise='USD',
            statut='en_cours'
        )

        # Calculer les cotisations
        cotisations = asyncio.run(
            self.service.calculate_social_contributions(salaire_brut, contrat_obj)
        )

        # Vérifier les plafonds INSS patronales
        inss_pension = cotisations['patronales']['inss_pension']
        inss_risque = cotisations['patronales']['inss_risque']

        # Vérifier les plafonds INSS salariales
        inss_employe = cotisations['salariales']['inss']

        # Plafonds réglementaires
        assert inss_pension <= Decimal('27000')
        assert inss_risque <= Decimal('2400')
        assert inss_employe <= Decimal('18000')

        # Les cotisations doivent être positives
        assert inss_pension >= Decimal('0')
        assert inss_risque >= Decimal('0')
        assert inss_employe >= Decimal('0')

        # Nettoyer
        contrat_obj.delete()
    @given(base_imposable=st.decimals(min_value=0, max_value=2000000, places=2))
    @settings(max_examples=100)
    def test_property_10_ire_progressive_tax_calculation(self, base_imposable):
        """
        Feature: paie-system, Property 10: IRE Progressive Tax Calculation
        For any taxable income, IRE should be calculated using the
        progressive tax brackets (0%, 20%, 30%).
        Validates: Requirements 2.5
        """
        # Calculer l'IRE
        ire = asyncio.run(self.service.calculate_income_tax(base_imposable))

        # Vérifier les tranches d'imposition
        if base_imposable <= Decimal('150000'):
            assert ire == Decimal('0')
        elif base_imposable <= Decimal('300000'):
            expected_ire = (base_imposable - Decimal('150000')) * Decimal('0.2')
            assert abs(ire - expected_ire) < Decimal('0.01')
        else:
            expected_ire = (base_imposable - Decimal('300000')) * Decimal('0.3') + Decimal('30000')
            assert abs(ire - expected_ire) < Decimal('0.01')

        # L'IRE doit toujours être positive ou nulle
        assert ire >= Decimal('0')

        # L'IRE ne peut pas dépasser la base imposable
        assert ire <= base_imposable
    @given(
        salaire_brut=st.decimals(min_value=200000, max_value=1000000, places=2),
        cotisations_salariales=st.decimals(min_value=10000, max_value=50000, places=2),
        ire=st.decimals(min_value=0, max_value=100000, places=2),
        retenues=st.decimals(min_value=0, max_value=50000, places=2)
    )
    @settings(max_examples=100)
    def test_property_11_net_salary_formula_correctness(self, salaire_brut, cotisations_salariales, ire, retenues):
        """
        Feature: paie-system, Property 11: Net Salary Formula Correctness
        For any salary calculation, the net salary should equal gross salary
        minus all employee contributions, taxes, and deductions.
        Validates: Requirements 2.6
        """
        # Préparer les composants
        components = {
            'salaire_brut': salaire_brut,
            'cotisations': {
                'salariales': {'total': cotisations_salariales}
            },
            'ire': ire,
            'retenues': {'total': retenues}
        }

        # Calculer le salaire net
        salaire_net = asyncio.run(self.service.calculate_net_salary(components))

        # Vérifier la formule
        expected_net = salaire_brut - cotisations_salariales - ire - retenues
        assert abs(salaire_net - expected_net) < Decimal('0.01')

        # Le salaire net doit être cohérent
        assert salaire_net <= salaire_brut

        # Si les déductions sont raisonnables, le salaire net doit être positif
        if (cotisations_salariales + ire + retenues) < salaire_brut:
            assert salaire_net > Decimal('0')
