"""
Serializers pour les périodes de paie.
"""
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from paie_app.models import periode_paie


class PeriodePaieSerializer(FlexFieldsModelSerializer):
    """Serializer complet pour les périodes de paie."""

    # Champs calculés en lecture seule
    total_employes = serializers.IntegerField(read_only=True)
    statut_display = serializers.CharField(
        source='get_statut_display', read_only=True
    )

    class Meta:
        model = periode_paie
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at',
            'masse_salariale_brute', 'total_net_a_payer',
            'nombre_employes', 'date_approbation'
        )
        expandable_fields = {
            'traite_par': ('user_app.modules.user.serializers.UserSerializer', {}),
            'approuve_par': ('user_app.modules.user.serializers.UserSerializer', {}),
        }

    def validate(self, data):
        """Validation des données de période."""
        annee = data.get('annee')
        mois = data.get('mois')

        if annee and mois:
            # Vérifier l'unicité de la période
            if self.instance:
                # Mise à jour - exclure l'instance actuelle
                existing = periode_paie.objects.filter(
                    annee=annee, mois=mois
                ).exclude(id=self.instance.id).first()
            else:
                # Création - vérifier l'existence
                existing = periode_paie.objects.filter(
                    annee=annee, mois=mois
                ).first()

            if existing:
                raise serializers.ValidationError(
                    f"Une période existe déjà pour {mois}/{annee}"
                )

        return data


class PeriodePaieListSerializer(FlexFieldsModelSerializer):
    """Serializer simplifié pour les listes de périodes."""

    statut_display = serializers.CharField(
        source='get_statut_display', read_only=True
    )

    class Meta:
        model = periode_paie
        fields = (
            'id', 'annee', 'mois', 'statut', 'statut_display',
            'date_debut', 'date_fin', 'nombre_employes',
            'masse_salariale_brute', 'total_net_a_payer',
            'created_at'
        )


class PeriodePaieProcessSerializer(serializers.Serializer):
    """Serializer pour le traitement des périodes."""

    force_reprocess = serializers.BooleanField(
        default=False,
        help_text="Forcer le retraitement même si déjà traité"
    )

    def validate(self, data):
        """Validation pour le traitement."""
        periode = self.context.get('periode')
        if not periode:
            raise serializers.ValidationError("Période non trouvée")

        if periode.statut == 'APPROVED' and not data.get('force_reprocess'):
            raise serializers.ValidationError(
                "Impossible de traiter une période approuvée"
            )

        return data


class PeriodePaieApprovalSerializer(serializers.Serializer):
    """Serializer pour l'approbation des périodes."""

    commentaire = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Commentaire d'approbation"
    )

    def validate(self, data):
        """Validation pour l'approbation."""
        periode = self.context.get('periode')
        if not periode:
            raise serializers.ValidationError("Période non trouvée")

        if periode.statut != 'FINALIZED':
            raise serializers.ValidationError(
                "Seules les périodes finalisées peuvent être approuvées"
            )

        return data
