"""
Modèles pour le système de paie.
"""
from django.db import models
from django.conf import settings
from user_app.models import employe, Base_model


class Alert(Base_model):
    """Modèle pour les alertes du système de paie"""

    ALERT_TYPES = [
        ('VALIDATION_ERROR', 'Erreur de validation'),
        ('CALCULATION_ERROR', 'Erreur de calcul'),
        ('CONTRACT_MISSING', 'Contrat manquant'),
        ('DEDUCTION_ERROR', 'Erreur de retenue'),
        ('REGULATORY_COMPLIANCE', 'Non-conformité réglementaire'),
        ('PERIOD_PROCESSING', 'Erreur de traitement de période'),
        ('SYSTEM_ERROR', 'Erreur système'),
    ]

    SEVERITY_LEVELS = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Élevée'),
        ('CRITICAL', 'Critique'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acquittée'),
        ('RESOLVED', 'Résolue'),
        ('DISMISSED', 'Ignorée'),
    ]

    # Informations de base
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    # Contenu de l'alerte
    title = models.CharField(max_length=255)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)

    # Contexte
    employe_id = models.ForeignKey(
        employe, on_delete=models.CASCADE, null=True, blank=True,
        related_name='alerts'
    )
    periode_paie_id = models.ForeignKey(
        'periode_paie', on_delete=models.CASCADE, null=True, blank=True,
        related_name='alerts'
    )

    # Gestion
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_alerts'
    )
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Notifications
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'paie_alert'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['severity', 'created_at']),
            models.Index(fields=['employe_id', 'status']),
            models.Index(fields=['periode_paie_id', 'status']),
        ]

    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"

    def is_active(self):
        """Vérifie si l'alerte est active"""
        return self.status == 'ACTIVE'

    def is_critical(self):
        """Vérifie si l'alerte est critique"""
        return self.severity == 'CRITICAL'


class retenue_employe(Base_model):
    """Modèle des retenues salariales supplémentaires"""

    TYPES_RETENUE = [
        ('LOAN', 'Remboursement prêt'),
        ('ADVANCE', 'Avance sur salaire'),
        ('FINE', 'Amende / Pénalité'),
        ('INSURANCE', 'Assurance complémentaire'),
        ('UNION', 'Cotisation syndicale'),
        ('OTHER', 'Autre retenue'),
    ]

    employe_id = models.ForeignKey(
        employe, on_delete=models.CASCADE, related_name='deductions'
    )
    type_retenue = models.CharField(max_length=20, choices=TYPES_RETENUE)
    description = models.CharField(max_length=500)
    montant_mensuel = models.DecimalField(max_digits=12, decimal_places=2)
    montant_total = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    montant_deja_deduit = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    est_recurrente = models.BooleanField(default=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    # Informations bancaires pour remboursements
    banque_beneficiaire = models.CharField(max_length=255, blank=True)
    compte_beneficiaire = models.CharField(max_length=255, blank=True)

    # Historique des modifications
    modification_history = models.JSONField(default=list)

    class Meta:
        db_table = 'paie_retenu_salaire'
        indexes = [
            models.Index(fields=['employe_id', 'est_active']),
            models.Index(fields=['type_retenue', 'date_debut']),
            models.Index(fields=['date_debut', 'date_fin']),
            models.Index(fields=['est_recurrente', 'est_active']),
        ]

    def __str__(self):
        return f"{self.employe_id.nom} {self.employe_id.prenom} - {self.description} - {self.montant_mensuel}"


class periode_paie(Base_model):
    """Modèle de période de paie"""
    annee = models.IntegerField()
    mois = models.IntegerField()
    date_debut = models.DateField()
    date_fin = models.DateField()

    STATUT_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('PROCESSING', 'En traitement'),
        ('COMPLETED', 'Terminé'),
        ('FINALIZED', 'Finalisé'),
        ('APPROVED', 'Approuvé'),
    ]

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DRAFT')
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    date_traitement = models.DateTimeField(null=True, blank=True)

    # Champs d'approbation
    approuve_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='periodes_approuvees'
    )
    date_approbation = models.DateTimeField(null=True, blank=True)

    # Statistiques de la période
    nombre_employes = models.IntegerField(default=0)
    masse_salariale_brute = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    total_cotisations_patronales = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    total_cotisations_salariales = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    total_net_a_payer = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )

    class Meta:
        unique_together = ['annee', 'mois']
        db_table = 'paie_periode'
        indexes = [
            models.Index(fields=['annee', 'mois']),
            models.Index(fields=['statut', 'date_traitement']),
            models.Index(fields=['traite_par', 'statut']),
            models.Index(fields=['date_approbation']),
        ]

    def __str__(self):
        return f"{self.annee}/{self.mois:02d}"

    def save(self, *args, **kwargs):
        """Calcul automatique des dates de début et fin"""
        if not self.date_debut or not self.date_fin:
            import calendar
            from datetime import date
            self.date_debut = date(self.annee, self.mois, 1)
            last_day = calendar.monthrange(self.annee, self.mois)[1]
            self.date_fin = date(self.annee, self.mois, last_day)
        super().save(*args, **kwargs)


class entree_paie(Base_model):
    """Modèle d'entrée de paie"""
    employe_id = models.ForeignKey(
        employe, on_delete=models.CASCADE, related_name='payroll_entries'
    )
    periode_paie_id = models.ForeignKey(
        periode_paie, on_delete=models.CASCADE, related_name='entries'
    )

    # Snapshot du contrat au moment du calcul
    contrat_reference = models.JSONField(default=dict)

    # Composants du salaire
    salaire_base = models.DecimalField(max_digits=12, decimal_places=2)
    indemnite_logement = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    indemnite_deplacement = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    indemnite_fonction = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    allocation_familiale = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    autres_avantages = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    salaire_brut = models.DecimalField(max_digits=12, decimal_places=2)

    # Cotisations et retenues (stockées en JSON pour flexibilité)
    cotisations_patronales = models.JSONField(default=dict)
    cotisations_salariales = models.JSONField(default=dict)
    retenues_diverses = models.JSONField(default=dict)

    # Totaux
    total_charge_salariale = models.DecimalField(max_digits=12, decimal_places=2)
    base_imposable = models.DecimalField(max_digits=12, decimal_places=2)
    salaire_net = models.DecimalField(max_digits=12, decimal_places=2)

    # Bulletin de paie
    payslip_generated = models.BooleanField(default=False)
    payslip_file = models.FileField(upload_to='payslips/', blank=True, null=True)
    payslip_generated_at = models.DateTimeField(null=True, blank=True)

    # Validation et statut
    is_validated = models.BooleanField(default=False)
    validation_errors = models.JSONField(default=list)

    # Audit et traçabilité
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calculated_entries'
    )
    calculated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_entries'
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    # Historique des modifications
    modification_history = models.JSONField(default=list)

    class Meta:
        unique_together = ['employe_id', 'periode_paie_id']
        db_table = 'paie_entree'
        indexes = [
            models.Index(fields=['periode_paie_id', 'employe_id']),
            models.Index(fields=['calculated_at']),
            models.Index(fields=['is_validated', 'calculated_at']),
            models.Index(fields=['payslip_generated', 'periode_paie_id']),
            models.Index(fields=['calculated_by', 'calculated_at']),
        ]

    def __str__(self):
        return f"{self.employe_id.nom} {self.employe_id.prenom} - {self.periode_paie_id}"
