"""
Tests de propriété pour PayslipGeneratorService.
Feature: paie-system
"""
import asyncio
from decimal import Decimal
from datetime import date
from hypothesis import given, strategies as st, settings as hypothesis_settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import override_settings

from paie_app.services import PayslipGeneratorService
from paie_app.models import periode_paie, entree_paie
from user_app.models import employe, contrat

User = get_user_model()


class PayslipGeneratorPropertyTests(TestCase):
    """Tests de propriété pour PayslipGeneratorService"""

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

        self.service = PayslipGeneratorService()

    def _create_entree_paie(self, **kwargs):
        """Crée une entrée de paie pour les tests"""
        defaults = {
            'employe_id': self.employe,
            'periode_paie_id': self.periode,
            'salaire_base': Decimal('500000'),
            'indemnite_logement': Decimal('50000'),
            'indemnite_deplacement': Decimal('25000'),
            'indemnite_fonction': Decimal('30000'),
            'allocation_familiale': Decimal('10000'),
            'autres_avantages': Decimal('15000'),
            'salaire_brut': Decimal('630000'),
            'cotisations_patronales': {
                'inss_pension': '27000',
                'inss_risque': '2400',
                'mfp': '15750'
            },
            'cotisations_salariales': {
                'inss': '18000',
                'mfp': '15750'
            },
            'retenues_diverses': {
                'avance_salaire': '50000'
            },
            'total_charge_salariale': Decimal('83750'),
            'base_imposable': Decimal('546250'),
            'salaire_net': Decimal('496250')
        }
        defaults.update(kwargs)
        return entree_paie.objects.create(**defaults)

    @given(
        salaire_base=st.decimals(min_value=100000, max_value=1000000, places=2),
        indemnite_logement=st.decimals(min_value=0, max_value=100000, places=2)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_16_payslip_information_completeness(
        self, salaire_base, indemnite_logement
    ):
        """
        Feature: paie-system, Property 16: Payslip Information Completeness
        For any generated payslip, it should contain all required employee
        and company information.
        Validates: Requirements 4.1
        """
        # Créer une entrée de paie
        entree = self._create_entree_paie(
            salaire_base=salaire_base,
            indemnite_logement=indemnite_logement
        )

        # Préparer les données du bulletin
        payslip_data = asyncio.run(self.service._prepare_payslip_data(entree))

        # Vérifier que les données contiennent les informations requises
        assert 'company' in payslip_data
        assert 'employee' in payslip_data
        assert 'period' in payslip_data
        assert 'salary_components' in payslip_data
        assert 'totals' in payslip_data

        # Vérifier les informations de l'employé
        employee_info = payslip_data['employee']
        assert 'nom_complet' in employee_info
        assert 'email' in employee_info
        assert 'numero_inss' in employee_info

        # Vérifier les informations de la période
        period_info = payslip_data['period']
        assert 'annee' in period_info
        assert 'mois' in period_info

        # Nettoyer
        entree.delete()

    @given(
        salaire_base=st.decimals(min_value=100000, max_value=1000000, places=2),
        indemnite_logement=st.decimals(min_value=0, max_value=100000, places=2),
        allocation_familiale=st.decimals(min_value=0, max_value=30000, places=2)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_17_payslip_salary_component_details(
        self, salaire_base, indemnite_logement, allocation_familiale
    ):
        """
        Feature: paie-system, Property 17: Payslip Salary Component Details
        For any generated payslip, it should detail all gross salary components.
        Validates: Requirements 4.2
        """
        # Calculer le salaire brut
        salaire_brut = salaire_base + indemnite_logement + allocation_familiale

        # Créer une entrée de paie avec les composants donnés
        entree = self._create_entree_paie(
            salaire_base=salaire_base,
            indemnite_logement=indemnite_logement,
            allocation_familiale=allocation_familiale,
            salaire_brut=salaire_brut
        )

        # Préparer les données du bulletin
        payslip_data = asyncio.run(self.service._prepare_payslip_data(entree))

        # Vérifier que les composants du salaire sont présents
        salary_components = payslip_data['salary_components']
        assert salary_components['salaire_base'] == salaire_base
        assert salary_components['indemnite_logement'] == indemnite_logement
        assert salary_components['allocation_familiale'] == allocation_familiale
        assert salary_components['salaire_brut'] == salaire_brut

        # Nettoyer
        entree.delete()

    @given(
        inss_pension=st.decimals(min_value=1000, max_value=27000, places=2),
        inss_employe=st.decimals(min_value=1000, max_value=18000, places=2)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_18_payslip_contribution_details(
        self, inss_pension, inss_employe
    ):
        """
        Feature: paie-system, Property 18: Payslip Contribution Details
        For any generated payslip, it should detail all employer
        and employee contributions.
        Validates: Requirements 4.3
        """
        # Créer une entrée de paie avec les cotisations données
        entree = self._create_entree_paie(
            cotisations_patronales={
                'inss_pension': str(inss_pension),
                'inss_risque': '2400',
                'mfp': '15750'
            },
            cotisations_salariales={
                'inss': str(inss_employe),
                'mfp': '15750'
            }
        )

        # Préparer les données du bulletin
        payslip_data = asyncio.run(self.service._prepare_payslip_data(entree))

        # Vérifier que les cotisations sont présentes dans les données
        contributions = payslip_data['contributions']

        # Vérifier les cotisations patronales
        patronales = contributions['cotisations_patronales']
        assert patronales['inss_pension'] == str(inss_pension)

        # Vérifier les cotisations salariales
        salariales = contributions['cotisations_salariales']
        assert salariales['inss'] == str(inss_employe)

        # Nettoyer
        entree.delete()

    @given(
        avance_salaire=st.decimals(min_value=0, max_value=100000, places=2)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_19_payslip_deduction_details(
        self, avance_salaire
    ):
        """
        Feature: paie-system, Property 19: Payslip Deduction Details
        For any generated payslip, it should detail all applied deductions.
        Validates: Requirements 4.4
        """
        # Créer une entrée de paie avec les retenues données
        retenues_diverses = {}
        if avance_salaire > 0:
            retenues_diverses['avance_salaire'] = str(avance_salaire)

        entree = self._create_entree_paie(
            retenues_diverses=retenues_diverses
        )

        # Préparer les données du bulletin
        payslip_data = asyncio.run(self.service._prepare_payslip_data(entree))

        # Vérifier que les retenues sont présentes dans les données
        contributions = payslip_data['contributions']
        retenues = contributions['retenues_diverses']

        # Vérifier la retenue si elle existe
        if avance_salaire > 0:
            assert 'avance_salaire' in retenues
            assert retenues['avance_salaire'] == str(avance_salaire)
        else:
            # Si aucune retenue, le dictionnaire peut être vide
            assert len(retenues) == 0 or retenues == {}

        # Nettoyer
        entree.delete()

    @given(
        salaire_brut=st.decimals(min_value=200000, max_value=1000000, places=2),
        total_deductions=st.decimals(min_value=50000, max_value=300000, places=2)
    )
    @hypothesis_settings(max_examples=100)
    def test_property_20_payslip_net_salary_display(
        self, salaire_brut, total_deductions
    ):
        """
        Feature: paie-system, Property 20: Payslip Net Salary Display
        For any generated payslip, it should calculate and display
        the correct net salary.
        Validates: Requirements 4.5
        """
        # S'assurer que les déductions ne dépassent pas le salaire brut
        if total_deductions >= salaire_brut:
            total_deductions = salaire_brut * Decimal('0.8')

        # Calculer le salaire net attendu
        salaire_net_expected = salaire_brut - total_deductions

        # Créer une entrée de paie
        entree = self._create_entree_paie(
            salaire_brut=salaire_brut,
            total_charge_salariale=total_deductions,
            salaire_net=salaire_net_expected
        )

        # Préparer les données du bulletin
        payslip_data = asyncio.run(self.service._prepare_payslip_data(entree))

        # Vérifier que les totaux sont corrects dans les données
        totals = payslip_data['totals']
        assert totals['salaire_net'] == salaire_net_expected
        assert totals['total_charge_salariale'] == total_deductions

        # Vérifier la cohérence : salaire net <= salaire brut
        assert salaire_net_expected <= salaire_brut
        assert salaire_net_expected >= Decimal('0')

        # Nettoyer
        entree.delete()
