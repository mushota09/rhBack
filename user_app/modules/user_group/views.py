from user_app.models import UserGroup, User, Group
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import (
    J_UserGroupSerializers,
    I_UserGroupSerializers,
    UserGroupBulkSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from asgiref.sync import sync_to_async
from django.db import transaction
from utilities.auth import JWT_AUTH
from user_app.modules.audit.utils import (
    log_user_group_assignment_manual,
    log_bulk_operation_manual
)
# from user_app.modules.audit.decorators import audit_user_group_assignment, audit_bulk_operation
# from user_app.modules.audit.services import UserManagementAuditService


class UserGroupViewSet(FlexFieldsModelViewSet):
    """
    Async ViewSet for UserGroup management with ADRF and flex_fields support

    Provides:
    - CRUD operations for user-group assignments
    - Bulk assignment/removal operations
    - Validation for group existence and user permissions
    - Async operations for better performance
    """
    queryset = UserGroup.objects.all().order_by('-assigned_at')
    serializer_class_read = J_UserGroupSerializers
    serializer_class_write = I_UserGroupSerializers
    authentication_classes = [JWT_AUTH]
    permission_classes = [IsAuthenticated]

    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'group', 'is_active', 'assigned_by']
    search_fields = ['user__email', 'user__nom', 'user__prenom', 'group__name', 'group__code']
    ordering_fields = ['assigned_at', 'user__email', 'group__code']
    ordering = ['-assigned_at']

    # Flex fields configuration
    permit_list_expands = ['user', 'group', 'assigned_by']

    async def get_queryset(self):
        """
        Override to provide async queryset with optimizations
        """
        queryset = UserGroup.objects.select_related(
            'user', 'group', 'assigned_by'
        ).order_by('-assigned_at')

        # Apply active filter by default if not specified
        is_active = self.request.query_params.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)

        return queryset

    # @audit_user_group_assignment('CREATE')
    async def create(self, request, *args, **kwargs):
        """
        Override create to add assigned_by and audit logging
        """
        # Set the assigned_by field to current user
        request.data['assigned_by'] = request.user.id

        response = await super().create(request, *args, **kwargs)

        # Manual audit logging
        if (response.status_code == status.HTTP_201_CREATED and
            hasattr(response, 'data') and 'id' in response.data):
            try:
                user_group = await UserGroup.objects.select_related('user', 'group').aget(
                    id=response.data['id']
                )
                await log_user_group_assignment_manual(
                    user_group=user_group,
                    action='CREATE',
                    request=request
                )
            except Exception:
                pass  # Don't fail the request if audit logging fails

        return response

    # @audit_user_group_assignment('UPDATE')
    async def update(self, request, *args, **kwargs):
        """
        Override update to add audit logging
        """
        instance = await sync_to_async(self.get_object)()
        old_data = {
            'user_id': instance.user.id,
            'user_email': instance.user.email,
            'group_id': instance.group.id,
            'group_code': instance.group.code,
            'group_name': instance.group.name,
            'is_active': instance.is_active
        }

        response = await super().update(request, *args, **kwargs)

        # Manual audit logging
        if response.status_code == status.HTTP_200_OK:
            try:
                # Refresh instance to get updated values
                await sync_to_async(instance.refresh_from_db)()
                new_data = {
                    'user_id': instance.user.id,
                    'user_email': instance.user.email,
                    'group_id': instance.group.id,
                    'group_code': instance.group.code,
                    'group_name': instance.group.name,
                    'is_active': instance.is_active
                }
                await log_user_group_assignment_manual(
                    user_group=instance,
                    action='UPDATE',
                    request=request,
                    old_values=old_data,
                    new_values=new_data
                )
            except Exception:
                pass  # Don't fail the request if audit logging fails

        return response

    # @audit_user_group_assignment('DELETE')
    async def destroy(self, request, *args, **kwargs):
        """
        Override destroy to add audit logging
        """
        instance = await sync_to_async(self.get_object)()
        old_data = {
            'user_id': instance.user.id,
            'user_email': instance.user.email,
            'group_id': instance.group.id,
            'group_code': instance.group.code,
            'group_name': instance.group.name,
            'is_active': instance.is_active
        }

        response = await super().destroy(request, *args, **kwargs)

        # Manual audit logging
        if response.status_code == status.HTTP_204_NO_CONTENT:
            try:
                await log_user_group_assignment_manual(
                    user_group=instance,
                    action='DELETE',
                    request=request,
                    old_values=old_data
                )
            except Exception:
                pass  # Don't fail the request if audit logging fails

        return response

    # @audit_bulk_operation('user_group_assignment')
    @action(detail=False, methods=['post'], url_path='bulk-assign')
    async def bulk_assign(self, request):
        """
        Bulk assign users to a group
        """
        serializer = UserGroupBulkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user_ids = serializer.validated_data['user_ids']
        group_id = serializer.validated_data['group_id']
        action_type = serializer.validated_data['action']

        try:
            # Get group and users
            group = await sync_to_async(Group.objects.get)(id=group_id)
            users = [
                user async for user in User.objects.filter(id__in=user_ids)
            ]

            results = []
            audit_assignments = []

            if action_type == 'assign':
                # Bulk assign users to group
                for user in users:
                    # Check if assignment already exists
                    existing = await sync_to_async(
                        UserGroup.objects.filter(
                            user=user, group=group, is_active=True
                        ).exists
                    )()

                    if not existing:
                        assignment = await sync_to_async(UserGroup.objects.create)(
                            user=user,
                            group=group,
                            assigned_by=request.user,
                            is_active=True
                        )
                        results.append({
                            'user_id': user.id,
                            'user_email': user.email,
                            'status': 'assigned',
                            'assignment_id': assignment.id
                        })
                        audit_assignments.append(assignment)
                    else:
                        results.append({
                            'user_id': user.id,
                            'user_email': user.email,
                            'status': 'already_assigned'
                        })

            elif action_type == 'remove':
                # Bulk remove users from group
                for user in users:
                    # Get existing assignment for audit logging
                    try:
                        assignment = await sync_to_async(
                            UserGroup.objects.get
                        )(user=user, group=group, is_active=True)

                        updated = await sync_to_async(
                            UserGroup.objects.filter(
                                user=user, group=group, is_active=True
                            ).update
                        )(is_active=False)

                        if updated:
                            results.append({
                                'user_id': user.id,
                                'user_email': user.email,
                                'status': 'removed'
                            })
                            # Refresh assignment for audit
                            await sync_to_async(assignment.refresh_from_db)()
                            audit_assignments.append(assignment)
                        else:
                            results.append({
                                'user_id': user.id,
                                'user_email': user.email,
                                'status': 'not_assigned'
                            })
                    except UserGroup.DoesNotExist:
                        results.append({
                            'user_id': user.id,
                            'user_email': user.email,
                            'status': 'not_assigned'
                        })

            # Log individual assignments for audit trail
            if audit_assignments:
                audit_action = 'CREATE' if action_type == 'assign' else 'UPDATE'
                # Manual audit logging for bulk operations
                try:
                    for assignment in audit_assignments:
                        await log_user_group_assignment_manual(
                            user_group=assignment,
                            action=audit_action,
                            request=request
                        )

                    # Log bulk operation summary
                    bulk_summary = {
                        'operation_type': 'user_group_assignment',
                        'action': action_type,
                        'group_id': group.id,
                        'group_code': group.code,
                        'total_users': len(user_ids),
                        'processed': len(results),
                        'successful': len([r for r in results if r['status'] in ['assigned', 'removed']]),
                        'failed': len([r for r in results if r['status'] in ['already_assigned', 'not_assigned']])
                    }
                    await log_bulk_operation_manual(
                        operation_type='user_group_assignment',
                        request=request,
                        summary_data=bulk_summary
                    )
                except Exception:
                    pass  # Don't fail the request if audit logging fails

            return Response({
                'message': f'Opération {action_type} terminée',
                'group': {
                    'id': group.id,
                    'code': group.code,
                    'name': group.name
                },
                'results': results,
                'summary': {
                    'total_users': len(user_ids),
                    'processed': len(results),
                    'successful': len([r for r in results if r['status'] in ['assigned', 'removed']]),
                    'failed': len([r for r in results if r['status'] in ['already_assigned', 'not_assigned']])
                }
            })

        except Group.DoesNotExist:
            return Response(
                {'error': f'Groupe avec l\'ID {group_id} introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de l\'opération: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    async def by_user(self, request, user_id=None):
        """
        Get all group assignments for a specific user
        """
        try:
            user = await sync_to_async(User.objects.get)(id=user_id)
            assignments = [
                assignment async for assignment in UserGroup.objects.filter(
                    user=user, is_active=True
                ).select_related('group')
            ]

            serializer = J_UserGroupSerializers(assignments, many=True)
            return Response({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nom': user.nom,
                    'prenom': user.prenom
                },
                'assignments': serializer.data,
                'total_groups': len(assignments)
            })

        except User.DoesNotExist:
            return Response(
                {'error': f'Utilisateur avec l\'ID {user_id} introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='by-group/(?P<group_id>[^/.]+)')
    async def by_group(self, request, group_id=None):
        """
        Get all user assignments for a specific group
        """
        try:
            group = await sync_to_async(Group.objects.get)(id=group_id)
            assignments = [
                assignment async for assignment in UserGroup.objects.filter(
                    group=group, is_active=True
                ).select_related('user')
            ]

            serializer = J_UserGroupSerializers(assignments, many=True)
            return Response({
                'group': {
                    'id': group.id,
                    'code': group.code,
                    'name': group.name,
                    'description': group.description
                },
                'assignments': serializer.data,
                'total_users': len(assignments)
            })

        except Group.DoesNotExist:
            return Response(
                {'error': f'Groupe avec l\'ID {group_id} introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
