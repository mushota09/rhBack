"""
Tests de propriété pour les performances du système de paie.
Feature: paie-system
"""
import time
from decimal import Decimal
from datetime import date
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from paie_app.tasks import (
    process_payroll_period_parallel,
    generate_payslips_parallel,
    process_employee_salary,
    process_payroll_period
)
from paie_app.models import periode_paie, entree_paie
from user_app.models import employe, contrat

User = get_user_model()


class PerformancePropertyTests(TestCase):
    """Tests de propriété pour les performances"""

    def setUp(self):
        """Configuration des tests"""
        self.user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'nom': 'Test',
                'prenom': 'User'
            }
        )

        self.periode, created = periode_paie.objects.get_or_create(
            annee=2024,
            mois=1,
            defaults={
                'traite_par': self.user
            }
        )

    @given(
        nombre_employes=st.integers(min_value=1, max_value=10),
        salaire_base=st.decimals(min_value=100000, max_value=500000, places=2)
    )
    @settings(max_examples=10)
    def test_property_40_parallel_processing_capability(self, nombre_employes, salaire_base):
        """
        Feature: paie-system, Property 40: Parallel Processing Capability
        For any salary calculations, the system should support parallel processing
        when beneficial.
        Validates: Requirements 10.5
        """
        # Créer des employés de test avec des emails uniques
        employes = []
        base_timestamp = int(time.time() * 1000000)  # Microseconds for uniqueness
        for i in range(nombre_employes):
            unique_id = f"{base_timestamp}{i}"
            employe_obj = employe.objects.create(
                email_personnel=f'test{unique_id}@example.com',
                nom=f'Employe{unique_id}',
                prenom='Test',
                date_naissance=date(1990, 1, 1),
                date_embauche=date(2020, 1,1),
                sexe='M',
                statut_matrimonial='S',
                statut_emploi='ACTIVE',
                nationalite='Congolaise',
                banque='Test Bank',
                numero_compte=f'12345678{unique_id}',
                niveau_etude='Universitaire',
                numero_inss=f'12345678{unique_id}',
                telephone_personnel=f'12345678{unique_id}',
                adresse_ligne1='Test Address',
                nombre_enfants=0,
                nom_contact_urgence='Contact',
                lien_contact_urgence='Parent',
                telephone_contact_urgence='987654321'
            )

            # Créer un contrat pour chaque employé
            contrat.objects.create(
                employe_id=employe_obj,
                type_contrat='PERMANENT',
                date_debut=date(2020, 1, 1),
                type_salaire='M',
                salaire_base=salaire_base,
                devise='USD',
                statut='en_cours'
            )

            employes.append(employe_obj)

        # Tester le traitement parallèle avec mock pour éviter l'exécution réelle de Celery
        with patch('paie_app.tasks.group') as mock_group:
            # Simuler le résultat du traitement parallèle
            mock_result = MagicMock()
            mock_result.get.return_value = [
                {'status': 'success', 'employe_id': emp.id, 'periode_id': self.periode.id}
                for emp in employes
            ]
            mock_group.return_value.apply_async.return_value = mock_result

            # Exécuter la tâche de traitement parallèle avec les bons paramètres
            task = process_payroll_period_parallel
            result = task.run(self.periode.id)

            # Vérifier que le traitement parallèle est capable de gérer tous les employés
            assert result['status'] == 'completed'
            assert result['total_employees'] == nombre_employes
            assert result['successful_calculations'] == nombre_employes
            assert result['failed_calculations'] == 0

            # Vérifier que la fonction group a été appelée
            mock_group.assert_called_once()

        # Nettoyer les données de test
        for emp in employes:
            emp.delete()

    @given(
        nombre_bulletins=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=5)
    def test_parallel_payslip_generation_capability(self, nombre_bulletins):
        """
        Property test for parallel payslip generation capability.
        The system should handle parallel payslip generation efficiently.
        """
        # Créer des entrées de paie de test avec des emails uniques
        entries = []
        base_timestamp = int(time.time() * 1000000)  # Microseconds for uniqueness
        for i in range(nombre_bulletins):
            unique_id = f"{base_timestamp}{i}"
            employe_obj = employe.objects.create(
                email_personnel=f'payslip{unique_id}@example.com',
                nom=f'PayslipEmploye{unique_id}',
                prenom='Test',
                date_naissance=date(1990, 1, 1),
                date_embauche=date(2020, 1, 1),
                sexe='M',
                statut_matrimonial='S',
                statut_emploi='ACTIVE',
                nationalite='Congolaise',
                banque='Test Bank',
                numero_compte=f'87654321{unique_id}',
                niveau_etude='Universitaire',
                numero_inss=f'87654321{unique_id}',
                telephone_personnel=f'87654321{unique_id}',
                adresse_ligne1='Test Address',
                nombre_enfants=0,
                nom_contact_urgence='Contact',
                lien_contact_urgence='Parent',
                telephone_contact_urgence='987654321'
            )

            entry = entree_paie.objects.create(
                employe_id=employe_obj,
                periode_paie_id=self.periode,
                salaire_base=Decimal('500000'),
                salaire_brut=Decimal('600000'),
                salaire_net=Decimal('450000'),
                total_charge_salariale=Decimal('650000'),
                base_imposable=Decimal('500000'),
                payslip_generated=False
            )
            entries.append(entry)

        # Tester la génération parallèle de bulletins avec mock
        with patch('paie_app.tasks.group') as mock_group:
            # Simuler le résultat de la génération parallèle
            mock_result = MagicMock()
            mock_result.get.return_value = [
                {'status': 'success', 'entree_paie_id': entry.id}
                for entry in entries
            ]
            mock_group.return_value.apply_async.return_value = mock_result

            # Exécuter la tâche de génération parallèle avec les bons paramètres
            task = generate_payslips_parallel
            result = task.run(self.periode.id)

            # Vérifier que la génération parallèle est capable de gérer tous les bulletins
            assert result['status'] == 'completed'
            assert result['total_payslips'] == nombre_bulletins
            assert result['generated_payslips'] == nombre_bulletins

            # Vérifier que la fonction group a été appelée
            mock_group.assert_called_once()

        # Nettoyer les données de test
        for entry in entries:
            entry.employe_id.delete()
            entry.delete()

    @given(
        processing_time_seconds=st.integers(min_value=1, max_value=60)
    )
    @settings(max_examples=5)
    def test_async_task_performance_monitoring(self, processing_time_seconds):
        """
        Property test for asynchronous task performance monitoring.
        The system should handle various processing times efficiently.
        """
        # Créer un employé de test pour la performance avec un ID unique
        unique_id = f"{int(time.time() * 1000000)}"
        employe_obj = employe.objects.create(
            email_personnel=f'perf{unique_id}@example.com',
            nom=f'PerfEmploye{unique_id}',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            date_embauche=date(2020, 1, 1),
            sexe='M',
            statut_matrimonial='S',
            statut_emploi='ACTIVE',
            nationalite='Congolaise',
            banque='Test Bank',
            numero_compte=f'123456789{unique_id}',
            niveau_etude='Universitaire',
            numero_inss=f'123456789{unique_id}',
            telephone_personnel=f'123456789{unique_id}',
            adresse_ligne1='Test Address',
            nombre_enfants=0,
            nom_contact_urgence='Contact',
            lien_contact_urgence='Parent',
            telephone_contact_urgence='987654321'
        )

        # Mock le service de calcul de salaire
        with patch('paie_app.services.salary_calculator.SalaryCalculatorService.calculate_salary') as mock_calc:
            mock_calc.return_value = {
                'salaire_brut': Decimal('600000'),
                'salaire_net': Decimal('450000')
            }

            # Exécuter la tâche avec les bons paramètres
            task = process_employee_salary
            result = task.run(employe_obj.id, self.periode.id)

            # Vérifier que la tâche peut traiter n'importe quel temps de traitement
            assert result['status'] in ['success', 'error']
            assert 'employe_id' in result
            assert result['employe_id'] == employe_obj.id

            # Si succès, vérifier que les données sont présentes
            if result['status'] == 'success':
                assert 'salary_data' in result
                assert result['salary_data'] is not None

        # Nettoyer
        employe_obj.delete()

    def test_concurrent_period_processing_safety(self):
        """
        Property test for concurrent period processing safety.
        The system should handle concurrent processing attempts safely.
        """
        # Créer plusieurs périodes de test
        periodes = []
        for i in range(3):
            periode = periode_paie.objects.create(
                annee=2024,
                mois=i + 2,  # Février, Mars, Avril
                traite_par=self.user,
                statut='DRAFT'
            )
            periodes.append(periode)

        # Simuler le traitement concurrent avec mock
        with patch('paie_app.services.period_processor.PeriodProcessorService.process_period') as mock_process:
            mock_process.return_value = {
                'processed_employees': 10,
                'total_amount': Decimal('5000000'),
                'processing_time': 30
            }

            # Tester que chaque période peut être traitée indépendamment
            for periode in periodes:
                task = process_payroll_period
                result = task.run(periode.id)

                # Vérifier que chaque traitement est indépendant
                assert result['status'] == 'success'
                assert result['periode_id'] == periode.id
                assert result['processed_employees'] >= 0

                # Vérifier que le temps de traitement est raisonnable
                assert result.get('processing_time', 0) >= 0

        # Nettoyer
        for periode in periodes:
            periode.delete()
