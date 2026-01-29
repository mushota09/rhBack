"""
Service de generation de rapports d'audit pour le systeme de paie.
"""
from typing import Dict, List, Any
from datetime import datetime, date

from paie_app.models import periode_paie, entree_paie
from paie_app.services.database_optimizer import DatabaseOptimizer
from user_app.models import employe


class AuditReportsService:
    """Service pour generer les rapports d'audit du systeme de paie"""

    def __init__(self):
        self.db_optimizer = DatabaseOptimizer()

    def generate_period_report(self, periode_id: int) -> Dict[str, Any]:
        """Genere un rapport d'audit complet pour une periode de paie."""
        try:
            periode = periode_paie.objects.get(id=periode_id)
        except periode_paie.DoesNotExist as e:
            raise ValueError(f"Periode {periode_id} non trouvee") from e

        entries = self.db_optimizer.get_optimized_entree_paie_queryset(
            periode_id
        )
        stats = self._calculate_period_stats(entries)

        return {
            'periode': {
                'id': periode.id,
                'annee': periode.annee,
                'mois': periode.mois,
                'statut': periode.statut,
                'nombre_employes': periode.nombre_employes,
            },
            'statistiques': stats,
            'generated_at': datetime.now().isoformat()
        }

    def generate_employee_history_report(
        self, employe_id: int, start_date: date = None, end_date: date = None
    ) -> Dict[str, Any]:
        """Genere un rapport d'historique pour un employe."""
        try:
            employee = employe.objects.get(id=employe_id)
        except employe.DoesNotExist as e:
            raise ValueError(f"Employe {employe_id} non trouve") from e

        entries_query = entree_paie.objects.select_related(
            'periode_paie_id'
        ).filter(
            employe_id=employe_id
        ).order_by('-periode_paie_id__annee', '-periode_paie_id__mois')

        # Apply date filters if provided
        if start_date:
            entries_query = entries_query.filter(
                periode_paie_id__date_debut__gte=start_date
            )
        if end_date:
            entries_query = entries_query.filter(
                periode_paie_id__date_fin__lte=end_date
            )

        entries = list(entries_query)
        employee_stats = self._calculate_employee_stats(entries)

        return {
            'employe': {
                'id': employee.id,
                'nom': employee.nom,
                'prenom': employee.prenom,
                'email': employee.email_personnel,
            },
            'statistiques': employee_stats,
            'generated_at': datetime.now().isoformat()
        }

    def generate_global_statistics_report(
        self, annee: int = None
    ) -> Dict[str, Any]:
        """Genere un rapport de statistiques globales."""
        if not annee:
            annee = datetime.now().year

        monthly_stats = self._get_monthly_statistics(annee)

        return {
            'annee': annee,
            'statistiques_mensuelles': monthly_stats,
            'generated_at': datetime.now().isoformat()
        }

    def _calculate_period_stats(self, entries) -> Dict[str, Any]:
        """Calcule les statistiques d'une periode."""
        entries_list = list(entries)
        if not entries_list:
            return {
                'nombre_employes': 0,
                'total_salaire_brut': 0,
                'total_salaire_net': 0,
            }

        salaires_bruts = [
            float(entry.salaire_brut) for entry in entries_list
        ]
        salaires_nets = [
            float(entry.salaire_net) for entry in entries_list
        ]

        return {
            'nombre_employes': len(entries_list),
            'total_salaire_brut': sum(salaires_bruts),
            'total_salaire_net': sum(salaires_nets),
            'moyenne_salaire_brut': (
                sum(salaires_bruts) / len(salaires_bruts)
                if salaires_bruts else 0
            ),
        }

    def _calculate_employee_stats(self, entries: List) -> Dict[str, Any]:
        """Calcule les statistiques pour un employe."""
        if not entries:
            return {
                'nombre_periodes': 0,
                'salaire_brut_total': 0,
                'salaire_net_total': 0,
            }

        salaires_bruts = [float(entry.salaire_brut) for entry in entries]
        salaires_nets = [float(entry.salaire_net) for entry in entries]

        return {
            'nombre_periodes': len(entries),
            'salaire_brut_total': sum(salaires_bruts),
            'salaire_net_total': sum(salaires_nets),
            'salaire_brut_moyen': sum(salaires_bruts) / len(salaires_bruts),
        }

    def _get_monthly_statistics(self, annee: int) -> List[Dict[str, Any]]:
        """Recupere les statistiques mensuelles pour une annee."""
        monthly_data = periode_paie.objects.filter(
            annee=annee
        ).order_by('mois')

        return [
            {
                'mois': periode.mois,
                'nombre_employes': periode.nombre_employes or 0,
                'masse_salariale_brute': float(
                    periode.masse_salariale_brute or 0
                ),
                'statut': periode.statut
            }
            for periode in monthly_data
        ]
