"""
Commande de management pour optimiser et nettoyer le système de paie.
"""
import logging
from typing import Dict, Any
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.db import connection, transaction
from django.utils import timezone
from datetime import timedelta

from paie_app.services.database_optimizer import DatabaseOptimizer
from paie_app.services.performance_monitor import PerformanceMonitor
from paie_app.services.error_handler import ErrorHandler

logger = logging.getLogger('paie_app')


class Command(BaseCommand):
    """Commande pour optimiser et nettoyer le système de paie."""
rchive et nettoie les anciens logs'
        )

        parser.add_argument(
            '--performance-report',
            action='store_true',
            help='Génère un rapport de performance'
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='Exécute toutes les optimisations'
        )

        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Nombre de jours pour le nettoyage des logs (défaut: 30)'
        )

    def handle(self, *args, **options):
        """Exécute les optimisations demandées."""

        self.stdout.write(
            self.style.SUCCESS('🚀 Début de l\'optimisation du système de paie')
        )

        results = {}

        try:
            if options['all'] or options['clear_cache']:
                results['cache'] = self._clear_cache()

            if options['all'] or options['optimize_db']:
                results['database'] = self._optimize_database()

            if options['all'] or options['clear_logs']:
                results['logs'] = self._clear_old_logs(options['days'])

            if options['all'] or options['performance_report']:
                results['performance'] = self._generate_performance_report()

            # Afficher le résumé
            self._display_summary(results)

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation: {e}")
            raise CommandError(f"Erreur lors de l'optimisation: {e}")

    def _clear_cache(self) -> Dict[str, Any]:
        """Vide le cache du système."""
        self.stdout.write('🧹 Nettoyage du cache...')

        try:
            # Vider le cache général
            cache.clear()

            # Vider le cache spécifique au système de paie
            DatabaseOptimizer.clear_cache()
            PerformanceMonitor.clear_metrics()

            self.stdout.write(
                self.style.SUCCESS('✅ Cache vidé avec succès')
            )

            return {
                'status': 'success',
                'message': 'Cache vidé avec succès'
            }

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors du nettoyage du cache: {e}')
            )
            return {
                'status': 'error',
                'message': str(e)
            }

    def _optimize_database(self) -> Dict[str, Any]:
        """Optimise la base de données."""
        self.stdout.write('🔧 Optimisation de la base de données...')

        try:
            with connection.cursor() as cursor:
                # Analyser les tables principales
                tables = [
                    'paie_app_periode_paie',
                    'paie_app_entree_paie',
                    'paie_app_retenue_employe',
                    'user_app_employe',
                    'user_app_contrat'
                ]

                optimizations = []

                for table in tables:
                    try:
                        # PostgreSQL: ANALYZE pour mettre à jour les statistiques
                        cursor.execute(f'ANALYZE {table};')
                        optimizations.append(f'Analysé: {table}')

                    except Exception as e:
                        logger.warning(f"Impossible d'analyser {table}: {e}")

                # Vérifier les index manquants
                missing_indexes = self._check_missing_indexes(cursor)

                self.stdout.write(
                    self.style.SUCCESS('✅ Base de données optimisée')
                )

                return {
                    'status': 'success',
                    'optimizations': optimizations,
                    'missing_indexes': missing_indexes
                }

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'optimisation DB: {e}')
            )
            return {
                'status': 'error',
                'message': str(e)
            }

    def _check_missing_indexes(self, cursor) -> list:
        """Vérifie les index manquants."""
        missing_indexes = []

        # Requêtes pour identifier les index manquants (PostgreSQL)
        queries = [
            """
            SELECT schemaname, tablename, attname, n_distinct, correlation
            FROM pg_stats
            WHERE schemaname = 'public'
            AND tablename LIKE 'paie_app_%'
            AND n_distinct > 100
            AND correlation < 0.1
            """,
        ]

        try:
            for query in queries:
                cursor.execute(query)
                results = cursor.fetchall()

                for row in results:
                    missing_indexes.append({
                        'table': row[1],
                        'column': row[2],
                        'reason': 'High cardinality, low correlation'
                    })

        except Exception as e:
            logger.warning(f"Impossible de vérifier les index: {e}")

        return missing_indexes

    def _clear_old_logs(self, days: int) -> Dict[str, Any]:
        """Archive et nettoie les anciens logs."""
        self.stdout.write(f'📋 Nettoyage des logs de plus de {days} jours...')

        try:
            from pathlib import Path
            import os
            import gzip
            import shutil

            logs_dir = Path('logs')
            if not logs_dir.exists():
                return {
                    'status': 'skipped',
                    'message': 'Répertoire logs non trouvé'
                }

            cutoff_date = timezone.now() - timedelta(days=days)
            archived_files = []
            deleted_files = []

            for log_file in logs_dir.glob('*.log'):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    # Compresser le fichier
                    compressed_name = f"{log_file}.{cutoff_date.strftime('%Y%m%d')}.gz"

                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_name, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    archived_files.append(str(log_file))

                    # Supprimer le fichier original
                    os.remove(log_file)
                    deleted_files.append(str(log_file))

            self.stdout.write(
                self.style.SUCCESS(f'✅ {len(archived_files)} fichiers archivés')
            )

            return {
                'status': 'success',
                'archived_files': len(archived_files),
                'deleted_files': len(deleted_files)
            }

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors du nettoyage des logs: {e}')
            )
            return {
                'status': 'error',
                'message': str(e)
            }

    def _generate_performance_report(self) -> Dict[str, Any]:
        """Génère un rapport de performance."""
        self.stdout.write('📊 Génération du rapport de performance...')

        try:
            # Récupérer les métriques de performance
            metrics = PerformanceMonitor.get_performance_metrics()
            health = PerformanceMonitor.get_system_health()

            # Afficher le rapport
            self.stdout.write('\n' + '='*50)
            self.stdout.write('📈 RAPPORT DE PERFORMANCE')
            self.stdout.write('='*50)

            self.stdout.write(f'Statut global: {health["status"]}')
            self.stdout.write(f'Score de santé: {health["health_score"]}/100')

            if health['issues']:
                self.stdout.write('\n🚨 PROBLÈMES DÉTECTÉS:')
                for issue in health['issues']:
                    self.stdout.write(f'  - {issue}')

            if health['warnings']:
                self.stdout.write('\n⚠️  AVERTISSEMENTS:')
                for warning in health['warnings']:
                    self.stdout.write(f'  - {warning}')

            if metrics:
                self.stdout.write('\n📋 MÉTRIQUES PAR OPÉRATION:')
                for operation, data in metrics.items():
                    self.stdout.write(f'\n{operation.upper()}:')
                    self.stdout.write(f'  Appels totaux: {data.get("total_calls", 0)}')
                    self.stdout.write(f'  Taux de succès: {(data.get("successful_calls", 0) / max(data.get("total_calls", 1), 1) * 100):.1f}%')
                    self.stdout.write(f'  Temps moyen: {data.get("avg_time", 0):.3f}s')
                    self.stdout.write(f'  Temps min/max: {data.get("min_time", 0):.3f}s / {data.get("max_time", 0):.3f}s')

            self.stdout.write('='*50 + '\n')

            self.stdout.write(
                self.style.SUCCESS('✅ Rapport de performance généré')
            )

            return {
                'status': 'success',
                'health': health,
                'metrics': metrics
            }

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la génération du rapport: {e}')
            )
            return {
                'status': 'error',
                'message': str(e)
            }

    def _display_summary(self, results: Dict[str, Any]) -> None:
        """Affiche le résumé des optimisations."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📋 RÉSUMÉ DES OPTIMISATIONS')
        self.stdout.write('='*50)

        for operation, result in results.items():
            status_icon = '✅' if result.get('status') == 'success' else '❌'
            self.stdout.write(f'{status_icon} {operation.upper()}: {result.get("status", "unknown")}')

            if result.get('message'):
                self.stdout.write(f'   {result["message"]}')

        self.stdout.write('='*50)
        self.stdout.write(
            self.style.SUCCESS('🎉 Optimisation terminée!')
        )
