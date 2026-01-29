# Fixtures du Système de Paie

Ce dossier contient les fixtures et utilitaires de test pour le système de paie. Les fixtures permettent de créer des jeux de données cohérents et réalistes pour les tests.

## Structure des Fixtures

### 1. Base Fixtures (`base_fixtures.py`)

Contient la classe `BaseFixtures` qui crée un jeu de données complet et réaliste :

- **10 employés** avec différents profils (directeur, managers, développeurs, techniciens, etc.)
- **10 contrats** avec différentes configurations salariales
- **10 retenues** de différents types (prêts, avances, assurances, etc.)
- **5 périodes de paie** avec différents statuts
- **4 utilisateurs** avec différents rôles
- **6 services** et **9 postes** organisationnels
- **5 alertes** de différents types et sévérités

### 2. Property Test Fixtures (`property_test_fixtures.py`)

Contient la classe `PropertyTestFixtures` pour générer des données aléatoires mais valides :

- Génération d'employés avec des données cohérentes
- Génération de contrats avec des salaires réalistes
- Génération de retenues avec des montants appropriés
- Support pour différentes tailles de jeux de données

### 3. Test Utils (`test_utils.py`)

Fournit des classes et fonctions utilitaires pour faciliter l'utilisation des fixtures :

- `FixtureTestCase` : Classe de base avec fixtures pré-chargées
- `PropertyTestCase` : Classe de base pour tests avec données aléatoires
- `FixtureDataMixin` : Mixin avec méthodes d'accès aux données
- Fonctions utilitaires pour créer des données simples

## Utilisation

### 1. Charger les Fixtures via Management Command

```bash
# Charger toutes les fixtures
python manage.py load_paie_fixtures

# Charger avec suppression des données existantes
python manage.py load_paie_fixtures --clear

# Charger avec informations détaillées
python manage.py load_paie_fixtures --verbose
```

### 2. Utiliser les Fixtures dans les Tests

#### Tests avec Fixtures Pré-définies

```python
from paie_app.fixtures.test_utils import FixtureTestCase

class MonTest(FixtureTestCase):
    def test_something(self):
        # Accès direct aux données
        directeur = self.get_employe('EMP001')
        admin_user = self.get_user('admin@company.com')
        periode_jan = self.get_periode(2024, 1)

        # Utiliser les données dans les tests
        self.assertEqual(directeur.nom, 'Mukendi')
        self.assertTrue(admin_user.is_superuser)
```

#### Tests avec Données Aléatoires

```python
from paie_app.fixtures.test_utils import PropertyTestCase

class MonTestPropriete(PropertyTestCase):
    def test_property(self):
        # Créer un jeu de données aléatoire
        dataset = self.create_random_dataset(num_employes=10)

        # Utiliser les données générées
        for employe in dataset['employes']:
            # Tester une propriété
            self.assertGreater(employe.date_embauche, employe.date_naissance)
```

#### Tests Simples

```python
from paie_app.fixtures.test_utils import create_simple_employe_with_contrat

class MonTestSimple(TestCase):
    def test_calcul_simple(self):
        employe, contrat = create_simple_employe_with_contrat()

        # Utiliser l'employé et le contrat
        composants = contrat.calcul_composants_salaire()
        self.asse
n
        employes = self.get_sample_employes(5)
        emp_with_children = self.get_employe_with_children()
        emp_high_salary = self.get_employe_with_high_salary()
```

## Données Créées

### Employés

| Matricule | Nom | Prénom | Poste | Enfants | Statut |
|-----------|-----|--------|-------|---------|--------|
| EMP001 | Mukendi | Jean | Directeur Général | 3 | ACTIVE |
| EMP002 | Kabongo | Marie | Responsable RH | 2 | ACTIVE |
| EMP003 | Tshimanga | Pierre | Développeur Senior | 0 | ACTIVE |
| EMP004 | Mbuyi | Sylvie | Développeur Junior | 1 | ACTIVE |
| EMP005 | Kasongo | Joseph | Comptable | 5 | ACTIVE |
| EMP006 | Ngoy | Beatrice | Commercial Senior | 2 | ACTIVE |
| EMP007 | Ilunga | Michel | Technicien | 0 | ACTIVE |
| EMP008 | Kalala | Francine | Assistant RH | 4 | ACTIVE |
| EMP009 | Mwamba | Andre | Ouvrier | 3 | ACTIVE |
| EMP010 | Katende | Rosine | Développeur Junior | 0 | SUSPENDED |

### Contrats (Salaires en USD)

| Employé | Type | Salaire Base | Logement % | Déplacement % | Fonction % |
|---------|------|--------------|------------|---------------|------------|
| EMP001 | PERMANENT | 2,000,000 | 25% | 15% | 30% |
| EMP002 | PERMANENT | 1,200,000 | 20% | 10% | 20% |
| EMP003 | PERMANENT | 800,000 | 15% | 5% | 15% |
| EMP004 | PERMAN
ENT | 500,000 | 10% | 5% | 10% |
| EMP005 | PERMANENT | 700,000 | 15% | 8% | 12% |

### Retenues

| Employé | Type | Description | Montant Mensuel | Montant Total |
|---------|------|-------------|-----------------|---------------|
| EMP001 | LOAN | Prêt véhicule | 150,000 | 1,800,000 |
| EMP002 | ADVANCE | Avance urgence | 100,000 | 500,000 |
| EMP003 | INSURANCE | Assurance vie | 25,000 | - |
| EMP004 | UNION | Cotisation syndicale | 15,000 | - |
| EMP005 | LOAN | Prêt immobilier | 200,000 | 4,800,000 |

### Périodes de Paie

| Année | Mois | Statut | Traité par | Approuvé par |
|-------|------|--------|------------|--------------|
| 2024 |
 **Maintenance** : Centralisées et faciles à maintenir

## Cas d'Usage

### Tests Unitaires
- Utiliser `create_simple_employe_with_contrat()` pour des tests rapides
- Utiliser `FixtureTestCase` pour des tests avec données complètes

### Tests d'Intégration
- Utiliser `BaseFixtures` pour tester les workflows complets
- Utiliser les données pré-définies pour tester les interactions

### Tests de Propriété
- Utiliser `PropertyTestFixtures` pour générer des données aléatoires
- Tester les propriétés universelles avec des données variées

### Tests de Performance
- Utiliser `create_large_dataset()` pour tester avec beaucoup de données
- Mesurer les performances avec des volumes réalistes

## Maintenance

Pour ajouter de nouvelles fixtures :

1. Étendre `BaseFixtures` avec de nouvelles méthodes
2. Ajouter des générateurs dans `PropertyTestFixtures`
3. Créer des utilitaires dans `test_utils.py`
4. Mettre à jour la commande de management si nécessaire
5. Documenter les nouvelles fixtures dans ce README

## Exemples Complets

Voir `test_fixtures_demo.py` pour des exemples complets d'utilisation de toutes les fixtures.
