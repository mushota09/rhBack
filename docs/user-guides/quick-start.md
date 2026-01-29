# Guide de Démarrage Rapide

Ce guide vous permettra de commencer rapidement avec le système de paie en vous montrant les opérations essentielles.

## Vue d'Ensemble

Le système de paie automatise le calcul des salaires, la gestion des retenues et la génération des bulletins de paie. Il suit un processus mensuel structuré :

1. **Création de période** → 2. **Traitement des salaires** → 3. **Validation** → 4. **Génération des bulletins** → 5. **Approbation**

## Prérequis

Avant de commencer, assurez-vous d'avoir :
- ✅ Accès au système avec les permissions appropriées
- ✅ Employés créés avec contrats actifs
- ✅ Paramètres de paie configurés (barèmes, taux)

## Processus Mensuel de Paie

### Étape 1 : Créer une Nouvelle Période

```http
POST /api/paie/periodes/
{
    "annee": 2024,
    "mois": 1
}
```

**Via l'interface :**
1. Accédez à **Paie > Périodes**
2. Cliquez sur **Nouvelle Période**
3. Sélectionnez l'année et le mois
4. Cliquez sur **Créer**

### Étape 2 : Traiter la Période

```http
POST /api/paie/periodes/{id}/process/
```

**Via l'interface :**
1. Sélectionnez la période créée
2. Cliquez sur **Traiter la Période**
3. Attendez la fin du traitement (barre de progression)
4. Vérifiez les résultats

### Étape 3 : Valider les Calculs

**Vérifications automatiques :**
- ✅ Contrats actifs pour tous les employés
- ✅ Calculs conformes aux barèmes
- ✅ Retenues appliquées correctement
- ✅ Totaux cohérents

**Actions si erreurs détectées :**
1. Consultez les alertes générées
2. Corrigez les données sources
3. Relancez le traitement

### Étape 4 : Générer les Bulletins

```http
POST /api/paie/periodes/{id}/generate-payslips/
```

**Via l'interface :**
1. Cliquez sur **Générer Bulletins**
2. Sélectionnez le template (Simple, Standard, Premium)
3. Lancez la génération
4. Téléchargez les fichiers PDF

### Étape 5 : Finaliser et Approuver

```http
POST /api/paie/periodes/{id}/finalize/
POST /api/paie/periodes/{id}/approve/
```

**Via l'interface :**
1. Cliquez sur **Finaliser** (verrouille les modifications)
2. Cliquez sur **Approuver** (validation finale)

## Exemple Complet

Voici un exemple de traitement pour janvier 2024 :

### 1. Création de la Période

```bash
curl -X POST http://localhost:8000/api/paie/periodes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "annee": 2024,
    "mois": 1
  }'
```

**Réponse :**
```json
{
    "id": 1,
    "annee": 2024,
    "mois": 1,
    "date_debut": "2024-01-01",
    "date_fin": "2024-01-3
alhost:8000/api/paie/periodes/1/generate-payslips/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"template": "standard"}'
```

## Vérifications Importantes

### Avant le Traitement
- [ ] Tous les employés ont un contrat actif
- [ ] Les retenues sont à jour
- [ ] Les paramètres de paie sont corrects
- [ ] Aucune période en cours pour le même mois

### Après le Traitement
- [ ] Nombre d'employés traités correct
- [ ] Masse salariale cohérente
- [ ] Aucune erreur de calcul
- [ ] Bulletins générés pour tous

### Avant l'Approbation
- [ ] Validation par le responsable RH
- [ ] Vérification des montants
- [ ] Contrôle des bulletins PDF
- [ ] Sauvegarde des données

## Raccourcis Clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl + N` | Nouvelle période |
| `Ctrl + P` | Traiter période |
| `Ctrl + G` | Générer bulletins |
| `Ctrl + F` | Finaliser |
| `Ctrl + A` | Approuver |

## Prochaines Étapes

Une fois familiarisé avec le processus de base :

1. **Personnalisation** : Configurez les [Paramètres de Paie](../configuration/payroll-parameters.md)
2. **Retenues** : Apprenez à gérer les [Retenues Employés](deductions.md)
3. **Rapports** : Explorez les [Exports et Rapports](exports-reports.md)
4. **Automatisation** : Configurez les [Tâches Automatiques](../administration/automation.md)

## Aide Rapide

**Problème courant :** "Aucun employé traité"
- ✅ Vérifiez que les contrats sont actifs
- ✅ Vérifiez les dates de contrat
- ✅ Consultez les logs d'erreur

**Problème courant :** "Calculs incorrects"
- ✅ Vérifiez les barèmes de cotisations
- ✅ Vérifiez les paramètres d'indemnités
- ✅ Relancez le traitement après correction

---

*Pour plus de détails, consultez les guides spécialisés dans la section [Guides Utilisateur](../README.md#guides-utilisateur).*
