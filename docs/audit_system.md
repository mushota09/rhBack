# Système d'Audit Global - Documentation

## Vue d'ensemble

Le système d'audit global capture automatiquement toutes les actions effectuées dans le système, offrant une traçabilité complète pour la conformité et la sécurité.

## Fonctionnalités

### 🔍 **Capture Automatique**
- **Toutes les requêtes API** : GET, POST, PUT, PATCH, DELETE
- **Actions d'authentification** : Connexions, déconnexions, échecs
- **Modifications de données** : États avant/après
- **Opérations en lot** : Créations, mises à jour, suppressions multiples
- **Exports de données** : Tous formats (Excel, PDF, etc.)

### 📊 **Informations Capturées**
- **Utilisateur** : Qui a effectué l'action
- **Action** : Type d'opération (CREATE, UPDATE, DELETE, etc.)
- **Ressource** : Quel objet a été affecté
- **Données** : Valeurs avant/après modification
- **Contexte** : IP, User-Agent, timestamp
- **Performance** : Temps d'exécution
- **Statut** : Succès ou échec avec code HTTP

## Architecture

### Composants Principaux

1. **AuditService** (`utilities/audit_service.py`)
   - Service centralisé pour l'audit
   - Méthodes pour tous types d'actions
   - Sanitisation automatique des données sensibles

2. **AuditMiddleware** (`utilities/middleware.py`)
   - Capture automatique de toutes les requêtes
   - Mesure du temps d'exécution
   - Extraction des données de requête/réponse

3. **AuditMixins** (`utilities/audit_mixins.py`)
   - Mixins pour ViewSets DRF
   - Audit automatique des opérations CRUD
   - Support des opérations en lot

4. **Modèle audit_log** (`user_app/models.py`)
   - Stockage des logs d'audit
   - Index optimisés pour les requêtes
   - Champs étendus pour plus de contexte

## Utilisation

### 1. Audit Automatique (Recommandé)

Le middleware capture automatiquement toutes les actions :

```python
# Aucune configuration nécessaire
# Toutes les requêtes API sont automatiquement auditées
```

### 2. Audit Manuel avec AuditService

```python
from utilities.audit_service import AuditService

# Audit d'une action personnalisée
AuditService.lo
odelViewSet

class MyViewSet(AuditedModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
    # L'audit est automatique pour toutes les opérations CRUD
```

### 4. Audit avec Gestionnaire de Contexte

```python
from utilities.audit_service import AuditContextManager

def my_complex_operation(user, data):
    with AuditContextManager(user, 'COMPLEX_OP', 'my_resource') as audit:
        # Opération complexe
        result = process_data(data)

        # Définir les données pour l'audit
        audit.set_data(
            old_values=data,
            new_values=result
        )

        return result
```

### 5. Décorateur d'Audit

```python
from utilities.audit_service import audit_action

@audit_action('PROCESS', 'document')
def process_document(user, document_id):
    # La fonction sera automatiquement auditée
    document = Document.objects.get(id=document_id)
    document.process()
    return document
```

## Configuration

### Settings Django

```python
# settings.py
MIDDLEWARE = [
    # ... autres middlewares
    'utilities.middleware.AuditMiddleware',  # Audit global
    # ... autres middlewares
]

# Configuration des logs
LOGGING = {
    'loggers': {
        'paie_app.audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Personnalisation

```python
# Personnaliser les champs sensibles à masquer
AuditService._sanitize_data({
    'password': 'secret123',
    'api_key': 'key123'
})
# Résultat: {'password': '***MASKED***', 'api_key': '***MASKED***'}
```

## Consultation des Logs

### API d'Audit

```python
# Consulter les logs via l'API
GET /api/audit-log/

# Filtrage avancé
GET /api/audit-log/?action=CREATE&user_email=admin@example.com&date_after=2024-01-01

# Recherche textuelle
GET /api/audit-log/?search=employee

# Tri
GET /api/audit-log/?ordering=-timestamp
```

### Filtres Disponibles

- **Par utilisateur** : `user_email`, `user_name`
- **Par action** : `action` (CREATE, UPDATE, DELETE, etc.)
- **Par ressource** : `type_ressource`
- **Par date** : `date_after`, `date_before`, `timestamp_after`, `timestamp_before`
- **Par IP** : `adresse_ip`
- **Par statut** : Actions réussies vs échouées

### Expansion des Données

```python
# Inclure les détails utilisateur
GET /api/audit-log/?expand=user_id

# Réponse avec détails utilisateur complets
{
    "results": [{
        "id": 1,
        "action": "CREATE",
        "user_id": {
            "id": 1,
            "email": "admin@example.com",
            "nom": "Admin",
            "prenom": "User"
        },
        // ... autres champs
    }]
}
```

## Sécurité et Conformité

### Données Sensibles

Le système masque automatiquement :
- Mots de passe
- Tokens d'authentification
- Clés API
- Clés secrètes
- Données de session

### Intégrité des Logs

- **Immutabilité** : Les logs ne peuvent pas être modifiés
- **Horodatage** : Timestamp automatique et précis
- **Traçabilité** : Lien vers l'utilisateur et la session
- **Contexte complet** : IP, User-Agent, méthode HTTP

### Performance

- **Index optimisés** : Requêtes rapides sur les champs fréquents
- **Pagination** : Gestion efficace des gros volumes
- **Cache** : Mise en cache des requêtes fréquentes
- **Archivage** : Rotation automatique des logs anciens

## Exemples d'Usage

### Audit de Connexion

```python
# Connexion réussie
POST /api/user/login/
# → Crée automatiquement un log avec action='LOGIN'

# Connexion échouée
POST /api/user/login/ (mauvais mot de passe)
# → Crée automatiquement un log avec action='LOGIN_FAILED'
```

### Audit CRUD

```python
# Création d'employé
POST /api/employees/
{
    "nom": "Dupont",
    "prenom": "Jean",
    "email": "jean.dupont@example.com"
}
# → Log avec action='CREATE', nouvelles_valeurs=données employé

# Modification d'employé
PUT /api/employees/123/
{
    "nom": "Dupont-Martin",
    "email": "jean.dupont-martin@example.com"
}
# → Log avec action='UPDATE', anciennes_valeurs + nouvelles_valeurs

# Suppression d'employé
DELETE /api/employees/123/
# → Log avec action='DELETE', anciennes_valeurs=données supprimées
```

### Audit d'Export

```python
# Export Excel des employés
GET /api/employees/export/?format=excel
# → Log avec action='EXPORT', nouvelles_valeurs={'format': 'excel', 'count': 150}
```

## Monitoring et Alertes

### Métriques Importantes

- **Tentatives de connexion échouées** : Détection d'intrusion
- **Actions privilégiées** : Modifications par administrateurs
- **Opérations en lot** : Changements massifs
- **Exports fréquents** : Surveillance des fuites de données

### Requêtes de Monitoring

```python
# Connexions échouées récentes
GET /api/audit-log/?action=LOGIN_FAILED&date_after=2024-01-01

# Actions d'un utilisateur spécifique
GET /api/audit-log/?user_email=admin@example.com&ordering=-timestamp

# Opérations sur une ressource critique
GET /api/audit-log/?type_ressource=salary&action=UPDATE
```

## Maintenance

### Archivage des Logs

```python
# Script de maintenance (à exécuter périodiquement)
from datetime import datetime, timedelta
from user_app.models import audit_log

# Archiver les logs de plus de 2 ans
cutoff_date = datetime.now() - timedelta(days=730)
old_logs = audit_log.objects.filter(timestamp__lt=cutoff_date)

# Exporter vers un système d'archivage
# puis supprimer les anciens logs
old_logs.delete()
```

### Optimisation des Performances

```python
# Index personnalisés pour requêtes spécifiques
class Meta:
    indexes = [
        models.Index(fields=['user_id', 'action', 'timestamp']),
        models.Index(fields=['type_ressource', 'timestamp']),
        models.Index(fields=['adresse_ip', 'timestamp']),
    ]
```

Ce système d'audit offre une traçabilité complète et automatique de toutes les actions du système, essentielle pour la conformité réglementaire et la sécurité des données RH.
