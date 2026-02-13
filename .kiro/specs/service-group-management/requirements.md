# Requirements Document - Service Group Management

## Introduction

Ce document définit les exigences pour la gestion asynchrone des ServiceGroups dans le système RBAC, permettant de lier les services aux groupes organisationnels avec support complet d'ADRF et adrf_flex_fields pour des opérations asynchrones performantes et une expansion dynamique des champs.

## Glossary

- **System**: Le système de gestion RH (rhBack)
- **ServiceGroup**: Table de liaison entre Service et Group
- **Group**: Groupe organisationnel avec rôles et permissions
- **Service**: Service/département de l'organisation
- **ADRF**: Async Django REST Framework
- **FlexFields**: Système d'expansion dynamique des champs via adrf_flex_fields
- **Expansion**: Processus de remplacement d'un ID par l'objet complet dans la réponse API
- **UserGroup**: Relation many-to-many entre User et Group avec métadonnées
- **Permission**: Permission système pour contrôler l'accès aux ressources
- **GroupPermission**: Relation many-to-many entre Group et Permission

## Requirements

### Requirement 1: Gestion Asynchrone des ServiceGroups

**User Story:** En tant que développeur système, je veux gérer les ServiceGroups de manière asynchrone, afin d'améliorer les performances et la scalabilité du système.

#### Acceptance Criteria

1. THE System SHALL utiliser ADRF pour toutes les opérations CRUD sur ServiceGroup
2. THE System SHALL utiliser adrf_flex_fields pour l'expansion dynamique des champs
3. WHEN une opération asynchrone est effectuée, THE System SHALL maintenir la cohérence des données
4. THE System SHALL gérer les erreurs asynchrones de manière appropriée

### Requirement 2: Création de Group avec ServiceGroups

**User Story:** En tant qu'administrateur, je veux créer un groupe avec des services associés, afin de définir les postes disponibles dans l'organisation.

#### Acceptance Criteria

1. WHEN un Group est créé avec une liste de service_ids, THE System SHALL créer automatiquement les ServiceGroups correspondants
2. WHEN un Group est créé sans service_ids, THE System SHALL créer uniquement le Group sans ServiceGroups
3. WHEN un service_id invalide est fourni, THE System SHALL retourner une erreur de validation
4. WHEN un ServiceGroup existe déjà pour un service donné, THE System SHALL ignorer la duplication
5. THE System SHALL effectuer toutes les créations de manière asynchrone

### Requirement 3: Suppression de Group avec Cascade

**User Story:** En tant qu'administrateur, je veux supprimer un groupe, afin de nettoyer les postes obsolètes du système.

#### Acceptance Criteria

1. WHEN un Group est supprimé, THE System SHALL supprimer automatiquement tous les ServiceGroups associés
2. WHEN un Group a des utilisateurs actifs assignés, THE System SHALL empêcher la suppression et retourner une erreur
3. WHEN un Group n'a pas d'utilisateurs actifs, THE System SHALL autoriser la suppression
4. THE System SHALL effectuer toutes les vérifications et suppressions de manière asynchrone

### Requirement 4: Suppression de ServiceGroup avec Validation

**User Story:** En tant qu'administrateur, je veux supprimer un ServiceGroup, afin de retirer un poste d'un service.

#### Acceptance Criteria

1. WHEN un ServiceGroup est supprimé, THE System SHALL vérifier si le Group associé a d'autres ServiceGroups
2. WHEN le Group n'a plus d'autres ServiceGroups, THE System SHALL supprimer également le Group
3. WHEN le Group a des utilisateurs actifs, THE System SHALL empêcher la suppression et retourner une erreur
4. WHEN le Group a d'autres ServiceGroups, THE System SHALL supprimer uniquement le ServiceGroup
5. THE System SHALL effectuer toutes les opérations de manière asynchrone

### Requirement 5: Expansion Dynamique des Champs

**User Story:** En tant que développeur frontend, je veux pouvoir étendre dynamiquement les champs des ServiceGroups, afin d'optimiser les requêtes API.

#### Acceptance Criteria

1. WHEN le paramètre expand=service est fourni, THE System SHALL retourner l'objet Service complet au lieu de l'ID
2. WHEN le paramètre expand=group est fourni, THE System SHALL retourner l'objet Group complet au lieu de l'ID
3. WHEN le paramètre expand=service,group est fourni, THE System SHALL retourner les deux objets complets
4. WHEN le paramètre fields est fourni, THE System SHALL retourner uniquement les champs spécifiés
5. WHEN le paramètre omit est fourni, THE System SHALL exclure les champs spécifiés
6. THE System SHALL supporter l'expansion imbriquée avec notation par points

### Requirement 6: Sérialisation Asynchrone

**User Story:** En tant que développeur système, je veux utiliser des serializers asynchrones, afin de bénéficier des performances d'ADRF.

#### Acceptance Criteria

1. THE System SHALL utiliser FlexFieldsModelSerializer pour ServiceGroup
2. THE System SHALL définir les champs expandables dans le serializer
3. WHEN une sérialisat
éfinir permit_list_expands pour contrôler les expansions en mode liste
3. THE System SHALL utiliser serializer_class_read et serializer_class_write pour séparer lecture et écriture
4. WHEN une requête liste est effectuée, THE System SHALL appliquer les restrictions d'expansion
5. THE System SHALL supporter les filtres, recherche et tri de manière asynchrone

### Requirement 8: Validation et Intégrité des Données

**User Story:** En tant qu'administrateur système, je veux garantir l'intégrité des données, afin d'éviter les incohérences dans le système RBAC.

#### Acceptance Criteria

1. WHEN un ServiceGroup est créé, THE System SHALL valider l'existence du Service et du Group
2. WHEN une contrainte unique est violée, THE System SHALL retourner une erreur appropriée
3. THE System SHALL utiliser des transactions pour les opérations multiples
4. WHEN une erreur survient, THE System SHALL effectuer un rollback automatique
5. THE System SHALL logger toutes les opérations critiques

### Requirement 9: Gestion des Employés avec ServiceGroup et UserGroup

**User Story:** En tant qu'administrateur RH, je veux assigner des employés à des ServiceGroups et des groupes utilisateurs, afin de définir leur poste et leurs permissions dans l'organisation.

#### Acceptance Criteria

1. WHEN un employé est créé ou modifié, THE System SHALL permettre l'assignation à un ServiceGroup via poste_id
2. WHEN un employé est créé avec un group_id, THE System SHALL créer automatiquement un UserGroup pour lier l'utilisateur au groupe
3. WHEN un ServiceGroup est supprimé, THE System SHALL mettre à NULL le poste_id des employés associés
4. THE System SHALL supporter l'expansion du ServiceGroup dans les requêtes employés
5. WHEN expand=poste_id.service est fourni, THE System SHALL retourner le service complet
6. WHEN expand=poste_id.group est fourni, THE System SHALL retourner le groupe complet
7. WHEN expand=user_account.user_groups.group est fourni, THE System SHALL retourner les groupes de l'utilisateur

### Requirement 10: Application d'adrf_flex_fields au Système RBAC Complet

**User Story:** En tant que développeur frontend, je veux utiliser adrf_flex_fields sur toutes les entités RBAC, afin d'optimiser les requêtes API et réduire le nombre d'appels.

#### Acceptance Criteria

1. THE System SHALL utiliser FlexFieldsModelSerializer pour Group, UserGroup, Permission, et GroupPermission
2. THE System SHALL utiliser FlexFieldsModelViewSet pour toutes les vues RBAC
3. WHEN expand=user_groups.user est fourni sur Group, THE System SHALL retourner les utilisateurs complets
4. WHEN expand=group_permissions.permission est fourni sur Group, THE System SHALL retourner les permissions complètes
5. WHEN expand=user,group est fourni sur UserGroup, THE System SHALL retourner les deux objets complets
6. WHEN expand=group,permission est fourni sur GroupPermission, THE System SHALL retourner les deux objets complets
7. THE System SHALL définir permit_list_expands appropriés pour chaque ViewSet
8. THE System SHALL supporter les champs sparse (fields) et l'omission (omit) sur toutes les entités RBAC

### Requirement 11: Performance et Optimisation

**User Story:** En tant qu'utilisateur du système, je veux des temps de réponse rapides, afin d'avoir une expérience fluide.

#### Acceptance Criteria

1. THE System SHALL utiliser select_related et prefetch_related pour optimiser les requêtes
2. WHEN des expansions sont demandées, THE System SHALL charger les relations de manière optimisée
3. THE System SHALL limiter la profondeur d'expansion pour éviter les requêtes excessives
4. THE System SHALL utiliser la pagination pour les listes volumineuses
5. THE System SHALL mettre en cache les résultats fréquemment demandés si approprié
