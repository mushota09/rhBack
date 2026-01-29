"""
Service de gestion des retenues employés.
"""
from decimal import Decimal
from typing import Dict, List
from datetime import date
from django.db import transaction
from django.db.models import Q

from paie_app.models import retenue_employe, periode_paie


class DeductionManagerService:
    """Service pour gérer les retenues des employés"""

    async def create_deduction(self, data: Dict) -> retenue_employe:
        """Crée une nouvelle retenue pour un employé."""
        required_fields = ['employe_id', 'type_retenue', 'description', 'montant_mensuel', 'date_debut']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Champ requis manquant: {field}")

        retenue = await retenue_employe.objects.acreate(
            employe_id_id=data['employe_id'],
            type_retenue=data['type_retenue'],
            description=data['description'],
            montant_mensuel=Decimal(str(data['montant_mensuel'])),
            montant_total=Decimal(str(data.get('montant_total', 0))) if data.get('montant_total') else None,
            date_debut=data['date_debut'],
            date_fin=data.get('date_fin'),
            est_active=data.get('est_active', True),
            est_recurrente=data.get('est_recurrente', True),
            cree_par_id=data.get('cree_par'),
            banque_beneficiaire=data.get('banque_beneficiaire', ''),
            compte_beneficiaire=data.get('compte_beneficiaire', '')
        )
        return retenue
    async def get_active_deductions(self, employe_id: int, periode: periode_paie) -> List[retenue_employe]:
        """Récupère les retenues actives pour un employé à une période donnée."""
        reference_date = date(periode.annee, periode.mois, 1)

        retenues = retenue_employe.objects.filter(
            employe_id=employe_id,
            est_active=True,
            date_debut__lte=reference_date
        ).filter(
            Q(date_fin__isnull=True) | Q(date_fin__gte=reference_date)
        )

        active_retenues = []
        async for retenue in retenues:
            if retenue.montant_total:
                restant = retenue.montant_total - retenue.montant_deja_deduit
                if restant > 0:
                    active_retenues.append(retenue)
            else:
                active_retenues.append(retenue)

        return active_retenues
    async def apply_deduction(self, retenue: retenue_employe, periode: periode_paie) -> Decimal:
        """Applique une retenue pour une période donnée."""
        montant_a_deduire = retenue.montant_mensuel

        if retenue.montant_total:
            restant = retenue.montant_total - retenue.montant_deja_deduit
            if restant <= 0:
                return Decimal('0')
            montant_a_deduire = min(montant_a_deduire, restant)

        if montant_a_deduire <= 0:
            return Decimal('0')

        return montant_a_deduire

    async def update_deduction_balance(self, retenue_id: int, montant_deduit: Decimal) -> None:
        """Met à jour le solde d'une retenue après déduction."""
        try:
            retenue = await retenue_employe.objects.aget(id=retenue_id)
            retenue.montant_deja_deduit += montant_deduit

            if retenue.montant_total and retenue.montant_deja_deduit >= retenue.montant_total:
                retenue.est_active = False

            await retenue.asave(update_fields=['montant_deja_deduit', 'est_active'])

        except retenue_employe.DoesNotExist:
            raise ValueError(f"Retenue {retenue_id} non trouvée")
