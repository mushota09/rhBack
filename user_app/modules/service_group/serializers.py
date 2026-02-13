"""
Serializers for ServiceGroup model
"""
from rest_framework import serializers
from adrf.serializers import ModelSerializer as AsyncModelSerializer
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.models import ServiceGroup


class J_ServiceGroupSerializer(FlexFieldsModelSerializer):
    """
    Read-only serializer for ServiceGroup model with expandable fields
    """
    service = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ServiceGroup
        fields = "__all__"
        expandable_fields = {
            'service': 'user_app.modules.service.serializers.I_serviceSerializers',
            'group': 'user_app.modules.group.serializers.J_GroupSerializers',
        }


class I_ServiceGroupSerializer(AsyncModelSerializer):
    """
    Write serializer for ServiceGroup model with validation
    """

    class Meta:
        model = ServiceGroup
        fields = ['service', 'group']

    def validate(self, data):
        """
        Validate service-group assignment
        """
        service = data.get('service')
        group = data.get('group')

        # Check if service exists
        if not service:
            raise serializers.ValidationError(
                "Le service est requis"
            )

        # Check if group exists
        if not group:
            raise serializers.ValidationError(
                "Le groupe est requis"
            )

        # Check for duplicate assignment (if this is a create operation)
        if not self.instance:  # Create operation
            existing = ServiceGroup.objects.filter(
                service=service,
                group=group
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    f"ServiceGroup existe déjà pour {service.titre} et {group.code}"
                )

        return data
