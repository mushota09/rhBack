"""
Serializers pour les retenues employés.
"""
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from paie_app.models import retenue_employe


class RetenueEmployeSerializer(FlexFieldsModelSerializer):
    """Serializer complet pour les retenues employés."""

    employe_nom_complet = serializers.SerializerMethodField()
    montant_restant = serializers.SerializerMethodField()

    class Meta:
        model = retenue_employe
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at',
            'montant_deja_deduit', 'cree_par', 'modification_history'
        )

    def get_employe_nom_complet(self, obj):
        """Retourne le nom complet de l'employé."""
        if obj.employe_id:
            return f"{obj.employe_id.nom} {obj.employe_id.prenom}"
        return None

    def get_montant_restant(self, obj):
        """Calcule le montant restant à déduire."""
        if obj.montant_total and obj.montant_deja_deduit:
            return obj.montant_total - obj.montant_deja_deduit
        if obj.montant_total:
            return obj.montant_total
        return None

    def validate(self, data):
        """Validation des données de retenue."""
        # Vérifier que la date de fin est après la date de début
        if data.get('date_fin') and data.get('date_debut'):
            if data['date_fin'] <= data['date_debut']:
                raise serializers.ValidationError(
                    "La date de fin doit être postérieure à la date de début"
                )

        # Vérifier que le montant mensuel est positif
        if data.get('montant_mensuel') and data['montant_mensuel'] <= 0:
            raise serializers.ValidationError(
                "Le montant mensuel doit être positif"
            )

        # Vérifier que le montant total est supérieur au montant mensuel
        if (data.get('montant_total') and data.get('montant_mensuel') and
                data['montant_total'] < data['montant_mensuel']):
            raise serializers.ValidationError(
                "Le montant total doit être supérieur ou égal "
                "au montant mensuel"
            )

        return data


class RetenueEmployeListSerializer(FlexFieldsModelSerializer):
    """Serializer simplifié pour les listes de retenues."""

    employe_nom_complet = serializers.SerializerMethodField()
    montant_restant = serializers.SerializerMethodField()

    class Meta:
        model = retenue_employe
        fields = (
            'id', 'employe_nom_complet', 'type_retenue',
            'description', 'montant_mensuel', 'montant_total', 'montant_restant',
            'date_debut', 'date_fin', 'est_active', 'est_recurrente',
            'created_at'
        )

    def get_employe_nom_complet(self, obj):
        """Retourne le nom complet de l'employé."""
        if obj.employe_id:
            return f"{obj.employe_id.nom} {obj.employe_id.prenom}"
        return None

    def get_montant_restant(self, obj):
        """Calcule le montant restant à déduire."""
        if obj.montant_total and obj.montant_deja_deduit:
            return obj.montant_total - obj.montant_deja_deduit
        if obj.montant_total:
            return obj.montant_total
        return None


class RetenueEmployeDeactivateSerializer(serializers.Serializer):
    """Serializer pour la désactivation des retenues."""

    raison = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Raison de la désactivation"
    )


class RetenueEmployeHistorySerializer(serializers.Serializer):
    """Serializer pour l'historique des retenues."""

    date_debut = serializers.DateField(
        required=False,
        help_text="Date de début pour filtrer l'historique"
    )

    date_fin = serializers.DateField(
        required=False,
        help_text="Date de fin pour filtrer l'historique"
    )
