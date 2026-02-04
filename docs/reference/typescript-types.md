# Types TypeScript - Référence Complète

Cette documentation détaille toutes les interfaces TypeScript utilisées dans le frontend pour assurer la cohérence des types avec l'API backend.

## Types de Base

### BaseModel
Interface de base pour tous les modèles avec timestamps:
```typescript
interface BaseModel {
  id: number;
  created_at: string;
  updated_at: string;
}
```

## Gestion Organisationnelle

### Service
Interface pour la gestion des services (3 colonnes - Dialog CRUD):
```typescript
interface Service {
  id: number;
  titre: string;
  code: string;
  description?: string;
}
```

### Poste
Interface pour la gestion des postes (4 colonnes - Dialog CRUD):
```typescript
interface Poste {
  id: number;
  titre: string;
  code: string;
  description?: string;
  service_id: number;
  service?: Service;
}
```

## Gestion des Employés

### Employe
Interface complète pour les employés (25+ colonnes - Page CRUD):
```typescript
interface Employe extends BaseModel {
  // Informations personnelles
  prenom: string;
  nom: string;
  postnom?: string;
  date_naissance: string;
  sexe: 'M' | 'F' | 'O';
  statut_matrimonial: 'S' | 'M' | 'D' | 'W';
  nationalite: string;
  
  // Informations financières
  banque: string;
  numero_compte: string;
  numero_inss: string;
  
  // Informations de contact
  email_personnel: string;
  email_professionnel?: string;
  telephone_personnel: string;
  telephone_professionnel?: string;
  
  // Adresse
  adresse_ligne1: string;
  adresse_ligne2?: string;
  ville?: string;
  province?: string;
  code_postal?: string;
  pays?: string;
  
  // Informations d'emploi
  matricule?: string;
  poste_id?: number;
  responsable_id?: number;
  date_embauche: string;
  statut_emploi: 'ACTIVE' | 'INACTIVE' | 'TERMINATED' | 'SUSPENDED';
  niveau_etude: string;
  
  // Informations familiales
  nombre_enfants: number;
  nom_conjoint?: string;
  biographie?: string;
  
  // Contact d'urgence
  nom_contact_urgence: string;
  lien_contact_urgence: string;
  telephone_contact_urgence: string;
  
  // Relations
  poste?: Poste;
  responsable?: Employe;
  full_name?: string;
}
```

### Contrat
Interface pour la gestion des contrats (15+ colonnes - Page CRUD):
```typescript
interface Contrat {
  id: number;
  employe_id: number;
  type_contrat: 'PERMANENT' | 'TEMPORARY' | 'INTERNSHIP' | 'CONSULTANT';
  date_debut: string;
  date_fin?: string;
  type_salaire: 'H' | 'M'; // Heure ou Mensuel
  salaire_base: number;
  devise: string;
  
  // Indemnités (en pourcentage)
  indemnite_logement: number;
  indemnite_deplacement: number;
  prime_fonction: number;
  autre_avantage: number;
  
  // Cotisations (en pourcentage)
  assurance_patronale: number;
  assurance_salariale: number;
  fpc_patronale: number;
  fpc_salariale: number;
  
  statut: string;
  commentaire?: string;
  employe?: Employe;
}
```

## Gestion des Documents

### Document
Interface pour la gestion des documents (8+ colonnes - Page CRUD):
```typescript
interface Document extends BaseModel {
  employe_id: number;
  document_type: 'CONTRACT' | 'ID' | 'RESUME' | 'CERTIFICATE' | 
                 'PERFORMANCE' | 'DISCIPLINARY' | 'MEDICAL' | 
                 'TRAINING' | 'OTHER';
  titre: string;
  description?: string;
  file: string;
  uploaded_by: string;
  expiry_date?: string;
  employe?: Employe;
}
```

## Gestion des Utilisateurs

### User
Interface pour les comptes utilisateurs (12+ colonnes - Page CRUD):
```typescript
interface User extends BaseModel {
  phone?: string;
  email: string;
  photo?: string;
  employe_id?: number;
  nom?: string;
  prenom?: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  last_login?: string;
  date_joined: string;
  employe?: Employe;
}
```

## Audit et Traçabilité

### AuditLog
Interface pour le journal d'audit (8+ colonnes - Page lecture seule):
```typescript
interface AuditLog {
  id: number;
  user_id?: number;
  action: 'CREATE' | 'UPDATE' | 'DELETE' | 'LOGIN' | 
          'LOGOUT' | 'VIEW' | 'EXPORT';
  type_ressource: string;
  id_ressource?: string;
  anciennes_valeurs?: Record<string, any>;
  nouvelles_valeurs?: Record<string, any>;
  adresse_ip?: string;
  user_agent?: string;
  timestamp: string;
  user?: User;
}
```

### HistoriqueContrat
Interface pour l'historique des contrats (8+ colonnes - Page CRUD):
```typescript
interface HistoriqueContrat {
  id: number;
  contrat_id: number;
  date_modification: string;
  ancien_salaire: number;
  nouveau_salaire: number;
  prime_fonction: number;
  indemnites: Record<string, any>;
  cotisations: Record<string, any>;
  allocation_familiale: number;
  autres_avantages: number;
  commentaire?: string;
  contrat?: Contrat;
}
```

## Options de Dropdown

### Sexe
```typescript
const SEXE_OPTIONS = [
  { label: 'Homme', value: 'M' },
  { label: 'Femme', value: 'F' },
  { label: 'Autre', value: 'O' },
];
```

### Statut Matrimonial
```typescript
const STATUT_MATRIMONIAL_OPTIONS = [
  { label: 'Célibataire', value: 'S' },
  { label: 'Marié', value: 'M' },
  { label: 'Divorcé', value: 'D' },
  { label: 'Veuf', value: 'W' },
];
```

### Statut d'Emploi
```typescript
const STATUT_EMPLOI_OPTIONS = [
  { label: 'Actif', value: 'ACTIVE' },
  { label: 'Inactif', value: 'INACTIVE' },
  { label: 'Résilié', value: 'TERMINATED' },
  { label: 'Suspendu', value: 'SUSPENDED' },
];
```

### Type de Contrat
```typescript
const TYPE_CONTRAT_OPTIONS = [
  { label: 'Permanent', value: 'PERMANENT' },
  { label: 'Temporaire', value: 'TEMPORARY' },
  { label: 'Stage', value: 'INTERNSHIP' },
  { label: 'Consultant', value: 'CONSULTANT' },
];
```

### Type de Salaire
```typescript
const TYPE_SALAIRE_OPTIONS = [
  { label: 'Heure', value: 'H' },
  { label: 'Mensuel', value: 'M' },
];
```

### Type de Document
```typescript
const DOCUMENT_TYPE_OPTIONS = [
  { label: 'Contrat de travail', value: 'CONTRACT' },
  { label: 'Pièce d\'identité', value: 'ID' },
  { label: 'CV', value: 'RESUME' },
  { label: 'Certificat', value: 'CERTIFICATE' },
  { label: 'Évaluation', value: 'PERFORMANCE' },
  { label: 'Action disciplinaire', value: 'DISCIPLINARY' },
  { label: 'Certificat médical', value: 'MEDICAL' },
  { label: 'Certificat de formation', value: 'TRAINING' },
  { label: 'Autre', value: 'OTHER' },
];
```

## Utilisation des Types

### Import des Types
```typescript
import {
  Employe,
  Contrat,
  Service,
  Poste,
  Document,
  User,
  AuditLog,
  HistoriqueContrat,
  SEXE_OPTIONS,
  STATUT_EMPLOI_OPTIONS
} from '@/types/user_app';
```

### Exemple d'Utilisation dans un Composant
```typescript
interface EmployeFormProps {
  employe?: Employe;
  onSubmit: (data: Partial<Employe>) => void;
}

const EmployeForm: React.FC<EmployeFormProps> = ({ employe, onSubmit }) => {
  const [formData, setFormData] = useState<Partial<Employe>>(
    employe || {
      prenom: '',
      nom: '',
      email_personnel: '',
      telephone_personnel: '',
      date_naissance: '',
      sexe: 'M',
      statut_matrimonial: 'S',
      statut_emploi: 'ACTIVE',
      nombre_enfants: 0
    }
  );

  // Logique du formulaire...
};
```

### Validation des Types
```typescript
const validateEmploye = (data: Partial<Employe>): string[] => {
  const errors: string[] = [];
  
  if (!data.prenom) errors.push('Le prénom est requis');
  if (!data.nom) errors.push('Le nom est requis');
  if (!data.email_personnel) errors.push('L\'email personnel est requis');
  if (!data.telephone_personnel) errors.push('Le téléphone personnel est requis');
  
  return errors;
};
```

## Correspondance API

Ces types TypeScript correspondent directement aux modèles Django du backend:

- `Employe` ↔ `user_app.models.employe`
- `Contrat` ↔ `user_app.models.contrat`
- `Service` ↔ `user_app.models.service`
- `Poste` ↔ `user_app.models.poste`
- `Document` ↔ `user_app.models.document`
- `User` ↔ `user_app.models.User`
- `AuditLog` ↔ `user_app.models.audit_log`
- `HistoriqueContrat` ↔ `user_app.models.historique_contrat`

Cette correspondance assure la cohérence des données entre le frontend et le backend, facilitant le développement et réduisant les erreurs de type.

---

*Dernière mise à jour : Février 2026*