# Paramètres de Paie

Ce guide détaille la configuration des paramètres de paie, incluant les barèmes de cotisations, les taux d'imposition, les allocations familiales et les règles de calcul.

## Vue d'Ensemble

Les paramètres de paie définissent les règles de calcul utilisées par le système. Ils sont organisés en plusieurs catégories :

- **Cotisations Sociales** : Taux et plafonds INSS, MFP, FPC
- **Fiscalité** : Barèmes IRE et exonérations
- **Allocations** : Barèmes d'allocation familiale
- **Indemnités** : Règles de calcul des indemnités
- **Retenues** : Types et limites de retenues

## Configuration des Cotisations Sociales

###
: {
        "nom": "INSS Risque Professionnel",
        "code": "INSS_RISQUE",
        "actif": true,
        "taux_patronal": 6.0,
        "taux_salarial": 1.5,
        "plafond_mensuel": 2400.00,
        "base_calcul": "salaire_brut",
        "date_effet": "2024-01-01",
        "description": "Cotisation risque professionnel avec plafond de 2,400 USD"
    }
}
```

### MFP (Mutuelle des Fonctionnaires et Agents Publics)

```json
{
    "mfp": {
        "nom": "MFP",
        "code": "MFP",
        "actif": true,
        "taux_patronal": 1.5,
        "taux_salarial": 1.0,
        "plafond_mensuel": null,
        "base_calcul": "salaire_brut",
        "date_effet": "2024-01-01",
        "description": "Cotisation MFP sans plafond"
    }
}
```

### FPC (Fonds de Promotion de la Culture)

```json
{
    "fpc": {
        "nom": "FPC",
        "code": "FPC",
        "actif": true,
        "taux_patronal": 0.5,
        "taux_salarial": 0.0,
        "plafond_mensuel": null,
        "base_calcul": "salaire_brut",
        "date_effet": "2024-01-01",
        "description": "Cotisation FPC à la charge de l'employeur uniquement"
    }
}
```

## Configuration de l'IRE (Impôt sur les Revenus)

### Barème Progressif

```json
{
    "ire_bareme": {
        "nom": "Barème IRE 2024",
        "code": "IRE_2024",
        "actif": true,
        "date_effet": "2024-01-01",
        "tranches": [
            {
                "numero": 1,
                "seuil_min": 0,
                "seuil_max": 150000,
                "taux": 0.0,
                "description": "Tranche exonérée"
            },
            {
                "numero": 2,
                "seuil_min": 150001,
                "seuil_max": 300000,
                "taux": 20.0,
                "description": "Première tranche imposable"
            },
            {
                "numero": 3,
                "seuil_min": 300001,
                "seuil_max": null,
                "taux": 30.0,
                "description": "Tranche supérieure"
            }
        ],
        "base_calcul": "base_imposable",
        "description": "Barème progressif IRE avec exonération jusqu'à 150,000 USD"
    }
}
```

### Calcul de la Base Imposable

```json
{
    "base_imposable_config": {
        "formule": "salaire_brut - cotisations_salariales",
        "elements_deductibles": [
            "inss_pension_salarial",
            "inss_risque_salarial",
            "mfp_salarial"
        ],
        "elements_non_deductibles": [
            "retenues_diverses",
            "avances_remboursement"
        ]
    }
}
```

## Configuration des Allocations Familiales

### Barème par Nombre d'Enfants

```json
{
    "allocation_familiale": {
        "nom": "Allocation Familiale 2024",
        "code": "ALLOC_FAM_2024",
        "actif": true,
        "date_effet": "2024-01-01",
        "bareme": [
            {
                "nombre_enfants": 0,
                "montant": 0,
                "description": "Aucun enfant"
            },
            {
                "nombre_enfants": 1,
                "montant": 15000,
                "description": "Un enfant"
            },
            {
                "nombre_enfants": 2,
                "montant": 35000,
                "description": "Deux enfants"
            },
            {
                "nombre_enfants": 3,
                "montant": 60000,
                "description": "Trois enfants"
            },
            {
                "nombre_enfants": 4,
                "montant": 90000,
                "description": "Quatre enfants"
            },
            {
                "nombre_enfants": 5,
                "montant": 125000,
                "description": "Cinq enfants et plus"
            }
        ],
        "age_limite": 18,
        "conditions": [
            "Enfant à charge",
            "Âge inférieur à 18 ans ou étudiant jusqu'à 25 ans",
            "Résidence au Congo"
        ]
    }
}
```

### Conditions d'Éligibilité

```json
{
    "conditions_allocation": {
        "age_minimum": 0,
        "age_maximum": 18,
        "age_maximum_etudiant": 25,
        "documents_requis": [
            "Acte de naissance",
            "Certificat de scolarité (si étudiant)",
            "Attestation de résidence"
        ],
        "verification_annuelle": true,
        "date_limite_declaration": "31-03"
    }
}
```

## Configuration des Indemnités

### Types d'Indemnités

```json
{
    "indemnites_config": {
        "logement": {
            "nom": "Indemnité de Logement",
            "code": "IND_LOGEMENT",
            "type": "pourcentage",
            "base_calcul": "salaire_base",
            "pourcentage_min": 0,
            "pourcentage_max": 50,
            "pourcentage_defaut": 15,
            "imposable": true,
            "soumis_cotisations": true
        },
        "deplacement": {
            "nom": "Indemnité de Déplacement",
            "code": "IND_DEPLACEMENT",
            "type": "pourcentage",
            "base_calcul": "salaire_base",
            "pourcentage_min": 0,
            "pourcentage_max": 30,
            "pourcentage_defaut": 5,
            "imposable": true,
            "soumis_cotisations": true
        },
        "fonction": {
            "nom": "Indemnité de Fonction",
            "code": "IND_FONCTION",
            "type": "pourcentage",
            "base_calcul": "salaire_base",
            "pourcentage_min": 0,
            "pourcentage_max": 40,
            "pourcentage_defaut": 10,
            "imposable": true,
            "soumis_cotisations": true
        }
    }
}
```

### Limites et Contrôles

```json
{
    "limites_indemnites": {
        "total_maximum_pourcentage": 100,
        "verification_coherence": true,
        "alertes": {
            "seuil_alerte": 80,
            "seuil_blocage": 100,
            "notification_rh": true
        }
    }
}
```

## Configuration des Retenues

### Types de Retenues Autorisées

```json
{
    "types_retenues": {
        "LOAN": {
            "nom": "Prêt",
            "code": "LOAN",
            "actif": true,
            "recurrent": true,
            "limite_montant": true,
            "pourcentage_max_salaire": 30,
            "duree_max_mois": 60,
            "taux_interet_max": 12.0,
            "documents_requis": [
                "Contrat de prêt",
                "Garanties"
            ]
        },
        "ADVANCE": {
            "nom": "Avance sur Salaire",
            "code": "ADVANCE",
            "actif": true,
            "recurrent": true,
            "limite_montant": true,
            "pourcentage_max_salaire": 50,
            "duree_max_mois": 12,
            "taux_interet_max": 0.0,
            "documents_requis": [
                "Demande d'avance",
                "Justificatifs"
            ]
        },
        "INSURANCE": {
            "nom": "Assurance",
            "code": "INSURANCE",
            "actif": true,
            "recurrent": true,
            "limite_montant": false,
            "pourcentage_max_salaire": 10,
            "duree_max_mois": null,
            "documents_requis": [
                "Contrat d'assurance",
                "Attestation"
            ]
        },
        "UNION": {
            "nom": "Cotisation Syndicale",
            "code": "UNION",
            "actif": true,
            "recurrent": true,
            "limite_montant": false,
            "pourcentage_max_salaire": 2,
            "duree_max_mois": null,
            "documents_requis": [
                "Adhésion syndicale"
            ]
        }
    }
}
```

### Règles de Validation

```json
{
    "regles_retenues": {
        "total_max_pourcentage_salaire": 50,
        "verification_solvabilite": true,
        "delai_preavis_jours": 30,
        "approbation_requise": {
            "montant_seuil": 100000,
            "role_approbateur": "RH_MANAGER"
        },
        "controles_automatiques": [
            "Vérification du salaire minimum après retenues",
            "Contrôle de la durée maximale",
            "Validation des garanties pour les prêts"
        ]
    }
}
```

## Gestion des Paramètres

### Interface de Configuration

```python
# API pour la gestion des paramètres
class PayrollParametersAPIView(APIView):
    def get(self, request):
        """Récupérer tous les paramètres de paie"""
        parameters = PayrollParameters.objects.filter(actif=True)
        return Response(PayrollParametersSerializer(parameters, many=True).data)

    def post(self, request):
        """Créer un nouveau paramètre"""
        serializer = PayrollParametersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cree_par=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        """Modifier un paramètre existant"""
        parameter = PayrollParameters.objects.get(pk=pk)
        # Créer une nouvelle version au lieu de modifier
        new_version = self.create_new_version(parameter, request.data)
        return Response(PayrollParametersSerializer(new_version).data)
```

### Versioning des Paramètres

```json
{
    "versioning": {
        "strategy": "date_based",
        "keep_history": true,
        "max_versions": 10,
        "activation_rules": {
            "immediate": false,
            "scheduled": true,
            "approval_required": true
        }
    }
}
```

### Exemple de Modification de Paramètre

```http
PUT /api/paie/parameters/inss-pension/
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "taux_patronal": 6.5,
    "taux_salarial": 3.5,
    "plafond_mensuel": 30000.00,
    "date_effet": "2024-07-01",
    "raison_modification": "Mise à jour réglementaire juillet 2024",
    "approuve_par": null,
    "activation_programmee": true
}
```

## Validation et Contrôles

### Règles de Cohérence

```python
def validate_payroll_parameters(parameters):
    """Valider la cohérence des paramètres de paie"""
    errors = []

    # Vérifier que les taux sont dans les limites acceptables
    for param in parameters:
        if param.type == 'cotisation':
            if param.taux_patronal < 0 or param.taux_patronal > 50:
                errors.append(f"Taux patronal invalide pour {param.nom}")

            if param.taux_salarial < 0 or param.taux_salarial > 30:
                errors.append(f"Taux salarial invalide pour {param.nom}")

    # Vérifier la cohérence des barèmes IRE
    ire_params = [p for p in parameters if p.code.startswith('IRE')]
    if ire_params:
        validate_ire_brackets(ire_params[0])

    return errors

def validate_ire_brackets(ire_param):
    """Valider la cohérence des tranches IRE"""
    tranches = ire_param.tranches

    # Vérifier que les tranches se suivent sans trou ni chevauchement
    for i in range(len(tranches) - 1):
        current = tranches[i]
        next_tranche = tranches[i + 1]

        if current.seuil_max + 1 != next_tranche.seuil_min:
            raise ValidationError(f"Incohérence entre tranches {i+1} et {i+2}")
```

### Tests de Régression

```python
def test_parameter_changes_impact():
    """Tester l'impact des changements de paramètres"""
    # Créer un jeu de données de test
    test_employees = create_test_employees()

    # Calculer avec anciens paramètres
    old_results = calculate_salaries(test_employees, old_parameters)

    # Calculer avec nouveaux paramètres
    new_results = calculate_salaries(test_employees, new_parameters)

    # Analyser les différences
    impact_analysis = analyze_impact(old_results, new_results)

    return impact_analysis
```

## Historique et Audit

### Traçabilité des Modifications

```json
{
    "audit_trail": [
        {
            "date": "2024-03-01T10:00:00Z",
            "utilisateur": "admin",
            "action": "MODIFICATION",
            "parametre": "INSS_PENSION",
            "ancienne_valeur": {
                "taux_patronal": 6.0,
                "plafond_mensuel": 27000.00
            },
            "nouvelle_valeur": {
                "taux_patronal": 6.5,
                "plafond_mensuel": 30000.00
            },
            "raison": "Mise à jour réglementaire",
            "approuve_par": "directeur_rh",
            "date_effet": "2024-07-01"
        }
    ]
}
```

### Rapports d'Impact

```python
def generate_impact_report(parameter_change):
    """Générer un rapport d'impact des changements de paramètres"""

    affected_employees = get_affected_employees(parameter_change)

    report = {
        'parameter_changed': parameter_change.nom,
        'effective_date': parameter_change.date_effet,
        'affected_employees_count': len(affected_employees),
        'financial_impact': {
            'total_increase': 0,
            'total_decrease': 0,
            'net_impact': 0
        },
        'employee_details': []
    }

    for employee in affected_employees:
        old_salary = calculate_salary(employee, old_parameters)
        new_salary = calculate_salary(employee, new_parameters)

        impact = new_salary - old_salary
        report['employee_details'].append({
            'employee_id': employee.id,
            'name': employee.nom_complet,
            'old_net_salary': old_salary,
            'new_net_salary': new_salary,
            'impact': impact
        })

        if impact > 0:
            report['financial_impact']['total_increase'] += impact
        else:
            report['financial_impact']['total_decrease'] += abs(impact)

    report['financial_impact']['net_impact'] = (
        report['financial_impact']['total_increase'] -
        report['financial_impact']['total_decrease']
    )

    return report
```

## Sauvegarde et Restauration

### Export des Paramètres

```python
def export_payroll_parameters():
    """Exporter tous les paramètres de paie"""
    parameters = PayrollParameters.objects.filter(actif=True)

    export_data = {
        'export_date': timezone.now().isoformat(),
        'version': '1.0',
        'parameters': []
    }

    for param in parameters:
        export_data['parameters'].append({
            'code': param.code,
            'nom': param.nom,
            'configuration': param.configuration,
            'date_effet': param.date_effet.isoformat(),
            'actif': param.actif
        })

    return export_data
```

### Import et Validation

```python
def import_payroll_parameters(import_data):
    """Importer des paramètres de paie avec validation"""

    # Valider la structure des données
    validate_import_structure(import_data)

    # Créer les paramètres
    created_parameters = []

    for param_data in import_data['parameters']:
        # Valider chaque paramètre
        validate_parameter_data(param_data)

        # Créer le paramètre
        parameter = PayrollParameters.objects.create(
            code=param_data['code'],
            nom=param_data['nom'],
            configuration=param_data['configuration'],
            date_effet=param_data['date_effet'],
            actif=False  # Désactivé par défaut
        )

        created_parameters.append(parameter)

    return created_parameters
```

---

*Pour plus d'informations sur la gestion des utilisateurs et permissions, consultez le [Guide de Gestion des Utilisateurs](user-management.md).*
