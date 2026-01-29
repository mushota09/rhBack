from user_app.models import audit_log
from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.user.serializers import I_userSerializers

class J_audit_logSerializers(FlexFieldsModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model=audit_log
        fields="__all__"
        expandable_fields = {
          'user_id': I_userSerializers,
        }

class I_audit_logSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=audit_log
        fields="__all__"
        