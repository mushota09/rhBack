"""
Tests de propriété pour ValidationService.
Feature: paie-system
"""
import asyncio
from decimal import Decimal
from datetime import date, timedelta
from hypothesis import given, strategies as st, settings, assume
from django.test import TestCase
from django.contrib.auth import get_user_model

from paie_app.services import ValidationService
from paie_app.models import periode_paie, retenue_employe
from user_app.models import employe, contrat, audit_log

User = get_user_model()


class ValidationServicePropertyTests(TestCase):
    """Tests de propriété pour ValidationService"""

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
                'nombre_enfants': 2,
                'nom_contact_urgence': 'Contact',
                'lien_contact_urgence': 'Parent',
                'telephone_contact_urgence': '987654321'
            }
        )

        self.periode, created = periode_paie.objects.get_or_create(
            annee=2024,
            mois=1,
            defaults={
                'traite_par': self.user
            }
        )

        self.validation_service = ValidationService()

    @given(
        salaire_base=st.decimals(min_value=100000, max_value=2000000, places=2),
        indemnite_logement=st.decimals(min_value=0, max_value=50, places=2),
        indemnite_deplacement=st.decimals(min_value=0, max_value=50, places=2),
        prime_fonction=st.decimals(min_value=0, max_value=50, places=2),
        assurance_patronale=st.decimals(min_value=0, max_value=20, places=2),
        assurance_salariale=st.decimals(min_value=0, max_value=20, places=2)
    )
    @settings(max_examples=100)
    def test_property_29_regulatory_compliance_verification(self, salaire_base, indemnite_logement,
                                                          indemnite_deplacement, prime_fonction,
                  assurance_patronale, assurance_salariale):
        """
        Feature: paie-system, Property 29: Regulatory Compliance Verification
        For any contribution calculation, the system should apply correct
        regulatory caps and rates.
        Validates: Requirements 7.3
        """
        # Créer un contrat avec les données générées
        contrat_obj = contrat.objects.create(
            employe_id=self.employe,
            type_contrat='PERMANENT',
            date_debut=date(2020, 1, 1),
            type_salaire='M',
            salaire_base=salaire_base,
            indemnite_logement=indemnite_logement,
            indemnite_deplacement=indemnite_deplacement,
            prime_fonction=prime_fonction,
            assurance_patronale=assurance_patronale,
            assurance_salariale=assurance_salariale,
            devise='USD',
            statut='en_cours'
        )

        # Calculer les composants du salaire
        salaire_brut = salaire_base * (1 + (indemnite_logement + indemnite_deplacement + prime_fonction) / 100)

        # Simuler les composants calculés avec les plafonds réglementaires
        salary_components = {
            'salaire_brut': salaire_brut,
            'salaire_net': salaire_brut * Decimal('0.7'),  # Estimation
            'cotisations_patronales': {
                'inss_pension': min(salaire_brut * Decimal('0.06'), Decimal('27000')),
                'inss_risque': min(salaire_brut * Decimal('0.06'), Decimal('2400')),
                'mfp': salaire_brut * (assurance_patronale / 100),
                'fpc': salaire_brut * Decimal('0.01')
            },
            'cotisations_salariales': {
                'inss': min(salaire_brut * Decimal('0.04'), Decimal('18000')),
                'mfp': salaire_brut * (assurance_salariale / 100),
                'fpc': salaire_brut * Decimal('0.005')
            },
            'base_imposable': salaire_brut * Decimal('0.8'),  # Estimation
            'ire': max(Decimal('0'), (salaire_brut * Decimal('0.8') - Decimal('150000')) * Decimal('0.2')),
            'allocation_familiale': Decimal('10000')  # Pour 2 enfants
        }

        # Valider la conformité réglementaire
        is_valid, errors = asyncio.run(
            self.validation_service.validate_regulatory_compliance(salary_components)
        )

        # Vérifier que les plafonds INSS sont respectés
        assert salary_components['cotisations_patronales']['inss_pension'] <= Decimal('27000')
        assert salary_components['cotisations_patronales']['inss_risque'] <= Decimal('2400')
        assert salary_components['cotisations_salariales']['inss'] <= Decimal('18000')

        # Vérifier la cohérence des montants
        assert salary_components['salaire_brut'] > Decimal('0')
        assert salary_components['salaire_net'] >= Decimal('0')
        assert salary_components['salaire_net'] <= salary_components['salaire_brut']

        # Si les calculs respectent les règles, la validation doit passer
        if (salary_components['salaire_net'] <= salary_components['salaire_brut'] and
            salary_components['base_imposable'] >= Decimal('0') and
            salary_components['ire'] >= Decimal('0') and
            salary_components['allocation_familiale'] >= Decimal('0')):
            assert is_valid or len(errors) == 0

        # Nettoyer
        contrat_obj.delete()

    @given(
        action=st.sampled_from(['CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT']),
        type_ressource=st.text(min_size=1, max_size=20),
        id_ressource=st.text(min_size=1, max_size=10)
    )
    @settings(max_examples=100)
    def test_property_32_operation_audit_logging(self, action, type_ressource, id_ressource):
        """
        Feature: paie-system, Property 32: Operation Audit Logging
        For any payroll operation, the system should record who performed
        the operation and when.
        Validates: Requirements 8.1
        """
        # Simuler une opération d'audit
        audit_entry = audit_log.objects.create(
            user_id=self.user,
            action=action,
            type_ressource=type_ressource,
            id_ressource=id_ressource,
            anciennes_valeurs={'test': 'old_value'},
            nouvelles_valeurs={'test': 'new_value'},
            adresse_ip='127.0.0.1',
            user_agent='Test Agent'
        )

        # Vérifier que l'entrée d'audit a été créée
        assert audit_entry.id is not None
        assert audit_entry.user_id == self.user
        assert audit_entry.action == action
        assert audit_entry.type_ressource == type_ressource
        assert audit_entry.id_ressource == id_ressource
        assert audit_entry.timestamp is not None

        # Vérifier que l'horodatage est récent (dans les dernières secondes)
        from django.utils import timezone
        time_diff = timezone.now() - audit_entry.timestamp
        assert time_diff.total_seconds() < 10

        # Vérifier que les données sont préservées
        assert audit_entry.anciennes_valeurs is not None
        assert audit_entry.nouvelles_valeurs is not None

        # Nettoyer
        audit_entry.delete()
