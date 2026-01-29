from rest_framework import serializers
from user_app.models import User as user
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.employe.serializers import I_employeSerializers

class J_userSerializers(FlexFieldsModelSerializer):
    employe_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=user
        fields="__all__"
        expandable_fields = {
          'employe_id': I_employeSerializers,
        }

class I_userSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=user
        fields="__all__"