from user_app.models import UserGroup, User, Group
from adrf.viewsets import ModelViewSet
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


class UserGroupViewSet(ModelViewSet):
    """
    Async ViewSet for UserGroup management with ADRF

    Provides:
    - CRUD operations for user-group assignments
    - Bulk assignment/removal operations
    - Validation for group existence and user permissions
    - Async operations for better performance
    """
    queryset = UserGroup.objects.all().order_by('-assigned_at')
    serializer_class = J_UserGroupSerializers
    # authentication_classes = [JWT_AUTH]
    # permission_classes = [IsAuthenticated]

    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user', 'group', 'is_active', 'assigned_by']
    search_fields = ['user__email', 'user__nom', 'user__prenom', 'group__name', 'group__code']
    ordering_fields = ['assigned_at', 'user__email', 'group__code']
    ordering = ['-assigned_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return I_UserGroupSerializers
        return J_UserGroupSerializers

    def get_queryset(self):
        """
        Override to provide queryset with optimizations
        """
        queryset = UserGroup.objects.select_related(
            'user', 'group', 'assigned_by'
        ).order_by('-assigned_at')

        # Apply active filter by default if not specified
        is_active = self.request.query_params.get('is_active')
        if is_active is None:
            queryset = queryset.filter(is_active=True)

        return queryset

    async def acreate(self, request, *args, **kwargs):
        """
        Override acreate to manually handle ADRF serializer data loss issue

        WORKAROUND: ADRF AsyncModelSerializer doesn't properly pass ForeignKey
        fields through validated_data. We extract them manually from request.data.
        """
        # Get serializer and validate
        serializer = self.get_serializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        # WORKAROUND: Extract ForeignKey fields manually from request.data
        # because ADRF doesn't pass them through validated_data
        user_id = request.data.get('user')
        group_id = request.data.get('group')
        assigned_by_id = request.data.get('assigned_by')

        # Validate required fields
        if not user_id:
            return Response(
                {'user': ['Ce champ est requis.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not group_id:
            return Response(
                {'group': ['Ce champ est requis.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get related objects
        try:
            user = await User.objects.aget(id=user_id)
            group = await Group.objects.aget(id=group_id)
            assigned_by = await User.objects.aget(id=assigned_by_id) if assigned_by_id else request.user
        except User.DoesNotExist:
            return Response(
                {'error': 'Utilisateur introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Group.DoesNotExist:
            return Response(
                {'error': 'Groupe introuvable'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is active
        if not user.is_active:
            return Response(
                {'error': "Impossible d'assigner un utilisateur inactif à un groupe"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if group is active
        if not group.is_active:
            return Response(
                {'error': "Impossible d'assigner un utilisateur à un groupe inactif"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicate assignment
        existing = await sync_to_async(
            UserGroup.objects.filter(
                user=user,
                group=group,
                is_active=True
            ).exists
        )()

        if existing:
            return Response(
                {'error': f"L'utilisateur {user.email} est déjà assigné au groupe {group.code}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the UserGroup instance directly
        user_group = await sync_to_async(UserGroup.objects.create)(
            user=user,
            group=group,
            assigned_by=assigned_by,
            is_active=True
        )

        # Serialize the response
        response_serializer = J_UserGroupSerializers(user_group)
        response_data = await sync_to_async(lambda: response_serializer.data)()

        # Manual audit logging
        try:
            await log_user_group_assignment_manual(
                user_group=user_group,
                action='CREATE',
                request=request
            )
        except Exception:
            pass  # Don't fail the request if audit logging fails

        return Response(response_data, status=status.HTTP_201_CREATED)

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
