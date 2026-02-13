from user_app.models import Group, ServiceGroup, service
from adrf.viewsets import ModelViewSet
from adrf_flex_fields.views import FlexFieldsMixin, SerializerMethodMixin
from .serializers import J_GroupSerializers, I_GroupSerializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from django.db import transaction
from utilities.auth import JWT_AUTH


class GroupViewSet(FlexFieldsMixin, SerializerMethodMixin, ModelViewSet):
    """
    Async ViewSet for Group management with ADRF and FlexFields

    Provides:
    - CRUD operations for groups
    - Dynamic field expansion for service_groups, user_groups, group_permissions
    - Pagination, filtering, and search capabilities
    - Async operations for better performance
    """
    queryset = Group.objects.all().order_by('code')
    serializer_class_read = J_GroupSerializers
    serializer_class_write = I_GroupSerializers
    authentication_classes = [JWT_AUTH]
    permission_classes = [IsAuthenticated]

    # FlexFields configuration
    permit_list_expands = ['service_groups', 'user_groups', 'group_permissions']

    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'code']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at', 'updated_at']
    ordering = ['code']

    def get_queryset(self):
        """
        Override to provide queryset with optimizations
        """
        queryset = Group.objects.prefetch_related(
            'service_groups',
            'service_groups__service',
            'user_groups',
            'user_groups__user',
            'group_permissions',
            'group_permissions__permission'
        ).all().order_by('code')

        # Apply active filter by default if not specified
        is_active = self.request.query_params.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)

        return queryset

    async def list(self, request, *args, **kwargs):
        """
        Override list to add custom response data
        """
        response = await super().list(request, *args, **kwargs)

        # Add metadata to response
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if 'results' in response.data:
                response.data['meta'] = {
                    'total_groups': await sync_to_async(Group.objects.count)(),
                    'active_groups': await sync_to_async(
                        Group.objects.filter(is_active=True).count
                    )(),
                }

        return response

    async def create(self, request, *args, **kwargs):
        """
        Override create to add validation, ServiceGroup creation, and audit logging
        """
        # Validate unique code
        code = request.data.get('code', '').upper()
        if code:
            exists = await sync_to_async(
                Group.objects.filter(code=code).exists
            )()
            if exists:
                return Response(
                    {'error': f'Un groupe avec le code "{code}" existe déjà'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Extract service_ids from request data
        service_ids = request.data.pop('service_ids', [])

        # Validate service_ids if provided
        if service_ids:
            # Check if all services exist
            for service_id in service_ids:
                service_exists = await sync_to_async(
                    service.objects.filter(id=service_id).exists
                )()
                if not service_exists:
                    return Response(
                        {'error': f'Service avec ID {service_id} n\'existe pas'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Create the Group
        response = await super().create(request, *args, **kwargs)

        # If Group creation was successful and service_ids were provided
        if response.status_code == status.HTTP_201_CREATED and service_ids:
            group_id = response.data.get('id')

            # Use atomic transaction to create ServiceGroups
            @sync_to_async
            @transaction.atomic
            def create_service_groups():
                group_instance = Group.objects.get(id=group_id)
                created_count = 0

                for service_id in service_ids:
                    # Get or create to handle duplicates gracefully
                    service_instance = service.objects.get(id=service_id)
                    _, created = ServiceGroup.objects.get_or_create(
                        service=service_instance,
                        group=group_instance
                    )
                    if created:
                        created_count += 1

                return created_count

            try:
                created_count = await create_service_groups()
                response.data['service_groups_created'] = created_count
            except Exception as e:
                # Log error but don't fail the Group creation
                response.data['service_groups_error'] = str(e)

        # TODO: Add audit logging here when audit system is integrated

        return response

    async def update(self, request, *args, **kwargs):
        """
        Override update to add validation and audit logging
        """
        instance = await sync_to_async(self.get_object)()
        old_data = {
            'code': instance.code,
            'name': instance.name,
            'description': instance.description,
            'is_active': instance.is_active
        }

        response = await super().update(request, *args, **kwargs)

        # TODO: Add audit logging here when audit system is integrated

        return response

    async def destroy(self, request, *args, **kwargs):
        """
        Override destroy to prevent deletion of groups with users
        and cascade delete ServiceGroups
        """
        instance = await sync_to_async(self.get_object)()

        # Check if group has active users
        user_count = await sync_to_async(
            instance.user_groups.filter(is_active=True).count
        )()

        if user_count > 0:
            return Response(
                {
                    'error': f'Impossible de supprimer le groupe "{instance.code}". '
                            f'Il contient {user_count} utilisateur(s) actif(s).'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use atomic transaction to delete Group and cascade ServiceGroups
        @sync_to_async
        @transaction.atomic
        def delete_group_with_cascade():
            # Delete all associated ServiceGroups
            service_groups_count = instance.service_groups.count()
            instance.service_groups.all().delete()

            # Delete the Group
            instance.delete()

            return service_groups_count

        try:
            service_groups_deleted = await delete_group_with_cascade()

            # TODO: Add audit logging here when audit system is integrated

            return Response(
                {
                    'message': f'Groupe "{instance.code}" supprimé avec succès',
                    'service_groups_deleted': service_groups_deleted
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
