# Implementation Plan: Système de Paie

## Overview

Ce plan d'implémentation détaille les étapes pour développer un système de paie complet avec calculs automatisés, génération de bulletins de paie et gestion des retenues. L'implémentation utilise Django avec ADRF pour les APIs asynchrones et suit une approche modulaire avec des services métier spécialisés.

## Tasks

- [x] 1. Setup et Configuration du Projet
  - Configurer les dépendances pour génération PDF (reportlab, weasyprint)
  - Configurer les settings pour stockage de fichiers
  - Mettre à jour les modèles existants avec les nouveaux champs
  - _Requirements: 9.5, 4.6, 4.7_

- [x] 2. Amélioration des Modèles de Données
  - [x] 2.1 Étendre le modèle periode_paie
    - Ajouter les champs de totaux et statistiques
    - Ajouter la relation avec User pour traite_par
    - _Requirements: 1.1, 1.3, 8.1_

  - [x] 2.2 Écrire les tests de propriété pour periode_paie
    - **Property 1: Period Creation Consistency**
    - **Property 2: Period Uniqueness Enforcement**
    - **Property 3: Period Status Transitions**
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [x] 2.3 Étendre le modèle entree_paie
    - Ajouter contrat_reference (JSONField)
    - Ajouter les champs de validation et audit
    - Restructurer les cotisations en JSONField
    - _Requirements: 5.3, 7.1, 8.2_

  - [x] 2.4 Écrire les tests de propriété pour entree_paie
    - **Property 21: Payslip File Storage**
    - **Property 33: Payslip Generation Audit**
    - **Validates: Requirements 4.7, 8.2**

  - [x] 2.5 Étendre le modèle retenue_employe
    - Ajouter montant_deja_deduit pour suivi des totaux
    - Ajouter relation avec User pour cree_par
    - Ajouter champs bancaires pour bénéficiaires
    - _Requirements: 3.1, 3.3, 8.3_

  - [x] 2.6 Écrire les tests de propriété pour retenue_employe
    - **Property 12: Deduction Creation Comp
ents: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [ ] 3.2 Écrire les tests de propriété pour SalaryCalculatorService
    - **Property 6: Base Salary Usage**
    - **Property 7: Allowance Percentage Application**
    - **Property 8: Family Allowance Progressive Scale**
    - **Property 9: INSS Contribution Caps**
    - **Property 10: IRE Progressive Tax Calculation**
    - **Property 11: Net Salary Formula Correctness**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

  - [ ] 3.3 Créer DeductionManagerService
    - Implémenter get_active_deductions avec filtres de période
    - Implémenter apply_deduction avec vérification des totaux
    - Implémenter update_deduction_balance pour suivi
    - _Requirements: 3.2, 3.3, 3.4, 3.5_

  - [ ] 3.4 Écrire les tests de propriété pour DeductionManagerService
    - **Property 13: Recurring Deduction Application**
    - **Property 15: Active Deductions Inclusion**
    - **Property 28: Deduction Validity Verification**
    - **Validates: Requirements 3.2, 3.4, 7.2**

  - [ ] 3.5 Créer PeriodProcessorService
    - Implémenter create_period avec calcul automatique des dates
    - Implémenter process_period avec traitement par lots
    - Implémenter validate_period avec contrôles de cohérence
    - Implémenter finalize_period et approve_period
    - _Requirements: 1.1, 1.3, 1.4, 5.1, 5.2, 5.4, 7.5_

  - [ ] 3.6 Écrire les tests de propriété pour PeriodProcessorService
    - **Property 5: Automatic Period Date Calculation**
    - **Property 22: Batch Processing Coverage**
    - **Property 23: Payroll Entry Creation**
    - **Property 25: Processing Atomicity**
    - **Property 31: Error Prevention Before Finalization**
    - **Validates: Requirements 1.5, 5.1, 5.2, 5.4, 7.5**

- [ ] 4. Checkpoint - Services Métier
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Développement du Générateur de Bulletins de Paie
  - [x] 5.1 Créer PayslipGeneratorService
    - Implémenter generate_payslip avec template HTML/CSS
    - Implémenter render_payslip_pdf avec reportlab ou weasyprint
    - Implémenter save_payslip_file avec gestion du stockage
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 5.2 Écrire les tests de propriété pour PayslipGeneratorService
    - **Property 16: Payslip Information Completeness**
    - **Property 17: Payslip Salary Component Details**
    - **Property 18: Payslip Contribution Details**
    - **Property 19: Payslip Deduction Details**
    - **Property 20: Payslip Net Salary Display**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

  - [x] 5.3 Créer les templates de bulletins de paie
    - Créer template HTML avec mise en forme professionnelle
    - Ajouter styles CSS pour impression PDF
    - Inclure logo entreprise et informations légales
    - _Requirements: 4.6_

  - [x] 5.4 Écrire les tests unitaires pour templates
    - Tester le rendu avec données complètes
    - Tester la gestion des cas avec données manquantes
    - _Requirements: 4.6_

- [ ] 6. Développement des APIs Asynchrones
  - [x] 6.1 Créer PeriodePaieAPIView
    - Implémenter CRUD asynchrone avec ADRF
    - Ajouter endpoints process, finalize, approve
    - Ajouter endpoint export Excel
    - Implémenter filtres et pagination
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 6.1, 6.4, 9.1, 9.2_

  - [x] 6.2 Écrire les tests de propriété pour PeriodePaieAPIView
    - **Property 4: Period Approval Immutability**
    - **Property 24: Contract Data Consistency**
    - **Property 26: Period Reprocessing Capability**
    - **Property 35: API Availability for Consultation**
    - **Property 36: API Availability for Processing**
    - **Validates: Requirements 1.4, 5.3, 5.5, 9.1, 9.2**

  - [x] 6.3 Créer EntreePaieAPIView
    - Implémenter consultation avec filtres avancés
    - Ajouter endpoint recalculate pour recalcul individuel
    - Ajouter endpoints generate_payslip et download_payslip
    - _Requirements: 6.2, 4.5, 4.7, 9.1, 9.3_

  - [ ] 6.4 Écrire les tests de propriété pour EntreePaieAPIView
    - **Property 37: API Availability for Payslip Generation**
    - **Property 39: Asynchronous Batch Processing**
    - **Validates: Requirements 9.3, 10.2**

  - [x] 6.5 Créer RetenueEmployeAPIView
    - Implémenter CRUD complet avec validation
    - Ajouter endpoint deactivate pour désactivation
    - Ajouter endpoint history pour historique
    - _Requirements: 3.1, 3.5, 6.3, 8.4, 9.1_

  - [ ] 6.6 Écrire les tests de propriété pour RetenueEmployeAPIView
    - **Property 27: Contract Validation Before Calculation**
    - **Property 30: Error Alert Generation**
    - **Validates: Requirements 7.1, 7.4**

- [x] 7. Implémentation de la Sécurité et Authentification
  - [x] 7.1 Configurer l'authentification JWT
    - Activer JWT dans settings Django
    - Configurer les middlewares d'authentification
    - Ajouter les permissions par rôle
    - _Requirements: 9.4_

  - [x] 7.2 Écrire les tests de propriété pour sécurité
    - **Property 38: API Security with JWT**
    - **Validates: Requirements 9.4**

  - [x] 7.3 Implémenter les contrôles d'accès
    - Définir les permissions par endpoint
    - Implémenter la validation des rôles utilisateur
    - Ajouter l'audit des accès
    - _Requirements: 8.1, 8.2_

- [x] 8. Développement des Fonctionnalités de Validation
  - [x] 8.1 Implémenter les validations métier
    - Validation des contrats actifs avant calcul
    - Validation des retenues avant application
    - Validation des plafonds réglementaires
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 8.2 Écrire les tests de propriété pour validations
    - **Property 29: Regulatory Compliance Verification**
    - **Property 32: Operation Audit Logging**
    - **Validates: Requirements 7.3, 8.1**

  - [x] 8.3 Implémenter le système d'alertes
    - Créer le modèle Alert pour stockage
    - Implémenter la génération d'alertes automatiques
    - Ajouter les notifications par email
    - _Requirements: 7.4_

- [x] 9. Optimisation des Performances
  - [x] 9.1 Implémenter le traitement asynchrone
    - Configurer Celery pour tâches en arrière-plan
    - Créer les tâches pour traitement de périodes
    - Créer les tâches pour génération de bulletins
    - _Requirements: 10.2, 10.5_

  - [x] 9.2 Écrire les tests de propriété pour performances
    - **Property 40: Parallel Processing Capability**
    - **Validates: Requirements 10.5**

  - [x] 9.3 Optimiser les requêtes de base de données
    - Ajouter select_related et prefetch_related
    - Créer les index nécessaires
    - Implémenter la mise en cache des données de référence
    - _Requirements: 10.3, 10.4_

- [x] 10. Développement des Fonctionnalités d'Export et Reporting
  - [x] 10.1 Implémenter l'export Excel
    - Créer les fonctions d'export avec openpyxl
    - Ajouter les formats pour différents types de données
    - Implémenter l'export asynchrone pour gros volumes
    - _Requirements: 6.4_

  - [x] 10.2 Écrire les tests unitaires pour export
    - Tester l'export de périodes de paie
    - Tester l'export d'entrées de paie
    - Tester l'export de retenues
    - _Requirements: 6.4_

  - [x] 10.3 Implémenter les rapports d'audit
    - Créer les vues pour rapports par période
    - Créer les vues pour historique par employé
    - Ajouter les totaux et statistiques
    - _Requirements: 6.5, 8.4, 8.5_

- [ ] 11. Checkpoint - Fonctionnalités Avancées
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Intégration et Tests d'Intégration
  - [ ] 12.1 Créer les tests d'intégration API
    - Tester les workflows complets de traitement
    - Tester l'intégration entre services
    - Tester les cas d'erreur et rollback
    - _Requirements: 5.4, 7.5_

  - [ ] 12.2 Écrire les tests de propriété d'intégration
    - Tester les propriétés sur workflows complets
    - Valider la cohérence des données entre services
    - _Requirements: All_

  - [x] 12.3 Créer les fixtures et données de test
    - Créer des employés avec différents profils
    - Créer des contrats avec différentes configurations
    - Créer des retenues de test
    - _Requirements: All_

- [x] 13. Documentation et Finalisation
  - [x] 13.1 Générer la documentation API
    - Configurer drf-spectacular pour OpenAPI
    - Ajouter les descriptions détaillées des endpoints
    - Générer la documentation Swagger
    - _Requirements: 9.5_

  - [x] 13.2 Créer la documentation utilisateur
    - Documenter les processus de paie
    - Créer les guides d'utilisation
    - Documenter les paramètres de configuration
    - _Requirements: 9.5_

  - [x] 13.3 Optimisations finales et nettoyage
    - Nettoyer le code et améliorer les performances
    - Ajouter les logs appropriés
    - Finaliser la gestion d'erreurs
    - _Requirements: 10.1, 10.3, 10.4_

- [ ] 14. Final Checkpoint - Système Complet
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Les tâches incluent maintenant tous les tests pour une couverture complète
- Chaque tâche référence les exigences spécifiques pour la traçabilité
- Les checkpoints permettent une validation incrémentale
- Les tests de propriété valident la correction universelle
- Les tests unitaires valident les exemples spécifiques et cas limites
- L'implémentation suit une approche modulaire avec services métier séparés
- Les APIs asynchrones optimisent les performances pour les gros volumes
- La génération de bulletins PDF utilise des templates professionnels
