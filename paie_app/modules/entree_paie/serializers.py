"""
Serializers pour les entrées de paie.
"""
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from paie_app.models import entree_paie


class EntreePaieSerializer(FlexFieldsModelSerializer):
    """Serializer complet pour les entrées de paie."""

    employe_nom_complet = serializers.SerializerMethodField()
    periode_display = serializers.SerializerMethodField()

    class Meta:
        model = entree_paie
        fields = '__all__'
        read_only_fields = (
            'id', 'created_at', 'updated_at',
            'calculated_at', 'calculated_by', 'validated_at', 'validated_by',
            'payslip_generated', 'payslip_generated_at', 'payslip_file'
        )

    def get_employe_nom_complet(self, obj):
        """Retourne le nom complet de l'employé."""
        if obj.employe_id:
            return f"{obj.employe_id.nom} {obj.employe_id.prenom}"
        return None

    def get_periode_display(self, obj):
        """Retourne l'affichage de la période."""
        if obj.periode_paie_id:
            return f"{obj.periode_paie_id.mois:02d}/{obj.periode_paie_id.annee}"
        return None


class EntreePaieListSerializer(FlexFieldsModelSerializer):
    """Serializer simplifié pour les listes d'entrées de paie."""

    employe_nom_complet = serializers.SerializerMethodField()
    periode_display = serializers.SerializerMethodField()

    class Meta:
        model = entree_paie
        fields = (
            'id', 'employe_nom_complet', 'periode_display',
            'salaire_base', 'salaire_brut', 'salaire_net',
            'calculated_at', 'payslip_generated', 'created_at'
        )

    def get_employe_nom_complet(self, obj):
        """Retourne le nom complet de l'employé."""
        if obj.employe_id:
            return f"{obj.employe_id.nom} {obj.employe_id.prenom}"
        return None

    def get_periode_display(self, obj):
        """Retourne l'affichage de la période."""
        if obj.periode_paie_id:
            return f"{obj.periode_paie_id.mois:02d}/{obj.periode_paie_id.annee}"
        return None


class EntreePaieRecalculateSerializer(serializers.Serializer):
    """Serializer pour le recalcul des entrées de paie."""

    force_recalculate = serializers.BooleanField(
        default=False,
        help_text="Forcer le recalcul même si déjà validé"
    )


class PayslipGenerationSerializer(serializers.Serializer):
    """Serializer pour la génération de bulletins de paie."""

    template_name = serializers.CharField(
        max_length=100,
        default='default',
        help_text="Nom du template à utiliser"
    )

    regenerate = serializers.BooleanField(
        default=False,
        help_text="Régénérer même si déjà généré"
    )
