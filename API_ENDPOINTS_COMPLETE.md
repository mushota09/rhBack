# Documentation Complète des Endpoints API - RH Management System

## Table des Matières
1. [Authentification](#1-authentification)
2. [ServiceGroup](#2-servicegroup)
3. [Group](#3-group)
4. [Service](#4-service)
5. [UserGroup](#5-usergroup)
6. [Permission & GroupPermission](#6-permission--grouppermission)
7. [Employe](#7-employe)
8. [Contrat](#8-contrat)
9. [Document](#9-document)
10. [Paie](#10-paie)
11. [Congé](#11-congé)
12. [Paramètres d'Expansion](#12-paramètres-dexpansion)

---

## Base URL
```
http://localhost:8000/api/
```

## Headers Requis
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 1. Authentification

### 1.1 Login
**Endpoint:** `POST /api/user/login/`

**Description:** Authentifier un utilisateur et obtenir les tokens JWT.

**Body:**
```json
{
  "email": "admin@example.com",
  "password": "votre_mot_de_passe"
}
```

**Réponse (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "admin@example.com"
  }
}
```

### 1.2 Refresh Token
**Endpoint:** `POST /api/user/refresh/`

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Réponse (200 OK):**
```json
{
  "access": "nouveau_access_token..."
}
```

### 1.3 Logout
**Endpoint:** `POST /api/user/logout/`

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Réponse (200 OK):**
```json
{
  "message": "Déconnexion réussie"
}
```

### 1.4 Protected Route (Test)
**Endpoint:** `GET /api/user/protected/`

**Description:** Route protégée pour tester l'authentification.

**Réponse (200 OK):**
```json
{
  "message": "Accès autorisé",
  "user": "admin@example.com"
}
```

---

## 2. ServiceGroup

### 2.1 Lister les ServiceGroups
**Endpoint:** `GET /api/service-group/`

**Paramètres Query:**
- `page` (int): Numéro de page
- `page_size` (int): Éléments par page
- `expand` (string): Champs à étendre
- `fields` (string): Champs à inclure
- `omit` (string): Champs à exclure
- `search` (string): Recherche
- `ordering` (string): Tri

**Exemples:**
```bash
# Liste simple
GET /api/service-group/

# Avec expansion
GET /api/service-group/?expand=service,group

# Avec pagination
GET /api/service-group/?page=1&page_size=20

# Avec champs sparse
GET /api/service-group/?fields=id,service,group

# Avec omission
GET /api/service-group/?omit=created_at,updated_at
```

**Réponse (200 OK):**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/service-group/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "service": 1,
      "group": 1,
      "created_at": "2026-02-13T10:00:00Z",
      "updated_at": "2026-02-13T10:00:00Z"
    }
  ]
}
```

**Avec expansion:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "service": {
        "id": 1,
        "code": "IT",
        "titre": "Informatique"
      },
      "group": {
        "id": 1,
        "code": "DEV",
        "name": "Développeurs"
      }
    }
  ]
}
```

### 2.2 Récupérer un ServiceGroup
**Endpoint:** `GET /api/service-group/{id}/`

**Exemple:**
```bash
GET /api/service-group/1/?expand=service,group
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "service": {
    "id": 1,
    "code": "IT",
    "titre": "Informatique",
    "description": "Service informatique"
  },
  "group": {
    "id": 1,
    "code": "DEV",
    "name": "Développeurs",
    "description": "Groupe des développeurs"
  },
  "created_at": "2026-02-13T10:00:00Z",
  "updated_at": "2026-02-13T10:00:00Z"
}
```

### 2.3 Créer un ServiceGroup
**Endpoint:** `POST /api/service-group/`

**Body:**
```json
{
  "service": 1,
  "group": 1
}
```

**Réponse (201 Created):**
```json
{
  "id": 2,
  "service": 1,
  "group": 1,
  "created_at": "2026-02-13T11:00:00Z",
  "updated_at": "2026-02-13T11:00:00Z"
}
```

**Erreur - Contrainte unique (409 Conflict):**
```json
{
  "error": "ServiceGroup existe déjà pour Informatique et Développeurs"
}
```

### 2.4 Mettre à jour un ServiceGroup
**Endpoint:** `PUT /api/service-group/{id}/`
**Endpoint:** `PATCH /api/service-group/{id}/`

**Body (PUT - tous les champs):**
```json
{
  "service": 2,
  "group": 1
}
```

**Body (PATCH - champs partiels):**
```json
{
  "group": 2
}
```

### 2.5 Supprimer un ServiceGroup
**Endpoint:** `DELETE /api/service-group/{id}/`

**Comportement:**
- Si le Group a d'autres ServiceGroups: Supprime uniquement ce ServiceGroup
- Si c'est le dernier ServiceGroup ET le Group n'a pas d'utilisateurs: Supprime le ServiceGroup ET le Group
- Si c'est le dernier ServiceGroup ET le Group a des utilisateurs: Erreur 400

**Réponse (204 No Content):** Suppression réussie

**Erreur - Group avec utilisateurs (400 Bad Request):**
```json
{
  "error": "Impossible de supprimer. Le groupe a 5 utilisateur(s) actif(s)."
}
```

---

## 3. Group

### 3.1 Lister les Groups
**Endpoint:** `GET /api/group/`

**Paramètres Query:**
- `expand`: `service_groups`, `user_groups`, `group_permissions`
- `search`: Recherche par code ou name
- `ordering`: Tri (ex: `code`, `-created_at`)
- `is_active`: Filtrer par statut (true/false)

**Exemples:**
```bash
# Liste simple
GET /api/group/

# Avec expansion des ServiceGroups
GET /api/group/?expand=service_groups

# Avec expansion imbriquée
GET /api/group/?expand=service_groups.service,service_groups.group

# Avec expansion multiple
GET /api/group/?expand=service_groups,user_groups,group_permissions

# Recherche
GET /api/group/?search=DEV

# Filtrer actifs
GET /api/group/?is_active=true
```

**Réponse (200 OK):**
```json
{
  "count": 22,
  "results": [
    {
      "id": 1,
      "code": "DEV",
      "name": "Développeurs",
      "description": "Groupe des développeurs",
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

**Avec expansion service_groups:**
```json
{
  "count": 22,
  "results": [
    {
      "id": 1,
      "code": "DEV",
      "name": "Développeurs",
      "service_groups": [
        {
          "id": 1,
          "service": {
            "id": 1,
            "code": "IT",
            "titre": "Informatique"
          },
          "group": 1
        },
        {
          "id": 2,
          "service": {
            "id": 2,
            "code": "RH",
            "titre": "Ressources Humaines"
          },
          "group": 1
        }
      ]
    }
  ]
}
```

### 3.2 Récupérer un Group
**Endpoint:** `GET /api/group/{id}/`

**Exemple:**
```bash
GET /api/group/1/?expand=service_groups,user_groups
```

### 3.3 Créer un Group
**Endpoint:** `POST /api/group/`

**Body (sans ServiceGroups):**
```json
{
  "code": "TEST",
  "name": "Test Group",
  "description": "Groupe de test",
  "is_active": true
}
```

**Body (avec ServiceGroups automatiques):**
```json
{
  "code": "TEST",
  "name": "Test Group",
  "description": "Groupe de test",
  "is_active": true,
  "service_ids": [1, 2, 3]
}
```

**Réponse (201 Created):**
```json
{
  "id": 23,
  "code": "TEST",
  "name": "Test Group",
  "description": "Groupe de test",
  "is_active": true,
  "created_at": "2026-02-13T12:00:00Z"
}
```

**Note:** Si `service_ids` est fourni, les ServiceGroups sont créés automatiquement.

**Erreur - service_ids invalides (400 Bad Request):**
```json
{
  "error": "Services invalides: [999, 1000]"
}
```

### 3.4 Mettre à jour un Group
**Endpoint:** `PUT /api/group/{id}/`
**Endpoint:** `PATCH /api/group/{id}/`

**Body:**
```json
{
  "name": "Nouveau nom",
  "description": "Nouvelle description"
}
```

### 3.5 Supprimer un Group
**Endpoint:** `DELETE /api/group/{id}/`

**Comportement:**
- Vérifie si le Group a des utilisateurs actifs (UserGroups)
- Si oui: Erreur 400
- Si non: Supprime le Group et tous ses ServiceGroups en cascade

**Réponse (204 No Content):** Suppression réussie

**Erreur - Utilisateurs actifs (400 Bad Request):**
```json
{
  "error": "Impossible de supprimer le groupe. 3 utilisateur(s) actif(s) assigné(s)."
}
```

---

## 4. Service

### 4.1 Lister les Services
**Endpoint:** `GET /api/service/`

**Paramètres Query:**
- `search`: Recherche par code ou titre
- `ordering`: Tri
- `is_active`: Filtrer par statut

**Exemples:**
```bash
GET /api/service/
GET /api/service/?search=IT
GET /api/service/?ordering=code
```

**Réponse (200 OK):**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "code": "IT",
      "titre": "Informatique",
      "description": "Service informatique",
      "is_active": true
    }
  ]
}
```

### 4.2 Récupérer un Service
**Endpoint:** `GET /api/service/{id}/`

### 4.3 Créer un Service
**Endpoint:** `POST /api/service/`

**Body:**
```json
{
  "code": "FIN",
  "titre": "Finance",
  "description": "Service financier",
  "is_active": true
}
```

### 4.4 Mettre à jour un Service
**Endpoint:** `PUT /api/service/{id}/`
**Endpoint:** `PATCH /api/service/{id}/`

### 4.5 Supprimer un Service
**Endpoint:** `DELETE /api/service/{id}/`

---

## 5. UserGroup

### 5.1 Lister les UserGroups
**Endpoint:** `GET /api/user-group/`

**Paramètres Query:**
- `expand`: `user`, `group`, `assigned_by`, `user.employe_id`, `group.service_groups`
- `user`: Filtrer par user_id
- `group`: Filtrer par group_id
- `is_active`: Filtrer par statut

**Exemples:**
```bash
# Liste simple
GET /api/user-group/

# Avec expansion
GET /api/user-group/?expand=user,group

# Expansion imbriquée
GET /api/user-group/?expand=user.employe_id,group.service_groups

# Filtrer par utilisateur
GET /api/user-group/?user=1

# Filtrer par groupe
GET /api/user-group/?group=1

# Utilisateurs actifs d'un groupe
GET /api/user-group/?group=1&is_active=true
```

**Réponse (200 OK):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "user": 1,
      "group": 1,
      "assigned_by": 1,
      "assigned_at": "2026-02-13T10:00:00Z",
      "is_active": true
    }
  ]
}
```

**Avec expansion:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User"
      },
      "group": {
        "id": 1,
        "code": "DEV",
        "name": "Développeurs",
        "service_groups": [
          {
            "id": 1,
            "service": {
              "id": 1,
              "code": "IT",
              "titre": "Informatique"
            }
          }
        ]
      },
      "assigned_by": {
        "id": 1,
        "email": "admin@example.com"
      },
      "assigned_at": "2026-02-13T10:00:00Z",
      "is_active": true
    }
  ]
}
```

### 5.2 Récupérer un UserGroup
**Endpoint:** `GET /api/user-group/{id}/`

### 5.3 Créer un UserGroup
**Endpoint:** `POST /api/user-group/`

**Body:**
```json
{
  "user": 2,
  "group": 1,
  "is_active": true
}
```

**Note:** `assigned_by` est automatiquement défini à l'utilisateur authentifié.

### 5.4 Mettre à jour un UserGroup
**Endpoint:** `PUT /api/user-group/{id}/`
**Endpoint:** `PATCH /api/user-group/{id}/`

**Body (désactiver):**
```json
{
  "is_active": false
}
```

### 5.5 Supprimer un UserGroup
**Endpoint:** `DELETE /api/user-group/{id}/`

---

## 6. Permission & GroupPermission

### 6.1 Lister les Permissions
**Endpoint:** `GET /api/permission/`

**Description:** Liste toutes les permissions système (lecture seule).

**Réponse (200 OK):**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "name": "Can add user",
      "codename": "add_user",
      "content_type": 1,
      "content_type_name": "user"
    }
  ]
}
```

### 6.2 Récupérer une Permission
**Endpoint:** `GET /api/permission/{id}/`

### 6.3 Lister les GroupPermissions
**Endpoint:** `GET /api/group-permission/`

**Paramètres Query:**
- `expand`: `group`, `permission`, `created_by`
- `group`: Filtrer par group_id
- `permission`: Filtrer par permission_id

**Exemples:**
```bash
# Liste simple
GET /api/group-permission/

# Avec expansion
GET /api/group-permission/?expand=group,permission

# Permissions d'un groupe
GET /api/group-permission/?group=1&expand=permission
```

**Réponse (200 OK):**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "group": 1,
      "permission": 1,
      "created_by": 1,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

**Avec expansion:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "group": {
        "id": 1,
        "code": "DEV",
        "name": "Développeurs"
      },
      "permission": {
        "id": 1,
        "name": "Can add user",
        "codename": "add_user"
      },
      "created_by": {
        "id": 1,
        "email": "admin@example.com"
      }
    }
  ]
}
```

### 6.4 Créer un GroupPermission
**Endpoint:** `POST /api/group-permission/`

**Body:**
```json
{
  "group": 1,
  "permission": 5
}
```

### 6.5 Supprimer un GroupPermission
**Endpoint:** `DELETE /api/group-permission/{id}/`

---

## 7. Employe

### 7.1 Lister les Employés
**Endpoint:** `GET /api/employees/`

**Paramètres Query:**
- `expand`: `poste_id`, `poste_id.service`, `poste_id.group`, `user_account`, `user_account.user_groups`
- `search`: Recherche par nom, prénom, email
- `poste_id`: Filtrer par ServiceGroup
- `is_active`: Filtrer par statut

**Exemples:**
```bash
# Liste simple
GET /api/employees/

# Avec expansion du poste (ServiceGroup)
GET /api/employees/?expand=poste_id

# Avec expansion imbriquée du service et groupe
GET /api/employees/?expand=poste_id.service,poste_id.group

# Avec expansion du compte utilisateur et ses groupes
GET /api/employees/?expand=user_account,user_account.user_groups

# Recherche
GET /api/employees/?search=Dupont

# Filtrer par poste
GET /api/employees/?poste_id=1
```

**Réponse (200 OK):**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "nom": "Dupont",
      "prenom": "Jean",
      "email": "jean.dupont@example.com",
      "telephone": "+33612345678",
      "date_naissance": "1990-01-15",
      "lieu_naissance": "Paris",
      "adresse": "123 Rue de la Paix",
      "poste_id": 1,
      "user_account": 2,
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

**Avec expansion complète:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "nom": "Dupont",
      "prenom": "Jean",
      "email": "jean.dupont@example.com",
      "poste_id": {
        "id": 1,
        "service": {
          "id": 1,
          "code": "IT",
          "titre": "Informatique"
        },
        "group": {
          "id": 1,
          "code": "DEV",
          "name": "Développeurs"
        }
      },
      "user_account": {
        "id": 2,
        "email": "jean.dupont@example.com",
        "user_groups": [
          {
            "id": 5,
            "group": {
              "id": 1,
              "code": "DEV",
              "name": "Développeurs"
            }
          }
        ]
      }
    }
  ]
}
```

### 7.2 Récupérer un Employé
**Endpoint:** `GET /api/employees/{id}/`

**Exemple:**
```bash
GET /api/employees/1/?expand=poste_id.service,poste_id.group,user_account.user_groups
```

### 7.3 Créer un Employé
**Endpoint:** `POST /api/employees/`

**Body (sans assignation de groupe):**
```json
{
  "nom": "Martin",
  "prenom": "Marie",
  "email": "marie.martin@example.com",
  "telephone": "+33612345679",
  "date_naissance": "1992-05-20",
  "lieu_naissance": "Lyon",
  "adresse": "456 Avenue des Champs",
  "poste_id": 1,
  "is_active": true
}
```

**Body (avec assignation automatique de groupe):**
```json
{
  "nom": "Martin",
  "prenom": "Marie",
  "email": "marie.martin@example.com",
  "telephone": "+33612345679",
  "date_naissance": "1992-05-20",
  "lieu_naissance": "Lyon",
  "adresse": "456 Avenue des Champs",
  "poste_id": 1,
  "group_id": 1,
  "is_active": true
}
```

**Note:**
- Si `group_id` est fourni, un compte utilisateur (User) est créé automatiquement
- Un UserGroup est créé pour lier l'utilisateur au groupe
- `assigned_by` est défini à l'utilisateur authentifié

**Réponse (201 Created):**
```json
{
  "id": 51,
  "nom": "Martin",
  "prenom": "Marie",
  "email": "marie.martin@example.com",
  "poste_id": 1,
  "user_account": 25,
  "is_active": true,
  "created_at": "2026-02-13T14:00:00Z"
}
```

**Erreur - group_id invalide (400 Bad Request):**
```json
{
  "error": "Groupe invalide ou inactif"
}
```

### 7.4 Mettre à jour un Employé
**Endpoint:** `PUT /api/employees/{id}/`
**Endpoint:** `PATCH /api/employees/{id}/`

**Body:**
```json
{
  "telephone": "+33612345680",
  "adresse": "789 Boulevard Nouveau"
}
```

### 7.5 Supprimer un Employé
**Endpoint:** `DELETE /api/employees/{id}/`

---

## 8. Contrat

### 8.1 Lister les Contrats
**Endpoint:** `GET /api/contracts/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `type_contrat`: Filtrer par type
- `is_active`: Filtrer par statut

**Exemples:**
```bash
GET /api/contracts/
GET /api/contracts/?employe=1
GET /api/contracts/?type_contrat=CDI
```

**Réponse (200 OK):**
```json
{
  "count": 30,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "type_contrat": "CDI",
      "date_debut": "2025-01-01",
      "date_fin": null,
      "salaire_base": 45000.00,
      "is_active": true
    }
  ]
}
```

### 8.2 Récupérer un Contrat
**Endpoint:** `GET /api/contracts/{id}/`

### 8.3 Créer un Contrat
**Endpoint:** `POST /api/contracts/`

**Body:**
```json
{
  "employe": 1,
  "type_contrat": "CDI",
  "date_debut": "2026-03-01",
  "salaire_base": 50000.00,
  "is_active": true
}
```

### 8.4 Mettre à jour un Contrat
**Endpoint:** `PUT /api/contracts/{id}/`
**Endpoint:** `PATCH /api/contracts/{id}/`

### 8.5 Supprimer un Contrat
**Endpoint:** `DELETE /api/contracts/{id}/`

---

## 9. Document

### 9.1 Lister les Documents
**Endpoint:** `GET /api/documents/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `type_document`: Filtrer par type

**Exemples:**
```bash
GET /api/documents/
GET /api/documents/?employe=1
GET /api/documents/?type_document=CV
```

**Réponse (200 OK):**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "type_document": "CV",
      "titre": "CV Jean Dupont",
      "fichier": "/media/documents/cv_jean_dupont.pdf",
      "date_upload": "2026-01-15T10:00:00Z"
    }
  ]
}
```

### 9.2 Récupérer un Document
**Endpoint:** `GET /api/documents/{id}/`

### 9.3 Créer un Document
**Endpoint:** `POST /api/document

**Paramètres Query:**
- `annee`: Filtrer par année
- `mois`: Filtrer par mois
- `is_closed`: Filtrer par statut (true/false)

**Exemples:**
```bash
GET /api/paie/periode_paie/
GET /api/paie/periode_paie/?annee=2026
GET /api/paie/periode_paie/?annee=2026&mois=2
GET /api/paie/periode_paie/?is_closed=false
```

**Réponse (200 OK):**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "annee": 2026,
      "mois": 2,
      "date_debut": "2026-02-01",
      "date_fin": "2026-02-28",
      "is_closed": false,
      "created_at": "2026-02-01T00:00:00Z"
    }
  ]
}
```

#### 10.1.2 Créer une Période
**Endpoint:** `POST /api/paie/periode_paie/`

**Body:**
```json
{
  "annee": 2026,
  "mois": 3,
  "date_debut": "2026-03-01",
  "date_fin": "2026-03-31"
}
```

#### 10.1.3 Clôturer une Période
**Endpoint:** `PATCH /api/paie/periode_paie/{id}/`

**Body:**
```json
{
  "is_closed": true
}
```

### 10.2 Entrée de Paie

#### 10.2.1 Lister les Entrées
**Endpoint:** `GET /api/paie/entree_paie/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `periode`: Filtrer par periode_paie_id
- `type_entree`: Filtrer par type

**Exemples:**
```bash
GET /api/paie/entree_paie/
GET /api/paie/entree_paie/?employe=1
GET /api/paie/entree_paie/?periode=1
GET /api/paie/entree_paie/?type_entree=SALAIRE
```

**Réponse (200 OK):**
```json
{
  "count": 200,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "periode": 1,
      "type_entree": "SALAIRE",
      "montant": 45000.00,
      "description": "Salaire de base",
      "created_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

#### 10.2.2 Créer une Entrée
**Endpoint:** `POST /api/paie/entree_paie/`

**Body:**
```json
{
  "employe": 1,
  "periode": 1,
  "type_entree": "PRIME",
  "montant": 5000.00,
  "description": "Prime de performance"
}
```

### 10.3 Retenue Employé

#### 10.3.1 Lister les Retenues
**Endpoint:** `GET /api/paie/retenue_employe/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `periode`: Filtrer par periode_paie_id
- `type_retenue`: Filtrer par type

**Exemples:**
```bash
GET /api/paie/retenue_employe/
GET /api/paie/retenue_employe/?employe=1
GET /api/paie/retenue_employe/?type_retenue=COTISATION
```

**Réponse (200 OK):**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "periode": 1,
      "type_retenue": "COTISATION",
      "montant": 2500.00,
      "description": "Cotisation sociale",
      "created_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

#### 10.3.2 Créer une Retenue
**Endpoint:** `POST /api/paie/retenue_employe/`

**Body:**
```json
{
  "employe": 1,
  "periode": 1,
  "type_retenue": "IMPOT",
  "montant": 3000.00,
  "description": "Impôt sur le revenu"
}
```

### 10.4 Rapports d'Audit

#### 10.4.1 Rapport de Paie
**Endpoint:** `GET /api/paie/audit/rapport-paie/`

**Paramètres Query:**
- `periode`: ID de la période (requis)
- `employe`: ID de l'employé (optionnel)

**Exemple:**
```bash
GET /api/paie/audit/rapport-paie/?periode=1
GET /api/paie/audit/rapport-paie/?periode=1&employe=1
```

---

## 11. Congé

### 11.1 Type de Congé

#### 11.1.1 Lister les Types
**Endpoint:** `GET /api/type_conge/`

**Réponse (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "code": "CP",
      "libelle": "Congé Payé",
      "nombre_jours_max": 30,
      "is_active": true
    }
  ]
}
```

#### 11.1.2 Créer un Type
**Endpoint:** `POST /api/type_conge/`

**Body:**
```json
{
  "code": "CM",
  "libelle": "Congé Maladie",
  "nombre_jours_max": 90,
  "is_active": true
}
```

### 11.2 Solde de Congé

#### 11.2.1 Lister les Soldes
**Endpoint:** `GET /api/solde_conge/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `type_conge`: Filtrer par type_conge_id
- `annee`: Filtrer par année

**Exemples:**
```bash
GET /api/solde_conge/
GET /api/solde_conge/?employe=1
GET /api/solde_conge/?employe=1&annee=2026
```

**Réponse (200 OK):**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "type_conge": 1,
      "annee": 2026,
      "solde_initial": 30,
      "solde_pris": 5,
      "solde_restant": 25
    }
  ]
}
```

#### 11.2.2 Créer un Solde
**Endpoint:** `POST /api/solde_conge/`

**Body:**
```json
{
  "employe": 1,
  "type_conge": 1,
  "annee": 2026,
  "solde_initial": 30
}
```

### 11.3 Demande de Congé

#### 11.3.1 Lister les Demandes
**Endpoint:** `GET /api/demande_conge/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `type_conge`: Filtrer par type_conge_id
- `statut`: Filtrer par statut (EN_ATTENTE, APPROUVE, REFUSE)
- `date_debut`: Filtrer par date de début (>=)
- `date_fin`: Filtrer par date de fin (<=)

**Exemples:**
```bash
GET /api/demande_conge/
GET /api/demande_conge/?employe=1
GET /api/demande_conge/?statut=EN_ATTENTE
GET /api/demande_conge/?date_debut=2026-03-01
```

**Réponse (200 OK):**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "type_conge": 1,
      "date_debut": "2026-03-15",
      "date_fin": "2026-03-20",
      "nombre_jours": 5,
      "motif": "Vacances familiales",
      "statut": "EN_ATTENTE",
      "created_at": "2026-02-13T10:00:00Z"
    }
  ]
}
```

#### 11.3.2 Créer une Demande
**Endpoint:** `POST /api/demande_conge/`

**Body:**
```json
{
  "employe": 1,
  "type_conge": 1,
  "date_debut": "2026-03-15",
  "date_fin": "2026-03-20",
  "motif": "Vacances familiales"
}
```

**Note:** Le nombre de jours est calculé automatiquement.

#### 11.3.3 Approuver/Refuser une Demande
**Endpoint:** `PATCH /api/demande_conge/{id}/`

**Body (Approuver):**
```json
{
  "statut": "APPROUVE"
}
```

**Body (Refuser):**
```json
{
  "statut": "REFUSE",
  "motif_refus": "Période de forte activité"
}
```

### 11.4 Historique de Congé

#### 11.4.1 Lister l'Historique
**Endpoint:** `GET /api/historique_conge/`

**Paramètres Query:**
- `employe`: Filtrer par employe_id
- `type_conge`: Filtrer par type_conge_id
- `annee`: Filtrer par année

**Exemples:**
```bash
GET /api/historique_conge/
GET /api/historique_conge/?employe=1
GET /api/historique_conge/?annee=2026
```

**Réponse (200 OK):**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "employe": 1,
      "type_conge": 1,
      "date_debut": "2026-01-10",
      "date_fin": "2026-01-15",
      "nombre_jours": 5,
      "statut": "TERMINE",
      "created_at": "2026-01-05T10:00:00Z"
    }
  ]
}
```

---

## 12. Paramètres d'Expansion

### 12.1 Expansion Simple
Étendre un seul champ relationnel.

**Syntaxe:**
```
?expand=field_name
```

**Exemples:**
```bash
GET /api/service-group/?expand=service
GET /api/user-group/?expand=group
GET /api/employees/?expand=poste_id
```

### 12.2 Expansion Multiple
Étendre plusieurs champs relationnels.

**Syntaxe:**
```
?expand=field1,field2,field3
```

**Exemples:**
```bash
GET /api/service-group/?expand=service,group
GET /api/user-group/?expand=user,group,assigned_by
GET /api/group/?expand=service_groups,user_groups,group_permissions
```

### 12.3 Expansion Imbriquée
Étendre des champs relationnels à plusieurs niveaux.

**Syntaxe:**
```
?expand=field.nested_field
?expand=field.nested_field.deep_field
```

**Exemples:**
```bash
# Étendre le ServiceGroup et son service
GET /api/employees/?expand=poste_id.service

# Étendre le ServiceGroup, son service et son groupe
GET /api/employees/?expand=poste_id.service,poste_id.group

# Étendre le user_account et ses user_groups
GET /api/employees/?expand=user_account.user_groups

# Étendre le groupe et ses service_groups
GET /api/user-group/?expand=group.service_groups

# Expansion profonde
GET /api/user-group/?expand=group.service_groups.service
```

### 12.4 Champs Sparse (fields)
Inclure uniquement les champs spécifiés dans la réponse.

**Syntaxe:**
```
?fields=field1,field2,field3
```

**Exemples:**
```bash
# Seulement id et nom
GET /api/group/?fields=id,code,name

# Seulement les champs essentiels
GET /api/employees/?fields=id,nom,prenom,email

# Combiné avec expansion
GET /api/service-group/?fields=id,service,group&expand=service,group
```

**Réponse avec fields:**
```json
{
  "count": 22,
  "results": [
    {
      "id": 1,
      "code": "DEV",
      "name": "Développeurs"
    }
  ]
}
```

### 12.5 Omission de Champs (omit)
Exclure des champs spécifiques de la réponse.

**Syntaxe:**
```
?omit=field1,field2,field3
```

**Exemples:**
```bash
# Exclure les timestamps
GET /api/service-group/?omit=created_at,updated_at

# Exclure les champs sensibles
GET /api/employees/?omit=salaire,date_naissance

# Combiné avec expansion
GET /api/group/?expand=service_groups&omit=created_at,updated_at
```

**Réponse avec omit:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "service": 1,
      "group": 1
    }
  ]
}
```

### 12.6 Combinaison de Paramètres
Combiner plusieurs paramètres pour des requêtes optimisées.

**Exemples:**
```bash
# Expansion + Pagination
GET /api/service-group/?expand=service,group&page=1&page_size=20

# Expansion + Recherche
GET /api/employees/?expand=poste_id.service&search=Dupont

# Expansion + Filtrage
GET /api/user-group/?expand=user,group&group=1&is_active=true

# Expansion + Tri
GET /api/group/?expand=service_groups&ordering=-created_at

# Expansion + Fields + Omit
GET /api/employees/?expand=poste_id&fields=id,nom,prenom,poste_id&omit=created_at

# Expansion imbriquée + Filtrage + Pagination
GET /api/employees/?expand=poste_id.service,user_account.user_groups&poste_id=1&page=1&page_size=10
```

### 12.7 Limites d'Expansion

**Profondeur maximale:** 3 niveaux
- ✅ `expand=field.nested.deep` (3 niveaux)
- ❌ `expand=field.nested.deep.too_deep` (4 niveaux - non supporté)

**Expansions en mode liste:**
Certaines expansions sont limitées en mode liste via `permit_list_expands`.

**Exemples:**
```bash
# ServiceGroupViewSet
permit_list_expands = ['service', 'group']

# GroupViewSet
permit_list_expands = ['service_groups', 'user_groups', 'group_permissions']

# EmployeViewSet
permit_list_expands = ['poste_id', 'poste_id.service', 'poste_id.group',
                       'user_account', 'user_account.user_groups']
```

---

## 13. Codes de Réponse HTTP

### Succès
- **200 OK**: Requête réussie
- **201 Created**: Ressource créée avec succès
- **204 No Content**: Suppression réussie

### Erreurs Client
- **400 Bad Request**: Données invalides ou contraintes violées
- **401 Unauthorized**: Non authentifié
- **403 Forbidden**: Non autorisé
- **404 Not Found**: Ressource introuvable
- **409 Conflict**: Conflit (ex: contrainte unique violée)

### Erreurs Serveur
- **500 Internal Server Error**: Erreur serveur

---

## 14. Exemples de Workflows Complets

### 14.1 Créer un Groupe avec Services et Assigner un Employé

**Étape 1: Créer le Group avec ServiceGroups**
```bash
POST /api/group/
{
  "code": "NEWTEAM",
  "name": "Nouvelle Équipe",
  "description": "Équipe de développement",
  "service_ids": [1, 2]
}
```

**Étape 2: Créer un Employé et l'assigner au Group**
```bash
POST /api/employees/
{
  "nom": "Nouveau",
  "prenom": "Employé",
  "email": "nouveau@example.com",
  "poste_id": 1,
  "group_id": 23,
  ...
}
```

**Étape 3: Vérifier l'assignation**
```bash
GET /api/employees/51/?expand=poste_id.service,poste_id.group,user_account.user_groups
```

### 14.2 Gérer les Permissions d'un Groupe

**Étape 1: Lister les permissions disponibles**
```bash
GET /api/permission/?search=user
```

**Étape 2: Assigner des permissions au groupe**
```bash
POST /api/group-permission/
{
  "group": 1,
  "permission": 5
}

POST /api/group-permission/
{
  "group": 1,
  "permission": 6
}
```

**Étape 3: Vérifier les permissions du groupe**
```bash
GET /api/group-permission/?group=1&expand=permission
```

### 14.3 Gérer les Congés d'un Employé

**Étape 1: Vérifier le solde de congés**
```bash
GET /api/solde_conge/?employe=1&annee=2026
```

**Étape 2: Créer une demande de congé**
```bash
POST /api/demande_conge/
{
  "employe": 1,
  "type_conge": 1,
  "date_debut": "2026-03-15",
  "date_fin": "2026-03-20",
  "motif": "Vacances"
}
```

**Étape 3: Approuver la demande**
```bash
PATCH /api/demande_conge/1/
{
  "statut": "APPROUVE"
}
```

**Étape 4: Vérifier l'historique**
```bash
GET /api/historique_conge/?employe=1
```

### 14.4 Traiter la Paie d'un Employé

**Étape 1: Créer une période de paie**
```bash
POST /api/paie/periode_paie/
{
  "annee": 2026,
  "mois": 3,
  "date_debut": "2026-03-01",
  "date_fin": "2026-03-31"
}
```

**Étape 2: Ajouter les entrées de paie**
```bash
POST /api/paie/entree_paie/
{
  "employe

GET /api/paie/audit/rapport-paie/?periode=1&employe=1
```

**Étape 5: Clôturer la période**
```bash
PATCH /api/paie/periode_paie/1/
{
  "is_closed": true
}
```

---

## 15. Bonnes Pratiques

### 15.1 Authentification
- Toujours inclure le token Bearer dans les headers
- Rafraîchir le token avant expiration
- Déconnecter proprement avec le endpoint logout

### 15.2 Expansion
- Utiliser l'expansion pour réduire le nombre de requêtes
- Ne pas abuser de l'expansion imbriquée (max 3 niveaux)
- Utiliser `fields` pour limiter les données transférées
- Utiliser `omit` pour exclure les champs non nécessaires

### 15.3 Pagination
- Toujours utiliser la pagination pour les listes volumineuses
- Ajuster `page_size` selon les besoins (défaut: 10, max: 100)
- Utiliser les liens `next` et `previous` pour naviguer

### 15.4 Filtrage et Recherche
- Utiliser les filtres pour réduire les données côté serveur
- Combiner filtres et expansion pour des requêtes optimisées
- Utiliser `search` pour la recherche textuelle

### 15.5 Performance
- Éviter les requêtes N+1 en utilisant l'expansion
- Utiliser `fields` pour réduire la taille des réponses
- Mettre en cache les données statiques (permissions, types)
- Utiliser la pagination pour les grandes listes

### 15.6 Gestion des Erreurs
- Toujours vérifier le code de statut HTTP
- Lire les messages d'erreur pour comprendre le problème
- Gérer les erreurs 401 (renouveler le token)
- Gérer les erreurs 400 (valider les données côté client)

---

## 16. Documentation Interactive

### Swagger UI
**URL:** `http://localhost:8000/api/docs/`

Interface interactive pour tester tous les endpoints avec:
- Documentation complète de chaque endpoint
- Schémas de requête/réponse
- Possibilité de tester directement depuis le navigateur
- Authentification intégrée

### ReDoc
**URL:** `http://localhost:8000/api/redoc/`

Documentation alternative avec:
- Présentation claire et organisée
- Recherche rapide
- Exemples de code
- Schémas détaillés

### Schema OpenAPI
**URL:** `http://localhost:8000/api/schema/`

Schéma OpenAPI 3.0 complet pour:
- Génération de clients API
- Intégration avec des outils tiers
- Documentation automatique

---

## 17. Support et Contact

Pour toute question ou problème:
1. Consulter cette documentation
2. Vérifier la documentation interactive (Swagger/ReDoc)
3. Consulter les tests unitaires dans `user_app/tests/`
4. Consulter les spécifications dans `.kiro/specs/service-group-management/`

---

**Version:** 1.0.0
**Date:** 13 février 2026
**Statut:** Production Ready ✅
