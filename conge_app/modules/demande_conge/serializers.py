from rest_framework import serializers
from conge_app.models import demande_conge
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.employe.serializers import J_employeSerializers
from conge_app.modules.type_conge.serializers import I_type_congeSerializers

class J_demande_congeSerializers(FlexFieldsModelSerializer):
    employe_id = serializers.PrimaryKeyRelatedField(read_only=True)
    type_conge_id = serializers.PrimaryKeyRelatedField(read_only=True)
    approuve_par_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=demande_conge
        fields="__all__"
        expandable_fields = {
          'employe_id': J_employeSerializers,
          'type_conge_id': I_type_congeSerializers,
          'approuve_par_id': J_employeSerializers,
        }

class I_demande_congeSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=demande_conge
        fields="__all__"