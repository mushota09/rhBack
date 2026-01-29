"""
Service de monitoring des performances pour le système de paie.
"""
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from contextlib import contextmanager

logger = logging.getLogger('paie_app.services')


class PerformanceMonitor:
    """Service de monitoring des performances."""

    # Clés de cache pour les métriques
    CACHE_PREFIX = 'perf_monitor'
    METRICS_CACHE_TIMEOUT = 300  # 5 minutes

    # Seuils de performance (en secondes)
    THRESHOLDS = {
        'calculation_warning': 5.0,
        'calculation_critical': 15.0,
        'period_processing_warning': 60.0,
        'period_processing_critical': 300.0,
        'payslip_generation_warning': 3.0,
        'payslip_generation_critical': 10.0,
        'database_query_warning': 1.0,
        'database_query_critical': 5.0
    }

    @classmethod
    def measure_execution_time(cls, operation_name: str,
                              threshold_warning: float = None,
                              threshold_critical: float = None):
        """
        Décorateur pour mesurer le temps d'exécution d'une fonction.

        Args:
            operation_name: Nom de l'opération à mesurer
            threshold_warning: Seuil d'avertissement personnalisé
            threshold_critical: Seuil critique personnalisé
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    cls._record_performance_metric(
                        operation_name, execution_time, True,
                        threshold_warning, threshold_critical
                    )

                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    cls._record_performance_metric(
                        operation_name, execution_time, False,
                        threshold_warning, threshold_critical
                    )
                    raise e

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    cls._record_performance_metric(

            # Retourner le wrapper approprié selon le type de fonction
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    @classmethod
    def _record_performance_metric(cls, operation_name: str, execution_time: float,
                                 success: bool, threshold_warning: float = None,
                                 threshold_critical: float = None) -> None:
        """Enregistre une métrique de performance."""

        # Utiliser les seuils par défaut si non spécifiés
        warning_threshold = threshold_warning or cls.THRESHOLDS.get(f'{operation_name}_warning', 5.0)
        critical_threshold = threshold_critical or cls.THRESHOLDS.get(f'{operation_name}_critical', 15.0)

        # Déterminer le niveau de performance
        if execution_time >= critical_threshold:
            level = 'CRITICAL'
            log_level = logging.ERROR
        elif execution_time >= warning_threshold:
            level = 'WARNING'
            log_level = logging.WARNING
        else:
            level = 'OK'
            log_level = logging.INFO

        # Logger la métrique
        logger.log(
            log_level,
            f"Performance {level}: {operation_name} - {execution_time:.3f}s",
            extra={
                'operation': operation_name,
                'execution_time': execution_time,
                'success': success,
                'performance_level': level,
                'timestamp': timezone.now().isoformat()
            }
        )

        # Stocker dans le cache pour les statistiques
        cls._update_performance_cache(operation_name, execution_time, success, level)

    @classmethod
    def _update_performance_cache(cls, operation_name: str, execution_time: float,
                                success: bool, level: str) -> None:
        """Met à jour les métriques en cache."""
        try:
            cache_key = f"{cls.CACHE_PREFIX}:metrics:{operation_name}"

            # Récupérer les métriques existantes
            metrics = cache.get(cache_key, {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'warning_count': 0,
                'critical_count': 0,
                'last_updated': timezone.now().isoformat()
            })

            # Mettre à jour les métriques
            metrics['total_calls'] += 1
            if success:
                metrics['successful_calls'] += 1
            else:
                metrics['failed_calls'] += 1

            metrics['total_time'] += execution_time
            metrics['min_time'] = min(metrics['min_time'], execution_time)
            metrics['max_time'] = max(metrics['max_time'], execution_time)

            if level == 'WARNING':
                metrics['warning_count'] += 1
            elif level == 'CRITICAL':
                metrics['critical_count'] += 1

            metrics['last_updated'] = timezone.now().isoformat()

            # Calculer la moyenne
            metrics['avg_time'] = metrics['total_time'] / metrics['total_calls']

            # Sauvegarder en cache
            cache.set(cache_key, metrics, cls.METRICS_CACHE_TIMEOUT)

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des métriques: {e}")

    @classmethod
    @contextmanager
    def measure_database_queries(cls, operation_name: str):
        """
        Context manager pour mesurer les requêtes de base de données.

        Args:
            operation_name: Nom de l'opération
        """
        initial_queries = len(connection.queries)
        start_time = time.time()

        try:
            yield
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            query_count = len(connection.queries) - initial_queries

            # Logger les informations de requête
            logger.info(
                f"DB Performance: {operation_name} - {query_count} queries in {execution_time:.3f}s",
                extra={
                    'operation': operation_name,
                    'query_count': query_count,
                    'execution_time': execution_time,
                    'queries_per_second': query_count / execution_time if execution_time > 0 else 0
                }
            )

            # Alerter si trop de requêtes
            if query_count > 50:
                logger.warning(
                    f"High query count detected: {operation_name} executed {query_count} queries"
                )

    @classmethod
    def get_performance_metrics(cls, operation_name: str = None) -> Dict[str, Any]:
        """
        Récupère les métriques de performance.

        Args:
            operation_name: Nom de l'opération spécifique (optionnel)

        Returns:
            Métriques de performance
        """
        if operation_name:
            cache_key = f"{cls.CACHE_PREFIX}:metrics:{operation_name}"
            return cache.get(cache_key, {})

        # Récupérer toutes les métriques
        all_metrics = {}
        operations = [
            'salary_calculation',
            'period_processing',
            'payslip_generation',
            'deduction_processing'
        ]

        for op in operations:
            cache_key = f"{cls.CACHE_PREFIX}:metrics:{op}"
            metrics = cache.get(cache_key)
            if metrics:
                all_metrics[op] = metrics

        return all_metrics

    @classmethod
    def get_system_health(cls) -> Dict[str, Any]:
        """
        Évalue la santé globale du système.

        Returns:
            Rapport de santé du système
        """
        metrics = cls.get_performance_metrics()

        health_score = 100
        issues = []
        warnings = []

        for operation, data in metrics.items():
            if not data:
                continue

            # Vérifier le taux de succès
            success_rate = (data['successful_calls'] / data['total_calls']) * 100 if data['total_calls'] > 0 else 0

            if success_rate < 95:
                health_score -= 10
                issues.append(f"{operation}: Taux de succès faible ({success_rate:.1f}%)")
            elif success_rate < 98:
                warnings.append(f"{operation}: Taux de succès modéré ({success_rate:.1f}%)")

            # Vérifier les performances
            if data.get('critical_count', 0) > 0:
                health_score -= 15
                issues.append(f"{operation}: {data['critical_count']} exécutions critiques")

            if data.get('warning_count', 0) > data.get('total_calls', 0) * 0.1:
                health_score -= 5
                warnings.append(f"{operation}: Nombreuses exécutions lentes")

        # Déterminer le statut global
        if health_score >= 90:
            status = 'EXCELLENT'
        elif health_score >= 75:
            status = 'GOOD'
        elif health_score >= 50:
            status = 'WARNING'
        else:
            status = 'CRITICAL'

        return {
            'status': status,
            'health_score': max(0, health_score),
            'issues': issues,
            'warnings': warnings,
            'metrics_summary': {
                'total_operations': len(metrics),
                'monitored_operations': list(metrics.keys())
            },
            'last_check': timezone.now().isoformat()
        }

    @classmethod
    def clear_metrics(cls, operation_name: str = None) -> None:
        """
        Efface les métriques de performance.

        Args:
            operation_name: Opération spécifique à effacer (optionnel)
        """
        if operation_name:
            cache_key = f"{cls.CACHE_PREFIX}:metrics:{operation_name}"
            cache.delete(cache_key)
        else:
            # Effacer toutes les métriques
            operations = [
                'salary_calculation',
                'period_processing',
                'payslip_generation',
                'deduction_processing'
            ]

            cache_keys = [f"{cls.CACHE_PREFIX}:metrics:{op}" for op in operations]
            cache.delete_many(cache_keys)

    @classmethod
    def log_slow_query(cls, query: str, execution_time: float, params: List = None) -> None:
        """
        Log une requête lente.

        Args:
            query: Requête SQL
            execution_time: Temps d'exécution
            params: Paramètres de la requête
        """
        if execution_time > cls.THRESHOLDS['database_query_warning']:
            logger.warning(
                f"Slow query detected: {execution_time:.3f}s",
                extra={
                    'query': query[:200] + '...' if len(query) > 200 else query,
                    'execution_time': execution_time,
                    'params': params[:5] if params else None,  # Limiter les paramètres loggés
                    'query_type': 'SLOW_QUERY'
                }
            )


# Décorateurs utilitaires
def monitor_salary_calculation(func):
    """Décorateur pour monitorer les calculs salariaux."""
    return PerformanceMonitor.measure_execution_time(
        'salary_calculation',
        threshold_warning=5.0,
        threshold_critical=15.0
    )(func)


def monitor_period_processing(func):
    """Décorateur pour monitorer le traitement des périodes."""
    return PerformanceMonitor.measure_execution_time(
        'period_processing',
        threshold_warning=60.0,
        threshold_critical=300.0
    )(func)


def monitor_payslip_generation(func):
    """Décorateur pour monitorer la génération de bulletins."""
    return PerformanceMonitor.measure_execution_time(
        'payslip_generation',
        threshold_warning=3.0,
        threshold_critical=10.0
    )(func)


def monitor_deduction_processing(func):
    """Décorateur pour monitorer le traitement des retenues."""
    return PerformanceMonitor.measure_execution_time(
        'deduction_processing',
        threshold_warning=2.0,
        threshold_critical=8.0
    )(func)
