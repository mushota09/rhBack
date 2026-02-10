# Test Fixes and System Validation Spec

## Vue d'ensemble

Cette spécification définit le plan pour corriger les 13 tests échoués dans le système de gestion des utilisateurs et atteindre 100% de réussite des tests (34/34).

## État Actuel

- **Tests Passants**: 22/34 (65%)
- **Tests Échoués**: 13/34 (35%)
- **Temps d'Exécution**: ~4min 30s

## Objectif

- **Tests Passants**: 34/34 (100%)
- **Couverture de Code**: > 90%
- **Temps d'Exécution**: < 5 minutes
- **Zéro Régression**: Tous les tests précédemment passants continuent de passer

## Problèmes Identifiés

### Problèmes Critiques (9 tests)

1. **Configuration PostgreSQL et Redis** (Tous les tests)
   - Approche: Utiliser PostgreSQL et Redis réels pour voir les erreurs concrètes
   - Tests affectés: Tous les tests
   - Solution: Supprimer la configuration de test spéciale et utiliser la config normale

2. **UserGroupSerializer** (3 tests)
   - Erreur: `IntegrityError: null value in column "user_id" violates not-null constraint`
   - Tests affectés: Workflows d'assignation utilisateur-groupe
   - Solution: Ajouter validations explicites dans le serializer

3. **GroupPermissionSerializer** (2 tests)
   - Erreur: `AttributeError: 'GroupPermissionReadSerializer' object has no attribute 'asave'`
   - Tests affectés: Workflows de gestion des permissions
   - Solution: Créer un write serializer séparé

### Problèmes Mineurs (4 tests)

4. **Noms de champs JWT** (2 tests)
   - Erreur: `KeyError: 'access'`
   - Tests affectés: Tests d'authentification et d'intégration
   - Solution: Standardiser sur 'access' et 'refresh'

5. **Codes HTTP** (1 test)
   - Erreur: `AssertionError: 403 != 401`
   - Test affecté: Test d'accès non autorisé
   - Solution: Clarifier 401 vs 403

6. **Variables manquantes** (1 test)
   - Erreur: `NameError: name 'user_groups_url' is not defined`
   - Test affecté: Test de suppression d'assignation
   - Solution: Définir la variable

## Plan d'Implémentation

### Phase 1: Configuration (4 tests) - 30 minutes
- Corriger la détection du mode test dans settings.py
- Utiliser
ur utiliser 'access' et 'refresh'
- Modifier RefreshTokenView
- Mettre à jour la documentation

### Phase 5: Finalisations (2 tests) - 30 minutes
- Corriger les codes HTTP (401 vs 403)
- Ajouter les variables manquantes
- Valider les corrections

### Phase 6: Validation (Tous les tests) - 30 minutes
- Exécuter la suite complète
- Vérifier la couverture de code
- Confirmer zéro régression

### Phase 7: Documentation - 45 minutes
- Documenter les corrections
- Créer un guide de bonnes pratiques
- Mettre à jour PROGRES_TESTS.md

**Temps Total Estimé**: 4h 30min

## Fichiers de la Spec

- **requirements.md**: Définit les 8 exigences pour corriger les tests
- **design.md**: Détaille les solutions techniques avec exemples de code
- **tasks.md**: Plan d'implémentation détaillé avec checkpoints
- **README.md**: Ce fichier - vue d'ensemble de la spec

## Comment Utiliser Cette Spec

1. **Lire requirements.md** pour comprendre les exigences
2. **Consulter design.md** pour voir les solutions techniques
3. **Suivre tasks.md** pour l'implémentation étape par étape
4. **Valider à chaque checkpoint** pour confirmer la progression

## Commandes Utiles

```bash
# Exécuter tous les tests
python -m pytest user_app/tests/ -v

# Exécuter avec couverture
python -m pytest user_app/tests/ --cov=user_app --cov-report=html

# Exécuter un test spécifique
python -m pytest user_app/tests/test_user_management_e2e.py::UserManagementE2ETestCase::test_user_group_assignment_workflow -v
```

## Critères de Succès

- ✅ 34/34 tests passent (100%)
- ✅ Couverture de code > 90%
- ✅ Temps d'exécution < 5 minutes
- ✅ Aucune régression
- ✅ Documentation complète
- ✅ Code propre et validé

## Prochaines Étapes

1. Commencer par la Phase 1 (Configuration Redis)
2. Valider avec Checkpoint 1 (26/34 tests passent)
3. Continuer avec les Phases 2-3 (Serializers)
4. Valider avec Checkpoint 2 (31/34 tests passent)
5. Finaliser avec les Phases 4-5
6. Valider avec Checkpoint 3 (34/34 tests passent)
7. Documenter dans la Phase 7

## Références

- **Conversation Summary**: Voir le contexte de transfert pour l'historique complet
- **PROGRES_TESTS.md**: État actuel des tests (22/34 passent)
- **RESULTATS_TESTS_COMPLETS.md**: Rapport détaillé des tests initiaux
- **user-management spec**: Spécification du système de gestion des utilisateurs
