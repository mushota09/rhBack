"""
Service de calcul des salaires.
"""
from decimal import Decimal
from typing import Dict, Optional
from django.db import transaction
from django.utils import timezone

from paie_app.models import entree_paie, periode_paie
from paie_app.constants import (
    INSS_PENSION_RATE, INSS_PENSION_CAP, INSS_RISK_RATE, INSS_RISK_CAP,
    IRE_BRACKETS, FAMILY_ALLOWANCE_SCALE
)
from user_app.models import employe, contrat


class SalaryCalculatorService:
    """Service pour calculer les salaires et leurs composants"""

    async def calculate_salary(self, employe_id: int, periode_id: int) -> Dict:
        """
        Calcule le salaire complet d'un employé pour une période donnée.

        Args:
            employe_id: ID de l'employé
            periode_id: ID de la période de paie

        Returns:
            Dict avec tous les composants du salaire calculé
        """
        try:
            # Récupérer l'employé et la période
            employe_obj = await employe.objects.aget(id=employe_id)
            periode_obj = await periode_paie.objects.aget(id=periode_id)

            # Récupérer le contrat actif
            contrat_obj = await contrat.objects.filter(
                employe_id=employe_obj,
                statut='en_cours'
            ).afirst()

            if not contrat_obj:
                raise ValueError(f"Aucun contrat actif trouvé pour l'employé {employe_id}")

            # Calculer les composants du salaire
            salary_components = await self._calculate_all_components(
                contrat_obj, periode_obj, employe_obj
            )

            return salary_components

        except employe.DoesNotExist:
            raise ValueError(f"Employé {employe_id} non trouvé")
        except periode_paie.DoesNotExist:
            raise ValueError(f"Période {periode_id} non trouvée")

    async def calculate_gross_salary(self, contrat_obj: contrat, periode: periode_paie) -> Decimal:
        """
        Calcule le salaire brut basé sur le contrat.

        Args:
            contrat_obj: Objet contrat de l'employé
            periode: Période de paie

        Returns:
            Montant du salaire brut
        """
        salaire_base = contrat_obj.salaire_base

        # Calculer les indemnités en pourcentage du salaire de base
        indemnite_logement = salaire_base * (Decimal(str(contrat_obj.indemnite_logement)) / 100)
        indemnite_deplacement = salaire_base * (Decimal(str(contrat_obj.indemnite_deplacement)) / 100)
        indemnite_fonction = salaire_base * (Decimal(str(contrat_obj.prime_fonction)) / 100)

        # Calculer l'allocation familiale
        allocation_familiale = await self.calculate_family_allowance(
            contrat_obj.employe_id.nombre_enfants
        )

        autres_avantages = contrat_obj.autre_avantage

        salaire_brut = (
            salaire_base +
            indemnite_logement +
            indemnite_deplacement +
            indemnite_fonction +
            allocation_familiale +
            autres_avantages
        )

        return salaire_brut

    async def calculate_family_allowance(self, nombre_enfants: int) -> Decimal:
        """
        Calcule l'allocation familiale selon le barème progressif.

        Args:
            nombre_enfants: Nombre d'enfants de l'employé

        Returns:
            Montant de l'allocation familiale
        """
        if nombre_enfants == 0:
            return Decimal('0')
        elif nombre_enfants == 1:
            return Decimal('5000')
        elif nombre_enfants == 2:
            return Decimal('10000')
        elif nombre_enfants == 3:
            return Decimal('15000')
        else:
            # 15000 pour les 3 premiers + 3000 par enfant supplémentaire
            return Decimal('15000') + (Decimal('3000') * (nombre_enfants - 3))

    async def calculate_social_contributions(self, gross_salary: Decimal, contrat_obj: contrat) -> Dict:
        """
        Calcule les cotisations sociales patronales et salariales.

        Args:
            gross_salary: Salaire brut
            contrat_obj: Contrat de l'employé

        Returns:
            Dict avec les cotisations patronales et salariales
        """
        # Cotisations patronales
        inss_pa_pension = min(gross_salary * INSS_PENSION_RATE, INSS_PENSION_CAP)
        inss_pa_risque = min(gross_salary * INSS_RISK_RATE, INSS_RISK_CAP)
        mfp_patron = gross_salary * (Decimal(str(contrat_obj.assurance_patronale)) / 100)
        fpc_patron = gross_salary * (Decimal(str(contrat_obj.fpc_patronale)) / 100)

        cotisations_patronales = {
            'inss_pension': inss_pa_pension,
            'inss_risque': inss_pa_risque,
            'mfp': mfp_patron,
            'fpc': fpc_patron,
            'total': inss_pa_pension + inss_pa_risque + mfp_patron + fpc_patron
        }

        # Cotisations salariales
        inss_employe = min(gross_salary * Decimal('0.04'), Decimal('18000'))
        mfp_employe = gross_salary * (Decimal(str(contrat_obj.assurance_salariale)) / 100)
        fpc_employe = gross_salary * (Decimal(str(contrat_obj.fpc_salariale)) / 100)

        cotisations_salariales = {
            'inss': inss_employe,
            'mfp': mfp_employe,
            'fpc': fpc_employe,
            'total': inss_employe + mfp_employe + fpc_employe
        }

        return {
            'patronales': cotisations_patronales,
            'salariales': cotisations_salariales
        }

    async def calculate_income_tax(self, taxable_base: Decimal) -> Decimal:
        """
        Calcule l'IRE selon le barème progressif.

        Args:
            taxable_base: Base imposable

        Returns:
            Montant de l'IRE
        """
        if taxable_base <= Decimal('150000'):
            return Decimal('0')
        elif taxable_base <= Decimal('300000'):
            return (taxable_base - Decimal('150000')) * Decimal('0.2')
        else:
            return (taxable_base - Decimal('300000')) * Decimal('0.3') + Decimal('30000')

    async def calculate_deductions(self, employe_id: int, periode_id: int) -> Dict:
        """
        Calcule les retenues diverses de l'employé pour la période.

        Args:
            employe_id: ID de l'employé
            periode_id: ID de la période

        Returns:
            Dict avec les retenues et le total
        """
        from paie_app.models import retenue_employe

        # Récupérer les retenues actives pour la période
        from django.db import models

        retenues = retenue_employe.objects.filter(
            employe_id=employe_id,
            est_active=True,
            date_debut__lte=timezone.now().date()
        ).filter(
            models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=timezone.now().date())
        )

        total_retenues = Decimal('0')
        retenues_detail = {}

        async for retenue in retenues:
            montant = retenue.montant_mensuel

            # Vérifier si la retenue a un montant total et si elle n'est pas dépassée
            if retenue.montant_total:
                restant = retenue.montant_total - retenue.montant_deja_deduit
                if restant <= 0:
                    continue
                montant = min(montant, restant)

            retenues_detail[retenue.type_retenue] = {
                'description': retenue.description,
                'montant': montant
            }
            total_retenues += montant

        return {
            'detail': retenues_detail,
            'total': total_retenues
        }

    async def calculate_net_salary(self, components: Dict) -> Decimal:
        """
        Calcule le salaire net final.

        Args:
            components: Dict avec tous les composants calculés

        Returns:
            Montant du salaire net
        """
        salaire_brut = components['salaire_brut']
        cotisations_salariales = components['cotisations']['salariales']['total']
        ire = components['ire']
        retenues = components['retenues']['total']

        salaire_net = salaire_brut - cotisations_salariales - ire - retenues

        return salaire_net

    async def _calculate_all_components(
        self,
        contrat_obj: contrat,
        periode: periode_paie,
        employe_obj: employe,
        tax_rates: Dict,
        contribution_rates: Dict,
        allowance_rates: Dict
    ) -> Dict:
        """
        Calcule tous les composants du salaire.

        Args:
            contrat_obj: Contrat de l'employé
            periode: Période de paie
            employe_obj: Employé

        Returns:
            Dict avec tous les composants calculés
        """
        # Salaire brut
        salaire_brut = await self.calculate_gross_salary(contrat_obj, periode)

        # Cotisations sociales
        cotisations = await self.calculate_social_contributions(salaire_brut, contrat_obj)

        # Base imposable (salaire brut - indemnités non imposables - cotisations salariales)
        indemnite_logement = salaire_brut * (Decimal(str(contrat_obj.indemnite_logement)) / 100)
        indemnite_deplacement = salaire_brut * (Decimal(str(contrat_obj.indemnite_deplacement)) / 100)
        indemnite_fonction = salaire_brut * (Decimal(str(contrat_obj.prime_fonction)) / 100)

        base_imposable = (
            salaire_brut -
            indemnite_logement -
            indemnite_deplacement -
            indemnite_fonction -
            cotisations['salariales']['total']
        )

        # IRE
        ire = await self.calculate_income_tax(base_imposable)

        # Retenues diverses
        retenues = await self.calculate_deductions(employe_obj.id, periode.id)

        # Salaire net
        components = {
            'salaire_brut': salaire_brut,
            'cotisations': cotisations,
            'ire': ire,
            'retenues': retenues
        }
        salaire_net = await self.calculate_net_salary(components)

        return {
            'employe_id': employe_obj.id,
            'periode_id': periode.id,
            'contrat_reference': {
                'salaire_base': float(contrat_obj.salaire_base),
                'indemnite_logement': float(contrat_obj.indemnite_logement),
                'indemnite_deplacement': float(contrat_obj.indemnite_deplacement),
                'prime_fonction': float(contrat_obj.prime_fonction),
                'autre_avantage': float(contrat_obj.autre_avantage),
            },
            'salaire_base': contrat_obj.salaire_base,
            'indemnite_logement': indemnite_logement,
            'indemnite_deplacement': indemnite_deplacement,
            'indemnite_fonction': indemnite_fonction,
            'allocation_familiale': await self.calculate_family_allowance(employe_obj.nombre_enfants),
            'autres_avantages': contrat_obj.autre_avantage,
            'salaire_brut': salaire_brut,
            'cotisations_patronales': cotisations['patronales'],
            'cotisations_salariales': cotisations['salariales'],
            'base_imposable': base_imposable,
            'ire': ire,
            'retenues_diverses': retenues['detail'],
            'total_charge_salariale': salaire_brut + cotisations['patronales']['total'],
            'salaire_net': salaire_net
        }
