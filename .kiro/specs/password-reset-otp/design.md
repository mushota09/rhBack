# Design Document: Password Reset OTP System

## Overview

Ce document décrit la conception d'un système de réinitialisation de mot de passe par OTP (One-Time Password) asynchrone utilisant ADRF et ADRF-flex-fields. Le système permettra aux utilisateurs de réinitialiser leur mot de passe de manière sécurisée via un code OTP envoyé par email, avec toutes les opérations exécutées de manière asynchrone pour optimiser les performances.

## Architecture

Le système suit une architecture modulaire Django avec les composants suivants :

```mermaid
graph TB
    A[Client] --> B[ADRF APIView]
    B --> C[Serializers ADRF-flex-fields]
    C --> D[Business Logic]
    D --> E[PasswordResetOTP Model]
    D --> F[User Model]
    D --> G
ash = models.CharField(max_length=255)  # Hash du code OTP
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
```

### 2. Serializers (ADRF-flex-fields)

#### PasswordResetRequestSerializer
- Validation de l'email
- Champs : email

#### PasswordResetConfirmSerializer
- Validation OTP et nouveau mot de passe
- Champs : email, otp_code, new_password, confirm_password

### 3. Views (ADRF APIView)

#### PasswordResetRequestView
- Endpoint : POST /api/password-reset/request/
- Génère et envoie OTP
- Méthodes asynchrones

#### PasswordResetConfirmView
- Endpoint : POST /api/password-reset/confirm/
- Valide OTP et met à jour le mot de passe
- Méthodes asynchrones

### 4. Utilities

#### OTP Generator
- Génération de codes OTP sécurisés
- Hachage des codes pour stockage

#### Email Service
- Envoi asynchrone d'emails
- Templates HTML pour les codes OTP

#### Rate Limiting
- Limitation des tentatives par IP/email
- Nettoyage automatique des anciens OTP

## Data Models

### PasswordResetOTP
```python
{
    "id": "UUID primary key",
    "user_id": "Foreign key vers User",
    "otp_hash": "Hash SHA256 du code OTP",
    "created_at": "Timestamp de création",
    "expires_at": "Timestamp d'expiration (created_at + 10 minutes)",
    "is_used": "Boolean indiquant si l'OTP a été utilisé",
    "attempts": "Nombre de tentatives de validation"
}
```

### Rate Limiting Cache
```python
{
    "email_requests": "Compteur de demandes par email",
    "ip_requests": "Compteur de demandes par IP",
    "otp_attempts": "Compteur de tentatives OTP par email"
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: OTP Generation and Storage Consistency
*For any* valid email address, when requesting an OTP, the system should generate a unique code, store it with proper timestamps, and set expiration to exactly 10 minutes from creation time.
**Validates: Requirements 1.1, 1.2, 5.4**

### Property 2: Email Notification Reliability
*For any* OTP creation request, the email service should be called with the correct reci
irements 1.5**

### Property 5: Password Update Correctness
*For any* valid OTP and new password combination, the system should successfully update the user's password and the user should be able to authenticate with the new password.
**Validates: Requirements 2.1**

### Property 6: OTP Expiration and Cleanup
*For any* OTP that has exceeded its expiration time, the system should reject it and automatically remove it from storage.
**Validates: Requirements 2.2, 3.3**

### Property 7: OTP Single-Use Enforcement
*For any* valid OTP, after it has been successfully used to reset a password, any subsequent attempt to use the same OTP should be rejected.
**Validates: Requirements 2.4**

### Property 8: Password Strength Validation
*For any* password reset attempt, passwords that don't meet strength requirements should be rejected while strong passwords should be accepted.
**Validates: Requirements 2.5**

### Property 9: Rate Limiting Protection
*For any* email address, after 3 reset requests within 1 hour, further requests should be temporarily blocked.
**Validates: Requirements 3.1**

### Property 10: Brute Force Protection
*For any* OTP, after 5 invalid validation attempts, the OTP should be invalidated and further attempts should be rejected.
**Validates: Requirements 3.2, 2.3**

### Property 11: Audit Trail Completeness
*For any* password reset attempt (successful or failed), a corresponding audit log entry should be created with appropriate details.
**Validates: Requirements 3.4**

### Property 12: OTP Security Storage
*For any* generated OTP, the value stored in the database should be a hash, never the plain text code.
**Validates: Requirements 3.5**

### Property 13: Input Validation and Error Messaging
*For any* invalid input data, the system should reject the request and provide clear, appropriate error messages without exposing sensitive information.
**Validates: Requirements 5.3, 5.5**

## Error Handling

### OTP Generation Errors
- **Email Service Failure**: Si l'envoi d'email échoue, l'OTP généré doit être supprimé et une erreur appropriée retournée
- **Database Errors**: Les erreurs de base de données lors de la création d'OTP doivent être gérées gracieusement
- **Rate Limiting**: Les demandes bloquées doivent retourner des messages d'erreur clairs avec le temps d'attente

### OTP Validation Errors
- **Invalid Format**: Les codes OTP mal formatés doivent être rejetés immédiatement
- **Expired Codes**: Les codes expirés doivent être supprimés automatiquement lors de la validation
- **Used Codes**: Les tentatives d'utilisation de codes déjà utilisés doivent être loggées comme tentatives suspectes

### Password Reset Errors
- **Weak Passwords**: Les mots de passe faibles doivent être rejetés avec des conseils de renforcement
- **User Not Found**: Les tentatives sur des utilisateurs inexistants doivent être gérées de manière sécurisée
- **Account Locked**: Les comptes verrouillés doivent empêcher la réinitialisation

## Testing Strategy

### Dual Testing Approach
Le système utilisera une approche de test double combinant :

**Unit Tests** :
- Tests spécifiques pour les cas d'usage courants
- Validation des cas limites et conditions d'erreur
- Tests d'intégration entre composants
- Vérification des formats de réponse API

**Property-Based Tests** :
- Validation des propriétés universelles sur de nombreuses entrées générées
- Tests de robustesse avec des données aléatoires
- Vérification de la cohérence comportementale
- Configuration minimale de 100 itérations par test de propriété

### Property Test Configuration
- **Framework**: Utilisation de `hypothesis` pour Python
- **Iterations**: Minimum 100 itérations par test de propriété
- **Tagging**: Chaque test de propriété sera tagué avec le format :
  **Feature: password-reset-otp, Property {number}: {property_text}**
- **Coverage**: Chaque propriété de correction doit être implémentée par UN SEUL test de propriété

### Test Data Generation
- **Emails**: Génération d'adresses email valides et invalides
- **OTP Codes**: Génération de codes de différentes longueurs et formats
- **Passwords**: Génération de mots de passe de différentes forces
- **Timestamps**: Génération de dates/heures pour tester l'expiration
- **Rate Limiting**: Simulation de requêtes multiples pour tester les limites
