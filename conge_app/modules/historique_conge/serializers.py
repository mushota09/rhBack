from rest_framework import serializers
from conge_app.models import historique_conge
from adrf_flex_fields import FlexFieldsModelSerializer
from conge_app.modules.demande_conge.serializers import J_demande_congeSerializers
from user_app.modules.service_group.serializers import J_ServiceGroupSerializer

class J_historique_congeSerializers(FlexFieldsModelSerializer):
    demande_conge_id = serializers.PrimaryKeyRelatedField(read_only=True)
    poste_valideur_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model=historique_conge
        fields="__all__"
        expandable_fields = {
          'demande_conge_id': J_demande_congeSerializers,
          'poste_valideur_id': J_ServiceGroupSerializer,
        }

class I_historique_congeSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=historique_conge
        fields="__all__"
