"""
Service de validation métier pour le système de paie.
"""
from decimal import Decimal
from typing import Dict, List, Tuple
from datetime import date
from django.db.models import Q

from paie_app.models import periode_paie, retenue_employe
from paie_app.constants import INSS_PENSION_CAP, INSS_RISK_CAP, INSS_EMPLOYEE_CAP
from user_app.models import employe, contrat


class ValidationService:
    """Service pour effectuer les validations métier du système de paie"""

    async def validate_regulatory_compliance(self, salary_components: Dict) -> Tuple[bool, List[str]]:
        """Valide que les calculs respectent les plafonds réglementaires."""
        errors = []

        cotisations_patronales = salary_components.get('cotisations_patronales', {})
        cotisations_salariales = salary_components.get('cotisations_salariales', {})

        # Vérifier les plafonds INSS
        if 'inss_pension' in cotisations_patronales:
            if cotisations_patronales['inss_pension'] > INSS_PENSION_CAP:
                errors.append("Cotisation INSS pension patronale dépasse le plafond")

        if 'inss_risque' in cotisations_patronales:
            if cotisations_patronales['inss_risque'] > INSS_RISK_CAP:
                errors.append("Cotisation INSS risque patronale dépasse le plafond")

        if 'inss' in cotisations_salariales:
            if cotisations_salariales['inss'] > INSS_EMPLOYEE_CAP:
                errors.append("Cotisation INSS employé dépasse le plafond")

        # Vérifier la cohérence des calculs
        salaire_brut = salary_components.get('salaire_brut', Decimal('0'))
        salaire_net = salary_components.get('salaire_net', Decimal('0'))

        if salaire_brut <= 0:
            errors.append("Salaire brut invalide")

        if salaire_net < 0:
            errors.append("Salaire net négatif")

        if salaire_net > salaire_brut:
            errors.append("Salaire net supérieur au salaire brut")

        ire = salary_components.get('ire', Decimal('0'))
        base_imposable = salary_components.get('base_imposable', Decimal('0'))

        if ire < 0:
            errors.append("IRE négatif")

        if base_imposable < 0:
            errors.append("Base imposable négative")

        allocation_familiale = salary_components.get('allocation_familiale', Decimal('0'))
        if allocation_familiale < 0:
            errors.append("Allocation familiale négative")

        return len(errors) == 0, errors

    async def validate_contract_for_calculation(self, employe_id: int, periode: periode_paie) -> Tuple[bool, List[str]]:
        """Valide qu'un employé a un contrat actif pour une période donnée."""
        errors = []

        try:
            employe_obj = await employe.objects.aget(id=employe_id)

            if employe_obj.statut_emploi != 'ACTIVE':
                errors.append("Employé n'est pas actif")
                return False, errors

            reference_date = date(periode.annee, periode.mois, 1)

            contrat_obj = await contrat.objects.filter(
                employe_id=employe_obj,
                statut='en_cours',
                date_debut__lte=reference_date
            ).filter(
                Q(date_fin__isnull=True) | Q(date_fin__gte=reference_date)
            ).afirst()

            if not contrat_obj:
                errors.append("Aucun contrat actif trouvé")
                return False, errors

            if contrat_obj.salaire_base <= 0:
                errors.append("Salaire de base invalide")

            return len(errors) == 0, errors

        except employe.DoesNotExist:
            errors.append("Employé non trouvé")
            return False, errors
