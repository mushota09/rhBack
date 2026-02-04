# Views for permission management endpoints

from rest_framework import status
from rest_framework.response import Response
from adrf_flex_fields.views import FlexFieldsModelViewSet
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
# from user_app.modules.audit.decorators import audit_group_permission_change


class GroupPermissionViewSet(FlexFieldsModelViewSet):
    # Async ViewSet for GroupPermission management
    queryset = GroupPermission.objects.all().select_related(
        'group', 'permission', 'created_by'
    ).order_by('group__code', 'permission__resource', 'permission__action')

    serializer_class_read = GroupPermissionReadSerializer
    serializer_class_write = GroupPermissionWriteSerializer
    authentication_classes = [JWT_AUTH]
    permission_classes = [CanManagePermissions]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['group', 'permission', 'granted']
    search_fields = ['group__code', 'group__name', 'permission__name']
    ordering_fields = ['group__code', 'permission__resource', 'created_at']
    ordering = ['group__code', 'permission__resource', 'permission__action']

    permit_list_expands = ['group', 'permission', 'created_by']

    async def get_queryset(self):
        # Override to provide async queryset with optimizations
        queryset = GroupPermission.objects.select_related(
            'group', 'permission', 'created_by'
        ).order_by('group__code', 'permission__resource', 'permission__action')

        show_inactive = self.request.query_params.get('show_inactive', 'false').lower()
        if show_inactive != 'true':
            queryset = queryset.filter(group__is_active=True)

        return queryset

    # @audit_group_permission_change('CREATE')
    async def create(self, request, *args, **kwargs):
        # Override create to add cache invalidation and audit logging
        # Set the created_by field to current user
        request.data['created_by'] = request.user.id

        response = await super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            PermissionService.invalidate_all_cache()

            # Manual audit logging
            if hasattr(response, 'data') and 'id' in response.data:
                try:
                    group_permission = await GroupPermission.objects.select_related(
                        'group', 'permission'
                    ).aget(id=response.data['id'])
                    await log_group_permission_change_manual(
                        group_permission=group_permission,
                        action='CREATE',
                        request=request
                    )
                except Exception:
                    pass  # Don't fail the request if audit logging fails

        return response

    # @audit_group_permission_change('UPDATE')
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
            PermissionService.invalidate_all_cache()

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

    # @audit_group_permission_change('DELETE')
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
            PermissionService.invalidate_all_cache()

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


class PermissionViewSet(FlexFieldsModelViewSet):
    # Read-only ViewSet for Permission model
    queryset = Permission.objects.all().order_by('resource', 'action')
    serializer_class = PermissionSerializer
    authentication_classes = [JWT_AUTH]
    permission_classes = [CanManagePermissions]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['resource', 'action', 'content_type']
    search_fields = ['name', 'codename', 'resource', 'action']
    ordering_fields = ['resource', 'action', 'name', 'codename']
    ordering = ['resource', 'action']

    http_method_names = ['get', 'head', 'options']
