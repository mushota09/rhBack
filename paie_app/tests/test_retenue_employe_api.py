"""
Tests basiques pour l'API RetenueEmployeAPIView.
"""
from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from paie_app.models import retenue_employe
from user_app.models import employe

User = get_user_model()


class RetenueEmployeAPITests(TestCase):
    """Tests pour l'API des retenues employés"""

    def setUp(self):
        """Configuration des tests"""
        self.client = APIClient()

        # Créer un utilisateur
        self.user = User.objects.create(
            email='test@example.com',
            nom='Test',
            prenom='User'
        )
        self.user.set_password('testpass123')
        self.user.save()

        # Créer un employé
        self.employe = employe.objects.create(
            email_personnel='employe@example.com',
            nom='Employe',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            date_embauche=date(2020, 1, 1),
            sexe='M',
            statut_matrimonial='S',
            statut_emploi='ACTIVE',
            nationalite='Congolaise',
            banque='Test Bank',
            numero_compte='123456789',
            niveau_etude='Universitaire',
            numero_inss='123456789',
            telephone_personnel='123456789',
            adresse_ligne1='Test Address'
        )

        # Authentifier l'utilisateur
        self.client.force_authenticate(user=self.user)

    def test_create_retenue_success(self):
        """Test de création d'une retenue avec succès"""
        data = {
            'employe_id': self.employe.id,
            'type_retenue': 'LOAN',
            'description': 'Remboursement prêt personnel',
            'montant_mensuel': '50000.00',
            'montant_total': '600000.00',
            'date_debut': '2024-01-01',
            'est_recurrente': True
        }

        response = self.client.post('/retenue_employe/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(retenue_employe.objects.count(), 1)

        retenue = retenue_employe.objects.first()
        self.assertEqual(retenue.employe_id, self.employe)
        self.assertEqual(retenue.type_retenue, 'LOAN')
        self.assertEqual(retenue.cree_par, self.user)

    def test_list_retenues(self):
        """Test de listage des retenues"""
        # Créer quelques retenues
        retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='LOAN',
            description='Prêt 1',
            montant_mensuel=Decimal('30000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='ADVANCE',
            description='Avance salaire',
            montant_mensuel=Decimal('20000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        response = self.client.get('/retenue_employe/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_deactivate_retenue(self):
        """Test de désactivation d'une retenue"""
        retenue = retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='LOAN',
            description='Prêt à désactiver',
            montant_mensuel=Decimal('25000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        data = {'raison': 'Remboursement anticipé'}
        response = self.client.post(
            f'/retenue_employe/{retenue.id}/deactivate/',
            data
        )

        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Vérifier que la retenue est désactivée
        retenue.refresh_from_db()
        self.assertFalse(retenue.est_active)

    def test_get_retenue_history(self):
        """Test de consultation de l'historique d'une retenue"""
        retenue = retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='ADVANCE',
            description='Avance sur salaire',
            montant_mensuel=Decimal('40000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        response = self.client.get(f'/retenue_employe/{retenue.id}/history/')

        if response.status_code != status.HTTP_200_OK:
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('retenue_id', response.data)
        self.assertIn('employe', response.data)
        self.assertIn('creation', response.data)
        self.assertIn('etat_actuel', response.data)

    def test_get_statistics(self):
        """Test de récupération des statistiques"""
        # Créer quelques retenues
        retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='LOAN',
            description='Prêt 1',
            montant_mensuel=Decimal('30000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        retenue_employe.objects.create(
            employe_id=self.employe,
            type_retenue='LOAN',
            description='Prêt 2',
            montant_mensuel=Decimal('20000'),
            date_debut=date.today(),
            cree_par=self.user
        )

        response = self.client.get('/retenue_employe/statistics/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_retenues', response.data)
        self.assertIn('retenues_actives', response.data)
        self.assertIn('repartition_par_type', response.data)
        self.assertEqual(response.data['total_retenues'], 2)
        self.assertEqual(response.data['retenues_actives'], 2)
