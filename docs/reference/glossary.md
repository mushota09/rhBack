# Glossaire

Ce glossaire définit tous les termes techniques et métier utilisés dans le système de paie.

## A

**Allocation Familiale**
: Montant versé aux employés en fonction du nombre d'enfants à charge. Suit un barème progressif défini par la réglementation.

**API (Application Programming Interface)**
: Interface de programmation permettant l'intégration du système de paie avec d'autres applications.

**ADRF (Async Django REST Framework)**
: Framework utilisé pour développer les APIs asynchrones du système.

**Audit Trail**
: Piste d'audit enregistrant toutes les opérations effectuées dans le système pour assurer la traçabilité.

**Avance sur Salaire**
: Montant versé à l'employé avant l'échéance normale, récupéré par déduction sur les salaires suivants.

## B

**Base Imposable**
: Montant sur lequel est calculé l'IRE, généralement égal au salaire brut moins les cotisations salariales.

**Barème Progressif**
: Système de calcul par tranches avec des taux différents selon les montants (utilisé pour l'IRE et l'allocation familiale).

**Bulletin de Paie**
: Document détaillant le
 l'employeur (INSS, MFP, FPC).

**Cotisations Salariales**
: Charges sociales déduites du salaire de l'employé (INSS, MFP).

**CRUD**
: Create, Read, Update, Delete - Opérations de base sur les données.

## D

**Déduction**
: Voir Retenue.

**Django**
: Framework web Python utilisé pour développer le système de paie.

## E

**Employé**
: Personne physique ayant un contrat de travail avec l'organisation.

**Entrée de Paie**
: Enregistrement détaillant le calcul salarial d'un employé pour une période donnée.

**Export**
: Fonctionnalité permettant d'extraire les données de paie vers des formats externes (Excel, PDF).

## F

**FPC (Fonds de Promotion de la Culture)**
: Cotisation sociale à la charge de l'employeur uniquement (0.5% du salaire brut).

**Fixtures**
: Jeux de données de test utilisés pour le développement et les tests du système.

## I

**Indemnité de Déplacement**
: Indemnité calculée en pourcentage du salaire de base pour compenser les frais de transport.

**Indemnité de Fonction**
: Indemnité liée aux responsabilités du poste, calculée en pourcentage du salaire de base.

**Indemnité de Logement**
: Indemnité calculée en pourcentage du salaire de base pour compenser les frais de logement.

**INSS (Institut National de Sécurité Sociale)**
: Organisme gérant les cotisations sociales avec deux composantes :
- Pension : 6% patronal, 3% salarial (plafond 27,000 USD)
- Risque professionnel : 6% patronal, 1.5% salarial (plafond 2,400 USD)

**IRE (Impôt sur les Revenus)**
: Impôt progressif calculé sur la base imposable avec trois tranches (0%, 20%, 30%).

## J

**JWT (JSON Web Token)**
: Système d'authentification utilisé pour sécuriser les APIs.

## M

**Masse Salariale**
: Somme totale des salaires bruts versés pour une période donnée.

**MFP (Mutuelle des Fonctionnaires et Agents Publics)**
: Cotisation sociale : 1.5% patronal, 1% salarial (sans plafond).

**Middleware**
: Composant logiciel interceptant les requêtes pour ajouter des fonctionnalités (authentification, audit).

## P

**Paie**
: Processus de calcul et de versement des salaires aux employés.

**Payslip**
: Terme anglais pour bulletin de paie.

**Période de Paie**
: Période mensuelle pour laquelle les salaires sont calculés et versés.

**PostgreSQL**
: Système de gestion de base de données utilisé par le système.

**Property-Based Testing (PBT)**
: Méthode de test validant des propriétés universelles avec des données générées aléatoirement.

## R

**Redis**
: Système de cache en mémoire utilisé pour améliorer les performances.

**Retenue**
: Déduction effectuée sur le salaire de l'employé (prêt, avance, assurance, cotisation syndicale).

**REST API**
: Interface de programmation suivant les principes REST pour l'accès aux données.

## S

**Salaire de Base**
: Montant fixe défini dans le contrat de travail, base de calcul des indemnités.

**Salaire Brut**
: Salaire de base + indemnités + allocations + autres avantages.

**Salaire Net**
: Salaire brut - cotisations salariales - IRE - retenues diverses.

**Serializer**
: Composant convertissant les données entre les formats internes et les APIs.

## T

**Template**
: Modèle de mise en forme utilisé pour générer les bulletins de paie PDF.

**Traçabilité**
: Capacité à suivre et enregistrer toutes les opérations effectuées dans le système.

## U

**UV (Python Package Manager)**
: Gestionnaire de paquets Python moderne utilisé pour l'installation et la gestion des dépendances.

## V

**Validation**
: Processus de vérification de la cohérence et de la conformité des données et calculs.

**ViewSet**
: Classe Django REST Framework regroupant les opérations CRUD pour une ressource.

## W

**Webhook**
: Mécanisme permettant d'envoyer des notifications automatiques lors d'événements système.

**Workflow**
: Processus métier définissant les étapes de traitement d'une période de paie.

---

## Acronymes Courants

| Acronyme | Signification |
|----------|---------------|
| API | Application Programming Interface |
| CRUD | Create, Read, Update, Delete |
| FPC | Fonds de Promotion de la Culture |
| INSS | Institut National de Sécurité Sociale |
| IRE | Impôt sur les Revenus |
| JWT | JSON Web Token |
| MFP | Mutuelle des Fonctionnaires et Agents Publics |
| PBT | Property-Based Testing |
| PDF | Portable Document Format |
| REST | Representational State Transfer |
| UUID | Universally Unique Identifier |

---

## Statuts du Système

### Statuts des Périodes de Paie

| Statut | Description |
|--------|-------------|
| DRAFT | Période créée, prête pour traitement |
| PROCESSING | Traitement en cours |
| COMPLETED | Traitement terminé avec succès |
| ERROR | Erreur pendant le traitement |
| FINALIZED | Période finalisée, calculs verrouillés |
| APPROVED | Période approuvée, aucune modification possible |

### Types de Retenues

| Type | Code | Description |
|------|------|-------------|
| Prêt | LOAN | Remboursement de prêt accordé |
| Avance | ADVANCE | Récupération d'avance sur salaire |
| Assurance | INSURANCE | Cotisation d'assurance vie/santé |
| Syndicat | UNION | Cotisation syndicale |

### Types de Contrats

| Type | Description |
|------|-------------|
| PERMANENT | Contrat à durée indéterminée |
| TEMPORARY | Contrat à durée déterminée |
| CONSULTANT | Contrat de consultation |
| INTERN | Contrat de stage |

---

*Ce glossaire est maintenu à jour avec l'évolution du système. Pour suggérer des ajouts ou modifications, contactez l'équipe de développement.*
