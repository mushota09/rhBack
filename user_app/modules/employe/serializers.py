from user_app.models import employe
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.poste.serializers import J_posteSerializers

class J_employeSerializers(FlexFieldsModelSerializer):
    poste_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=employe
        fields="__all__"
        expandable_fields = {
          'poste_id': J_posteSerializers,
        }

class I_employeSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=employe
        fields="__all__"
        