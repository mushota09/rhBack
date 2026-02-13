"""
ViewSet for ServiceGroup model
"""
from user_app.models import ServiceGroup
from adrf.viewsets import ModelViewSet
from adrf_flex_fields.views import FlexFieldsMixin, SerializerMethodMixin
from .serializers import J_ServiceGroupSerializer, I_ServiceGroupSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from utilities.auth import JWT_AUTH
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from asgiref.sync import sync_to_async


class ServiceGroupViewSet(FlexFieldsMixin, SerializerMethodMixin, ModelViewSet):
    """
    Async ViewSet for ServiceGroup management with ADRF and FlexFields

    Provides:
    - CRUD operations for service-group relationships
    - Dynamic field expansion for service and group
    - Pagination, filtering, and search capabilities
    - Async operations for better performance
    """
    queryset = ServiceGroup.objects.all()
    serializer_class_read = J_ServiceGroupSerializer
    serializer_class_write = I_ServiceGroupSerializer
    authentication_classes = [JWT_AUTH]
    permission_classes = [IsAuthenticated]

    # FlexFields configuration
    permit_list_expands = ['service', 'group']

    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['service', 'group']
    search_fields = ['service__titre', 'service__code', 'group__name', 'group__code']
    ordering_fields = ['id', 'service__titre', 'group__code']
    ordering = ['id']

    def get_queryset(self):
        """
        Override to provide queryset with optimizations using select_related
        """
        return ServiceGroup.objects.select_related('service', 'group').all()

    async def adestroy(self, request, *args, **kwargs):
        """
        Delete a ServiceGroup with validation logic.

        If this is the last ServiceGroup for the associated Group:
        - Check if the Group has active users
        - If no active users, delete the Group as well
        - If active users exist, prevent deletion and return error

        Requirements: 4.1, 4.2, 4.3, 4.4, 8.3
        """
        instance = await self.aget_object()
        group = instance.group

        # Use sync_to_async for database operations
        @sync_to_async
        def check_and_delete():
            with transaction.atomic():
                # Count other ServiceGroups for this Group
                other_service_groups_count = ServiceGroup.objects.filter(
                    group=group
                ).exclude(id=instance.id).count()

                # If this is the last ServiceGroup, check for active users
                if other_service_groups_count == 0:
                    active_user_count = group.user_groups.filter(
                        is_active=True
                    ).count()

                    if active_user_count > 0:
                        return {
                            'error': True,
                            'message': (
                                f'Impossible de supprimer ce ServiceGroup. '
                                f'Le groupe {group.code} a {active_user_count} '
                                f'utilisateur(s) actif(s).'
                            )
                        }

                    # No active users, safe to delete both
                    instance.delete()
                    group.delete()
                    return {
                        'error': False,
                        'message': (
                            f'ServiceGroup et groupe {group.code} '
                            f'supprimés avec succès.'
                        )
                    }
                else:
                    # Other ServiceGroups exist, only delete this one
                    instance.delete()
                    return {
                        'error': False,
                        'message': 'ServiceGroup supprimé avec succès.'
                    }

        result = await check_and_delete()

        if result['error']:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': result['message']},
            status=status.HTTP_204_NO_CONTENT
        )
