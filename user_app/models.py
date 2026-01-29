from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from asgiref.sync import sync_to_async
import hashlib

# ****************************************************************************************************************
# MODELE BASE                      MODELE BASE                      MODELE BASE                      MODELE BASE
# ****************************************************************************************************************
class Base_model(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

# *******************************************************************************************************
# SERVICE                         SERVICE                         SERVICE                         SERVICE
# *******************************************************************************************************
class service(models.Model):
    titre = models.CharField(max_length=255)
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'rh_service'

    def __str__(self):
        return self.titre

# *******************************************************************************************************
# POSTE                           POSTE                           POSTE                           POSTE
# *******************************************************************************************************
class poste(models.Model):
    titre = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    service_id = models.ForeignKey(service, on_delete=models.CASCADE, related_name='postes')
    class Meta:
        db_table = 'rh_poste'

    def __str__(self):
        return self.titre


# *******************************************************************************************************
# EMPLOYE                         EMPLOYE                         EMPLOYE                         EMPLOYE
# *******************************************************************************************************
class employe(Base_model):
    SEXE_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
        ('O', 'Autre'),
    ]

    STATUT_MATRIMONIAL_CHOICES = [
        ('S', 'Célibataire'),
        ('M', 'Marié'),
        ('D', 'Divorcé'),
        ('W', 'Veuf'),
    ]

    STATUT_EMPLOI_CHOICES = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('TERMINATED', 'Résilié'),
        ('SUSPENDED', 'Suspendu'),
    ]

    prenom = models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    postnom = models.CharField(max_length=255, blank=True)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    statut_matrimonial = models.CharField(max_length=1, choices=STATUT_MATRIMONIAL_CHOICES)
    nationalite = models.CharField(max_length=100)

    banque = models.CharField(max_length=255)
    numero_compte = models.CharField(max_length=255)
    niveau_etude = models.CharField(max_length=255)
    numero_inss = models.CharField(max_length=255)

    email_personnel = models.EmailField()
    email_professionnel = models.EmailField(blank=True, unique=True)

    telephone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    telephone_personnel = models.CharField(validators=[telephone_regex], max_length=17)
    telephone_professionnel = models.CharField(validators=[telephone_regex], max_length=17, blank=True)

    adresse_ligne1 = models.CharField(max_length=200)
    adresse_ligne2 = models.CharField(max_length=200, blank=True)
    ville = models.CharField(max_length=100, null=True)
    province = models.CharField(max_length=100, null=True)
    code_postal = models.CharField(max_length=20, null=True)
    pays = models.CharField(max_length=100, null=True)
    matricule = models.CharField(max_length=100, null=True)

    poste_id = models.ForeignKey(poste, on_delete=models.SET_NULL, null=True, related_name='employes')
    responsable_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordonnes')
    date_embauche = models.DateField()
    statut_emploi = models.CharField(max_length=20, choices=STATUT_EMPLOI_CHOICES, default='ACTIVE')

    nombre_enfants = models.IntegerField(default=0)
    nom_conjoint = models.CharField(max_length=100, blank=True)
    biographie = models.TextField(blank=True)

    nom_contact_urgence = models.CharField(max_length=100)
    lien_contact_urgence = models.CharField(max_length=50)
    telephone_contact_urgence = models.CharField(validators=[telephone_regex], max_length=17)

    class Meta:
        db_table = 'rh_employe'

    def __str__(self):
        return f"{self.id} - {self.nom} {self.prenom}"

    @property
    def full_name(self):
        return f"{self.nom} {self.postnom} {self.prenom}"



# *******************************************************************************************************
# CONTRAT                         CONTRAT                         CONTRAT                       CONTRAT
# *******************************************************************************************************
class contrat(models.Model):
    TYPE_CONTRAT_CHOICES = [
        ('PERMANENT', 'Permanent'),
        ('TEMPORARY', 'Temporaire'),
        ('INTERNSHIP', 'Stage'),
        ('CONSULTANT', 'Consultant'),
    ]

    TYPE_SALAIRE_CHOICES = [
        ('H', 'Heure'),
        ('M', 'Mensuel'),
    ]

    employe_id = models.ForeignKey(employe, on_delete=models.CASCADE, related_name='contrats')
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT_CHOICES)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    type_salaire = models.CharField(max_length=50, choices=TYPE_SALAIRE_CHOICES)

    salaire_base = models.DecimalField(max_digits=12, decimal_places=2)
    devise = models.CharField(max_length=3, default='USD')

    indemnite_logement = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    indemnite_deplacement = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    prime_fonction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    autre_avantage = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    assurance_patronale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    assurance_salariale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fpc_patronale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fpc_salariale = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    statut = models.CharField(max_length=50, default='en_cours')
    commentaire = models.TextField(blank=True)

    class Meta:
        db_table = 'rh_contrat'

    def __str__(self):
        return f"{self.type_contrat} salaire de base {self.salaire_base}"

    def calcul_allocation_familiale(self):
        """Calcule l'allocation familiale selon le nombre d'enfants"""
        if self.employe_id.nombre_enfants == 0:
            return 0
        elif self.employe_id.nombre_enfants == 1:
            return 5000
        elif self.employe_id.nombre_enfants == 2:
            return 10000
        elif self.employe_id.nombre_enfants == 3:
            return 15000
        else:
            return 15000 + ((self.employe_id.nombre_enfants - 3) * 3000)

    def calcul_composants_salaire(self):
        """Calcule tous les composants du salaire et les retenues"""

        indemnite_logement = float(self.salaire_base) * (float(self.indemnite_logement) / 100)
        indemnite_deplacement = float(self.salaire_base) * (float(self.indemnite_deplacement) / 100)
        indemnite_fonction = float(self.salaire_base) * (float(self.prime_fonction) / 100)
        allocation = self.calcul_allocation_familiale()
        autres_avantages = float(self.autre_avantage)

        salaire_brut = (
            float(self.salaire_base) +
            indemnite_logement +
            indemnite_deplacement +
            indemnite_fonction +
            allocation +
            autres_avantages
        )

        # Cotisations patronales
        mfp_patron = (salaire_brut - indemnite_logement) * (float(self.assurance_patronale) / 100)
        inss_pa_pension = min(salaire_brut * 0.06, 27000) if salaire_brut < 450000 else 27000
        inss_pa_risque = min(salaire_brut * 0.06, 2400) if salaire_brut < 80000 else 2400
        fpc_patron = salaire_brut * (float(self.fpc_patronale) / 100)

        # Cotisations salariales
        mfp_employe = (salaire_brut - indemnite_logement) * (float(self.assurance_salariale) / 100)
        inss_employe = min(salaire_brut * 0.04, 18000) if salaire_brut < 450000 else 18000
        fpc_employe = salaire_brut * (float(self.fpc_salariale) / 100)

        total_charge_salariale = (
            salaire_brut +
            inss_pa_pension +
            inss_pa_risque +
            mfp_patron +
            fpc_patron
        )

        base_imposable = (
            salaire_brut -
            indemnite_logement -
            indemnite_deplacement -
            indemnite_fonction -
            mfp_employe -
            inss_employe
        )

        # IRE
        if base_imposable <= 150000:
            ire = 0
        elif base_imposable <= 300000:
            ire = (base_imposable - 150000) * 0.2
        else:
            ire = (base_imposable - 300000) * 0.3 + 30000

        # Retenues supplémentaires
        autres_retenues = sum([
            float(retenue.montant_mensuel)
            for retenue in self.employe_id.deductions.filter(est_active=True)
        ])

        salaire_net = (
            total_charge_salariale -
            mfp_patron -
            inss_pa_pension -
            inss_pa_risque -
            mfp_employe -
            inss_employe -
            ire -
            autres_retenues -
            fpc_patron -
            fpc_employe
        )

        return {
            'indemnite_logement': round(indemnite_logement),
            'indemnite_deplacement': round(indemnite_deplacement),
            'indemnite_fonction': round(indemnite_fonction),
            'autres_avantages': round(autres_avantages),
            'allocation_familiale': allocation,
            'salaire_brut': round(salaire_brut),
            'mfp_patron': round(mfp_patron),
            'inss_pa_pension': round(inss_pa_pension),
            'inss_pa_risque': round(inss_pa_risque),
            'mfp_employe': round(mfp_employe),
            'inss_employe': round(inss_employe),
            'base_fpc': round(salaire_brut),
            'fpc_patron': round(fpc_patron),
            'fpc_employe': round(fpc_employe),
            'total_charge_salariale': round(total_charge_salariale),
            'base_imposable': round(base_imposable),
            'ire': round(ire),
            'autres_retenues': round(autres_retenues),
            'salaire_net': round(salaire_net),
        }

# ********************************************************************************************************
# HISTORIQUE CONTRAT               HISTORIQUE CONTRAT               HISTORIQUE CONTRAT               HISTORIQUE CONTRAT
# ********************************************************************************************************
class historique_contrat(models.Model):
    contrat_id = models.ForeignKey(contrat, on_delete=models.CASCADE, related_name='historique')
    date_modification = models.DateTimeField(auto_now_add=True)
    ancien_salaire = models.DecimalField(max_digits=12, decimal_places=2)
    nouveau_salaire = models.DecimalField(max_digits=12, decimal_places=2)
    prime_fonction = models.DecimalField(max_digits=12, decimal_places=2)
    indemnites = models.JSONField(default=dict)
    cotisations = models.JSONField(default=dict)
    allocation_familiale = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    autres_avantages = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commentaire = models.TextField(blank=True)

    class Meta:
        db_table = 'rh_historique_contrat'

    def __str__(self):
        return f"Historique contrat {self.contrat_id}"

# *******************************************************************************************************
# USER                            USER                            USER                            USER
# *******************************************************************************************************


class UserManager(BaseUserManager):
    async def acreate_user(self, email, password=None, **extra_fields):
        """Version asynchrone simple avec gestion d'erreur"""
        if not email:
            raise ValueError(_('L\'email est requis'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            from asgiref.sync import sync_to_async
            await sync_to_async(user.set_password)(password)

        from django.db import IntegrityError
        try:
            await user.asave()
            return user
        except IntegrityError:
            raise ValueError(_('Cet email est déjà utilisé. Veuillez utiliser un email différent.'))

    async def acreate_superuser(self, email, password=None, **extra_fields):
        """Version asynchrone de create_superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return await self.acreate_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, db_column='id')
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(null=False, unique=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    employe_id = models.OneToOneField(employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_account')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nom = models.CharField(max_length=200, blank=True)
    prenom = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.nom} {self.prenom}".strip()

    def get_short_name(self):
        return self.prenom or self.nom
# *******************************************************************************************************
# AUDIT LOG                       AUDIT LOG                       AUDIT LOG                       AUDIT LOG
# *******************************************************************************************************

class audit_log(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Créer'),
        ('UPDATE', 'Modifier'),
        ('DELETE', 'Supprimer'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('VIEW', 'Voir'),
        ('EXPORT', 'Exporter'),
    ]

    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    type_ressource = models.CharField(max_length=50)
    id_ressource = models.CharField(max_length=100, blank=True)
    anciennes_valeurs = models.JSONField(null=True, blank=True)
    nouvelles_valeurs = models.JSONField(null=True, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auth_audit_log'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user_id} - {self.action} - {self.type_ressource} - {self.timestamp}"



# *******************************************************************************************************
# DOCUMENTS EMPLOYE                 DOCUMENTS EMPLOYE                 DOCUMENTS EMPLOYE                 DOCUMENTS EMPLOYE
# *******************************************************************************************************


class document(Base_model):
    """Document model for employee documents"""
    DOCUMENT_TYPES = [
        ('CONTRACT', 'Employment Contract'),
        ('ID', 'Identification Document'),
        ('RESUME', 'Resume/CV'),
        ('CERTIFICATE', 'Certificate'),
        ('PERFORMANCE', 'Performance Review'),
        ('DISCIPLINARY', 'Disciplinary Action'),
        ('MEDICAL', 'Medical Certificate'),
        ('TRAINING', 'Training Certificate'),
        ('OTHER', 'Other'),
    ]

    employe_id = models.ForeignKey(employe, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    titre = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='employee_documents/')
    uploaded_by = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True, help_text="For documents that expire")

    class Meta:
        db_table = 'rh_employe_document'

    def __str__(self):
        return f"{self.employe_id.full_name} - {self.titre}"
