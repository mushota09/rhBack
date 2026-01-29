from conge_app.models import solde_conge
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.employe.serializers import J_employeSerializers
from conge_app.modules.type_conge.serializers import I_type_congeSerializers

class J_solde_congeSerializers(FlexFieldsModelSerializer):
    employe_id = serializers.PrimaryKeyRelatedField(read_only=True)
    type_conge_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=solde_conge
        fields="__all__"
        expandable_fields = {
          'employe_id': J_employeSerializers,
          'type_conge_id': I_type_congeSerializers,
        }

class I_solde_congeSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=solde_conge
        fields="__all__"