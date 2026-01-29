from django.db import models
from user_app.models import employe,Base_model, poste



# *******************************************************************************************************
# TYPE DE CONGÉ     TYPE DE CONGÉ     TYPE DE CONGÉ     TYPE DE CONGÉ     TYPE DE CONGÉ
# *******************************************************************************************************

class type_conge(Base_model):
    """Modèle de type de congé"""
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    nb_jours_max_par_an = models.IntegerField(default=0)
    report_autorise = models.BooleanField(default=False)
    necessite_validation = models.BooleanField(default=True)

    class Meta:
        unique_together = ['code','nom']
        db_table = 'cg_type_conge'

    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    

# *******************************************************************************************************   
# DEMANDE DE CONGÉ     DEMANDE DE CONGÉ     DEMANDE DE CONGÉ     DEMANDE DE CONGÉ     DEMANDE DE CONGÉ
# *******************************************************************************************************  
 
class demande_conge(Base_model):
    """Modèle de demande de congé"""
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('APPROVED', 'Approuvé'),
        ('REJECTED', 'Refusé'),
        ('CANCELLED', 'Annulé'),
    ]

    employe_id = models.ForeignKey(employe, on_delete=models.CASCADE, related_name='demandes_conge')
    type_conge_id = models.ForeignKey(type_conge, on_delete=models.CASCADE, related_name='demandes')
    date_debut = models.DateField()
    date_fin = models.DateField()
    nb_jours_total = models.IntegerField()
    raison = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    documents = models.JSONField(default=list, blank=True)
    approuve_par_id = models.ForeignKey(employe, on_delete=models.SET_NULL, null=True, blank=True, related_name='conges_approuves')
    date_approbation = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cg_demande_conge'

    def __str__(self):
        return f"{self.employe_id.full_name} - {self.type_conge_id.nom} ({self.date_debut} à {self.date_fin})"




# *****************************************************************************************************************
# SOLDE CONGE              SOLDE CONGE                      SOLDE CONGE              SOLDE CONGE       SOLDE CONGE
# *****************************************************************************************************************

class solde_conge(Base_model):
    """Modèle de solde de congé"""
    employe_id = models.ForeignKey(employe, on_delete=models.CASCADE, related_name='soldes_conge')
    type_conge_id = models.ForeignKey(type_conge, on_delete=models.CASCADE, related_name='soldes')
    annee = models.IntegerField()
    alloue = models.IntegerField(default=0)
    utilise = models.IntegerField(default=0)
    restant = models.IntegerField(default=0)
    reporte = models.IntegerField(default=0)

    class Meta:
        unique_together = ['employe_id', 'type_conge_id', 'annee']
        db_table = 'cg_solde_conge'

    def __str__(self):
        return f"{self.employe_id.full_name} - {self.type_conge_id.nom} ({self.annee})"
    
    
    
# *****************************************************************************************************************************************
# HISTORIQUE CONGE              HISTORIQUE CONGE                      HISTORIQUE CONGE              HISTORIQUE CONGE       HISTORIQUE CONGE
# *****************************************************************************************************************************************


class historique_conge(Base_model):
    demande_conge_id = models.ForeignKey(demande_conge, on_delete=models.CASCADE, related_name='historique')
    poste_valideur_id = models.ForeignKey(poste, on_delete=models.SET_NULL, null=True)
    date_validation = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True)

    class Meta:
        db_table = 'cg_historique_conge'

    def __str__(self):
        return f"Validation {self.demande_conge_id}"
