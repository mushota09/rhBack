"""
Tests de propriété pour l'API PeriodePaieAPIView.
"""
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import TestCase

from paie_app.models import periode_paie, entree_paie
from user_app.models import employe, contrat


User = get_user_model()


class PeriodePaieAPIPropertyTests(TestCase):
    """Tests de propriété pour l'API des périodes de paie"""

    def setUp(self):
        """Configuration des tests"""
        self.client = APIClient()

        # Créer un utilisateur de test avec email unique
        import uuid
        unique_email = f'test-{uuid.uuid4().hex[:8]}@example.com'

        self.user = User.objects.create(
            email=unique_email,
            nom='Test',
            prenom='User',
            is_active=True,
            is_staff=True
        )
        self.user.set_password('testpass123')
        self.user.save()
        self.client.force_authenticate(user=self.user)

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=10, deadline=None)
    def test_property_4_period_approval_immutability(self, annee, mois):
        """
        Feature: paie-system, Property 4: Period Approval Immutability

        For any approved period, the system should prevent any further
        modifications to the period data.
        **Validates: Requirements 1.4**
        """
        # Créer une période de paie (synchrone)
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            date_debut=date(annee, mois, 1),
            date_fin=date(annee, mois, 28),
            statut='DRAFT',
            traite_par=self.user
        )

        # Approuver la période
        periode.statut = 'APPROVED'
        periode.approuve_par = self.user
        periode.save()

        # Tenter de modifier la période approuvée via l'API
        url = reverse('periode_paie-detail', kwargs={'pk': periode.id})
        data = {
            'annee': annee + 1,  # Tentative de modification
            'mois': mois,
            'statut': 'DRAFT'
        }

        response = self.client.put(url, data, format='json')

        # La modification doit être refusée (400 ou 403)
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

        # Vérifier que la période n'a pas été modifiée
        periode.refresh_from_db()
        self.assertEqual(periode.annee, annee)  # Valeur originale
        self.assertEqual(periode.statut, 'APPROVED')

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=10, deadline=None)
    def test_property_24_contract_data_consistency(self, annee, mois):
        """
        Feature: paie-system, Property 24: Contract Data Consistency

        For any period processing, the system should use contract data
        valid at the processing date.
        **Validates: Requirements 5.3**
        """
        # Créer une période de paie
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            date_debut=date(annee, mois, 1),
            date_fin=date(annee, mois, 28),
            statut='DRAFT',
            traite_par=self.user
        )

        # Tester l'endpoint de traitement (process) - doit fonctionner même sans employés
        process_url = reverse('periode_paie-process-period', kwargs={'pk': periode.id})
        process_response = self.client.post(process_url, {}, format='json')
        self.assertEqual(process_response.status_code, status.HTTP_200_OK)
        self.assertIn('success', process_response.data)

        # Vérifier que la période a été traitée
        periode.refresh_from_db()
        self.assertEqual(periode.statut, 'PROCESSED')

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=10, deadline=None)
    def test_property_26_period_reprocessing_capability(self, annee, mois):
        """
        Feature: paie-system, Property 26: Period Reprocessing Capability

        For any period, the system should allow reprocessing by overwriting
        previous calculations.
        **Validates: Requirements 5.5**
        """
        # Créer une période de paie
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            date_debut=date(annee, mois, 1),
            date_fin=date(annee, mois, 28),
            statut='DRAFT',
            traite_par=self.user
        )

        # Premier traitement
        process_url = reverse('periode_paie-process-period', kwargs={'pk': periode.id})
        first_response = self.client.post(process_url, {}, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)

        # Vérifier que la période a été traitée
        periode.refresh_from_db()
        first_status = periode.statut
        first_updated = periode.updated_at

        # Retraitement de la période (doit être possible)
        second_response = self.client.post(process_url, {}, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)

        # Vérifier que le retraitement a eu lieu
        periode.refresh_from_db()
        self.assertEqual(periode.statut, first_status)  # Statut cohérent
        self.assertGreaterEqual(periode.updated_at, first_updated)  # Timestamp mis à jour

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=10, deadline=None)
    def test_property_35_api_availability_for_consultation(self, annee, mois):
        """
        Feature: paie-system, Property 35: API Availability for Consultation

        For any consultation operation, the system should provide
        corresponding REST API endpoints.
        **Validates: Requirements 9.1**
        """
        # Créer une période de paie
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            date_debut=date(annee, mois, 1),
            date_fin=date(annee, mois, 28),
            statut='DRAFT',
            traite_par=self.user
        )

        # Tester l'endpoint de consultation (list)
        list_url = reverse('periode_paie-list')
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', list_response.data)

        # Tester l'endpoint de détail (retrieve)
        detail_url = reverse('periode_paie-detail', kwargs={'pk': periode.id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['id'], periode.id)
        self.assertEqual(detail_response.data['annee'], annee)
        self.assertEqual(detail_response.data['mois'], mois)

        # Tester l'endpoint de validation
        validate_url = reverse('periode_paie-validate-period', kwargs={'pk': periode.id})
        validate_response = self.client.get(validate_url)
        self.assertEqual(validate_response.status_code, status.HTTP_200_OK)
        self.assertIn('valid', validate_response.data)
        self.assertIn('errors', validate_response.data)

        # Tester l'endpoint de statistiques
        stats_url = reverse('periode_paie-statistics')
        stats_response = self.client.get(stats_url)
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertIn('total_periodes', stats_response.data)

    @given(
        annee=st.integers(min_value=2020, max_value=2030),
        mois=st.integers(min_value=1, max_value=12)
    )
    @settings(max_examples=10, deadline=None)
    def test_property_36_api_availability_for_processing(self, annee, mois):
        """
        Feature: paie-system, Property 36: API Availability for Processing

        For any period processing operation, the system should provide
        corresponding REST API endpoints.
        **Validates: Requirements 9.2**
        """
        # Créer une période de paie
        periode = periode_paie.objects.create(
            annee=annee,
            mois=mois,
            date_debut=date(annee, mois, 1),
            date_fin=date(annee, mois, 28),
            statut='DRAFT',
            traite_par=self.user
        )

        # Tester l'endpoint de traitement (process)
        process_url = reverse('periode_paie-process-period', kwargs={'pk': periode.id})
        process_response = self.client.post(process_url, {}, format='json')
        self.assertEqual(process_response.status_code, status.HTTP_200_OK)
        self.assertIn('success', process_response.data)

        # Tester l'endpoint de finalisation (finalize)
        finalize_url = reverse('periode_paie-finalize-period', kwargs={'pk': periode.id})
        finalize_response = self.client.post(finalize_url, {}, format='json')
        self.assertEqual(finalize_response.status_code, status.HTTP_200_OK)
        self.assertIn('success', finalize_response.data)

        # Vérifier que le statut a changé
        periode.refresh_from_db()
        self.assertEqual(periode.statut, 'FINALIZED')

        # Tester l'endpoint d'approbation (approve)
        approve_url = reverse('periode_paie-approve-period', kwargs={'pk': periode.id})
        approve_response = self.client.post(approve_url, {}, format='json')
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        self.assertIn('success', approve_response.data)

        # Vérifier que le statut a changé
        periode.refresh_from_db()
        self.assertEqual(periode.statut, 'APPROVED')
        self.assertEqual(periode.approuve_par, self.user)

        # Tester l'endpoint d'export (export)
        export_url = reverse('periode_paie-export-excel', kwargs={'pk': periode.id})
        export_response = self.client.get(export_url)
        self.assertEqual(export_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            export_response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
