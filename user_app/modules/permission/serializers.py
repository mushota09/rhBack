# Serializers for permission management endpoints

from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.models import Permission, GroupPermission


class PermissionSerializer(FlexFieldsModelSerializer):
    # Serializer for Permission model
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)

    class Meta:
        model = Permission
        fields = [
            'id', 'codename', 'name', 'content_type', 'content_type_name',
            'resource', 'action', 'description'
        ]
        read_only_fields = ['id']


class GroupPermissionReadSerializer(FlexFieldsModelSerializer):
    # Read serializer for GroupPermission model with expandable fields
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    permission = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GroupPermission
        fields = [
            'id', 'group', 'permission', 'granted', 'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at']
        expandable_fields = {
            'group': 'user_app.modules.group.serializers.J_GroupSerializers',
            'permission': 'user_app.modules.permission.serializers.PermissionSerializer',
            'created_by': 'user_app.modules.user.serializers.J_userSerializers',
        }


class GroupPermissionWriteSerializer(serializers.ModelSerializer):
    # Write serializer for GroupPermission model

    class Meta:
        model = GroupPermission
        fields = ['id', 'group', 'permission', 'granted']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Validate the group permission data
        group = attrs.get('group')
        permission = attrs.get('permission')

        # Validate group is active
        if group and not group.is_active:
            raise serializers.ValidationError({
                'group': 'Cannot assign permissions to inactive groups.'
            })

        # Check for duplicates (only for creation)
        if not self.instance:  # Creating new instance
            if GroupPermission.objects.filter(group=group, permission=permission).exists():
                raise serializers.ValidationError({
                    'non_field_errors': [
                        f'Permission "{permission.name}" is already assigned to group "{group.code}".'
                    ]
                })

        return attrs

    def create(self, validated_data):
        # Create a new group permission
        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user

        return super().create(validated_data)


class BulkGroupPermissionSerializer(serializers.Serializer):
    # Serializer for bulk operations on group permissions
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of group IDs to assign permissions to"
    )
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of permission IDs to assign to groups"
    )
    granted = serializers.BooleanField(
        default=True,
        help_text="Whether to grant or revoke the permissions"
    )

    def validate(self, attrs):
        # Validate bulk operation data
        group_ids = attrs.get('group_ids', [])
        permission_ids = attrs.get('permission_ids', [])

        if not group_ids and not permission_ids:
            raise serializers.ValidationError(
                "Either group_ids or permission_ids must be provided."
            )

        return attrs


class GroupPermissionSummarySerializer(serializers.Serializer):
    # Serializer for group permission summary information
    group_code = serializers.CharField(read_only=True)
    group_name = serializers.CharField(read_only=True)
    permission_count = serializers.IntegerField(read_only=True)
    granted_count = serializers.IntegerField(read_only=True)
    denied_count = serializers.IntegerField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)
