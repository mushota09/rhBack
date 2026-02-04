# Système de Gestion RH - Backend

## Vue d'ensemble

Ce projet est le backend du système de gestion des ressources humaines, développé avec Django et Django REST Framework. Il fournit une API complète pour la gestion des employés, le traitement de la paie, et les fonctions administratives.

## Modules Principaux

### Module Utilisateur (`user_app`)
- **Gestion des Employés**: CRUD complet pour les dossiers employés avec 25+ champs
- **Gestion des Services et Postes**: Structure organisationnelle
- **Gestion des Contrats**: Cycle de vie des contrats employés
- **Gestion des Documents**: Stockage et suivi des documents employés
- **Gestion des Comptes Utilisateurs**: Comptes système liés aux employés
- **Journal d'Audit**: Traçabilité complète des actions système

### Module Paie (`paie_app`)
- **Calculs Salariaux**: Service de calcul automatisé des salaires
- **Périodes de Paie**: Gestion des cycles de paie
- **Retenues**: Gestion des retenues employés
- **Bulletins de Paie**: Génération automatique des bulletins
- **Cotisations Sociales**: Calcul INSS, IRE, et autres cotisations

### Module Congés (`conge_app`)
- **Demandes de Congés**: Traitement des demandes
- **Calendrier des Congés**: Planification et visualisation
- **Types de Congés**: Configuration des différents types

### Module Authentification (`auth_app`)
- **Authentification JWT**: Sécurisation des API
- **Gestion des Permissions**: Contrôle d'accès granulaire
- **Sessions Utilisateurs**: Gestion des sessions actives

## Types de Données Frontend

Le système utilise des interfaces TypeScript complètes pour la sécurité des types:

### Entités Principales

#### Employé (`Employe`)
- Informations personnelles (nom, date de naissance, sexe, état matrimonial)
- Informations de contact (email personnel/professionnel, téléphones)
- Informations d'adresse (adresse complète avec ville, province, code postal)
- Détails d'emploi (poste, superviseur, date d'embauche, statut d'emploi)
- Informations financières (détails bancaires, numéro INSS)
- Informations familiales (nombre d'enfants, nom du conjoint)
- Contact d'urgence

#### Contrat (`Contrat`)
- Type de contrat (permanent, temporaire, stage, consultant)
- Structure salariale (salaire de base, indemnités, avantages)
- Taux d'assurance et de cotisations
- Durée et statut du contrat

#### Service et Poste (`Service`, `Poste`)
- Hiérarchie organisationnelle
- Codes et descriptions des services
- Affectations et relations des postes

#### Gestion des Documents (`Document`)
- Catégorisation des documents (contrat, pièce d'identité, CV, certificats, etc.)
- Stockage de fichiers et métadonnées
- Suivi des dates d'expiration
- Historique des téléchargements

#### Gestion des Utilisateurs (`User`)
- Authentification système
- Permissions basées sur les rôles
- Liaison avec les employés
- Suivi d'activité

#### Journal d'Audit (`AuditLog`)
- Journalisation complète des actions
- Suivi d'activité utilisateur
- Historique des changements de ressources
- Suivi IP et user agent

## Installation

### Prérequis
- Python 3.11+
- uv (gestionnaire de paquets Python)

### Installation sous Mac/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation sous Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Configuration du Projet

1. Cloner le repository
2. Se déplacer dans le dossier du projet (même niveau que manage.py)
3. Installer les dépendances:
   ```bash
   uv sync
   ```

4. Démarrer le serveur de développement:
   ```bash
   uv run uvicorn rhBack.asgi:application --reload --host 0.0.0.0 --port 8000
   ```

## Structure du Projet

```
rhBack/
├── auth_app/           # Module d'authentification
├── conge_app/          # Module de gestion des congés
├── hr_app/             # Module RH principal
├── paie_app/           # Module de paie
│   └── services/       # Services de calcul salarial
├── user_app/           # Module de gestion des utilisateurs
├── utilities/          # Utilitaires partagés
├── templates/          # Templates Django
├── docs/               # Documentation
├── logs/               # Fichiers de logs
└── rhBack/             # Configuration Django principale
```

## Services de Calcul Salarial

### SalaryCalculatorService

Le service `SalaryCalculatorService` dans `paie_app/services/salary_calculator.py` fournit:

- **Calcul du salaire brut**: Salaire de base + indemnités + allocations familiales
- **Cotisations sociales**: Calcul des cotisations patronales et salariales (INSS, MFP, FPC)
- **Calcul de l'IRE**: Impôt sur les revenus selon le barème progressif
- **Retenues diverses**: Gestion des retenues employés (prêts, avances, etc.)
- **Salaire net**: Calcul final du salaire net à payer

#### Fonctionnalités principales:
- Calcul automatisé des allocations familiales selon le barème progressif
- Gestion des cotisations sociales avec plafonds
- Calcul de l'IRE selon les tranches d'imposition
- Traitement des retenues avec suivi des montants restants
- Support pour différents types de contrats et de salaires

## API REST

L'API fournit des endpoints complets pour:
- Gestion des employés et contrats
- Traitement des périodes de paie
- Calculs salariaux automatisés
- Gestion des retenues
- Génération de bulletins de paie
- Rapports et exports

Consultez la [documentation API complète](docs/reference/api-reference.md) pour plus de détails.

## Tests

Exécuter les tests:
```bash
python manage.py test paie_app.tests.test_fixtures_simple.SimpleFixturesTest.test_base_fixtures_creation -v 2
```

## Configuration

### Variables d'environnement
Configurez les variables suivantes dans le fichier `.env`:
- `DEBUG`: Mode debug (True/False)
- `SECRET_KEY`: Clé secrète Django
- `DATABASE_URL`: URL de la base de données
- `ALLOWED_HOSTS`: Hôtes autorisés

### Base de données
Le système supporte PostgreSQL pour la production et SQLite pour le développement.

## Mises à jour récentes

### Amélioration du système de types (Février 2026)
- Ajout d'interfaces TypeScript complètes pour toutes les entités user_app
- Implémentation de la vérification de type stricte pour la gestion des employés
- Amélioration des définitions de types pour les contrats et documents
- Ajout du support de types pour le journal d'audit
- Amélioration de la sécurité des types pour les options de dropdown

### Service de calcul salarial
- Service complet de calcul automatisé des salaires
- Support pour les cotisations sociales congolaises (INSS, MFP, FPC)
- Calcul de l'IRE selon le barème fiscal en vigueur
- Gestion des allocations familiales progressives
- Traitement des retenues avec suivi automatique

## Documentation

La documentation complète est disponible dans le dossier `docs/`:
- [Guides utilisateur](docs/user-guides/)
- [Configuration système](docs/configuration/)
- [Référence API](docs/reference/api-reference.md)

## Support

Pour le support technique ou les questions concernant le backend, consultez la documentation du projet ou contactez l'équipe de développement.
