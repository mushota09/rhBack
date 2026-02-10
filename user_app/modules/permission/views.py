# Views for permission management endpoints

from rest_framework import status
from rest_framework.response import Response
from adrf.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from asgiref.sync import sync_to_async

from user_app.models import GroupPermission, Permission
from utilities.auth import JWT_AUTH
from .serializers import (
    GroupPermissionReadSerializer,
    GroupPermissionWriteSerializer,
    PermissionSerializer
)
from .permissions import CanManagePermissions
from .services import PermissionService
from user_app.modules.audit.utils import log_group_permission_change_manual


class GroupPermissionViewSet(ModelViewSet):
    """
    Async ViewSet for GroupPermission management
    """
    queryset = GroupPermission.objects.all().select_related(
        'group', 'permission', 'created_by'
    ).order_by('group__code', 'permission__resource', 'permission__action')

    serializer_class = GroupPermissionReadSerializer
    # authentication_classes = [JWT_AUTH]
    # permission_classes = [CanManagePermissions]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group', 'permission', 'granted']
    search_fields = ['group__code', 'group__name', 'permission__name']
    ordering_fields = ['group__code', 'permission__resource', 'created_at']
    ordering = ['group__code', 'permission__resource', 'permission__action']

    def get_queryset(self):
        # Override to provide queryset with optimizations
        queryset = GroupPermission.objects.select_related(
            'group', 'permission', 'created_by'
        ).order_by('group__code', 'permission__resource', 'permission__action')

        show_inactive = self.request.query_params.get('show_inactive', 'false').lower()
        if show_inactive != 'true':
            queryset = queryset.filter(group__is_active=True)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update', 'aupdate', 'partial_aupdate']:
            return GroupPermissionWriteSerializer
        return GroupPermissionReadSerializer

    async def acreate(self, request, *args, **kwargs):
        """
        Override acreate to manually handle ADRF serializer issues

        WORKAROUND: Similar to UserGroupViewSet, we manually extract and validate
        fields because ADRF doesn't properly handle ForeignKey fields.
        """
        # Get and validate serializer
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # Extract ForeignKey fields manually
        group_id = request.data.get('group')
        permission_id = request.data.get('permission')
        granted = request.data.get('granted', True)
        created_by_id = request.data.get('created_by', request.user.id)

        # Validate required fields
        if not group_id:
            return Response(
                {'group': ['Ce champ est requis.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not permission_id:
            return Response(
                {'permission': ['Ce champ est requis.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get related objects
        try:
            from user_app.models import Group
            group = await Group.objects.aget(id=group_id)
            permission = await Permission.objects.aget(id=permission_id)
            from user_app.models import User
            created_by = await User.objects.aget(id=created_by_id) if created_by_id else request.user
        except Group.DoesNotExist:
            return Response(
                {'error': 'Groupe introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Permission.DoesNotExist:
            return Response(
                {'error': 'Permission introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Utilisateur introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicate
        existing = await sync_to_async(
            GroupPermission.objects.filter(
                group=group,
                permission=permission
            ).exists
        )()

        if existing:
            return Response(
                {'error': f"La permission {permission.codename} est déjà assignée au groupe {group.code}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the GroupPermission instance directly
        group_permission = await sync_to_async(GroupPermission.objects.create)(
            group=group,
            permission=permission,
            granted=granted,
            created_by=created_by
        )

        # Serialize the response
        response_serializer = GroupPermissionReadSerializer(group_permission)
        response_data = await sync_to_async(lambda: response_serializer.data)()

        # Invalidate cache
        try:
            PermissionService.invalidate_all_cache()
        except Exception:
            pass  # Don't fail if cache invalidation fails

        # Manual audit logging
        try:
            await log_group_permission_change_manual(
                group_permission=group_permission,
                action='CREATE',
                request=request
            )
        except Exception:
            pass  # Don't fail the request if audit logging fails

        return Response(response_data, status=status.HTTP_201_CREATED)

    async def update(self, request, *args, **kwargs):
        # Override update to add cache invalidation and audit logging
        instance = await sync_to_async(self.get_object)()
        old_data = {
            'group_id': instance.group.id,
            'group_code': instance.group.code,
            'group_name': instance.group.name,
            'permission_id': instance.permission.id,
            'permission_codename': instance.permission.codename,
            'permission_name': instance.permission.name,
            'permission_resource': instance.permission.resource,
            'permission_action': instance.permission.action,
            'granted': instance.granted
        }

        response = await super().update(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            try:
                PermissionService.invalidate_all_cache()
            except Exception:
                pass  # Don't fail if cache invalidation fails

            # Manual audit logging
            try:
                # Refresh instance to get updated values
                await sync_to_async(instance.refresh_from_db)()
                new_data = {
                    'group_id': instance.group.id,
                    'group_code': instance.group.code,
                    'group_name': instance.group.name,
                    'permission_id': instance.permission.id,
                    'permission_codename': instance.permission.codename,
                    'permission_name': instance.permission.name,
                    'permission_resource': instance.permission.resource,
                    'permission_action': instance.permission.action,
                    'granted': instance.granted
                }
                await log_group_permission_change_manual(
                    group_permission=instance,
                    action='UPDATE',
                    request=request,
                    old_values=old_data,
                    new_values=new_data
                )
            except Exception:
                pass  # Don't fail the request if audit logging fails

        return response

    async def destroy(self, request, *args, **kwargs):
        # Override destroy to add cache invalidation and audit logging
        instance = await sync_to_async(self.get_object)()
        old_data = {
            'group_id': instance.group.id,
            'group_code': instance.group.code,
            'group_name': instance.group.name,
            'permission_id': instance.permission.id,
            'permission_codename': instance.permission.codename,
            'permission_name': instance.permission.name,
            'permission_resource': instance.permission.resource,
            'permission_action': instance.permission.action,
            'granted': instance.granted
        }

        response = await super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            try:
                PermissionService.invalidate_all_cache()
            except Exception:
                pass  # Don't fail if cache invalidation fails

            # Manual audit logging
            try:
                await log_group_permission_change_manual(
                    group_permission=instance,
                    action='DELETE',
                    request=request,
                    old_values=old_data
                )
            except Exception:
                pass  # Don't fail the request if audit logging fails

        return response


class PermissionViewSet(ModelViewSet):
    """
    Read-only ViewSet for Permission model
    """
    queryset = Permission.objects.all().order_by('resource', 'action')
    serializer_class = PermissionSerializer
    # authentication_classes = [JWT_AUTH]
    # permission_classes = [CanManagePermissions]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['resource', 'action', 'content_type']
    search_fields = ['name', 'codename', 'resource', 'action']
    ordering_fields = ['resource', 'action', 'name', 'codename']
    ordering = ['resource', 'action']

    # Read-only ViewSet - only allow list and retrieve
    http_method_names = ['get', 'head', 'options']
