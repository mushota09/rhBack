# Documentation API - Système de Gestion RH

## Vue d'ensemble

Cette documentation couvre l'API complète du système de gestion des ressources humaines, incluant la gestion des utilisateurs, des permissions, de la paie et des congés.

## Structure de la Documentation

### 📚 Documentation Interactive

- **[Swagger UI](http://localhost:8000/api/docs/)** - Interface interactive pour tester l'API
- **[ReDoc](http://localhost:8000/api/redoc/)** - Documentation lisible et détaillée
- **[Schéma OpenAPI](http://localhost:8000/api/schema/)** - Schéma JSON/YAML pour
- [Export et Rapports](user-guides/exports-reports.md)

### ⚙️ Configuration
- [Configuration Système](configuration/system-setup.md)
- [Paramètres de Paie](configuration/payroll-parameters.md)
- [Gestion des Utilisateurs](configuration/user-management.md)
- [Sécurité et Permissions](configuration/security.md)

### 🔧 Administration
- [Maintenance du Système](administration/maintenance.md)
- [Monitoring et Alertes](administration/monitoring.md)
- [Sauvegarde et Restauration](administration/backup-restore.md)
- [Dépannage](administration/troubleshooting.md)

### 📖 Référence
- [API Documentation](reference/api-reference.md)
- [Types TypeScript](reference/typescript-types.md)
- [Glossaire](reference/glossary.md)
- [FAQ](reference/faq.passe"
  }'
```

### 2. Utilisation du Token

```bash
# Utiliser le token dans les requêtes suivantes
curl -X GET "http://localhost:8000/api/user/group/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Endpoints Principaux

| Endpoint | Description |
|----------|-------------|
| `POST /api/user/login/` | Connexion utilisateur |
| `GET /api/user/group/` | Lister les groupes |
| `GET /api/user/user-group/` | Lister les assignations |
| `GET /api/user/permission/` | Lister les permissions |
| `GET /api/user/audit_log/` | Consulter l'audit |

## Fonctionnalités Clés

### 🔐 Gestion des Utilisateurs et Permissions

- **Groupes organisationnels** : 21 groupes prédéfinis (ADM, RRH, DIR, etc.)
- **Assignations flexibles** : Utilisateurs peuvent appartenir à plusieurs groupes
- **Permissions granulaires** : Contrôle CRUD par ressource
- **Audit complet** : Traçabilité de toutes les modifications

### 🏢 Structure Organisationnelle

Le système reflète la structure organisationnelle réelle avec des groupes comme :

- **ADM** - Administrateur (accès complet)
- **RRH** - Responsable RH (gestion des employés)
- **DIR** - Directeur (approbations)
- **RAF** - Responsable Administratif et Financier
- **IT** - Informaticien (administration technique)
- Et 16 autres groupes spécialisés

### 💰 Gestion de la Paie

- **Périodes de paie** : Création et traitement mensuel
- **Calculs automatisés** : Salaires, cotisations, retenues
- **Bulletins PDF** : Génération automatique
- **Exports Excel** : Rapports détaillés

### 🏖️ Gestion des Congés

- **Demandes** : Soumission et approbation
- **Planification** : Calendrier des congés
- **Soldes** : Suivi par employé

## Authentification JWT

### Tokens

- **Access Token** : 24 heures de validité
- **Refresh Token** : 10 jours de validité

### Workflow

1. **Login** → Récupération des tokens
2. **Requêtes** → Utilisation de l'access token
3. **Renouvellement** → Utilisation du refresh token
4. **Logout** → Suppression côté client

## Fonctionnalités Avancées

### 🔍 Filtrage et Recherche

Tous les endpoints supportent :

```bash
# Filtrage
?user_id=1&is_active=true

# Recherche textuelle
?search=responsable

# Tri
?ordering=-created_at

# Pagination
?page=2&page_size=20
```

### 🎯 Sélection Flexible des Champs

```bash
# Sélectionner des champs spécifiques
?fields=id,name,code

# Inclure des relations
?expand=user,group
```

### 📊 Audit et Traçabilité

```bash
# Logs par utilisateur
?user_id=1

# Logs par action
?action=CREATE

# Logs par période
?date_after=2024-01-01&date_before=2024-01-31
```

## Codes de Réponse

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 201 | Créé |
| 204 | Supprimé |
| 400 | Erreur de validation |
| 401 | Non authentifié |
| 403 | Permissions insuffisantes |
| 404 | Non trouvé |
| 500 | Erreur serveur |

## Limites et Quotas

- **Pagination** : 7 éléments par défaut, max 100
- **Taille requête** : Max 10MB
- **Timeout** : 30 secondes
- **Rate limiting** : Selon configuration serveur

## Environnements

### Développement
- **URL** : http://localhost:8000
- **Swagger** : http://localhost:8000/api/docs/
- **ReDoc** : http://localhost:8000/api/redoc/

### Production
- **URL** : https://api.company.com
- **Documentation** : https://api.company.com/api/docs/

## Support et Ressources

### 📞 Contact

- **Email** : dev-team@company.com
- **Slack** : #api-support
- **Issues** : GitHub Issues

### 🔗 Liens Utiles

- [Documentation Swagger](http://localhost:8000/api/docs/)
- [Schéma OpenAPI](http://localhost:8000/api/schema/)
- [Exemples Postman](postman_collection.json)
- [SDK Python](sdk/python/)
- [SDK JavaScript](sdk/javascript/)

### 📝 Changelog

#### Version 1.0.0 (2024-01-01)
- ✅ API de gestion des utilisateurs
- ✅ Système de permissions RBAC
- ✅ Authentification JWT
- ✅ Audit logging complet
- ✅ Documentation OpenAPI

#### Prochaines Versions
- 🔄 Notifications en temps réel
- 🔄 API GraphQL
- 🔄 Webhooks
- 🔄 Rate limiting avancé

## Contribution

### Signaler un Bug

1. Vérifiez les [issues existantes](https://github.com/company/hr-api/issues)
2. Créez une nouvelle issue avec :
   - Description détaillée
   - Étapes de reproduction
   - Réponse attendue vs réelle
   - Version de l'API

### Demander une Fonctionnalité

1. Ouvrez une [feature request](https://github.com/company/hr-api/issues/new?template=feature_request.md)
2. Décrivez le cas d'usage
3. Proposez une solution si possible

### Contribuer au Code

1. Fork le repository
2. Créez une branche feature
3. Implémentez avec tests
4. Soumettez une pull request

---

## Licence

Cette API est propriétaire et réservée à l'usage interne de l'entreprise.

**© 2024 Company Name. Tous droits réservés.**
