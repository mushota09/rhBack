from rest_framework import serializers
from user_app.models import document
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.employe.serializers import I_employeSerializers

class J_documentSerializers(FlexFieldsModelSerializer):
    employe_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=document
        fields="__all__"
        expandable_fields = {
          'employe_id': I_employeSerializers,
        }

class I_documentSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=document
        fields="__all__"