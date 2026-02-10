from user_app.models import Group
from adrf.viewsets import ModelViewSet
from .serializers import J_GroupSerializers, I_GroupSerializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from utilities.auth import JWT_AUTH


class GroupViewSet(ModelViewSet):
    """
    Async ViewSet for Group management with ADRF

    Provides:
    - CRUD operations for groups
    - Pagination, filtering, and search capabilities
    - Async operations for better performance
    """
    queryset = Group.objects.all().order_by('code')
    serializer_class = J_GroupSerializers
    authentication_classes = [JWT_AUTH]
    permission_classes = [IsAuthenticated]

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
        queryset = Group.objects.all().order_by('code')

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
        Override create to add validation and audit logging
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

        response = await super().create(request, *args, **kwargs)

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

        response = await super().destroy(request, *args, **kwargs)

        # TODO: Add audit logging here when audit system is integrated

        return response
