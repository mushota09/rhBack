"""
Tests simples pour vérifier que les fixtures fonctionnent correctement.
"""
from decimal import Decimal
from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from paie_app.fixtures.base_fixtures import BaseFixtures
from paie_app.fixtures.property_test_fixtures import PropertyTestFixtures
from paie_app.fixtures.test_utils import create_simple_employe_with_contrat, get_test_user

User = get_user_model()


class SimpleFixturesTest(TestCase):
    """Tests simples pour vérifier les fixtures"""

    def test_base_fixtures_creation(self):
        """Test de création des fixtures de base"""
        fixtures = BaseFixtures()
        data = fixtures.create_all_fixtures()

        # Vérifier que toutes les catégories sont créées
        self.assertIn('users', data)
        self.assertIn('employes', data)
        self.assertIn('contrats', data)
        self.assertIn('retenues', data)
        self.assertIn('periodes', data)

        # Vérifier les quantités
        self.assertEqual(len(data['users']), 4)
        self.assertEqual(len(data['employes']), 10)
        self.assertEqual(len(data['contrats']), 10)
        self.assertEqual(len(data['retenues']), 10)
        self.assertEqual(len(data['periodes']), 5)

    def test_property_fixtures_creation(self):
        """Test de création des fixtures pour tests de propriété"""
        property_fixtures = PropertyTestFixtures()
        dataset = property_fixtures.create_minimal_dataset()

        # Vérifier la structure
        self.assertIn('employes', dataset)
        self.assertIn('contrats', dataset)
        self.assertIn('retenues', dataset)

        # Vérifier les quantités
        self.assertEqual(len(dataset['employes']), 3)
        self.assertEqual(len(dataset['contrats']), 3)

    def test_simple_employe_creation(self):
        """Test de création d'employé simple"""
        employe_obj, contrat_obj = create_simple_employe_with_contrat()

        self.assertIsNotNone(employe_obj)
        self.assertIsNotNone(contrat_obj)
        self.assertEqual(employe_obj.matricule, 'TEST001')
        self.assertEqual(contrat_obj.salaire_base, Decimal('500000'))
        self.assertEqual(contrat_obj.employe_id, employe_obj)

    def test_test_user_creation(self):
        """Test de création d'utilisateur de test"""
        user = get_test_user()

        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.nom, 'Test')
        self.assertEqual(user.prenom, 'User')

    def test_data_consistency(self):
        """Test de cohérence des données créées"""
        fixtures = BaseFixtures()
        data = fixtures.create_all_fixtures()

        # Vérifier qu'il y a autant de contrats que d'employés
        self.assertEqual(len(data['employes']), len(data['contrats']))

        # Vérifier que chaque employé a un contrat
        for matricule, employe_obj in data['employes'].items():
            self.assertIn(matricule, data['contrats'])
            contrat_obj = data['contrats'][matricule]
            self.assertEqual(contrat_obj.employe_id, employe_obj)

    def test_salary_calculation_with_fixtures(self):
        """Test de calcul de salaire avec les fixtures"""
        fixtures = BaseFixtures()
        data = fixtures.create_all_fixtures()

        # Prendre le premier employé
        employe_obj = list(data['employes'].values())[0]
        contrat_obj = list(data['contrats'].values())[0]

        # Calculer les composants du salaire
        composants = contrat_obj.calcul_composants_salaire()

        # Vérifier que les composants essentiels sont présents
        self.assertIn('salaire_brut', composants)
        self.assertIn('salaire_net', composants)
        self.assertGreater(composants['salaire_brut'], 0)
        self.assertGreater(composants['salaire_net'], 0)
        self.assertLess(composants['salaire_net'], composants['salaire_brut'])

    def test_retenues_creation(self):
        """Test de création des retenues"""
        fixtures = BaseFixtures()
        data = fixtures.create_all_fixtures()

        # Vérifier qu'on a des retenues
        self.assertGreater(len(data['retenues']), 0)

        # Vérifier qu'on a différents types de retenues
        types_retenues = set()
        for retenue in data['retenues'].values():
            types_retenues.add(retenue.type_retenue)

        # Vérifier qu'on a au moins 3 types différents
        self.assertGreaterEqual(len(types_retenues), 3)

    def test_periodes_creation(self):
        """Test de création des périodes de paie"""
        fixtures = BaseFixtures()
        data = fixtures.create_all_fixtures()

        # Vérifier qu'on a des périodes
        self.assertGreater(len(data['periodes']), 0)

        # Vérifier qu'on a différents statuts
        statuts = set()
        for periode in data['periodes'].values():
            statuts.add(periode.statut)

        # Vérifier qu'on a au moins 2 statuts différents
        self.assertGreaterEqual(len(statuts), 2)
