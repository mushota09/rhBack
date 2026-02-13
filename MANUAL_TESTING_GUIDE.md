# Guide de Test Manuel - Service Group Management

## Vue d'ensemble

Ce guide fournit des instructions pour tester manuellement tous les endpoints du système ServiceGroup Management avec les expansions dynamiques.

## Prérequis

- Serveur de développement en cours d'exécution: `python manage.py runserver`
- Token d'authentification valide
- Outil de test API (Postman, curl, ou navigateur)

## 1. Tests ServiceGroup

### 1.1 Lister les ServiceGroups

```bash
GET /api/service-group/
```

**Avec expansion:**
```bash
GET /api/service-group/?expand=service,group
```

**Résultat attendu:**
- Liste paginée des ServiceGroups
- Avec expand: objets service et group complets au lieu des IDs

### 1.2 Créer un ServiceGroup

```bash
POST /api/service-group/
Content-Type: application/json

{
  "service": 1,
  "group": 1
}
```

**Résultat attendu:**
- Status 201 Created
- ServiceGroup créé avec ID

**Test contrainte unique:**
```bash
POST /api/service-group/
Content-Type: application/json

{
  "service": 1,
  "group": 1
}
```

**Résultat attendu:**
- Status 409 Conflict
- Message d'erreur sur contrainte unique

### 1.3 Récupérer un ServiceGroup

```bash
GET /api/service-group/{id}/
```

**Avec expansion:**
```bash
GET /api/service-group/{id}/?expand=service,group
```

### 1.4 Supprimer un ServiceGroup

```bash
DELETE /api/service-group/{id}/
```

**Résultat attendu:**
- Si Group a d'autres ServiceGroups: ServiceGroup supprimé uniquement
- Si dernier ServiceGroup et Group sans utilisateurs: Group et ServiceGroup supprimés
- Si dernier ServiceGroup et Group avec utilisateurs: Status 400, message d'erreur

## 2. Tests Group

### 2.1 Créer un Group avec ServiceGroups

```bash
POST /api/group/
Content-Type: application/json

{
  "code": "TEST",
  "name": "Test Group",
  "description": "Test group with services",
  "service_ids": [1, 2, 3]
}
```

**Résultat attendu:**
- Status 201 Created
- Group créé
- 3 ServiceGroups créés automatiquement

**Test avec service_ids invalides:**
```bash
POST /api/group/
Content-Type: application/json

{
  "code": "TEST2",
  "name": "Test Group 2",
  "service_ids": [999, 1000]
}
```

**Résultat attendu:**
- Status 400 Bad Request
- Message d'erreur sur services invalides

### 2.2 Lister les Groups avec expansion

```bash
GET /api/group/?expand=service_groups
```

**Résultat attendu:**
- Liste des groups avec service_groups étendus

**Expansion imbriquée:**
```bash
GET /api/group/?expand=service_groups.service,service_groups.group
```

### 2.3 Supprimer un Group

**Sans utilisateurs:**
```bash
DELETE /api/group/{id}/
```

**Résultat attendu:**
- Status 204 No Content
- Group et tous ses ServiceGroups supprimés

**Avec utilisateurs actifs:**
```bash
DELETE /api/group/{id_with_users}/
```

**Résultat attendu:**
- Status 400 Bad Request
- Message: "Impossible supprimer. X utilisateur(s) actif(s)."

## 3. Tests Employe

### 3.1 Créer un Employé avec ServiceGroup

```bash
POST /api/employe/
Content-Type: application/json

{
  "nom": "Dupont",
  "prenom": "Jean",
  "email": "jean.dupont@example.com",
  "poste_id": 1,
  ...autres champs requis...
}
```

**Résultat attendu:**
- Status 201 Created
- Employé créé avec poste_id référençant un ServiceGroup

### 3.2 Créer un Employé avec assignation UserGroup

```bash
POST /api/employe/
Content-Type: application/json

{
  "nom": "Martin",
  "prenom": "Marie",
  "email": "marie.martin@example.com",
  "poste_id": 1,
  "group_id": 1,
  ...autres champs requis...
}
```

**Résultat attendu:**
- Status 201 Created
- Employé créé
- User créé
- UserGroup créé automatiquement

### 3.3 Récupérer un Employé avec expansions

```bash
GET /api/employe/{id}/?expand=poste_id.service,poste_id.group
```

**Résultat attendu:**
- Employé avec ServiceGroup étendu
- Service et Group complets

**Expansion UserGroups:**
```bash
GET /api/employe/{id}/?expand=user_account.user_groups
```

**Résultat attendu:**
- Employé avec user_account étendu
- user_groups du user_account étendus

## 4. Tests UserGroup

### 4.1 Lister les UserGroups avec expansion

```bash
GET /api/user-group/?expand=user,group
```

**Résultat attendu:**
- Liste des UserGroups avec user et group étendus

**Expansion imbriquée:**
```bash
GET /api/user-group/?expand=user,group.service_groups
```

**Résultat attendu:**
- UserGroups avec group.service_groups étendus

## 5. Tests Champs Sparse et Omission

### 5.1 Champs Sparse

```bash
GET /api/service-group/?fields=id,service,group
```

**Résultat attendu:**
- Seulement les champs id, service, group dans la réponse

### 5.2 Omission de Champs

```bash
GET /api/service-group/?omit=created_at,updated_at
```

**Résultat attendu:**
- Tous les champs sauf created_at et updated_at

## 6. Tests de Performance

### 6.1 Vérifier N+1 Queries

**Sans expansion:**
```bash
GET /api/service-group/
```

**Avec expansion:**
```bash
GET /api/service-group/?expand=service,group
```

**Vérification:**
- Activer Django Debug Toolbar
- Compter le nombre de requêtes SQL
- Avec select_related: devrait être ≤ 3 requêtes

### 6.2 Test avec Pagination

```bash
GET /api/service-group/?page=1&page_size=10&expand=service,group
```

**Résultat attendu:**
- 10 résultats par page
- Requêtes optimisées même avec expansion

## 7. Tests d'Intégration

### 7.1 Workflow Complet: Création Group → ServiceGroups → Employé

1. Créer un Group avec service_ids
2. Vérifier que les ServiceGroups sont créés
3. Créer un Employé avec poste_id (ServiceGroup) et group_id
4. Vérifier que le UserGroup est créé
5. Récupérer l'Employé avec expansions complètes
6. Vérifier toutes les relations

### 7.2 Workflow Suppression

1. Créer un Group avec ServiceGroups
2. Supprimer un ServiceGroup
3. Vérifier que le Group existe toujours
4. Supprimer le dernier ServiceGroup
5. Vérifier que le Group est supprimé (si pas d'utilisateurs)

## 8. Tests d'Erreur

### 8.1 Validation des Données

- Créer ServiceGroup avec service_id invalide
- Créer ServiceGroup avec group_id invalide
- Créer Group avec service_ids en double
- Créer Employé avec group_id invalide

### 8.2 Contraintes d'Intégrité

- Créer ServiceGroup en double (même service + group)
- Supprimer Group avec utilisateurs actifs
- Supprimer dernier ServiceGroup d'un Group avec utilisateurs

## 9. Checklist de Validation

- [ ] Tous les endpoints ServiceGroup fonctionnent
- [ ] Création Group avec service_ids fonctionne
- [ ] Suppression cascade ServiceGroups fonctionne
- [ ] Protection suppression avec utilisateurs fonctionne
- [ ] Création Employé avec group_id crée UserGroup
- [ ] Expansions simples fonctionnent (expand=service)
- [ ] Expansions multiples fonctionnent (expand=service,group)
- [ ] Expansions imbriquées fonctionnent (expand=poste_id.service)
- [ ] Champs sparse fonctionnent (fields=id,name)
- [ ] Omission fonctionnent (omit=created_at)
- [ ] Requêtes optimisées (pas de N+1)
- [ ] Pagination fonctionne
- [ ] Validation des erreurs fonctionne
- [ ] Messages d'erreur en français et clairs

## 10. Résultats Attendus

### Système Opérationnel Si:

✓ Tous les endpoints répondent correctement
✓ Expansions dynamiques fonctionnent
✓ Contraintes d'intégrité respectées
✓ Performances optimales (requêtes SQL minimales)
✓ Messages d'erreur appropriés
✓ Transactions atomiques garantissent cohérence

### Problèmes Potentiels:

- Erreurs 500: Vérifier logs serveur
- Expansions ne fonctionnent pas: Vérifier permit_list_expands
- N+1 queries: Vérifier select_related/prefetch_related
- Contraintes violées: Vérifier validation serializers
