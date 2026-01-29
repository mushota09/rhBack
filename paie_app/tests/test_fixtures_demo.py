"""
Tests de démonstration pour les fixtures du système de paie.
Montre comment utiliser les différents types de fixtures créées.
"""
from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from paie_app.fixtures.test_utils import (
    FixtureTestCase, PropertyTestCase, FixtureDataMixin,
    get_test_user, create_simple_employe_with_contrat
)
from paie_app.models import periode_paie, retenue_employe
from user_app.models import employe, contrat

User = get_user_model()


class BaseFixturesTest(FixtureTestCase):
    """Tests utilisant les fixtures de base"""

    def test_fixtures_loaded_correctly(self):
        """Vérifie que toutes les fixtures sont chargées correctement"""
        # Vérifier les utilisateurs
        self.assertEqual(len(self.fixture_data['users']), 4)
        admin_user = self.get_user('admin@company.com')
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.is_superuser)

        # Vérifier les services
        self.assertEqual(len(self.fixture_data['services']), 6)
        self.assertIn('DG', self.fixture_data['services'])
        self.assertIn('RH', self.fixture_data['services'])

        # Vérifier les employés
        self.assertEqual(len(self.fixture_data['employes']), 10)
        directeur = self.get_employe('EMP001')
        self.assertIsNotNone(directeur)
        self.assertEqual(directeur.nom, 'Mukendi')
        self.assertEqual(directeur.statut_emploi, 'ACTIVE')

        # Vérifier les contrats
        self.assertEqual(len(self.fixture_data['contrats']), 10)
        contrat_directeur = self.get_contrat('EMP001')
        self.assertIsNotNone(contrat_directeur)
        self.assertEqual(contrat_directeur.salaire_base, Decimal('2000000'))

        # Vérifier les périodes
        self.assertEqual(len(self.fixture_data['periodes']), 5)
        periode_jan = self.get_periode(2024, 1)
        self.assertIsNotNone(periode_jan)
        self.assertEqual(periode_jan.statut, 'APPROVED')

        # Vérifier les retenues
        self.assertEqual(len(self.fixture_data['retenues']), 10)
        retenues_directeur = self.get_retenues_employe('EMP001')
        self.assertEqual(len(retenues_directeur), 1)
        self.assertEqual(retenues_directeur[0].type_retenue, 'LOAN')

    def test_employes_actifs(self):
        """Test de récupération des employés actifs"""
        employes_actifs = self.get_active_employes()
        self.assertEqual(len(employes_actifs), 9)  # 10 - 1 suspendu

        for emp in employes_actifs:
            self.assertEqual(emp.statut_emploi, 'ACTIVE')

    def test_employes_avec_retenues(self):
        """Test de récupération des employés avec retenues"""
        employes_avec_retenues = self.get_employes_with_retenues()
        self.assertEqual(len(employes_avec_retenues), 9)  # 9 employés ont des retenues

    def test_calcul_allocation_familiale(self):
        """Test du calcul d'allocation familiale avec les fixtures"""
        # Employé avec 3 enfants
        emp_3_enfants = self.get_employe('EMP001')
        contrat_3_enfants = self.get_contrat('EMP001')
        self.assertEqual(emp_3_enfants.nombre_enfants, 3)
        allocation = contrat_3_enfants.calcul_allocation_familiale()
        self.assertEqual(allocation, 15000)

        # Employé avec 5 enfants
        emp_5_enfants = self.get_employe('EMP005')
        contrat_5_enfants = self.get_contrat('EMP005')
        self.assertEqual(emp_5_enfants.nombre_enfants, 5)
        allocation = contrat_5_enfants.calcul_allocation_familiale()
        self.assertEqual(allocation, 21000)  # 15000 + (5-3)*3000

    def test_retenues_par_type(self):
        """Test de classification des retenues par type"""
        types_retenues = {}
        for retenue in self.fixture_data['retenues'].values():
            type_ret = retenue.type_retenue
            types_retenues[type_ret] = types_retenues.get(type_ret, 0) + 1

        # Vérifier qu'on a différents types
        self.assertIn('LOAN', types_retenues)
        self.assertIn('ADVANCE', types_retenues)
        self.assertIn('INSURANCE', types_retenues)
        self.assertIn('UNION', types_retenues)
        self.assertIn('FINE', types_retenues)
        self.assertIn('OTHER', types_retenues)


class PropertyTestFixturesTest(PropertyTestCase):
    """Tests utilisant les fixtures pour tests de propriété"""

    def test_random_dataset_creation(self):
        """Test de création d'un jeu de données aléatoire"""
        dataset = self.create_random_dataset(num_employes=5, num_retenues_per_employe=2)

        # Vérifier la structure
        self.assertIn('user', dataset)
        self.assertIn('employes', dataset)
        self.assertIn('contrats', dataset)
        self.assertIn('retenues', dataset)
        self.assertIn('periodes', dataset)

        # Vérifier les quantités
        self.assertEqual(len(dataset['employes']), 5)
        self.assertEqual(len(dataset['contrats']), 5)
        self.assertLessEqual(len(dataset['retenues']), 10)  # Max 2 par employé

        # Vérifier la cohérence des données
        for employe_obj in dataset['employes']:
            self.assertIsNotNone(employe_obj.matricule)
            self.assertIn(employe_obj.sex
e, ['M', 'F'])
            self.assertGreaterEqual(employe_obj.nombre_enfants, 0)
            self.assertLessEqual(employe_obj.nombre_enfants, 6)

        for contrat_obj in dataset['contrats']:
            self.assertGreater(contrat_obj.salaire_base, 0)
            self.assertIn(contrat_obj.type_contrat, ['PERMANENT', 'TEMPORARY', 'CONSULTANT'])

    def test_minimal_dataset(self):
        """Test de création d'un jeu de données minimal"""
        dataset = self.create_minimal_dataset()

        self.assertEqual(len(dataset['employes']), 3)
        self.assertEqual(len(dataset['contrats']), 3)
        self.assertLessEqual(len(dataset['retenues']), 3)

    def test_large_dataset(self):
        """Test de création d'un jeu de données volumineux"""
        dataset = self.create_large_dataset()

        self.assertEqual(len(dataset['employes']), 50)
        self.assertEqual(len(dataset['contrats']), 50)
        self.assertLessEqual(len(dataset['retenues']), 150)  # Max 3 par employé

    def test_data_consistency(self):
        """Test de cohérence des données générées aléatoirement"""
        dataset = s
at_obj in dataset['contrats']:
            # Vérifier que le contrat commence à la date d'embauche
            self.assertEqual(contrat_obj.date_debut, contrat_obj.employe_id.date_embauche)

            # Vérifier les pourcentages d'indemnités
            self.assertGreaterEqual(contrat_obj.indemnite_logement, 0)
            self.assertLessEqual(contrat_obj.indemnite_logement, 30)


class UtilityFunctionsTest(TestCase, FixtureDataMixin):
    """Tests des fonctions utilitaires"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Charger quelques fixtures pour les tests
        from paie_app.fixtures.base_fixtures import BaseFixtures
        fixtures = BaseFixtures()
        fixtures.create_all_fixtures()

    def test_get_test_user(self):
        """Test de création d'utilisateur de test simple"""
        user = get_test_user()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.nom, 'Test')

        # Vérifier qu'on récupère le même utilisateur
        user2 = get_test_user()
        self.assertEqual(user.id, user2.id)

    def test_create_simple_employe_with_contrat(self):
        """Test de création d'employé simple avec contrat"""
        employe_obj, contrat_obj = create_simple_employe_with_contrat()

        self.assertIsNotNone(employe_obj)
        self.assertIsNotNone(contrat_obj)
        self.assertEqual(contrat_obj.employe_id, employe_obj)
        self.assertEqual(employe_obj.matricule, 'TEST001')
        self.assertEqual(contrat_obj.salaire_base, Decimal('500000'))

    def test_fixture_data_mixin_methods(self):
        """Test des méthodes du mixin FixtureDataMixin"""
        # Test des échantillons
        employes = self.get_sample_employes(3)
        self.assertLessEqual(len(employes), 3)

        contrats = self.get_sample_contrats(3)
ues = self.get_employe_with_retenues()
        if emp_with_retenues:
            retenues_count = retenue_employe.objects.filter(
                employe_id=emp_with_retenues,
                est_active=True
            ).count()
            self.assertGreater(retenues_count, 0)


class FixturesIntegrationTest(TestCase):
    """Tests d'intégration des fixtures avec les services"""

    def setUp(self):
        """Configuration des tests d'intégration"""
        from paie_app.fixtures.base_fixtures import BaseFixtures
        fixtures = BaseFixtures()
        self.fixture_data = fixtures.create_all_fixtures()

    def test_salary_calculation_with_fixtures(self):
        """Test de calcul de salaire avec les données de fixtures"""
        # Prendre un employé avec contrat
        employe_obj = list(self.fixture_data['employes'].values())[0]
        contrat_obj = list(self.fixture_data['contrats'].values())[0]

        # Calculer les composants du salaire
        composants = contrat_obj.calcul_composants_salaire()

        # Vérifier que tous les composants sont présents
        required_keys = [
            'salaire_brut', 'salaire_net', 'base_imposable',
            'ire', 'inss_employe', 'mfp_employe'
        ]
        for key in required_keys:
            self.assertIn(key, com
       emp for emp in self.fixture_data['employes'].values()
            if emp.statut_emploi == 'ACTIVE'
        ]

        # Vérifier qu'on a des employés actifs pour traiter
        self.assertGreater(len(employes_actifs), 0)

        # Vérifier que la période a les bonnes dates
        self.assertIsNotNone(periode.date_debut)
        self.assertIsNotNone(periode.date_fin)
        self.assertLess(periode.date_debut, periode.date_fin)

    def test_deduction_application_with_fixtures(self):
        """Test d'application des retenues avec les fixtures"""
        retenues_actives = [
            ret for ret in self.fixture_data['retenues'].values()
            if ret.est_active
        ]

        self.assertGreater(len(retenues_actives), 0)

        for retenue in retenues_actives[:3]:  # Tester les 3 premières
            self.assertGreater(retenue.montant_mensuel, 0)
            self.assertIsNotNone(retenue.employe_id)
            self.assertIsNotNone(retenue.date_debut)

            # Si c'est une retenue avec montant total, vérifier la cohérence
            if retenue.montant_total:
                self.assertGreaterEqual(retenue.montant_total, retenue.montant_mensuel)
