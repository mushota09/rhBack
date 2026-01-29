"""
Service de gestion centralisée des erreurs pour le système de paie.
"""
import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

# Configuration des loggers
logger = logging.getLogger('paie_app')
audit_logger = logging.getLogger('paie_app.audit')
error_logger = logging.getLogger('paie_app.errors')


class PayrollError(Exception):
    """Exception de base pour les erreurs du système de paie."""

    def __init__(self, message: str, error_code: s
eriode_id:
            context['periode_id'] = periode_id
        super().__init__(message, 'CALCULATION_ERROR', context)


class ValidationError(PayrollError):
    """Erreur de validation des données."""

    def __init__(self, message: str, field: str = None, value: Any = None):
        context = {}
        if field:
            context['field'] = field
        if value is not None:
            context['value'] = str(value)
        super().__init__(message, 'VALIDATION_ERROR', context)


class ProcessingError(PayrollError):
    """Erreur lors du traitement des périodes."""

    def __init__(self, message: str, periode_id: int = None, step: str = None):
        context = {}
        if periode_id:
            context['periode_id'] = periode_id
        if step:
            context['processing_step'] = step
        super().__init__(message, 'PROCESSING_ERROR', context)


class ErrorHandler:
    """Service centralisé de gestion des erreurs."""

    # Seuils d'alerte
    ERROR_THRESHOLD_CRITICAL = 10  # Erreurs critiques par heure
    ERROR_THRESHOLD_WARNING = 50   # Erreurs d'avertissement par heure

    @classmethod
    def handle_error(cls, error: Exception, context: Dict = None,
                    user_id: int = None, request_path: str = None) -> Dict[str, Any]:
        """
        Gère une erreur de manière centralisée.

        Args:
            error: L'exception à traiter
            context: Contexte additionnel
            user_id: ID de l'utilisateur concerné
            request_path: Chemin de la requête

        Returns:
            Dict contenant les informations de l'erreur formatées
        """
        error_info = {
            'timestamp': timezone.now().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'user_id': user_id,
            'request_path': request_path,
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }

        # Ajouter des informations spécifiques aux erreurs de paie
        if isinstance(error, PayrollError):
            error_info.update({
                'error_code': error.error_code,
                'payroll_context': error.context,
                'error_timestamp': error.timestamp.isoformat()
            })

        # Logger l'erreur selon sa gravité
        cls._log_error(error, error_info)

        # Envoyer des alertes si nécessaire
        if cls._should_send_alert(error):
            cls._send_error_alert(error_info)

        return error_info

    @classmethod
    def _log_error(cls, error: Exception, error_info: Dict) -> None:
        """Log l'erreur avec le niveau approprié."""
        if isinstance(error, (CalculationError, ProcessingError)):
            error_logger.error(
                f"Erreur critique: {error_info['message']}",
                extra=error_info
            )
        elif isinstance(error, ValidationError):
            logger.warning(
                f"Erreur de validation: {error_info['message']}",
                extra=error_info
            )
        else:
            logger.error(
                f"Erreur système: {error_info['message']}",
                extra=error_info
            )

    @classmethod
    def _should_send_alert(cls, error: Exception) -> bool:
        """Détermine si une alerte doit être envoyée."""
        # Envoyer des alertes pour les erreurs critiques
        return isinstance(error, (CalculationError, ProcessingError))

    @classmethod
    def _send_error_alert(cls, error_info: Dict) -> None:
        """Envoie une alerte par email pour les erreurs critiques."""
        try:
            if not settings.DEBUG and hasattr(settings, 'ADMINS'):
                subject = f"[PAIE] Erreur critique: {error_info['error_type']}"
                message = cls._format_error_email(error_info)

                admin_emails = [admin[1] for admin in settings.ADMINS]
                if admin_emails:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=admin_emails,
                        fail_silently=True
                    )
        except Exception as e:
            logger.error(f"Impossible d'envoyer l'alerte d'erreur: {e}")

    @classmethod
    def _format_error_email(cls, error_info: Dict) -> str:
        """Formate le contenu de l'email d'alerte."""
        return f"""
Une erreur critique s'est produite dans le système de paie:

Timestamp: {error_info['timestamp']}
Type d'erreur: {error_info['error_type']}
Message: {error_info['message']}
Utilisateur: {error_info.get('user_id', 'Non identifié')}
Chemin: {error_info.get('request_path', 'Non spécifié')}

Contexte:
{cls._format_context(error_info.get('context', {}))}

Contexte Paie:
{cls._format_context(error_info.get('payroll_context', {}))}

Veuillez vérifier les logs pour plus de détails.
        """.strip()

    @classmethod
    def _format_context(cls, context: Dict) -> str:
        """Formate le contexte pour l'affichage."""
        if not context:
            return "Aucun contexte disponible"

        formatted = []
        for key, value in context.items():
            formatted.append(f"  {key}: {value}")
        return "\n".join(formatted)

    @classmethod
    def log_audit_event(cls, action: str, resource_type: str, resource_id: int,
                       user_id: int, details: Dict = None, success: bool = True) -> None:
        """
        Enregistre un événement d'audit.

        Args:
            action: Action effectuée (CREATE, UPDATE, DELETE, etc.)
            resource_type: Type de ressource (periode_paie, entree_paie, etc.)
            resource_id: ID de la ressource
            user_id: ID de l'utilisateur
            details: Détails additionnels
            success: Si l'action a réussi
        """
        audit_info = {
            'timestamp': timezone.now().isoformat(),
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'user_id': user_id,
            'success': success,
            'details': details or {}
        }

        audit_logger.info(
            f"AUDIT: {action} {resource_type}#{resource_id} by user#{user_id} - {'SUCCESS' if success else 'FAILED'}",
            extra=audit_info
        )

    @classmethod
    def validate_calculation_inputs(cls, employe_id: int, periode_id: int,
                                  contrat_data: Dict) -> List[str]:
        """
        Valide les données d'entrée pour les calculs salariaux.

        Returns:
            Liste des erreurs de validation
        """
        errors = []

        if not employe_id or employe_id <= 0:
            errors.append("ID employé invalide")

        if not periode_id or periode_id <= 0:
            errors.append("ID période invalide")

        if not contrat_data:
            errors.append("Données contractuelles manquantes")
        else:
            # Valider les champs obligatoires du contrat
            required_fields = ['salaire_base', 'date_debut', 'statut']
            for field in required_fields:
                if field not in contrat_data or contrat_data[field] is None:
                    errors.append(f"Champ contractuel manquant: {field}")

            # Valider les montants
            if 'salaire_base' in contrat_data:
                try:
                    salaire = float(contrat_data['salaire_base'])
                    if salaire <= 0:
                        errors.append("Le salaire de base doit être positif")
                except (ValueError, TypeError):
                    errors.append("Format de salaire de base invalide")

        return errors

    @classmethod
    def create_user_friendly_message(cls, error: Exception) -> str:
        """
        Crée un message d'erreur convivial pour l'utilisateur.

        Args:
            error: L'exception à traiter

        Returns:
            Message d'erreur formaté pour l'utilisateur
        """
        if isinstance(error, CalculationError):
            return "Une erreur s'est produite lors du calcul du salaire. Veuillez vérifier les données contractuelles."

        elif isinstance(error, ValidationError):
            return f"Données invalides: {error.message}"

        elif isinstance(error, ProcessingError):
            return "Une erreur s'est produite lors du traitement de la période. Veuillez réessayer."

        else:
            return "Une erreur inattendue s'est produite. L'équipe technique a été notifiée."

    @classmethod
    def get_error_statistics(cls, hours: int = 24) -> Dict[str, Any]:
        """
        Récupère les statistiques d'erreurs des dernières heures.

        Args:
            hours: Nombre d'heures à analyser

        Returns:
            Statistiques d'erreurs
        """
        # Cette méthode pourrait être étendue pour analyser les logs
        # et retourner des statistiques détaillées
        return {
            'period_hours': hours,
            'total_errors': 0,  # À implémenter avec analyse des logs
            'critical_errors': 0,
            'warning_errors': 0,
            'most_common_errors': [],
            'error_trend': 'stable'  # stable, increasing, decreasing
        }


# Fonctions utilitaires pour l'utilisation dans les vues
def handle_view_error(error: Exception, request=None) -> Dict[str, Any]:
    """Fonction utilitaire pour gérer les erreurs dans les vues."""
    context = {}
    user_id = None
    request_path = None

    if request:
        context['method'] = request.method
        context['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') else None
        request_path = request.path

    return ErrorHandler.handle_error(error, context, user_id, request_path)


def log_calculation_start(employe_id: int, periode_id: int, user_id: int) -> None:
    """Log le début d'un calcul salarial."""
    logger.info(
        f"Début calcul salarial - Employé: {employe_id}, Période: {periode_id}",
        extra={
            'employe_id': employe_id,
            'periode_id': periode_id,
            'user_id': user_id,
            'action': 'CALCULATION_START'
        }
    )


def log_calculation_success(employe_id: int, periode_id: int,
                          salaire_net: float, user_id: int) -> None:
    """Log le succès d'un calcul salarial."""
    logger.info(
        f"Calcul salarial réussi - Employé: {employe_id}, Salaire net: {salaire_net}",
        extra={
            'employe_id': employe_id,
            'periode_id': periode_id,
            'salaire_net': salaire_net,
            'user_id': user_id,
            'action': 'CALCULATION_SUCCESS'
        }
    )
