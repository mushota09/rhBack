# Design Document - Service Group Management

## Overview

Système complet de gestion des ServiceGroups avec ADRF et adrf_flex_fields pour lier services et groupes organisationnels avec expansion dynamique des champs.

### Objectifs

1. Créer module ServiceGroup avec CRUD asynchrone
2. Gestion automatique relations Group ↔ ServiceGroup
3. Migrer système RBAC vers FlexFieldsModelViewSet
4. Assignation automatique UserGroup lors création employé
5. Expansion dynamique pour toutes entités RBAC

### Technologies

- ADRF (Async Django REST Framework)
- adrf_flex_fields
- Django ORM
- Python 3.11+ (async/await)

## Architecture

### Nouveau Module: service_group

**Structure:**
```
user_app/modules/service_group/
├── __init__.py
├── views.py          # ServiceGroupViewSet
├── serializers.py    # J/I_ServiceGroupSerializer
└── urls.py
```

**Serializers:**
- `J_ServiceGroupSerializer`: Read avec expandable_fields (service, group)
- `I_ServiceGroupSerializer`: Write avec validation

**ViewSet:**
- Hérite de `FlexFieldsModelViewSet`
- `permit_list_expands = ['service', 'group']`
- Optimisation: `select_related('service', 'group')`
- Logique suppression avec validation Group

### Modifications Modules Existants

#### 1. Group Module
- Migrer vers `FlexFieldsModelViewSet`
- Ajouter `expandable_fields`: service_groups, user_groups, group_permissions
- `create()`: Créer ServiceGroups si service_ids fournis
- `destroy()`: Vérifier utilisateurs actifs + supprimer ServiceGroups cascade

#### 2. Employe Module
- Remplacer référence `poste` par `service_group`
- Ajouter `expandable_fields`: poste_id, poste_id.service, poste_id.group, user_account
- `acreate()`: Si group_id fourni, créer UserGroup automatiquement

#### 3. UserGroup Module
- Migrer vers `FlexFieldsModelViewSet`
- Enrichir `expandable_fields`: user, user.employe_id, group, group.service_groups
- Optimisation: `prefetch_related('group__service_groups')`

#### 4. Permission Module
- Migrer vers `FlexFieldsModelViewSet`
- Convertir serializers vers `FlexFieldsModelSerializer`
- Ajouter `expandable_fields`: group, permission, created_by

#### 5. Service Module
- Migrer vers `FlexFieldsModelViewSet`
- Déjà utilise `FlexFieldsModelSerializer`

## Components and Interfaces

### ServiceGroup Serializers

```python
class J_ServiceGroupSerializer(FlexFieldsModelSerializer):
    service = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ServiceGroup
        fields = "__all__"
        expandable_fields = {
            'service': 'user_app.modules.service.serializers.I_serviceSerializers',
            'group': 'user_app.modules.group.serializers.J_GroupSerializers',
        }

class I_ServiceGroupSerializer(AsyncModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ['service', 'group']
```

### ServiceGroup ViewSet

```python
class ServiceGroupViewSet(FlexFieldsModelViewSet):
    queryset = ServiceGroup.objects.all()
    serializer_class_read = J_ServiceGroupSerializer
    serializer_class_write = I_ServiceGroupSerializer
    permit_list_expands = ['service', 'group']

    def get_queryset(self):
        return ServiceGroup.object
 service_ids valides, tous ServiceGroups correspondants créés.
**Validates: Requirements 2.1, 2.2**

### Property 2: Unicité ServiceGroup
*Pour tout* couple (service, group), un seul ServiceGroup actif existe.
**Validates: Requirements 8.2**

### Property 3: Suppression cascade Group → ServiceGroups
*Pour tout* Group supprimé, tous ServiceGroups associés supprimés.
**Validates: Requirements 3.1**

### Property 4: Protection suppression avec utilisateurs
*Pour tout* Group avec UserGroups actifs, suppression refusée.
**Validates: Requirements 3.2**

### Property 5: Suppression ServiceGroup avec validation
*Pour tout* ServiceGroup supprimé, si Group sans autres ServiceGroups ni utilisateurs, Group supprimé.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 6: Expansion dynamique
*Pour toute* requête avec expand valide, champs remplacés par objets complets.
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 7: Champs sparse
*Pour toute* requête avec fields, seuls champs spécifiés présents.
**Validates: Requirements 5.4**

### Property 8: Omission champs
*Pour toute* requête avec omit, champs spécifiés absents.
**Validates: Requirements 5.5**

### Property 9: Assignation UserGroup automatique
*Pour tout* employé créé avec group_id, UserGroup actif créé automatiquement.
**Validates: Requirements 9.2**

### Property 10: Validation intégrité
*Pour tout* ServiceGroup créé, service et groupe existent et valides.
**Validates: Requirements 8.1**

### Property 11: Optimisation requêtes
*Pour toute* requête avec expansion, requêtes SQL optimisées via select_related/prefetch_related.
**Validates: Requirements 11.1, 11.2**

### Property 12: Expansion imbriquée
*Pour toute* requête avec expansion imbriquée (notation points), tous niveaux étendus.
**Validates: Requirements 5.6**

## Error Handling

### Stratégie
- Validation: Serializers DRF
- Erreurs async: try/except + Response appropriée
- Transactions: `@transaction.atomic`
- Messages: Français, clairs

### Codes HTTP
- 400: Données invalides, contraintes violées
- 404: Ressource introuvable
- 409: Conflit contrainte unique
- 500: Erreur serveur

### Exemples

**Contrainte unique:**
```python
except IntegrityError:
    return Response(
        {'error': f'ServiceGroup existe déjà pour {service.titre} et {group.code}'},
        status=status.HTTP_409_CONFLICT
    )
```

**Protection suppression:**
```python
if user_count > 0:
    return Response(
        {'error': f'Impossible supprimer. {user_count} utilisateur(s) actif(s).'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

## Testing Strategy

### Approche Duale
1. **Tests unitaires**: Exemples spécifiques, cas limites, erreurs
2. **Tests propriétés**: Vérification propriétés universelles

### Tests Unitaires
- Création/suppression spécifiques
- Cas limites (listes vides, nulls)
- Conditions erreur
- Intégration composants

### Tests Propriétés
- Framework: Hypothesis (Python)
- Configuration: Min 100 itérations
- Tag format: `# Feature: service-group-management, Property N: Description`

**Générateurs:**
- `group_data()`: Données Group valides
- `service_ids()`: Listes IDs services
- `user_with_groups()`: Utilisateurs avec groupes
- `expand_params()`: Paramètres expand valides

### Optimisation
- `select_related()` pour ForeignKeys
- `prefetch_related()` pour many-to-many
- Django Debug Toolbar pour compter requêtes

## Implementation Notes

### Ordre Implémentation

1. **Phase 1**: Module ServiceGroup (serializers, viewset, urls, tests)
2. **Phase 2**: Modifier Group (logique service_ids, cascade, tests)
3. **Phase 3**: Migrer vers FlexFieldsModelViewSet (Group, UserGroup, Permission, Service)
4. **Phase 4**: Configurer expandable_fields (tous serializers RBAC)
5. **Phase 5**: Logique UserGroup dans Employe
6. **Phase 6**: Tests propriétés (générateurs, tests, validation)

### Considérations Techniques

**ADRF Workarounds:**
- Extraction manuelle ForeignKeys dans acreate
- Pattern établi: UserGroupViewSet, GroupPermissionViewSet

**Lazy String References:**
- Format: `'user_app.modules.xxx.serializers.YYYSerializer'`
- Évite imports circulaires

**Performance:**
- Toujours select_related/prefetch_related
- Limiter profondeur expansion (max 3 niveaux)
- Paginer listes volumineuses

**Sécurité:**
- Valider tous IDs
- Vérifier permissions
- Logger opérations critiques (audit)
