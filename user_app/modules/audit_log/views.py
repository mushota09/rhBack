"""
Audit Log ViewSet for querying audit history with filtering and search.

This module provides comprehensive audit log querying functionality with:
- Filtering by user, action, resource type, date ranges
- Search across user details, actions, and resource information
- Ordering by timestamp and other relevant fields
- Permission-based access control for audit data
"""

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from adrf.viewsets import ModelViewSet

from user_app.models import audit_log
from utilities.permissions import CanViewAuditLogs
from .serializers import J_audit_logSerializers, I_audit_logSerializers


class AuditLogFilter(django_filters.FilterSet):
    """
    Custom filter set for audit logs with advanced filtering capabilities.

    Provides date range filtering, action filtering, and resource type
    filtering for comprehensive audit log querying.
    """

    # Date range filtering
    timestamp_after = django_filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='gte',
        help_text='Filter audit logs after this timestamp (inclusive)'
    )
    timestamp_before = django_filters.DateTimeFilter(
        field_name='timestamp',
        lookup_expr='lte',
        help_text='Filter audit logs before this timestamp (inclusive)'
    )

    # Date filtering (without time)
    date_after = django_filters.DateFilter(
        field_name='timestamp__date',
        lookup_expr='gte',
        help_text='Filter audit logs after this date (inclusive)'
    )
    date_before = django_filters.DateFilter(
        field_name='timestamp__date',
        lookup_expr='lte',
        help_text='Filter audit logs before this date (inclusive)'
    )

    # Action filtering with multiple choices
    action = django_filters.MultipleChoiceFilter(
        choices=audit_log.ACTION_CHOICES,
        help_text='Filter by one or more actions'
    )

    # Resource type filtering
    type_ressource = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text='Filter by resource type (case-insensitive partial match)'
    )

    # User filtering with related field lookups
    user_email = django_filters.CharFilter(
        field_name='user_id__email',
        lookup_expr='icontains',
        help_text='Filter by user email (case-insensitive partial match)'
    )

    user_name = django_filters.CharFilter(
        method='filter_user_name',
        help_text='Filter by user name (searches both nom and prenom)'
    )

    # IP address filtering
    adresse_ip = django_filters.CharFilter(
        lookup_expr='exact',
        help_text='Filter by exact IP address'
    )

    class Meta:
        model = audit_log
        fields = {
            'user_id': ['exact'],
            'action': ['exact', 'in'],
            'type_ressource': ['exact', 'icontains'],
            'id_ressource': ['exact', 'icontains'],
            'adresse_ip': ['exact'],
        }

    def filter_user_name(self, queryset, name, value):  # pylint: disable=unused-argument
        """
        Custom filter method to search across user's nom and prenom fields.
        """
        if not value:
            return queryset

        return queryset.filter(
            django_filters.Q(user_id__nom__icontains=value) |
            django_filters.Q(user_id__prenom__icontains=value)
        )


class AuditLogViewSet(ModelViewSet):
    """
    ViewSet for querying audit logs with comprehensive filtering and search.

    Provides endpoints to query audit logs with filtering capabilities as
    required by Requirements 7.3 and 7.5 for audit history display and
    querying.

    Features:
    - Filter by user, action, resource type, date ranges
    - Search across user details, actions, and resource information
    - Order by timestamp, action, resource type
    - Permission-based access control (superuser only)
    - Flexible field selection via ADRF flex_fields
    - Advanced date range filtering
    - Multiple action filtering
    """

    queryset = audit_log.objects.select_related('user_id').all().order_by(
        '-timestamp'
    )
    serializer_class_read = J_audit_logSerializers
    serializer_class_write = I_audit_logSerializers
    permission_classes = [CanViewAuditLogs]

    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuditLogFilter

    # Search fields for text-based searching
    search_fields = [
        'user_id__email',
        'user_id__nom',
        'user_id__prenom',
        'action',
        'type_ressource',
        'id_ressource',
        'adresse_ip',
        'user_agent'
    ]

    # Ordering fields
    ordering_fields = [
        'timestamp',
        'action',
        'type_ressource',
        'user_id__email',
        'user_id__nom'
    ]

    # Default ordering
    ordering = ['-timestamp']

    # Expandable fields for flexible responses
    permit_list_expands = ['user_id']


# Maintain backward compatibility with existing URL configuration
audit_logAPIView = AuditLogViewSet
