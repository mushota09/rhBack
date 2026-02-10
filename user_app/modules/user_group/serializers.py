from rest_framework import serializers
from adrf.serializers import ModelSerializer as AsyncModelSerializer
from user_app.models import UserGroup, User, Group
from adrf_flex_fields import FlexFieldsModelSerializer
from user_app.modules.user.serializers import J_userSerializers
from user_app.modules.group.serializers import J_GroupSerializers


class J_UserGroupSerializers(FlexFieldsModelSerializer):
    """
    Read-only serializer for UserGroup model with expandable fields
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)
    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserGroup
        fields = "__all__"
        expandable_fields = {
            'user': J_userSerializers,
            'group': J_GroupSerializers,
            'assigned_by': J_userSerializers,
        }


class I_UserGroupSerializers(AsyncModelSerializer):
    """
    Write serializer for UserGroup model with validation
    """

    class Meta:
        model = UserGroup
        fields = ['user', 'group', 'assigned_by', 'is_active']

    def validate(self, data):
        """
        Validate user-group assignment
        """
        user = data.get('user')
        group = data.get('group')

        # Check if user exists and is active
        if user and not user.is_active:
            raise serializers.ValidationError(
                "Impossible d'assigner un utilisateur inactif à un groupe"
            )

        # Check if group exists and is active
        if group and not group.is_active:
            raise serializers.ValidationError(
                "Impossible d'assigner un utilisateur à un groupe inactif"
            )

        # Check for duplicate assignment (if this is a create operation)
        if not self.instance:  # Create operation
            existing = UserGroup.objects.filter(
                user=user,
                group=group,
                is_active=True
            ).exists()

            if existing:
                raise serializers.ValidationError(
                    f"L'utilisateur {user.email} est déjà assigné au groupe {group.code}"
                )

        return data


class UserGroupBulkSerializer(serializers.Serializer):
    """
    Serializer for bulk user-group operations
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of user IDs"
    )
    group_id = serializers.IntegerField(help_text="Group ID")
    action = serializers.ChoiceField(
        choices=['assign', 'remove'],
        help_text="Action to perform: assign or remove"
    )

    def validate_user_ids(self, value):
        """
        Validate that all user IDs exist and are active
        """
        existing_users = User.objects.filter(
            id__in=value,
            is_active=True
        ).values_list('id', flat=True)

        missing_users = set(value) - set(existing_users)
        if missing_users:
            raise serializers.ValidationError(
                f"Utilisateurs introuvables ou inactifs: {list(missing_users)}"
            )

        return value

    def validate_group_id(self, value):
        """
        Validate that group exists and is active
        """
        try:
            group = Group.objects.get(id=value, is_active=True)
            return value
        except Group.DoesNotExist:
            raise serializers.ValidationError(
                f"Groupe avec l'ID {value} introuvable ou inactif"
            )
