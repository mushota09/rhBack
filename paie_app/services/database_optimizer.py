"""
Service d'optimisation des requêtes de base de données pour le système de paie.
"""
import logging
from typing import List, Dict, Optional
from django.db.models import Prefetch, Sum, Count, Avg, QuerySet
from django.core.cache import cache
from django.conf import settings
from datetime import datetime

from paie_app.models import periode_paie, entree_paie, retenue_employe
from user_app.models import employe, contrat

logger = logging.getLogger('paie_app.services')


class DatabaseOptimizer:
    """Service pour optimiser les requêtes de base de données"""

    # Configuration du cache
    CACHE_TIMEOUT = getattr(settings, 'PAIE_CACHE_TIMEOUT', 3600)  # 1 heure par défaut
    CACHE_PREFIX = 'paie_system'

    @classmethod
    def get_optimized_periode_paie_queryset(cls, include_entries: bool = False) -> QuerySet:
        """
        Retourne un queryset optimisé pour les périodes de paie.

        Args:
            include_entries: Si True, inclut les entrées de paie avec select_related
        """
        try:
            queryset = periode_paie.objects.select_related(
                'traite_par',
                'approuve_par'
            )

            if include_entries:
                queryset = queryset.prefetch_related(
                    Prefetch(
                        'entries',
                        queryset=entree_paie.objects.select_related(
                            'employe_id',
                            'calculated_by'
                        ).order_by('employe_id__nom', 'employe_id__prenom')
                    )
                )

            return queryset.order_by('-annee', '-mois')

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation du queryset période: {e}")
            return periode_paie.objects.all()

    @classmethod
    def get_optimized_entree_paie_queryset(cls, periode_id: Optional[int] = None) -> QuerySet:
        """
        Retourne un queryset optimisé pour les entrées de paie.

        Args:
            periode_id: ID de la période pour filtrer (optionnel)
        """
        queryset = entree_paie.objects.select_related(
            'employe_id',
            'periode_paie_id',
            'calculated_by'
        ).prefetch_related(
            Prefetch(
                'employe_id__contrats',
                queryset=contrat.objects.filter(statut='en_cours').order_by('-date_debut')
            )
        )

        if periode_id:
            queryset = queryset.filter(periode_paie_id=periode_id)

        return queryset.order_by('employe_id__nom', 'employe_id__prenom')

    @classmethod
    def get_optimized_employe_queryset(cls, with_contracts: bool = True, with_deductions: bool = False) -> QuerySet:
        """
        Retourne un queryset optimisé pour les employés.

        Args:
            with_contracts: Si True, inclut les contrats actifs
            with_deductions: Si True, inclut les retenues actives
        """
        queryset = employe.objects.filter(statut_emploi='ACTIVE')

        if with_contracts:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'contrats',
                    queryset=contrat.objects.filter(statut='en_cours').order_by('-date_debut')
                )
            )

        if with_deductions:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'retenue_employe_set',
                    queryset=retenue_employe.objects.filter(est_active=True).order_by('-date_debut')
                )
            )

        return queryset.order_by('nom', 'prenom')

    @classmethod
    def get_cached_reference_data(cls, data_type: str, force_refresh: bool = False) -> Dict:
        """
        Récupère les données de référence mises en cache.

        Args:
            data_type: Type de données ('tax_rates', 'contribution_rates', 'allowances')
            force_refresh: Force le rechargement des données
        """
        cache_key = f"{cls.CACHE_PREFIX}:reference_data:{data_type}"

        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        # Charger les données selon le type
        if data_type == 'tax_rates':
            data = cls._get_tax_rates()
        elif data_type == 'contribution_rates':
            data = cls._get_contribution_rates()
        elif data_type == 'allowances':
            data = cls._get_allowance_rates()
        else:
            raise ValueError(f"Type de données non supporté: {data_type}")

        # Mettre en cache pour 1 heure
        cache.set(cache_key, data, cls.CACHE_TIMEOUT)
        return data

    @classmethod
    def _get_tax_rates(cls) -> Dict:
        """Retourne les barèmes d'impôt sur le revenu."""
        return {
            'ire_brackets': [
                {'min': 0, 'max': 524160, 'rate': 0.0},
                {'min': 524160, 'max': 1572480, 'rate': 0.15},
                {'min': 1572480, 'max': 3144960, 'rate': 0.20},
                {'min': 3144960, 'max': 5241600, 'rate': 0.25},
                {'min': 5241600, 'max': float('inf'), 'rate': 0.30}
            ],
            'last_updated': datetime.now().isoformat()
        }

    @classmethod
    def _get_contribution_rates(cls) -> Dict:
        """Retourne les taux de cotisations sociales."""
        return {
            'inss_rate': 0.035,  # 3.5%
            'inss_max': 72000,   # Plafond mensuel INSS
            'last_updated': datetime.now().isoformat()
        }

    @classmethod
    def _get_allowance_rates(cls) -> Dict:
        """Retourne les taux d'allocations familiales."""
        return {
            'family_allowance_base': 5000,  # Montant de base par enfant
            'family_allowance_progressive': [
                {'children': 1, 'rate': 1.0},
                {'children': 2, 'rate': 1.1},
                {'children': 3, 'rate': 1.2},
                {'children': 4, 'rate': 1.3},
                {'children': 5, 'rate': 1.4}
            ],
            'last_updated': datetime.now().isoformat()
        }

    @classmethod
    def get_period_statistics_cached(cls, periode_id: int, force_refresh: bool = False) -> Dict:
        """
        Récupère les statistiques d'une période avec mise en cache.

        Args:
            periode_id: ID de la période
            force_refresh: Force le recalcul des statistiques
        """
        cache_key = f"{cls.CACHE_PREFIX}:period_stats:{periode_id}"

        if not force_refresh:
            try:
                cached_stats = cache.get(cache_key)
                if cached_stats:
                    return cached_stats
            except Exception:
                # En cas d'erreur de cache, continuer sans cache
                pass

        # Calculer les statistiques
        stats = cls._calculate_period_statistics(periode_id)

        # Mettre en cache pour 30 minutes
        try:
            cache.set(cache_key, stats, 1800)
        except Exception:
            # En cas d'erreur de cache, continuer sans cache
            logger.warning("Erreur lors de l'accès au cache, continuant sans cache")
            pass

        return stats

    @classmethod
    def _calculate_period_statistics(cls, periode_id: int) -> Dict:
        """Calcule les statistiques d'une période avec requêtes optimisées."""
        # Une seule requête pour toutes les statistiques
        stats = entree_paie.objects.filter(
            periode_paie_id=periode_id
        ).aggregate(
            total_employees=Count('id'),
            total_salaire_brut=Sum('salaire_brut'),
            total_salaire_net=Sum('salaire_net'),
            total_charges=Sum('total_charge_salariale'),
            avg_salaire_brut=Avg('salaire_brut'),
            avg_salaire_net=Avg('salaire_net')
        )

        # Convertir les Decimal en float pour la sérialisation JSON
        for key, value in stats.items():
            if value is not None and hasattr(value, 'quantize'):
                stats[key] = float(value)

        stats['calculated_at'] = datetime.now().isoformat()
        return stats

    @classmethod
    def bulk_create_entries(cls, entries_data: List[Dict]) -> List[entree_paie]:
        """
        Création en lot d'entrées de paie pour optimiser les performances.

        Args:
            entries_data: Liste des données d'entrées à créer
        """
        entries = []
        for data in entries_data:
            entry = entree_paie(**data)
            entries.append(entry)

        # Création en lot - plus efficace que des créations individuelles
        return entree_paie.objects.bulk_create(entries, batch_size=100)

    @classmethod
    def bulk_update_entries(cls, entries: List[entree_paie], fields: List[str]) -> None:
        """
        Mise à jour en lot d'entrées de paie.

        Args:
            entries: Liste des entrées à mettre à jour
            fields: Liste des champs à mettre à jour
        """
        entree_paie.objects.bulk_update(entries, fields, batch_size=100)

    @classmethod
    def clear_cache(cls, cache_pattern: Optional[str] = None) -> None:
        """
        Nettoie le cache du système de paie.

        Args:
            cache_pattern: Pattern spécifique à nettoyer (optionnel)
        """
        if cache_pattern:
            # Nettoyer un pattern spécifique
            cache_key = f"{cls.CACHE_PREFIX}:{cache_pattern}"
            cache.delete(cache_key)
        else:
            # Nettoyer tout le cache du système de paie
            try:
                cache.delete_many([
                    f"{cls.CACHE_PREFIX}:reference_data:tax_rates",
                    f"{cls.CACHE_PREFIX}:reference_data:contribution_rates",
                    f"{cls.CACHE_PREFIX}:reference_data:allowances"
                ])
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du cache: {e}")
                print(f"Erreur lors du nettoyage du cache: {e}")
