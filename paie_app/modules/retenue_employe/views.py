"""
Vues API pour les retenues employés.
"""
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from adrf_flex_fields.views import FlexFieldsModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from paie_app.models import retenue_employe
from utilities.permissions import (
    CanManageDeductions, PayrollReadPermission, PayrollWritePermission, IsEmployee
)
from utilities.decorators import audit_action
from paie_app.modules.retenue_employe.serializers import (
    RetenueEmployeSerializer,
    RetenueEmployeListSerializer,
    RetenueEmployeDeactivateSerializer,
    RetenueEmployeHistorySerializer
)


class RetenueEmployeAPIView(FlexFieldsModelViewSet):
    """API View pour la gestion des retenues employés."""

    queryset = retenue_employe.objects.all().order_by('-created_at')
    serializer_class = RetenueEmployeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'employe_id', 'type_retenue', 'est_active', 'est_recurrente'
    ]
    search_fields = [
        'employe_id__nom', 'employe_id__prenom', 'description'
    ]
    ordering_fields = [
        'created_at', 'date_debut', 'montant_mensuel'
    ]
    ordering = ['-created_at']

    # Role-based permissions
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        """
        if self.action in ['list', 'retrieve', 'history']:
            # Read operations - employees can see their own deductions, HR can see all
            permission_classes = [PayrollReadPermission]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'deactivate']:
            # Write operations - only users who can manage deductions
            permission_classes = [CanManageDeductions]
        else:
            # Default to authenticated users
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        """
        queryset = super().get_queryset()

        # If user is not staff, only show their own deductions
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            if hasattr(self.request.user, 'employe_id') and self.request.user.employe_id:
                queryset = queryset.filter(employe_id=self.request.user.employe_id)
            else:
                # User has no employee record, return empty queryset
                queryset = queryset.none()

        return queryset

    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action."""
        if self.action == 'list':
            return RetenueEmployeListSerializer
        if self.action == 'deactivate':
            return RetenueEmployeDeactivateSerializer
        if self.action == 'history':
            return RetenueEmployeHistorySerializer
        return RetenueEmployeSerializer


    async def list(self, request, *args, **kwargs):
        """Liste les retenues employés avec filtres."""
        return await super().list(request, *args, **kwargs)


    async def create(self, request, *args, **kwargs):
        """Crée une nouvelle retenue employé."""
        return await super().create(request, *args, **kwargs)


    async def retrieve(self, request, *args, **kwargs):
        """Récupère les détails d'une retenue employé."""
        return await super().retrieve(request, *args, **kwargs)

    async def perform_acreate(self, serializer):
        """Personnaliser la création pour ajouter l'utilisateur créateur.

        Implements requirement 3.1: Record type, amount, dates and bank info.
        """
        await serializer.asave(cree_par=self.request.user)

    async def update(self, request, pk=None):
        """Modifier une retenue employé.

        Implements requirement 8.3: Preserve modification history.
        """
        try:
            instance = await retenue_employe.objects.aget(pk=pk)

            # Sauvegarder l'état avant modification pour l'historique
            old_data = {
                'montant_mensuel': str(instance.montant_mensuel),
                'montant_total': (
                    str(instance.montant_total)
                    if instance.montant_total else None
                ),
                'date_debut': instance.date_debut.isoformat(),
                'date_fin': (
                    instance.date_fin.isoformat()
                    if instance.date_fin else None
                ),
                'est_active': instance.est_active,
                'description': instance.description
            }

            serializer = self.get_serializer(
                instance, data=request.data, partial=True
            )
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Mettre à jour avec historique
            updated_instance = await self._update_with_history(
                instance, serializer.validated_data, old_data, request.user
            )

            response_serializer = RetenueEmployeSerializer(updated_instance)
            return Response(response_serializer.data)

        except retenue_employe.DoesNotExist:
            return Response(
                {'error': 'Retenue non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la mise à jour: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=True, methods=['post'])
    async def deactivate(self, request, pk=None):
        """Désactiver une retenue sans la supprimer.

        Implements requirement 3.5: Allow deactivating without deleting.
        """
        try:
            retenue = await self.aget_object()

            if not retenue.est_active:
                return Response(
                    {'error': 'Cette retenue est déjà désactivée'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = RetenueEmployeDeactivateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Désactiver la retenue avec historique
            await self._deactivate_with_history(
                retenue,
                serializer.validated_data.get('raison', ''),
                request.user
            )

            return Response({
                'message': 'Retenue désactivée avec succès',
                'retenue_id': retenue.id,
                'date_desactivation': timezone.now().isoformat()
            })

        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la désactivation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=True, methods=['get'])
    async def history(self, request, pk=None):
        """Consulter l'historique complet des modifications.

        Implements requirement 8.4: Allow consulting complete operation history.
        """
        try:
            # Fetch with related objects
            retenue = await retenue_employe.objects.select_related(
                'employe_id', 'cree_par'
            ).aget(pk=pk)

            # Construire l'historique complet
            history_data = {
                'retenue_id': retenue.id,
                'employe': {
                    'id': retenue.employe_id.id,
                    'nom_complet': (
                        f"{retenue.employe_id.nom} "
                        f"{retenue.employe_id.prenom}"
                    )
                },
                'creation': {
                    'date': retenue.created_at.isoformat(),
                    'par': (
                        retenue.cree_par.email
                        if retenue.cree_par else None
                    )
                },
                'etat_actuel': {
                    'est_active': retenue.est_active,
                    'montant_mensuel': str(retenue.montant_mensuel),
                    'montant_total': (
                        str(retenue.montant_total)
                        if retenue.montant_total else None
                    ),
                    'montant_deja_deduit': str(retenue.montant_deja_deduit)
                },
                'modifications': (
                    retenue.modification_history
                    if hasattr(retenue, 'modification_history')
                    else []
                )
            }

            return Response(history_data)

        except Exception as e:
            return Response(
                {
                    'error': (
                        f'Erreur lors de la récupération de '
                        f'l\'historique: {str(e)}'
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['get'])
    async def statistics(self, request):
        """Retourne les statistiques des retenues employés.

        Implements requirement 9.1: Expose REST APIs for consultation.
        """
        try:
            total_retenues = await retenue_employe.objects.acount()
            retenues_actives = await retenue_employe.objects.filter(
                est_active=True
            ).acount()

            # Statistiques par type
            types_stats = {}
            async for retenue in retenue_employe.objects.filter(
                est_active=True
            ):
                type_retenue = retenue.type_retenue
                if type_retenue not in types_stats:
                    types_stats[type_retenue] = 0
                types_stats[type_retenue] += 1

            return Response({
                'total_retenues': total_retenues,
                'retenues_actives': retenues_actives,
                'retenues_inactives': total_retenues - retenues_actives,
                'repartition_par_type': types_stats
            })

        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def _update_with_history(self, instance, validated_data,
                                   old_data, user):
        """Mettre à jour une instance avec sauvegarde de l'historique."""
        # Créer l'entrée d'historique
        history_entry = {
            'date': timezone.now().isoformat(),
            'par': user.email,  # Use email instead of username
            'action': 'modification',
            'ancien_etat': old_data,
            'nouveau_etat': {
                'montant_mensuel': str(validated_data.get(
                    'montant_mensuel', instance.montant_mensuel)),
                'montant_total': (
                    str(validated_data.get(
                        'montant_total', instance.montant_total))
                    if validated_data.get('montant_total',
                                          instance.montant_total) else None
                ),
                'date_debut': validated_data.get(
                    'date_debut', instance.date_debut).isoformat(),
                'date_fin': (
                    validated_data.get(
                        'date_fin', instance.date_fin).isoformat()
                    if validated_data.get('date_fin', instance.date_fin)
                    else None
                ),
                'est_active': validated_data.get(
                    'est_active', instance.est_active),
                'description': validated_data.get(
                    'description', instance.description)
            }
        }

        # Mettre à jour l'historique
        if (not hasattr(instance, 'modification_history') or
                instance.modification_history is None):
            instance.modification_history = []
        instance.modification_history.append(history_entry)

        # Appliquer les modifications
        for field, value in validated_data.items():
            setattr(instance, field, value)

        await instance.asave()
        return instance

    async def _deactivate_with_history(self, instance, raison, user):
        """Désactiver une retenue avec sauvegarde de l'historique."""
        # Créer l'entrée d'historique
        history_entry = {
            'date': timezone.now().isoformat(),
            'par': user.email,  # Use email instead of username
            'action': 'desactivation',
            'raison': raison,
            'ancien_etat': {'est_active': True},
            'nouveau_etat': {'est_active': False}
        }

        # Mettre à jour l'historique
        if (not hasattr(instance, 'modification_history') or
                instance.modification_history is None):
            instance.modification_history = []
        instance.modification_history.append(history_entry)

        # Désactiver
        instance.est_active = False
        await instance.asave()
