# Référence API

Cette documentation détaille toutes les APIs REST disponibles dans le système de paie, incluant les endpoints, paramètres, réponses et exemples d'utilisation.

## Base URL et Authentification

**Base URL :** `https://your-domain.com/api/`

**Authentification :** JWT Bearer Token

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Types de Données Frontend

Le système utilise des interfaces TypeScript complètes pour assurer la cohérence entre le frontend et l'API. Les principales entités incluent:

### Employé (`Employe`)
Interface complète avec 25+ champs incluant informations personnelles, contact, adresse, emploi, financières, familiales et contact d'urgence.

### Contrat (`Contrat`) 
Gestion complète des contrats avec types (permanent, temporaire, stage, consultant), structure salariale, et cotisations.

### Service/Poste (`Service`, `Poste`)
Hiérarchie organisationnelle avec codes, descriptions et relations.

### Document (`Document`)
Catégorisation des documents (contrat, pièce d'identité, CV, certificats, etc.) avec métadonnées et suivi d'expiration.

### Utilisateur (`User`)
Comptes système avec authentification, permissions basées sur les rôles, et liaison avec les employés.

### Journal d'Audit (`AuditLog`)
Traçabilité complète des actions avec suivi utilisateur, changements de ressources, IP et user agent.

## Authentification

### Obtenir un Token

```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "admin",
    "password": "password"
}
```

**Réponse :**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@company.com",
        "role": "ADMIN"
    }
}
```

### Rafraîchir un Token

```http
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Gestion des Employés (user_app)

### Lister les Employés

```http
GET /api/user_app/employes/
```

**Paramètres de requête :**
- `service_id` (integer) : Filtrer par service
- `poste_id` (integer) : Filtrer par poste
- `statut_emploi` (string) : Filtrer par statut (ACTIVE, INACTIVE, TERMINATED, SUSPENDED)
- `search` (string) : Recherche par nom, prénom, matricule
- `expand` (string) : Champs à étendre (poste, responsable, service)

**Réponse :**
```json
{
    "count": 150,
    "results": [
        {
            "id": 1,
            "prenom": "Jean",
            "nom": "MUKENDI",
            "postnom": "Claude",
            "matricule": "EMP001",
            "email_personnel": "jean.mukendi@gmail.com",
            "email_professionnel": "j.mukendi@company.com",
            "telephone_personnel": "+243123456789",
            "date_naissance": "1985-03-15",
            "sexe": "M",
            "statut_matrimonial": "M",
            "nationalite": "Congolaise",
            "date_embauche": "2020-01-15",
            "statut_emploi": "ACTIVE",
            "nombre_enfants": 2,
            "poste_id": 5,
            "responsable_id": 3,
            "full_name": "MUKENDI Jean Claude",
            "poste": {
                "id": 5,
                "titre": "Développeur Senior",
                "code": "DEV_SR",
                "service": {
                    "id": 2,
                    "titre": "Informatique",
                    "code": "IT"
                }
            },
            "created_at": "2020-01-15T08:00:00Z",
            "updated_at": "2024-02-01T10:30:00Z"
        }
    ]
}
```

### Créer un Employé

```http
POST /api/user_app/employes/
Content-Type: application/json

{
    "prenom": "Marie",
    "nom": "KASONGO",
    "postnom": "Grace",
    "date_naissance": "1990-07-20",
    "sexe": "F",
    "statut_matrimonial": "S",
    "nationalite": "Congolaise",
    "banque": "Banque Commerciale du Congo",
    "numero_compte": "001-234567-89",
    "niveau_etude": "Licence",
    "numero_inss": "123456789",
    "email_personnel": "marie.kasongo@gmail.com",
    "email_professionnel": "m.kasongo@company.com",
    "telephone_personnel": "+243987654321",
    "adresse_ligne1": "123 Avenue de la Paix",
    "ville": "Kinshasa",
    "province": "Kinshasa",
    "pays": "République Démocratique du Congo",
    "poste_id": 3,
    "responsable_id": 1,
    "date_embauche": "2024-03-01",
    "statut_emploi": "ACTIVE",
    "nombre_enfants": 0,
    "nom_contact_urgence": "KASONGO Paul",
    "lien_contact_urgence": "Père",
    "telephone_contact_urgence": "+243111222333"
}
```

### Détail d'un Employé

```http
GET /api/user_app/employes/{id}/
```

**Réponse complète avec tous les champs de l'interface Employe**

### Gestion des Contrats

```http
GET /api/user_app/contrats/
```

**Paramètres :**
- `employe_id` (integer) : Filtrer par employé
- `type_contrat` (string) : Type (PERMANENT, TEMPORARY, INTERNSHIP, CONSULTANT)
- `statut` (string) : Statut du contrat

**Réponse :**
```json
{
    "count": 45,
    "results": [
        {
            "id": 1,
            "employe_id": 1,
            "type_contrat": "PERMANENT",
            "date_debut": "2020-01-15",
            "date_fin": null,
            "type_salaire": "M",
            "salaire_base": "2000000.00",
            "devise": "CDF",
            "indemnite_logement": 25.0,
            "indemnite_deplacement": 15.0,
            "prime_fonction": 30.0,
            "autre_avantage": "0.00",
            "assurance_patronale": 1.5,
            "assurance_salariale": 1.0,
            "fpc_patronale": 0.5,
            "fpc_salariale": 0.5,
            "statut": "en_cours",
            "commentaire": "Contrat initial",
            "employe": {
                "id": 1,
                "nom": "MUKENDI",
                "prenom": "Jean",
                "matricule": "EMP001"
            }
        }
    ]
}
```

### Gestion des Services

```http
GET /api/user_app/services/
POST /api/user_app/services/
PUT /api/user_app/services/{id}/
DELETE /api/user_app/services/{id}/
```

**Structure Service :**
```json
{
    "id": 1,
    "titre": "Informatique",
    "code": "IT",
    "description": "Service informatique et développement"
}
```

### Gestion des Postes

```http
GET /api/user_app/postes/
POST /api/user_app/postes/
PUT /api/user_app/postes/{id}/
DELETE /api/user_app/postes/{id}/
```

**Structure Poste :**
```json
{
    "id": 1,
    "titre": "Développeur Senior",
    "code": "DEV_SR",
    "description": "Développeur avec 5+ années d'expérience",
    "service_id": 1,
    "service": {
        "id": 1,
        "titre": "Informatique",
        "code": "IT"
    }
}
```

### Gestion des Documents

```http
GET /api/user_app/documents/
POST /api/user_app/documents/
PUT /api/user_app/documents/{id}/
DELETE /api/user_app/documents/{id}/
```

**Paramètres pour GET :**
- `employe_id` (integer) : Filtrer par employé
- `document_type` (string) : Type de document
- `expiry_date_before` (date) : Documents expirant avant cette date

**Structure Document :**
```json
{
    "id": 1,
    "employe_id": 1,
    "document_type": "CONTRACT",
    "titre": "Contrat de travail - Jean MUKENDI",
    "description": "Contrat permanent signé le 15/01/2020",
    "file": "/media/documents/contracts/emp001_contract.pdf",
    "uploaded_by": "admin",
    "expiry_date": null,
    "created_at": "2020-01-15T08:00:00Z",
    "updated_at": "2020-01-15T08:00:00Z",
    "employe": {
        "id": 1,
        "nom": "MUKENDI",
        "prenom": "Jean",
        "matricule": "EMP001"
    }
}
```

### Gestion des Utilisateurs Système

```http
GET /api/user_app/users/
POST /api/user_app/users/
PUT /api/user_app/users/{id}/
DELETE /api/user_app/users/{id}/
```

**Structure User :**
```json
{
    "id": 1,
    "email": "admin@company.com",
    "phone": "+243123456789",
    "photo": "/media/photos/admin.jpg",
    "employe_id": 1,
    "nom": "MUKENDI",
    "prenom": "Jean",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false,
    "last_login": "2024-02-02T08:00:00Z",
    "date_joined": "2020-01-15T08:00:00Z",
    "created_at": "2020-01-15T08:00:00Z",
    "updated_at": "2024-02-01T10:30:00Z",
    "employe": {
        "id": 1,
        "nom": "MUKENDI",
        "prenom": "Jean",
        "matricule": "EMP001"
    },
    "groups": [
        {
            "id": 1,
            "code": "RRH",
            "name": "Ressources Humaines"
        }
    ],
    "permissions": [
        {
            "id": 1,
            "codename": "view_employe",
            "name": "Can view employee",
            "resource": "employe",
            "action": "READ"
        }
    ]
}
```

### Gestion des Groupes

```http
GET /api/user_app/groups/
POST /api/user_app/groups/
PUT /api/user_app/groups/{id}/
DELETE /api/user_app/groups/{id}/
```

**Structure Group :**
```json
{
    "id": 1,
    "code": "RRH",
    "name": "Ressources Humaines",
    "description": "Groupe pour la gestion des ressources humaines",
    "is_active": true,
    "created_at": "2020-01-15T08:00:00Z",
    "updated_at": "2024-02-01T10:30:00Z",
    "user_count": 5,
    "permission_count": 12
}
```

### Gestion des Permissions

```http
GET /api/user_app/permissions/
GET /api/user_app/permissions/{id}/
```

**Paramètres pour GET :**
- `resource` (string) : Filtrer par type de ressource

**Structure Permission :**
```json
{
    "id": 1,
    "codename": "view_employe",
    "name": "Can view employee",
    "content_type": 15,
    "resource": "employe",
    "action": "READ",
    "description": "Permission to view employee records"
}
```

### Relations Utilisateur-Groupe

```http
GET /api/user_app/user-groups/
POST /api/user_app/user-groups/
PUT /api/user_app/user-groups/{id}/
DELETE /api/user_app/user-groups/{id}/
GET /api/user_app/user-groups/by-user/{user_id}/
GET /api/user_app/user-groups/by-group/{group_id}/
POST /api/user_app/user-groups/bulk-assign/
```

**Structure UserGroup :**
```json
{
    "id": 1,
    "user": 1,
    "group": 1,
    "assigned_by": 2,
    "assigned_at": "2024-02-01T10:30:00Z",
    "is_active": true,
    "group_details": {
        "id": 1,
        "code": "RRH",
        "name": "Ressources Humaines"
    },
    "user_details": {
        "id": 1,
        "email": "admin@company.com",
        "nom": "MUKENDI",
        "prenom": "Jean"
    }
}
```

**Assignation en masse :**
```http
POST /api/user_app/user-groups/bulk-assign/
Content-Type: application/json

{
    "group_id": 1,
    "user_ids": [1, 2, 3, 4]
}
```

### Permissions de Groupe

```http
GET /api/user_app/group-permissions/
POST /api/user_app/group-permissions/
PUT /api/user_app/group-permissions/{id}/
DELETE /api/user_app/group-permissions/{id}/
```

**Paramètres pour GET :**
- `group` (integer) : Filtrer par groupe
- `permission` (integer) : Filtrer par permission

**Structure GroupPermission :**
```json
{
    "id": 1,
    "group": 1,
    "permission": 1,
    "granted": true,
    "created_at": "2024-02-01T10:30:00Z",
    "created_by": 2,
    "group_details": {
        "id": 1,
        "code": "RRH",
        "name": "Ressources Humaines"
    },
    "permission_details": {
        "id": 1,
        "codename": "view_employe",
        "name": "Can view employee",
        "resource": "employe",
        "action": "READ"
    }
}
```

### Journal d'Audit

```http
GET /api/user_app/audit-logs/
```

**Paramètres :**
- `user_id` (integer) : Filtrer par utilisateur
- `action` (string) : Type d'action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW, EXPORT)
- `type_ressource` (string) : Type de ressource modifiée
- `date_after` (datetime) : Actions après cette date
- `date_before` (datetime) : Actions avant cette date

**Réponse :**
```json
{
    "count": 1250,
    "results": [
        {
            "id": 1,
            "user_id": 1,
            "action": "UPDATE",
            "type_ressource": "employe",
            "id_ressource": "123",
            "anciennes_valeurs": {
                "telephone_personnel": "+243111111111",
                "adresse_ligne1": "Ancienne adresse"
            },
            "nouvelles_valeurs": {
                "telephone_personnel": "+243123456789",
                "adresse_ligne1": "123 Avenue de la Paix"
            },
            "adresse_ip": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            "timestamp": "2024-02-02T10:30:00Z",
            "user": {
                "id": 1,
                "email": "admin@company.com",
                "nom": "MUKENDI",
                "prenom": "Jean"
            }
        }
    ]
}
```

### Historique des Contrats

```http
GET /api/user_app/historique-contrats/
POST /api/user_app/historique-contrats/
```

**Structure HistoriqueContrat :**
```json
{
    "id": 1,
    "contrat_id": 1,
    "date_modification": "2024-01-01",
    "ancien_salaire": "1800000.00",
    "nouveau_salaire": "2000000.00",
    "prime_fonction": "600000.00",
    "indemnites": {
        "logement": "500000.00",
        "deplacement": "300000.00"
    },
    "cotisations": {
        "inss_pension": "13500.00",
        "inss_risque": "1200.00",
        "mfp": "20000.00"
    },
    "allocation_familiale": "10000.00",
    "autres_avantages": "0.00",
    "commentaire": "Augmentation annuelle",
    "contrat": {
        "id": 1,
        "employe_id": 1,
        "type_contrat": "PERMANENT"
    }
}
```

**Paramètres de requête pour GET :**
- `contrat_id` (integer) : Filtrer par contrat spécifique
- `contrat_id__employe_id` (integer) : Filtrer par employé (via contrat)

**Exemples d'utilisation :**
```http
# Récupérer l'historique d'un contrat spécifique
GET /api/user_app/historique-contrats/?contrat_id=1

# Récupérer tout l'historique des contrats d'un employé
GET /api/user_app/historique-contrats/?contrat_id__employe_id=123
```

## Périodes de Paie

### Lister les Périodes

```http
GET /api/paie/periodes/
```

**Paramètres de requête :**
- `annee` (integer) : Filtrer par a
te_debut": "2024-03-01",
            "date_fin": "2024-03-31",
            "statut": "APPROVED",
            "nombre_employes": 50,
            "masse_salariale": "25000000.00",
            "total_cotisations_patronales": "3750000.00",
            "total_cotisations_salariales": "2500000.00",
            "date_creation": "2024-03-01T08:00:00Z",
            "traite_par": {
                "id": 1,
                "username": "admin",
                "nom_complet": "Administrateur"
            }
        }
    ]
}
```

### Créer une Période

```http
POST /api/paie/periodes/
Content-Type: application/json

{
    "annee": 2024,
    "mois": 4,
    "description": "Paie Avril 2024"
}
```

**Réponse :**
```json
{
    "id": 26,
    "annee": 2024,
    "mois": 4,
    "date_debut": "2024-04-01",
    "date_fin": "2024-04-30",
    "statut": "DRAFT",
    "description": "Paie Avril 2024",
    "nombre_employes": 0,
    "masse_salariale": "0.00",
    "date_creation": "2024-04-01T08:00:00Z",
    "cree_par": {
        "id": 1,
        "username": "admin"
    }
}
```

### Détail d'une Période

```http
GET /api/paie/periodes/{id}/
```

**Paramètres de requête :**
- `expand` (string) : Champs à étendre (entries, traite_par, approuve_par)

**Réponse :**
```json
{
    "id": 1,
    "annee": 2024,
    "mois": 3,
    "statut": "APPROVED",
    "statistiques": {
        "nombre_employes": 50,
        "masse_salariale": "25000000.00",
        "total_cotisations_patronales": "3750000.00",
        "total_cotisations_salariales": "2500000.00",
        "total_ire": "1200000.00",
        "total_retenues": "800000.00",
        "salaire_net_total": "20200000.00"
    },
    "entries": [...],  // Si expand=entries
    "traite_par": {...},  // Si expand=traite_par
    "approuve_par": {...}  // Si expand=approuve_par
}
```

### Traiter une Période

```http
POST /api/paie/periodes/{id}/process/
Content-Type: application/json

{
    "force_reprocess": false,
    "include_suspended": false,
    "batch_size": 50,
    "async_processing": true
}
```

**Réponse :**
```json
{
    "status": "success",
    "message": "Traitement lancé avec succès",
    "task_id": "celery-task-uuid",
    "estimated_duration": "00:05:00",
    "employes_eligibles": 50
}
```

### Statut du Traitement

```http
GET /api/paie/periodes/{id}/processing-status/
```

**Réponse :**
```json
{
    "status": "PROCESSING",
    "progress": 75,
    "employes_traites": 38,
    "employes_total": 50,
    "temps_ecoule": "00:02:15",
    "temps_estime": "00:03:00",
    "erreurs": [
        {
            "employe_id": 123,
            "type": "MISSING_CONTRACT",
            "message": "Aucun contrat actif pour la période"
        }
    ],
    "derniere_mise_a_jour": "2024-03-01T08:15:30Z"
}
```

### Finaliser une Période

```http
POST /api/paie/periodes/{id}/finalize/
Content-Type: application/json

{
    "confirmation": true,
    "notes": "Validation terminée, prêt pour approbation"
}
```

### Approuver une Période

```http
POST /api/paie/periodes/{id}/approve/
Content-Type: application/json

{
    "approved_by": "Directeur RH",
    "approval_notes": "Période validée et approuvée pour paiement"
}
```

### Exporter une Période

```http
POST /api/paie/periodes/{id}/export/
Content-Type: application/json

{
    "format": "excel",
    "include_details": true,
    "template": "standard"
}
```

**Réponse :**
```json
{
    "status": "success",
    "download_url": "/media/exports/periode_2024_03_export.xlsx",
    "file_size": 2048576,
    "expires_at": "2024-03-08T08:00:00Z"
}
```

## Entrées de Paie

### Lister les Entrées

```http
GET /api/paie/entrees/
```

**Paramètres de requête :**
- `periode_paie_id` (integer) : Filtrer par période
- `employe_id` (integer) : Filtrer par employé
- `salaire_net_min` (decimal) : Salaire net minimum
- `salaire_net_max` (decimal) : Salaire net maximum
- `is_validated` (boolean) : Filtrer par statut de validation
- `expand` (string) : Champs à étendre (employe_id, periode_paie_id)

**Réponse :**
```json
{
    "count": 150,
    "results": [
        {
            "id": 1,
            "employe_id": {
                "id": 1,
                "matricule": "EMP001",
                "nom": "MUKENDI",
                "prenom": "Jean"
            },
            "periode_paie_id": {
                "id": 1,
                "annee": 2024,
                "mois": 3
            },
            "salaire_base": "2000000.00",
            "salaire_brut": "3400000.00",
            "salaire_net": "2456750.00",
            "cotisations_salariales": {
                "inss_pension": "13500.00",
                "inss_risque": "1200.00",
                "mfp": "34000.00",
                "total": "48700.00"
            },
            "ire": "894550.00",
            "retenues_diverses": {
                "pret_vehicule": "150000.00",
                "total": "150000.00"
            },
            "is_validated": true,
            "payslip_generated": true,
            "payslip_file": "/media/payslips/2024/03/EMP001_payslip.pdf"
        }
    ]
}
```

### Détail d'une Entrée

```http
GET /api/paie/entrees/{id}/
```

**Réponse :**
```json
{
    "id": 1,
    "employe_id": {...},
    "periode_paie_id": {...},
    "contrat_reference": {
        "salaire_base": "2000000.00",
        "pourcentage_logement": 25,
        "pourcentage_deplacement": 15,
        "pourcentage_fonction": 30,
        "date_debut": "2023-01-01",
        "type_contrat": "PERMANENT"
    },
    "composants_salaire": {
        "salaire_base": "2000000.00",
        "indemnite_logement": "500000.00",
        "indemnite_deplacement": "300000.00",
        "indemnite_fonction": "600000.00",
        "allocation_familiale": "60000.00",
        "autres_avantages": "0.00",
        "salaire_brut": "3460000.00"
    },
    "cotisations_patronales": {
        "inss_pension": "27000.00",
        "inss_risque": "2400.00",
        "mfp": "51900.00",
        "fpc": "17300.00",
        "total": "98600.00"
    },
    "cotisations_salariales": {
        "inss_pension": "13500.00",
        "inss_risque": "1200.00",
        "mfp": "34600.00",
        "total": "49300.00"
    },
    "calcul_ire": {
        "base_imposable": "3410700.00",
        "tranche_1": {"montant": "150000.00", "taux": 0, "ire": "0.00"},
        "tranche_2": {"montant": "150000.00", "taux": 20, "ire": "30000.00"},
        "tranche_3": {"montant": "3110700.00", "taux": 30, "ire": "933210.00"},
        "total_ire": "963210.00"
    },
    "retenues_diverses": {
        "pret_vehicule": {
            "type": "LOAN",
            "description": "Prêt véhicule",
            "montant": "150000.00",
            "restant": "1650000.00"
        },
        "total": "150000.00"
    },
    "totaux": {
        "salaire_brut": "3460000.00",
        "total_deductions": "1162510.00",
        "salaire_net": "2297490.00",
        "cout_employeur": "3558600.00"
    }
}
```

### Recalculer une Entrée

```http
POST /api/paie/entrees/{id}/recalculate/
Content-Type: application/json

{
    "reason": "Correction des données contractuelles",
    "force_recalculate": true
}
```

### Générer un Bulletin de Paie

```http
POST /api/paie/entrees/{id}/generate-payslip/
Content-Type: application/json

{
    "template": "standard",
    "force_regenerate": false
}
```

**Réponse :**
```json
{
    "status": "success",
    "payslip_url": "/media/payslips/2024/03/EMP001_payslip.pdf",
    "generated_at": "2024-03-05T10:30:00Z",
    "file_size": 245760
}
```

### Télécharger un Bulletin

```http
GET /api/paie/entrees/{id}/download-payslip/
```

**Réponse :** Fichier PDF en téléchargement direct

## Retenues Employés

### Lister les Retenues

```http
GET /api/paie/retenues/
```

**Paramètres de requête :**
- `employe_id` (integer) : Filtrer par employé
- `type_retenue` (string) : Type de retenue (LOAN, ADVANCE, INSURANCE, UNION)
- `est_active` (boolean) : Filtrer par statut actif
- `date_debut_after` (date) : Date de début après
- `date_fin_before` (date) : Date de fin avant

**Réponse :**
```json
{
    "count": 45,
    "results": [
        {
            "id": 1,
            "employe_id": {
                "id": 1,
                "matricule": "EMP001",
                "nom_complet": "MUKENDI Jean"
            },
            "type_retenue": "LOAN",
            "description": "Prêt véhicule Toyota Corolla",
            "montant_mensuel": "150000.00",
            "montant_total": "1800000.00",
            "montant_deja_deduit": "150000.00",
            "montant_restant": "1650000.00",
            "date_debut": "2024-03-01",
            "date_fin": "2025-02-28",
            "est_active": true,
            "est_recurrente": true,
            "progression": 8.33,
            "cree_par": {
                "id": 2,
                "username": "rh_manager"
            }
        }
    ]
}
```

### Créer une Retenue

```http
POST /api/paie/retenues/
Content-Type: application/json

{
    "employe_id": 1,
    "type_retenue": "LOAN",
    "description": "Prêt personnel urgence médicale",
    "montant_mensuel": "100000.00",
    "montant_total": "1200000.00",
    "date_debut": "2024-04-01",
    "date_fin": "2025-03-31",
    "est_recurrente": true,
    "banque_beneficiaire": "Banque Commerciale du Congo",
    "compte_beneficiaire": "001-234567-89"
}
```

### Modifier une Retenue

```http
PUT /api/paie/retenues/{id}/
Content-Type: application/json

{
    "montant_mensuel": "120000.00",
    "description": "Prêt personnel - montant ajusté",
    "raison_modification": "Demande de l'employé pour augmenter le remboursement"
}
```

### Désactiver une Retenue

```http
POST /api/paie/retenues/{id}/deactivate/
Content-Type: application/json

{
    "raison": "Remboursement anticipé complet",
    "date_desactivation": "2024-03-15"
}
```

### Historique d'une Retenue

```http
GET /api/paie/retenues/{id}/history/
```

**Réponse :**
```json
{
    "retenue_id": 1,
    "historique": [
        {
            "date": "2024-03-01T08:00:00Z",
            "action": "CREATION",
            "utilisateur": "rh_manager",
            "details": {
                "montant_mensuel": "150000.00",
                "montant_total": "1800000.00"
            }
        },
        {
            "date": "2024-03-01T18:30:00Z",
            "action": "DEDUCTION_APPLIED",
            "periode": "2024-03",
            "montant_deduit": "150000.00",
            "montant_restant": "1650000.00"
        }
    ]
}
```

## Rapports et Exports

### Rapport de Masse Salariale

```http
GET /api/paie/reports/masse-salariale/
```

**Paramètres :**
- `annee` (integer) : Année du rapport
- `mois_debut` (integer) : Mois de début (optionnel)
- `mois_fin` (integer) : Mois de fin (optionnel)
- `format` (string) : Format de sortie (json, excel, pdf)

**Réponse :**
```json
{
    "periode": {
        "annee": 2024,
        "mois_debut": 1,
        "mois_fin": 3
    },
    "resume": {
        "nombre_employes_moyen": 48,
        "masse_salariale_totale": "72500000.00",
        "cotisations_patronales_totales": "10875000.00",
        "cotisations_salariales_totales": "7250000.00",
        "ire_total": "3600000.00",
        "cout_total_employeur": "83375000.00"
    },
    "evolution_mensuelle": [
        {
            "mois": 1,
            "nombre_employes": 47,
            "masse_salariale": "23500000.00",
            "cout_employeur": "27025000.00"
        },
        {
            "mois": 2,
            "masse_salariale": "24000000.00",
            "cout_employeur": "27600000.00"
        },
        {
            "mois": 3,
            "nombre_employes": 50,
            "masse_salariale": "25000000.00",
            "cout_employeur": "28750000.00"
        }
    ]
}
```

### Rapport par Employé

```http
GET /api/paie/reports/employe/{employe_id}/
```

**Paramètres :**
- `annee` (integer) : Année du rapport
- `include_payslips` (boolean) : Inclure les bulletins de paie

### Export Excel Personnalisé

```http
POST /api/paie/exports/custom/
Content-Type: application/json

{
    "type": "custom",
    "periode_debut": "2024-01-01",
    "periode_fin": "2024-03-31",
    "colonnes": [
        "employe.matricule",
        "employe.nom_complet",
        "salaire_base",
        "salaire_brut",
        "salaire_net",
        "cotisations_salariales.total",
        "ire"
    ],
    "filtres": {
        "service": "IT",
        "salaire_net_min": "500000"
    },
    "format": "excel",
    "nom_fichier": "rapport_it_q1_2024"
}
```

## Codes d'Erreur

### Erreurs d'Authentification (401)

```json
{
    "error": "AUTHENTICATION_FAILED",
    "message": "Token invalide ou expiré",
    "code": "AUTH_001"
}
```

### Erreurs de Validation (400)

```json
{
    "error": "VALIDATION_ERROR",
    "message": "Données invalides",
    "details": {
        "montant_mensuel": ["Ce champ est requis"],
        "date_debut": ["La date doit être dans le futur"]
    },
    "code": "VAL_001"
}
```

### Erreurs Métier (422)

```json
{
    "error": "BUSINESS_RULE_VIOLATION",
    "message": "Une période existe déjà pour ce mois/année",
    "code": "BUS_001"
}
```

### Erreurs de Calcul (500)

```json
{
    "error": "CALCULATION_ERROR",
    "message": "Erreur lors du calcul salarial",
    "details": {
        "employe_id": 123,
        "error_type": "MISSING_CONTRACT"
    },
    "code": "CALC_001"
}
```

## Limites et Quotas

### Limites de Taux

- **Requêtes par minute** : 1000 pour les utilisateurs authentifiés
- **Requêtes par heure** : 10000 pour les utilisateurs authentifiés
- **Taille maximale de requête** : 10 MB
- **Timeout de requête** : 30 secondes (60 secondes pour les exports)

### Pagination

- **Taille de page par défaut** : 20
- **Taille de page maximale** : 100
- **Format de pagination** : Offset-based avec liens next/previous

## Webhooks

### Configuration des Webhooks

```http
POST /api/webhooks/
Content-Type: application/json

{
    "url": "https://your-app.com/webhooks/paie",
    "events": ["period.processed", "payslip.generated"],
    "secret": "your-webhook-secret",
    "active": true
}
```

### Événements Disponibles

- `period.created` : Période créée
- `period.processed` : Période traitée
- `period.finalized` : Période finalisée
- `period.approved` : Période approuvée
- `payslip.generated` : Bulletin généré
- `deduction.created` : Retenue créée
- `calculation.error` : Erreur de calcul

### Format des Webhooks

```json
{
    "event": "period.processed",
    "timestamp": "2024-03-01T10:30:00Z",
    "data": {
        "period_id": 1,
        "annee": 2024,
        "mois": 3,
        "employes_traites": 50,
        "masse_salariale": "25000000.00"
    },
    "signature": "sha256=..."
}
```

---

*Cette documentation API est générée automatiquement. Pour la version interactive avec possibilité de test, consultez l'interface Swagger à `/api/docs/`.*
