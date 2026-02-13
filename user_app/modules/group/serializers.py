from rest_framework import serializers
from user_app.models import Group
from adrf_flex_fields import FlexFieldsModelSerializer


class J_GroupSerializers(FlexFieldsModelSerializer):
    """
    Read-only serializer for Group model with expandable fields
    """
    user_count = serializers.ReadOnlyField()
    permission_count = serializers.ReadOnlyField()
    service_groups = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Group
        fields = "__all__"
        expandable_fields = {
            'service_groups': (
                'user_app.modules.service_group.serializers.J_ServiceGroupSerializer',
                {'many': True}
            ),
            'user_groups': (
                'user_app.modules.user_group.serializers.J_UserGroupSerializers',
                {'many': True}
            ),
            'group_permissions': (
                'user_app.modules.group_permission.serializers.GroupPermissionReadSerializer',
                {'many': True}
            ),
        }


class I_GroupSerializers(FlexFieldsModelSerializer):
    """
    Write serializer for Group model
    """
    class Meta:
        model = Group
        fields = "__all__"
