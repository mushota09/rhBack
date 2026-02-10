# API Documentation - Système de Gestion RH

## Vue d'ensemble

Cette documentation présente l'API complète du système de gestion des ressources humaines, incluant la gestion de la paie, des utilisateurs, des permissions et des congés.

## Accès à la documentation

- **Swagger UI**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc**: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **Schéma OpenAPI**: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

## Authentification

### JWT (JSON Web Tokens)

L'API utilise l'authentification JWT avec deux types de tokens :

- **Access Token** : Durée de vie de 24 heures, utilisé pour les requêtes API
- **Refresh Token** : Durée de vie de 10 jours, utilisé po
Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

4. **Renouvellement** : `POST /api/user/refresh/`
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Gestion des Utilisateurs et Permissions

### Groupes Organisationnels

Le système utilise des groupes prédéfinis correspondant à la structure organisationnelle :

| Code | Nom | Description |
|------|-----|-------------|
| ADM | Administrateur | Accès complet au système |
| RRH | Responsable RH | Gestion des ressources humaines |
| DIR | Directeur | Direction et approbations |
| RAF | Responsable Administratif et Financier | Gestion financière |
| CM | Comptable | Comptabilité et finances |
| IT | Informaticien | Administration technique |
| AP | Analyste des Projets | Analyse et suivi de projets |
| AI | Auditeur interne | Audit et contrôle |
| CSE | Chargé du Suivi-Evaluation | Suivi et évaluation |
| CH | Chauffeur | Transport |
| CS | Chef de service | Direction de service |
| CSFP | Chef Service Financement Projets | Financement de projets |
| CCI | Chef du contrôle interne | Contrôle interne |
| GS | Gestionnaire de Stock | Gestion des stocks |
| JR | Juriste | Affaires juridiques |
| LG | Logisticien | Logistique |
| PL | Planton | Accueil et sécurité |
| PCA | Président commission d'appel | Commission d'appel |
| PCR | Président commission réception | Commission de réception |
| PCDR | Président commission recrutement | Commission de recrutement |
| SEC | Secrétaire | Secrétariat |

### Endpoints Principaux

#### Gestion des Groupes
- `GET /api/user/group/` - Lister tous les groupes
- `POST /api/user/group/` - Créer un nouveau groupe
- `GET /api/user/group/{id}/` - Récupérer un groupe spécifique
- `PUT /api/user/group/{id}/` - Mettre à jour un groupe
- `DELETE /api/user/group/{id}/` - Supprimer un groupe

#### Assignation Utilisateur-Groupe
- `GET /api/user/user-group/` - Lister les assignations
- `POST /api/user/user-group/` - Créer une assignation
- `POST /api/user/user-group/bulk-assign/` - Assignation en masse
- `GET /api/user/user-group/by-user/{user_id}/` - Groupes d'un utilisateur
- `GET /api/user/user-group/by-group/{group_id}/` - Utilisateurs d'un groupe

#### Gestion des Permissions
- `GET /api/user/permission/` - Lister toutes les permissions
- `GET /api/user/group-permission/` - Lister les permissions de groupes
- `POST /api/user/group-permission/` - Assigner une permission à un groupe

### Exemples d'utilisation

#### Assigner un utilisateur à un groupe
```bash
curl -X POST http://localhost:8000/api/user/user-group/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "group": 2
  }'
```

#### Assignation en masse
```bash
curl -X POST http://localhost:8000/api/user/user-group/bulk-assign/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2, 3],
    "group_id": 2,
    "action": "assign"
  }'
```

#### Rechercher des groupes
```bash
curl "http://localhost:8000/api/user/group/?search=admin&is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Fonctionnalités Avancées

### Sélection Flexible des Champs

Utilisez le paramètre `fields` pour sélectionner uniquement les champs nécessaires :

```bash
# Récupérer seulement l'ID, le code et le nom des groupes
curl "http://localhost:8000/api/user/group/?fields=id,code,name" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Expansion des Relations

Utilisez le paramètre `expand` pour inclure les données des relations :

```bash
# Inclure les détails de l'utilisateur et du groupe dans les assignations
curl "http://localhost:8000/api/user/user-group/?expand=user,group" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filtrage et Recherche

Tous les endpoints supportent le filtrage et la recherche :

```bash
# Filtrer les assignations par utilisateur
curl "http://localhost:8000/api/user/user-group/?user=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Rechercher dans les groupes
curl "http://localhost:8000/api/user/group/?search=responsable" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filtrer les logs d'audit par date
curl "http://localhost:8000/api/user/audit_log/?date_after=2024-01-01&date_before=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Tri

Utilisez le paramètre `ordering` pour trier les résultats :

```bash
# Trier les groupes par nom (croissant)
curl "http://localhost:8000/api/user/group/?ordering=name" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Trier par date de création (décroissant)
curl "http://localhost:8000/api/user/user-group/?ordering=-assigned_at" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Audit et Traçabilité

### Consultation des Logs d'Audit

L'API fournit un accès complet aux logs d'audit avec filtrage avancé :

```bash
# Logs d'un utilisateur spécifique
curl "http://localhost:8000/api/user/audit_log/?user_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Logs d'une action spécifique
curl "http://localhost:8000/api/user/audit_log/?action=CREATE" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Logs par plage de dates
curl "http://localhost:8000/api/user/audit_log/?date_after=2024-01-01&date_before=2024-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Gestion des Erreurs

### Codes de Statut HTTP

- `200 OK` - Requête réussie
- `201 Created` - Ressource créée avec succès
- `204 No Content` - Suppression réussie
- `400 Bad Request` - Erreur de validation
- `401 Unauthorized` - Non authentifié
- `403 Forbidden` - Permissions insuffisantes
- `404 Not Found` - Ressource non trouvée
- `500 Internal Server Error` - Erreur serveur

### Format des Erreurs

```json
{
  "error": "Description de l'erreur",
  "details": {
    "field": ["Message d'erreur spécifique au champ"]
  }
}
```

## Pagination

Toutes les listes sont paginées par défaut (7 éléments par page) :

```json
{
  "count": 21,
  "next": "http://localhost:8000/api/user/group/?page=2",
  "previous": null,
  "results": [...]
}
```

Paramètres de pagination :
- `page` - Numéro de page
- `page_size` - Nombre d'éléments par page (max 100)

## Limites et Quotas

- **Taille maximale des requêtes** : 10MB
- **Timeout des requêtes** : 30 secondes
- **Pagination maximale** : 100 éléments par page
- **Durée de vie des tokens** :
  - Access token : 24 heures
  - Refresh token : 10 jours

## Support et Contact

Pour toute question ou problème avec l'API :

1. Consultez d'abord cette documentation
2. Vérifiez les logs d'erreur dans la console développeur
3. Contactez l'équipe de développement avec :
   - L'endpoint utilisé
   - Les paramètres de la requête
   - Le message d'erreur complet
   - Les étapes pour reproduire le problème

## Changelog

### Version 1.0.0 (2024-01-01)
- Implémentation initiale de l'API de gestion des utilisateurs
- Système de permissions basé sur les groupes
- Authentification JWT
- Audit logging complet
- Documentation OpenAPI/Swagger

---

*Cette documentation est générée automatiquement à partir du schéma OpenAPI. Pour la version la plus récente, consultez [/api/docs/](/api/docs/).*
