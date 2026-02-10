"""
Vues API pour les entrées de paie.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from adrf.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from paie_app.models import entree_paie
from paie_app.services import SalaryCalculatorService, PayslipGeneratorService
from utilities.permissions import (
    IsEmployee, PayrollReadPermission, PayrollWritePermission
)
from paie_app.modules.entree_paie.serializers import (
    EntreePaieSerializer,
    EntreePaieListSerializer,
    EntreePaieRecalculateSerializer,
    PayslipGenerationSerializer
)


class EntreePaieAPIView(ModelViewSet):
    """API View pour la gestion des entrées de paie."""

    queryset = entree_paie.objects.all().order_by('-created_at')
    serializer_class = EntreePaieSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'periode_paie_id', 'employe_id', 'calculated_at',
        'payslip_generated', 'validated_at'
    ]
    search_fields = [
        'employe_id__nom', 'employe_id__prenom', 'employe_id__email_personnel'
    ]
    ordering_fields = [
        'created_at', 'calculated_at', 'salaire_base',
        'salaire_brut', 'salaire_net'
    ]
    ordering = ['-created_at']

    # Role-based permissions
    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.salary_calculator = SalaryCalculatorService()
        self.payslip_generator = PayslipGeneratorService()

    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        """
        if self.action in ['list', 'retrieve']:
            # Read operations - employees can see their own data, HR can see all
            permission_classes = [PayrollReadPermission]
        elif self.action in ['update', 'partial_update']:
            # Write operations - only HR admins
            permission_classes = [PayrollWritePermission]
        elif self.action in ['recalculate', 'generate_payslip']:
            # Processing operations - only HR staff
            permission_classes = [PayrollWritePermission]
        elif self.action == 'download_payslip':
            # Download operations - employees can download their own, HR can download all
            permission_classes = [IsEmployee]
        else:
            # Default to authenticated users
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        """
        queryset = super().get_queryset()

        # If user is not staff, only show their own payroll entries
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
            return EntreePaieListSerializer
        if self.action == 'recalculate':
            return EntreePaieRecalculateSerializer
        if self.action in ['generate_payslip', 'regenerate_payslip']:
            return PayslipGenerationSerializer
        return EntreePaieSerializer

    async def list(self, request, *args, **kwargs):
        """Liste les entrées de paie avec filtres."""
        return await super().list(request, *args, **kwargs)

    async def retrieve(self, request, *args, **kwargs):
        """Récupère les détails d'une entrée de paie."""
        return await super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    async def statistics(self, request):
        """Retourne les statistiques des entrées de paie."""
        try:
            # Compter les entrées par statut
            total_entrees = await entree_paie.objects.acount()
            entrees_calculees = await entree_paie.objects.filter(
                calculated_at__isnull=False
            ).acount()
            entrees_validees = await entree_paie.objects.filter(
                validated_at__isnull=False
            ).acount()
            bulletins_generes = await entree_paie.objects.filter(
                payslip_generated=True
            ).acount()

            # Calculer les totaux
            from decimal import Decimal
            total_salaire_brut = Decimal('0')
            total_salaire_net = Decimal('0')

            async for entree in entree_paie.objects.all():
                if entree.salaire_brut:
                    total_salaire_brut += entree.salaire_brut
                if entree.salaire_net:
                    total_salaire_net += entree.salaire_net

            return Response({
                'total_entrees': total_entrees,
                'entrees_calculees': entrees_calculees,
                'entrees_validees': entrees_validees,
                'bulletins_generes': bulletins_generes,
                'total_salaire_brut': total_salaire_brut,
                'total_salaire_net': total_salaire_net,
                'taux_validation': (entrees_validees / total_entrees * 100) if total_entrees > 0 else 0,
                'taux_generation_bulletins': (bulletins_generes / total_entrees * 100) if total_entrees > 0 else 0
            })

        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
