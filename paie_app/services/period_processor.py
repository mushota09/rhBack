"""
Service de traitement des périodes de paie.
"""
from decimal import Decimal
from typing import Dict, List
from datetime import date
from calendar import monthrange
from django.utils import timezone
from django.contrib.auth import get_user_model

from paie_app.models import periode_paie, entree_paie
from paie_app.services.salary_calculator import SalaryCalculatorService
from user_app.models import employe, contrat

User = get_user_model()


class PeriodProcessorService:
    """Service pour traiter les périodes de paie"""

    def __init__(self):
        self.salary_calculator = SalaryCalculatorService()

    async def create_period(
        self, annee: int, mois: int, user_id: int
    ) -> periode_paie:
        """Crée une nouvelle période de paie avec calcul automatique
        des dates."""
        # Vérifier qu'une période n'existe pas déjà
        existing_period = await periode_paie.objects.filter(
            annee=annee,
            mois=mois
        ).afirst()

        if existing_period:
            raise ValueError(f"Une période existe déjà pour {mois}/{annee}")

        # Calculer automatiquement les dates
        date_debut = date(annee, mois, 1)
        _, last_day = monthrange(annee, mois)
        date_fin = date(annee, mois, last_day)

        # Créer la période
        periode = await periode_paie.objects.acreate(
            annee=annee,
            mois=mois,
            date_debut=date_debut,
            date_fin=date_fin,
            statut='DRAFT',
            traite_par_id=user_id
        )

        return periode

    async def process_period(self, periode_id: int) -> Dict:
        """Traite une période de paie en calculant les salaires."""
        try:
            periode = await periode_paie.objects.aget(id=periode_id)

            if periode.statut != 'DRAFT':
                raise ValueError(
                    f"La période {periode_id} ne peut pas être traitée"
                )

            # Récupérer les employés actifs avec contrats
            employes_actifs = []
            async for emp in employe.objects.filter(statut_emploi='ACTIVE'):
                contrat_actif = await contrat.objects.filter(
                    employe_id=emp,
                    statut='en_cours'
                ).afirst()

                if contrat_actif:
                    employes_actifs.append(emp)

            # Résultats du traitement
            results = {
                'periode_id': periode_id,
                'employes_traites': 0,
                'employes_erreurs': 0,
                'total_salaire_brut': Decimal('0'),
                'total_salaire_net': Decimal('0'),
                'erreurs': []
            }

            # Traiter chaque employé
            for emp in employes_actifs:
                try:
                    salary_data = await self.salary_calculator.calculate_salary(
                        emp.id, periode_id
                    )

                    # Créer l'entrée de paie
                    _, _ = await entree_paie.objects.aupdate_or_create(
                        employe_id=emp,
                        periode_paie_id=periode,
                        defaults={
                            'salaire_base': salary_data['salaire_base'],
                            'salaire_brut': salary_data['salaire_brut'],
                            'salaire_net': salary_data['salaire_net'],
                            'calculated_at': timezone.now(),
                            'calculated_by_id': periode.traite_par_id
                        }
                    )

                    results['employes_traites'] += 1
                    results['total_salaire_brut'] += (
                        salary_data['salaire_brut']
                    )
                    results['total_salaire_net'] += (
                        salary_data['salaire_net']
                    )

                except Exception as e:
                    results['employes_erreurs'] += 1
                    results['erreurs'].append({
                        'employe_id': emp.id,
                        'erreur': str(e)
                    })

            # Mettre à jour la période
            periode.masse_salariale_brute = results['total_salaire_brut']
            periode.total_net_a_payer = results['total_salaire_net']
            periode.nombre_employes = results['employes_traites']
            periode.statut = (
                'COMPLETED' if results['employes_erreurs'] == 0
                else 'PROCESSING'
            )

            await periode.asave(update_fields=[
                'masse_salariale_brute', 'total_net_a_payer',
                'nombre_employes', 'statut'
            ])

            return results

        except periode_paie.DoesNotExist as e:
            raise ValueError(f"Période {periode_id} non trouvée") from e

    async def validate_period(self, periode_id: int) -> List[str]:
        """Valide une période de paie et retourne la liste des erreurs."""
        errors = []

        try:
            periode = await periode_paie.objects.aget(id=periode_id)

            if periode.statut == 'DRAFT':
                errors.append("La période n'a pas encore été traitée")
                return errors

            # Vérifier les entrées de paie
            entrees_count = await entree_paie.objects.filter(
                periode_paie_id=periode
            ).acount()
            if entrees_count == 0:
                errors.append("Aucune entrée de paie trouvée")

        except periode_paie.DoesNotExist:
            errors.append(f"Période {periode_id} non trouvée")

        return errors

    async def finalize_period(self, periode_id: int) -> bool:
        """Finalise une période de paie après validation."""
        try:
            periode = await periode_paie.objects.aget(id=periode_id)

            errors = await self.validate_period(periode_id)
            if errors:
                error_msg = f"Impossible de finaliser: {', '.join(errors)}"
                raise ValueError(error_msg)

            periode.statut = 'FINALIZED'
            await periode.asave(update_fields=['statut'])

            return True

        except periode_paie.DoesNotExist as e:
            raise ValueError(f"Période {periode_id} non trouvée") from e

    async def approve_period(self, periode_id: int, user_id: int) -> bool:
        """Approuve une période de paie finalisée."""
        try:
            periode = await periode_paie.objects.aget(id=periode_id)

            if periode.statut != 'FINALIZED':
                raise ValueError(
                    "La période doit être finalisée avant approbation"
                )

            periode.statut = 'APPROVED'
            periode.approuve_par = User.objects.get(id=user_id)
            periode.date_approbation = timezone.now()

            await periode.asave(update_fields=[
                'statut', 'approuve_par', 'date_approbation'
            ])

            return True

        except periode_paie.DoesNotExist as e:
            raise ValueError(f"Période {periode_id} non trouvée") from e
