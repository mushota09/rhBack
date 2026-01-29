"""
Tâches Celery pour le système de paie.
"""
from celery import shared_task, group, chord
from django.utils import timezone
from django.db import transaction
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_payroll_period(self, periode_id):
    """
    Traite une période de paie de manière asynchrone.
    """
    try:
        from paie_app.services.period_processor import PeriodProcessorService
        from paie_app.services.alert_service import AlertService

        service = PeriodProcessorService()
        alert_service = AlertService()

        # Traitement avec gestion d'erreurs et alertes
        with transaction.atomic():
            result = service.process_period(periode_id)

            # Créer une alerte de succès si tout s'est bien passé
            if result.get('processed_employees', 0) > 0:
                alert_service.create_alert(
                    alert_type='PERIOD_PROCESSING',
                    title=f"Période {periode_id} traitée avec succès",
                    message=f"Traitement terminé: {result.get('processed_employees')} employés traités",
                    severity='LOW',
                    periode_paie_id=periode_id,
                    details=result
                )

        return {
            'status': 'success',
            'periode_id': periode_id,
            'processed_employees': result.get('processed_employees', 0),
            'total_amount': str(result.get('total_amount', 0)),
            'processing_time': result.get('processing_time', 0)
        }
    except Exception as exc:
        logger.error(f"Error processing payroll period {periode_id}: {exc}")

        # Créer une alerte d'erreur
        try:
            from paie_app.services.alert_service import AlertService
            alert_service = AlertService()
            alert_service.create_alert(
                alert_type='PERIOD_PROCESSING',
                title=f"Erreur lors du traitement de la période {periode_id}",
                message=str(exc),
                severity='HIGH',
                periode_paie_id=periode_id,
                details={'error': str(exc), 'task_id': self.request.id}
            )
        except:
            pass

        self.retry(countdown=60, max_retries=3)


@shared_task(bind=True)
def process_employee_salary(self, employe_id, periode_id):
    """
    Traite le salaire d'un employé spécifique de manière asynchrone.
    Utilisé pour le traitement parallèle.
    """
    try:
        from paie_app.services.salary_calculator import SalaryCalculatorService
        from paie_app.services.validation_service import ValidationService

        calculator = SalaryCalculatorService()
        validator = ValidationService()

        # Valider avant calcul
        is_valid, errors = validator.validate_contract_for_calculation(employe_id, periode_id)
        if not is_valid:
            return {
                'status': 'error',
                'employe_id': employe_id,
                'errors': errors
            }

        # Calculer le salaire
        result = calculator.calculate_salary(employe_id, periode_id)

        return {
            'status': 'success',
            'employe_id': employe_id,
            'periode_id': periode_id,
            'salary_data': result
        }
    except Exception as exc:
        logger.error(f"Error processing salary for employee {employe_id}: {exc}")
        return {
            'status': 'error',
            'employe_id': employe_id,
            'error': str(exc)
        }


@shared_task(bind=True)
def process_payroll_period_parallel(self, periode_id):
    """
    Traite une période de paie en parallèle pour améliorer les performances.
    """
    try:
        from paie_app.models import periode_paie
        from user_app.models import employe

        # Récupérer tous les employés actifs
        active_employees = list(employe.objects.filter(statut_emploi='ACTIVE').values_list('id', flat=True))

        if not active_employees:
            return {
                'status': 'error',
                'message': 'Aucun employé actif trouvé'
            }

        # Créer un groupe de tâches parallèles
        job = group(process_employee_salary.s(emp_id, periode_id) for emp_id in active_employees)
        result = job.apply_async()

        # Attendre que toutes les tâches se terminent
        results = result.get()

        # Analyser les résultats
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']

        return {
            'status': 'completed',
            'periode_id': periode_id,
            'total_employees': len(active_employees),
            'successful_calculations': len(successful),
            'failed_calculations': len(failed),
            'failed_details': failed
        }

    except Exception as exc:
        logger.error(f"Error in parallel payroll processing for period {periode_id}: {exc}")
        self.retry(countdown=60, max_retries=2)


@shared_task(bind=True)
def generate_payslip(self, entree_paie_id):
    """
    Génère un bulletin de paie de manière asynchrone.
    """
    try:
        from paie_app.services.payslip_generator import PayslipGeneratorService
        service = PayslipGeneratorService()
        result = service.generate_payslip(entree_paie_id)
        return {
            'status': 'success',
            'entree_paie_id': entree_paie_id,
            'payslip_file': result.get('payslip_file')
        }
    except Exception as exc:
        logger.error(f"Error generating payslip {entree_paie_id}: {exc}")
        self.retry(countdown=30, max_retries=3)


@shared_task(bind=True)
def generate_batch_payslips(self, periode_id):
    """
    Génère tous les bulletins de paie d'une période de manière asynchrone.
    """
    try:
        from paie_app.services.payslip_generator import PayslipGeneratorService
        service = PayslipGeneratorService()
        result = service.generate_batch_payslips(periode_id)
        return {
            'status': 'success',
            'periode_id': periode_id,
            'generated_payslips': result.get('generated_payslips', 0)
        }
    except Exception as exc:
        logger.error(f"Error generating batch payslips for period {periode_id}: {exc}")
        self.retry(countdown=60, max_retries=3)


@shared_task(bind=True)
def generate_payslips_parallel(self, periode_id):
    """
    Génère les bulletins de paie en parallèle pour une période.
    """
    try:
        from paie_app.models import entree_paie

        # Récupérer toutes les entrées de paie de la période
        entries = list(entree_paie.objects.filter(
            periode_paie_id=periode_id,
            payslip_generated=False
        ).values_list('id', flat=True))

        if not entries:
            return {
                'status': 'completed',
                'message': 'Aucun bulletin à générer'
            }

        # Créer un groupe de tâches parallèles
        job = group(generate_payslip.s(entry_id) for entry_id in entries)
        result = job.apply_async()

        # Attendre que toutes les tâches se terminent
        results = result.get()

        # Analyser les résultats
        successful = [r for r in results if r['status'] == 'success']

        return {
            'status': 'completed',
            'periode_id': periode_id,
            'total_payslips': len(entries),
            'generated_payslips': len(successful)
        }

    except Exception as exc:
        logger.error(f"Error in parallel payslip generation for period {periode_id}: {exc}")
        self.retry(countdown=60, max_retries=2)


@shared_task(bind=True)
def export_payroll_data(self, periode_id, export_type='excel'):
    """
    Exporte les données de paie d'une période de manière asynchrone.
    """
    try:
        from paie_app.services.export_service import ExportService
        from paie_app.services.alert_service import AlertService

        service = ExportService()
        alert_service = AlertService()

        # Exporter les données
        export_data = service.export_period_data(periode_id, export_type)

        # Créer une alerte de succès
        alert_service.create_alert(
            alert_type='SYSTEM_ERROR',  # Utiliser un type existant
            title=f"Export terminé pour la période {periode_id}",
            message=f"Export {export_type} généré avec succès: {export_data['filename']}",
            severity='LOW',
            periode_paie_id=periode_id,
            details={
                'filename': export_data['filename'],
                'size': export_data['size'],
                'export_type': export_type
            }
        )

        return {
            'status': 'success',
            'periode_id': periode_id,
            'export_file': export_data['filename'],
            'export_type': export_type,
            'file_size': export_data['size']
        }
    except Exception as exc:
        logger.error(f"Error exporting payroll data for period {periode_id}: {exc}")

        # Créer une alerte d'erreur
        try:
            from paie_app.services.alert_service import AlertService
            alert_service = AlertService()
            alert_service.create_alert(
                alert_type='SYSTEM_ERROR',
                title=f"Erreur d'export pour la période {periode_id}",
                message=str(exc),
                severity='HIGH',
                periode_paie_id=periode_id,
                details={'error': str(exc), 'task_id': self.request.id}
            )
        except:
            pass

        self.retry(countdown=60, max_retries=3)


@shared_task(bind=True)
def cleanup_old_alerts(self, days_old=30):
    """
    Nettoie les anciennes alertes résolues.
    """
    try:
        from paie_app.models import Alert
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days_old)

        deleted_count = Alert.objects.filter(
            status='RESOLVED',
            resolved_at__lt=cutoff_date
        ).delete()[0]

        return {
            'status': 'success',
            'deleted_alerts': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as exc:
        logger.error(f"Error cleaning up old alerts: {exc}")
        return {
            'status': 'error',
            'error': str(exc)
        }


@shared_task(bind=True)
def send_payroll_notifications(self, periode_id):
    """
    Envoie les notifications de fin de traitement de paie.
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        from paie_app.models import periode_paie

        periode = periode_paie.objects.get(id=periode_id)

        subject = f"Traitement de paie terminé - {periode.annee}/{periode.mois:02d}"
        message = f"""
        Le traitement de la paie pour la période {periode.annee}/{periode.mois:02d} est terminé.

        Statistiques:
        - Nombre d'employés: {periode.nombre_employes}
        - Masse salariale brute: {periode.masse_salariale_brute}
        - Total net à payer: {periode.total_net_a_payer}

        Vous pouvez maintenant consulter les bulletins de paie.
        """

        # Envoyer aux administrateurs RH
        admin_emails = ['hr@company.com']  # À configurer selon l'environnement

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            fail_silently=False
        )

        return {
            'status': 'success',
            'periode_id': periode_id,
            'emails_sent': len(admin_emails)
        }

    except Exception as exc:
        logger.error(f"Error sending payroll notifications for period {periode_id}: {exc}")
        return {
            'status': 'error',
            'error': str(exc)
        }


@shared_task(bind=True)
def export_employees_data(self, format_type='excel'):
    """
    Exporte les données des employés de manière asynchrone.
    """
    try:
        from paie_app.services.export_service import ExportService
        from paie_app.services.alert_service import AlertService

        service = ExportService()
        alert_service = AlertService()

        # Exporter les données
        export_data = service.export_employees_data(format_type)

        # Créer une alerte de succès
        alert_service.create_alert(
            alert_type='SYSTEM_ERROR',  # Utiliser un type existant
            title="Export des employés terminé",
            message=f"Export {format_type} des employés généré avec succès: {export_data['filename']}",
            severity='LOW',
            details={
                'filename': export_data['filename'],
                'size': export_data['size'],
                'export_type': format_type
            }
        )

        return {
            'status': 'success',
            'export_file': export_data['filename'],
            'export_type': format_type,
            'file_size': export_data['size']
        }
    except Exception as exc:
        logger.error(f"Error exporting employees data: {exc}")

        # Créer une alerte d'erreur
        try:
            from paie_app.services.alert_service import AlertService
            alert_service = AlertService()
            alert_service.create_alert(
                alert_type='SYSTEM_ERROR',
                title="Erreur d'export des employés",
                message=str(exc),
                severity='HIGH',
                details={'error': str(exc), 'task_id': self.request.id}
            )
        except:
            pass

        self.retry(countdown=60, max_retries=3)
