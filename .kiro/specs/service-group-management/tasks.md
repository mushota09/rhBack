# Implementation Plan: Service Group Management

## Overview

Plan d'implémentation pour le système complet de gestion des ServiceGroups avec ADRF et adrf_flex_fields. Les tâches sont organisées en 6 phases progressives pour assurer une implémentation incrémentale et testable.

## Tasks

- [x] 1. Créer le module ServiceGroup
  - Créer la structure du module avec serializers, views et URLs
  - Implémenter les opérations CRUD asynchrones de base
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 1.1 Créer la structure du module service_group
  - Créer le dossier `user_app/modules/service_group/`
  - Créer les fichiers `__init__.py`, `views.py`, `serializers.py`, `urls.py`
  - _Requirements: 1.1_

- [x] 1.2 Implémenter les serializers ServiceGroup
  - Créer `J_ServiceGroupSerializer` avec FlexFieldsModelSerializer
  - Ajouter expandable_fields pour service et group
  - Créer `I_ServiceGroupSerializer` pour les opérations d'écriture
  - Ajouter validation pour contrainte unique (service, group)
  - _Requirements: 1.2, 6.1, 6.2, 8.1, 8.2_

- [x] 1.3 Implémenter ServiceGroupViewSet
  - Créer ViewSet héritant de FlexFieldsModelViewSet
  - Configurer serializer_class_read et serializer_class_write
  - Définir permit_list_expands = ['service', 'group']
  - Implémenter get_queryset avec select_related('service', 'group')
  - Ajouter filtres, recherche et tri
  - _Requirements: 1.1, 1.3, 7.1, 7.2, 7.5, 11.1_

- [x] 1.4 Configurer les URLs pour ServiceGroup
  - Créer le fichier urls.py avec router
  - Enregistrer ServiceGroupViewSet
  - Intégrer dans user_app/urls.py principal
  - _Requirements: 1.1_

- [x] 1.5 Écrire tests unitaires pour ServiceGroup
  - Test création ServiceGroup valide
  - Test contrainte unique (service, group)
  - Test expansion ?expand=service,group
  - Test filtrage par service et group
  - _Requirements: 1.1, 1.2, 8.2_

- [x] 2. Modifier le module Group pour gestion ServiceGroups
  - Ajouter logique de création avec service_ids
  - Implémenter suppression cascade des ServiceGroups
  - Migrer vers FlexFieldsModelViewSet
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3_

- [x] 2.1 Enrichir J_GroupSerializers avec expandable_fields
  - Ajouter champ service_groups (PrimaryKeyRelatedField, many=True, read_only)
  - Configurer expandable_fields pour service_groups, user_groups, group_permissions
  - Utiliser lazy string references pour éviter imports circulaires
  - _Requirements: 10.1, 10.2_

- [x] 2.2 Migrer GroupViewSet vers FlexFieldsModelViewSet
  - Changer héritage de ModelViewSet vers FlexFieldsModelViewSet
  - Configurer serializer_class_read et serializer_class_write
  - Définir permit_list_expands = ['service_groups', 'user_groups', 'group_permissions']
  - _Requirements: 7.1, 7.2, 10.2_

- [x] 2.3 Implémenter logique création Group avec ServiceGroups
  - Modifier méthode create() pour accepter service_ids dans request.data
  - Valider existence des services fournis
  - Créer ServiceGroups de manière asynchrone pour chaque service_id
  - Gérer les doublons (ignorer si ServiceGroup existe déjà)
  - Utiliser transaction atomique pour garantir cohérence
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 8.3_

- [x] 2.4 Implémenter logique suppression Group avec cascade
  - Modifier méthode destroy() pour vérifier utilisateurs actifs
  - Si utilisateurs actifs, refuser suppression avec message d'erreur
  - Si pas d'utilisateurs, supprimer tous ServiceGroups associés en cascade
  - Utiliser transaction atomique
  - _Requirements: 3.1, 3.2, 3.3, 8.3_

- [x] 2.5 Écrire tests unitaires pour Group modifié
  - Test création Group avec service_ids valides
  - Test création Group avec service_ids invalides
  - Test suppression Group sans utilisateurs (cascade ServiceGroups)
  - Test refus suppression Group avec utilisateurs actifs
  - Test expansion ?expand=service_groups
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2_

- [-] 3. Modifier le module ServiceGroup pour suppression avec validation
  - Implémenter logique de suppression avec vérification Group
  - Supprimer Group si plus de ServiceGroups et pas d'utilisateurs
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 3.1 Implémenter logique destroy dans ServiceGroupViewSet
  - Récupérer le Group associé au ServiceGroup
  - Compter les autres ServiceGroups du Group
  - Si c'est le dernier ServiceGroup, vérifier utilisateurs actifs du Group
  - Si pas d'utilisateurs actifs, supprimer le Group également
  - Si utilisateurs actifs, refuser avec message d'erreur
  - Utiliser transaction atomique
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.3_

- [x] 3.2 Écrire tests unitaires pour suppression ServiceGroup
  - Test suppression ServiceGroup (Group garde autres ServiceGroups)
  - Test suppression dernier ServiceGroup (Group supprimé si pas d'utilisateurs)
  - Test refus suppression dernier ServiceGroup (Group a utilisateurs actifs)
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 4. Checkpoint - Valider module ServiceGroup complet
  - Vérifier que tous les tests passent ✅
  - Tester manuellement les endpoints ServiceGroup
  - Valider les expansions dynamiques ✅
  - Demander validation utilisateur si questions

- [x] 5. Migrer les modules RBAC vers FlexFieldsModelViewSet
  - Migrer UserGroup, Permission, Service vers FlexFieldsModelViewSet
  - Configurer expandable_fields pour chaque module
  - _Requirements: 7.1, 7.2, 7.3, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [x] 5.1 Enrichir J_UserGroupSerializers avec expandable_fields
  - Ajouter expandable_fields pour user, user.employe_id, group, group.service_groups, assigned_by
  - Utiliser lazy string references
  - _Requirements: 10.1, 10.5_

- [x] 5.2 Migrer UserGroupViewSet vers FlexFieldsModelViewSet
  - Changer héritage vers FlexFieldsModelViewSet
  - Configurer serializer_class_read et serializer_class_write
  - Définir permit_list_expands = ['user', 'user.employe_id', 'group', 'group.service_groups', 'assigned_by']
  - Optimiser get_queryset avec prefetch_related('group__service_groups')
  - _Requirements: 7.1, 7.2, 10.2, 10.5, 11.1_

- [x] 5.3 Migrer GroupPermissionReadSerializer vers FlexFieldsModelSerializer
  - Convertir de serializers.ModelSerializer vers FlexFieldsModelSerializer
  - Ajouter expandable_fields pour group, permission, created_by
  - Utiliser lazy string references
  - _Requirements: 6.1, 10.1, 10.6_

- [x] 5.4 Migrer PermissionSerializer vers FlexFieldsModelSerializer
  - Convertir vers FlexFieldsModelSerializer
  - Garder champ content_type_name en read_only
  - _Requirements: 6.1, 10.1_

- [x] 5.5 Migrer GroupPermissionViewSet vers FlexFieldsModelViewSet
  - Changer héritage vers FlexFieldsModelViewSet
  - Configurer serializer_class_read et serializer_class_write
  - Définir permit_list_expands = ['group', 'permission', 'created_by']
  - _Requirements: 7.1, 7.2, 10.2, 10.6_

- [x] 5.6 Migrer PermissionViewSet vers FlexFieldsModelViewSet
  - Changer héritage vers FlexFieldsModelViewSet
  - Configurer serializer_class
  - Définir permit_list_expands = [] (read-only)
  - _Requirements: 7.1, 7.2, 10.2_

- [x] 5.7 Migrer serviceAPIView vers FlexFieldsModelViewSet
  - Renommer classe en ServiceViewSet (convention)
  - Changer héritage vers FlexFieldsModelViewSet
  - Configurer serializer_class (déjà FlexFieldsModelSerializer)
  - Ajouter filtres, recherche et tri appropriés
  - _Requirements: 7.1, 7.2, 10.2_

- [x] 5.8 Écrire tests unitaires pour modules RBAC migrés
  - Test expansion UserGroup: ?expand=user,group
  - Test expansion GroupPermission: ?expand=group,permission
  - Test expansion imbriquée: ?expand=user.employe_id
  - Test champs sparse: ?fields=id,user,group
  - Test omission: ?omit=assigned_at
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.3, 10.4, 10.5, 10.6_

- [ ] 6. Checkpoint - Valider migrations FlexFieldsModelViewSet
  - Vérifier que tous les tests passent
  - Tester expansions sur tous les modules RBAC
  - Valider optimisations de requêtes
  - Demander validation utilisateur si questions

- [x] 7. Modifier le module Employe pour ServiceGroup et UserGroup
  - Remplacer référence poste par service_group
  - Ajouter logique assignation automatique UserGroup
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 7.1 Mettre à jour J_employeSerializers
  - Remplacer import J_posteSerializers par J_ServiceGroupSerializer
  - Mettre à jour expandable_fields: poste_id vers ServiceGroup
  - Ajouter expandable_fields: poste_id.service, poste_id.group
  - Ajouter expandable_fields: user_account, user_account.user_groups
  - Utiliser lazy string references
  - _Requirements: 9.1, 9.3, 9.4, 9.5, 9.6, 9.7, 10.1_

- [x] 7.2 Migrer employeAPIView vers FlexFieldsModelViewSet
  - Renommer en EmployeViewSet (convention)
  - Changer héritage vers FlexFieldsModelViewSet
  - Configurer serializer_class_read et serializer_class_write
  - Définir permit_list_expands = ['poste_id', 'poste_id.service', 'poste_id.group', 'user_account', 'user_account.user_groups']
  - _Requirements: 7.1, 7.2, 10.2_

- [x] 7.3 Ajouter logique assignation UserGroup dans acreate
  - Extraire group_id de request.data (optionnel)
  - Si group_id fourni, valider existence du Group
  - Après création User, créer UserGroup automatiquement
  - Lier User au Group avec assigned_by = request.user
  - Gérer erreurs (Group inexistant, Group inactif)
  - Utiliser transaction atomique pour garantir cohérence
  - _Requirements: 9.2, 8.3_

- [x] 7.4 Écrire tests unitaires pour Employe modifié
  - Test création employé avec poste_id (ServiceGroup)
  - Test création employé avec group_id (UserGroup créé automatiquement)
  - Test création employé sans group_id (pas de UserGroup)
  - Test expansion ?expand=poste_id.service,poste_id.group
  - Test expansion ?expand=user_account.user_groups
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 8. Checkpoint - Valider module Employe complet
  - Vérifier que tous les tests passent
  - Tester création employé avec assignation UserGroup
  - Valider expansions imbriquées
  - Demander validation utilisateur si questions

- [x] 9. Optimiser les performances des requêtes
  - Ajouter select_related et prefetch_related appropriés
  - Valider réduction du nombre de requêtes SQL
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 9.1 Optimiser ServiceGroupViewSet
  - Vérifier select_related('service', 'group') dans get_queryset

  - _Requirements: 11.1, 11.2_

- [x] 9.2 Optimiser GroupViewSet
  - Ajouter prefetch_related('service_groups', 'user_groups', 'group_permissions') si nécessaire
  - Tester avec expansions multiples
  - _Requirements: 11.1, 11.2_

- [x] 9.3 Optimiser UserGroupViewSet
  - Vérifier select_related('user', 'group', 'assigned_by')
  - Vérifier prefetch_related('group__service_groups')
  - Tester avec expansions imbriquées
  - _Requirements: 11.1, 11.2_

- [x] 9.4 Optimiser EmployeViewSet
  - Ajouter select_related('poste_id', 'poste_id__service', 'poste_id__group', 'user_account')
  - Ajouter prefetch_related('user_account__user_groups') si nécessaire
  - Tester avec expansions multiples
  - _Requirements: 11.1, 11.2_

- [x] 9.5 Valider optimisations avec tests de performance
  - Mesurer nombre de requêtes avant/après optimisation
  - Vérifier que N+1 queries sont éliminées
  - Documenter les résultats
  - _Requirements: 11.1, 11.2_

- [x] 10. Checkpoint final - Validation complète du système
  - Exécuter tous les tests unitaires
  - Tester manuellement tous les endpoints
  - Valider toutes les expansions dynamiques
  - Vérifier les performances
  - Demander validation utilisateur finale

## Notes

- Toutes les tâches sont obligatoires pour garantir un système complet et testé
- Chaque tâche référence les requirements spécifiques pour traçabilité
- Les checkpoints permettent une validation incrémentale
- Les tests de propriétés ne sont pas inclus dans ce plan (peuvent être ajoutés ultérieurement)
- Utiliser transactions atomiques pour toutes opérations multiples
- Toujours valider les données avant création/modification
- Logger les opérations critiques pour audit
