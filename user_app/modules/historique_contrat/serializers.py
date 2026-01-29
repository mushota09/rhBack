from rest_framework import serializers
from user_app.models import historique_contrat
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.contrat.serializers import J_contratSerializers

class J_historique_contratSerializers(FlexFieldsModelSerializer):
    contrat_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=historique_contrat
        fields="__all__"
        expandable_fields = {
          'contrat_id':J_contratSerializers,
        }

class I_historique_contratSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=historique_contrat
        fields="__all__"