from user_app.models import poste
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.service.serializers import I_serviceSerializers

class J_posteSerializers(FlexFieldsModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=poste
        fields="__all__"
        expandable_fields = {
          'service_id': I_serviceSerializers,
        }

class I_posteSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=poste
        fields="__all__"