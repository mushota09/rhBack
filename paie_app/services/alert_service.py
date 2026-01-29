"""
Service de gestion des alertes pour le système de paie.
"""
from typing import Dict, List, Optional
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from paie_app.models import periode_paie, Alert
from user_app.models import employe

User = get_user_model()


class AlertService:
    """Service pour gérer les alertes du système de paie"""

    async def create_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        severity: str = 'MEDIUM',
        employe_id: Optional[int] = None,
        periode_paie_id: Optional[int] = None,
        details: Optional[Dict] = None,
        created_by: Optional[User] = None
    ) -> Alert:
        """Crée une nouvelle alerte."""
        alert_data = {
            'alert_type': alert_type,
            'title': title,
            'message': message,
            'severity': severity,
            'details': details or {},
            'created_by': created_by
        }

        if employe_id:
            try:
                employe_obj = await employe.objects.aget(id=employe_id)
                alert_data['employe_id'] = employe_obj
            except employe.DoesNotExist:
                pass

        if periode_paie_id:
            try:
                periode_obj = await periode_paie.objects.aget(id=periode_paie_id)
                alert_data['periode_paie_id'] = periode_obj
            except periode_paie.DoesNotExist:
                pass

        alert = await Alert.objects.acreate(**alert_data)

        # Envoyer notification email si critique
        if severity == 'CRITICAL':
            await self._send_email_notification(alert)

        return alert

    async def create_validation_error_alert(
        self,
        errors: List[str],
        employe_id: Optional[int] = None,
        periode_paie_id: Optional[int] = None,
        created_by: Optional[User] = None
    ) -> Alert:
        """Crée une alerte pour les erreurs de validation."""
        title = "Erreurs de validation détectées"
        message = "Des erreurs de validation ont été détectées lors du traitement."

        details = {
            'errors': errors,
            'error_count': len(errors),
            'timestamp': timezone.now().isoformat()
        }

        severity = 'HIGH' if len(errors) > 5 else 'MEDIUM'

        return await self.create_alert(
            alert_type='VALIDATION_ERROR',
            title=title,
            message=message,
            severity=severity,
            employe_id=employe_id,
            periode_paie_id=periode_paie_id,
            details=details,
            created_by=created_by
        )

    async def acknowledge_alert(self, alert_id: int, user: User) -> bool:
        """Acquitte une alerte."""
        try:
            alert = await Alert.objects.aget(id=alert_id)
            alert.status = 'ACKNOWLEDGED'
            alert.acknowledged_by = user
            alert.acknowledged_at = timezone.now()
            await alert.asave(update_fields=['status', 'acknowledged_by', 'acknowledged_at'])
            return True
        except Alert.DoesNotExist:
            return False

    async def resolve_alert(self, alert_id: int, user: User) -> bool:
        """Résout une alerte."""
        try:
            alert = await Alert.objects.aget(id=alert_id)
            alert.status = 'RESOLVED'
            alert.resolved_by = user
            alert.resolved_at = timezone.now()
            await alert.asave(update_fields=['status', 'resolved_by', 'resolved_at'])
            return True
        except Alert.DoesNotExist:
            return False

    async def get_active_alerts(self, limit: int = 50) -> List[Alert]:
        """Récupère les alertes actives."""
        alerts = Alert.objects.filter(status='ACTIVE').order_by('-created_at')[:limit]
        return [alert async for alert in alerts]

    async def get_critical_alerts(self, limit: int = 20) -> List[Alert]:
        """Récupère les alertes critiques."""
        alerts = Alert.objects.filter(
            severity='CRITICAL',
            status__in=['ACTIVE', 'ACKNOWLEDGED']
        ).order_by('-created_at')[:limit]
        return [alert async for alert in alerts]

    async def _send_email_notification(self, alert: Alert) -> bool:
        """Envoie une notification email pour une alerte critique."""
        try:
            subject = f"[CRITIQUE] {alert.title}"
            message = f"""
Une alerte critique a été générée dans le système de paie:

Titre: {alert.title}
Message: {alert.message}
Sévérité: {alert.get_severity_display()}
Type: {alert.alert_type}
Créé le: {alert.created_at}

Veuillez vérifier le système de paie.
            """

            admin_emails = await self._get_admin_emails()
            if admin_emails:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_emails,
                    fail_silently=False
                )

                # Marquer l'email comme envoyé
                alert.email_sent = True
                alert.email_sent_at = timezone.now()
                await alert.asave(update_fields=['email_sent', 'email_sent_at'])

                return True
        except Exception as e:
            # Log l'erreur mais ne pas faire échouer la création d'alerte
            print(f"Erreur lors de l'envoi d'email: {e}")

        return False

    async def _get_admin_emails(self) -> List[str]:
        """Récupère les emails des administrateurs."""
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        emails = []
        async for user in admin_users:
            if user.email:
                emails.append(user.email)
        return emails
