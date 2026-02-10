# Exemples d'Utilisation de l'API - Gestion des Utilisateurs

## Table des Matières

1. [Authentification](#authentification)
2. [Gestion des Groupes](#gestion-des-groupes)
3. [Assignation Utilisateur-Groupe](#assignation-utilisateur-groupe)
4. [Gestion des Permissions](#gestion-des-permissions)
5. [Audit et Traçabilité](#audit-et-traçabilité)
6. [Cas d'Usage Avancés](#cas-dusage-avancés)

## Authentification

### Connexion d'un utilisateur

**Requête :**
```bash
curl -X POST http://localhost:8000/api/user/
curl -X POST http://localhost:8000/api/user/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDQ5OTg0MDB9.def456"
  }'
```

**Réponse :**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MDQxNTM2MDB9.xyz789"
}
```

## Gestion des Groupes

### Lister tous les groupes

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/group/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Réponse :**
```json
{
  "count": 21,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "code": "ADM",
      "name": "Administrateur",
      "description": "Accès complet au système",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "code": "RRH",
      "name": "Responsable Ressources Humaines",
      "description": "Gestion des ressources humaines",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "total_groups": 21,
    "active_groups": 21
  }
}
```

### Rechercher des groupes

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/group/?search=responsable&is_active=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Créer un nouveau groupe

**Requête :**
```bash
curl -X POST http://localhost:8000/api/user/group/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "TEST",
    "name": "Groupe Test",
    "description": "Groupe de test pour démonstration",
    "is_active": true
  }'
```

**Réponse :**
```json
{
  "id": 22,
  "code": "TEST",
  "name": "Groupe Test",
  "description": "Groupe de test pour démonstration",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Mettre à jour un groupe

**Requête :**
```bash
curl -X PATCH http://localhost:8000/api/user/group/22/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Description mise à jour"
  }'
```

## Assignation Utilisateur-Groupe

### Assigner un utilisateur à un groupe

**Requête :**
```bash
curl -X POST http://localhost:8000/api/user/user-group/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 5,
    "group": 2
  }'
```

**Réponse :**
```json
{
  "id": 10,
  "user": {
    "id": 5,
    "email": "employee@company.com",
    "nom": "Dupont",
    "prenom": "Jean"
  },
  "group": {
    "id": 2,
    "code": "RRH",
    "name": "Responsable Ressources Humaines"
  },
  "assigned_by": {
    "id": 1,
    "email": "admin@company.com"
  },
  "assigned_at": "2024-01-15T10:45:00Z",
  "is_active": true
}
```

### Assignation en masse

**Requête :**
```bash
curl -X POST http://localhost:8000/api/user/user-group/bulk-assign/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [3, 4, 5, 6],
    "group_id": 2,
    "action": "assign"
  }'
```

**Réponse :**
```json
{
  "message": "Opération assign terminée",
  "group": {
    "id": 2,
    "code": "RRH",
    "name": "Responsable Ressources Humaines"
  },
  "results": [
    {
      "user_id": 3,
      "user_email": "user3@company.com",
      "status": "assigned",
      "assignment_id": 11
    },
    {
      "user_id": 4,
      "user_email": "user4@company.com",
      "status": "assigned",
      "assignment_id": 12
    },
    {
      "user_id": 5,
      "user_email": "user5@company.com",
      "status": "already_assigned"
    },
    {
      "user_id": 6,
      "user_email": "user6@company.com",
      "status": "assigned",
      "assignment_id": 13
    }
  ],
  "summary": {
    "total_users": 4,
    "processed": 4,
    "successful": 3,
    "failed": 1
  }
}
```

### Récupérer les groupes d'un utilisateur

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/user-group/by-user/5/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Réponse :**
```json
{
  "user": {
    "id": 5,
    "email": "employee@company.com",
    "nom": "Dupont",
    "prenom": "Jean"
  },
  "assignments": [
    {
      "id": 10,
      "group": {
        "id": 2,
        "code": "RRH",
        "name": "Responsable Ressources Humaines"
      },
      "assigned_at": "2024-01-15T10:45:00Z",
      "is_active": true
    },
    {
      "id": 15,
      "group": {
        "id": 8,
        "code": "CS",
        "name": "Chef de service"
      },
      "assigned_at": "2024-01-10T14:20:00Z",
      "is_active": true
    }
  ],
  "total_groups": 2
}
```

### Récupérer les utilisateurs d'un groupe

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/user-group/by-group/2/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Réponse :**
```json
{
  "group": {
    "id": 2,
    "code": "RRH",
    "name": "Responsable Ressources Humaines",
    "description": "Gestion des ressources humaines"
  },
  "assignments": [
    {
      "id": 10,
      "user": {
        "id": 5,
        "email": "employee@company.com",
        "nom": "Dupont",
        "prenom": "Jean"
      },
      "assigned_at": "2024-01-15T10:45:00Z",
      "is_active": true
    },
    {
      "id": 11,
      "user": {
        "id": 3,
        "email": "user3@company.com",
        "nom": "Martin",
        "prenom": "Marie"
      },
      "assigned_at": "2024-01-15T11:00:00Z",
      "is_active": true
    }
  ],
  "total_users": 2
}
```

## Gestion des Permissions

### Lister toutes les permissions disponibles

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/permission/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Réponse :**
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/user/permission/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "codename": "create_user",
      "name": "Peut créer des utilisateurs",
      "resource": "user",
      "action": "CREATE",
      "content_type": "user"
    },
    {
      "id": 2,
      "codename": "read_user",
      "name": "Peut consulter les utilisateurs",
      "resource": "user",
      "action": "READ",
      "content_type": "user"
    },
    {
      "id": 3,
      "codename": "update_user",
      "name": "Peut modifier les utilisateurs",
      "resource": "user",
      "action": "UPDATE",
      "content_type": "user"
    }
  ]
}
```

### Lister les permissions d'un groupe

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/group-permission/?group=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Réponse :**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "group": {
        "id": 1,
        "code": "ADM",
        "name": "Administrateur"
      },
      "permission": {
        "id": 1,
        "codename": "create_user",
        "name": "Peut créer des utilisateurs",
        "resource": "user",
        "action": "CREATE"
      },
      "granted": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Assigner une permission à un groupe

**Requête :**
```bash
curl -X POST http://localhost:8000/api/user/group-permission/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group": 2,
    "permission": 5,
    "granted": true
  }'
```

## Audit et Traçabilité

### Consulter l'historique d'audit

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/audit_log/?ordering=-timestamp" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Réponse :**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/user/audit_log/?page=2",
  "previous": null,
  "results": [
    {
      "id": 150,
      "user_id": {
        "id": 1,
        "email": "admin@company.com",
        "nom": "Admin",
        "prenom": "System"
      },
      "action": "CREATE",
      "type_ressource": "user_group",
      "id_ressource": "10",
      "timestamp": "2024-01-15T10:45:00Z",
      "adresse_ip": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "details": "Assignation utilisateur 5 au groupe RRH"
    },
    {
      "id": 149,
      "user_id": {
        "id": 1,
        "email": "admin@company.com",
        "nom": "Admin",
        "prenom": "System"
      },
      "action": "UPDATE",
      "type_ressource": "group_permission",
      "id_ressource": "15",
      "timestamp": "2024-01-15T10:30:00Z",
      "adresse_ip": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "details": "Modification permission create_payroll pour groupe RRH",
      "old_values": {"granted": false},
      "new_values": {"granted": true}
    }
  ]
}
```

### Filtrer les logs par utilisateur

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/audit_log/?user_id=1&expand=user_id" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Filtrer les logs par date

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/audit_log/?date_after=2024-01-15&date_before=2024-01-15" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Filtrer les logs par action

**Requête :**
```bash
curl -X GET "http://localhost:8000/api/user/audit_log/?action=CREATE&type_ressource=user_group" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Cas d'Usage Avancés

### Workflow complet : Créer un utilisateur et l'assigner à des groupes

```bash
# 1. Créer un nouvel utilisateur
curl -X POST http://localhost:8000/api/user/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nouveau@company.com",
    "username": "nouveau",
    "nom": "Nouveau",
    "prenom": "Utilisateur",
    "password": "motdepasse123"
  }'

# 2. Assigner l'utilisateur à plusieurs groupes
curl -X POST http://localhost:8000/api/user/user-group/bulk-assign/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [7],
    "group_id": 2,
    "action": "assign"
  }'

# 3. Vérifier les permissions effectives
curl -X GET "http://localhost:8000/api/user/user-group/by-user/7/?expand=group" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Audit d'une opération spécifique

```bash
# Rechercher toutes les modifications d'un utilisateur spécifique
curl -X GET "http://localhost:8000/api/user/audit_log/?search=user5@company.com&expand=user_id" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Rechercher les assignations de groupes d'aujourd'hui
curl -X GET "http://localhost:8000/api/user/audit_log/?action=CREATE&type_ressource=user_group&date_after=2024-01-15" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Utilisation de la sélection flexible des champs

```bash
# Récupérer seulement les informations essentielles des groupes
curl -X GET "http://localhost:8000/api/user/group/?fields=id,code,name&is_active=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Récupérer les assignations avec détails complets
curl -X GET "http://localhost:8000/api/user/user-group/?expand=user,group,assigned_by&fields=id,user,group,assigned_at" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Gestion des erreurs courantes

#### Erreur d'authentification
```bash
# Requête sans token
curl -X GET "http://localhost:8000/api/user/group/"

# Réponse
{
  "detail": "Authentication credentials were not provided."
}
```

#### Erreur de validation
```bash
# Tentative de création d'un groupe avec un code existant
curl -X POST http://localhost:8000/api/user/group/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ADM",
    "name": "Test"
  }'

# Réponse
{
  "error": "Un groupe avec le code \"ADM\" existe déjà"
}
```

#### Erreur de permissions
```bash
# Tentative d'accès aux logs d'audit sans permissions
curl -X GET "http://localhost:8000/api/user/audit_log/" \
  -H "Authorization: Bearer USER_TOKEN"

# Réponse
{
  "detail": "You do not have permission to perform this action."
}
```

---

Ces exemples couvrent les cas d'usage les plus courants de l'API de gestion des utilisateurs. Pour des cas plus spécifiques, consultez la documentation Swagger à l'adresse [/api/docs/](/api/docs/).
