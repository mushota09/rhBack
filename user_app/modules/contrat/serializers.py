from user_app.models import contrat
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.employe.serializers import J_employeSerializers

class J_contratSerializers(FlexFieldsModelSerializer):
    employe_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=contrat
        fields="__all__"
        expandable_fields = {
          'employe_id': J_employeSerializers,
        }

class I_contratSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=contrat
        fields="__all__"
        