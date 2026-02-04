"""
Serializers for audit log data with flexible field selection and proper formatting.

This module provides serializers for audit log data with:
- Flexible field selection via ADRF flex_fields
- Proper user relationship handling
- Read and write serializers for different use cases
- Comprehensive field coverage for audit data
"""

from rest_framework import serializers
from adrf_flex_fields import FlexFieldsModelSerializer

from user_app.models import audit_log
from user_app.modules.user.serializers import I_userSerializers


class J_audit_logSerializers(FlexFieldsModelSerializer):
    """
    Read serializer for audit log data with expandable user information.

    Provides comprehensive audit log data with the ability to expand
    user details for better audit trail visibility.
    """

    user_id = serializers.PrimaryKeyRelatedField(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = audit_log
        fields = '__all__'
        expandable_fields = {
            'user_id': I_userSerializers,
        }


class I_audit_logSerializers(FlexFieldsModelSerializer):
    """
    Write serializer for audit log data creation and updates.

    Handles audit log entry creation with proper validation
    and field handling for audit data integrity.
    """

    class Meta:
        model = audit_log
        fields = '__all__'
