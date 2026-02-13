from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.models import employe


class J_employeSerializers(FlexFieldsModelSerializer):
    poste_id = serializers.PrimaryKeyRelatedField(read_only=True)
    user_account = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = employe
        fields = "__all__"
        expandable_fields = {
            'poste_id': 'user_app.modules.service_group.serializers.J_ServiceGroupSerializer',
            'poste_id.service': (
                'user_app.modules.service.serializers.I_serviceSerializers',
                {'source': 'poste_id.service'}
            ),
            'poste_id.group': (
                'user_app.modules.group.serializers.J_GroupSerializers',
                {'source': 'poste_id.group'}
            ),
            'user_account': 'user_app.modules.user.serializers.J_userSerializers',
            'user_account.user_groups': (
                'user_app.modules.user_group.serializers.J_UserGroupSerializers',
                {'source': 'user_account.user_groups', 'many': True}
            ),
        }


class I_employeSerializers(FlexFieldsModelSerializer):
    class Meta:
        model = employe
        fields = "__all__"
