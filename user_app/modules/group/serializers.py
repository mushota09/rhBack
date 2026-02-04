from rest_framework import serializers
from user_app.models import Group
from adrf_flex_fields import FlexFieldsModelSerializer


class J_GroupSerializers(FlexFieldsModelSerializer):
    """
    Read-only serializer for Group model with expandable fields
    """
    user_count = serializers.ReadOnlyField()
    permission_count = serializers.ReadOnlyField()

    class Meta:
        model = Group
        fields = "__all__"


class I_GroupSerializers(FlexFieldsModelSerializer):
    """
    Write serializer for Group model
    """
    class Meta:
        model = Group
        fields = "__all__"
