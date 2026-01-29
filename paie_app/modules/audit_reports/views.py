"""
Vues API pour les rapports d'audit du système de paie.
"""
from datetime import datetime
from adrf.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from paie_app.services.audit_reports_service import AuditReportsService
from utilities.permissions import CanViewAuditLogs


class AuditReportsAPIView(APIView):
    """API pour les rapports d'audit du système de paie"""

    permission_classes = [CanViewAuditLogs]

    def __init__(self):
        super().__init__()
        self.audit_service = AuditReportsService()

    @extend_schema(
        summary="Générer des rapports d'audit",
        description="Génère différents types de rapports d'audit selon les paramètres",
        tags=["Rapports d'Audit"],
        parameters=[
            OpenApiParameter(
                name='report_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Type de rapport: period, employee, global',
                enum=['period', 'employee', 'global']
            ),
            OpenApiParameter(
                name='periode_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='ID de la période (requis pour report_type=period)'
            ),
            OpenApiParameter(
                name='employe_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='ID de l\'employé (requis pour report_type=employee)'
            ),
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date de début (format YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Date de fin (format YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='annee',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Année (pour report_type=global)'
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Rapport d'audit généré",
                examples=[
                    OpenApiExample(
                        "Rapport de période",
                        value={
                            "periode": {
                                "id": 123,
                                "annee": 2024,
                                "mois": 3,
                                "statut": "APPROVED"
                            },
                            "statistiques": {
                                "total_employes": 25,
                                "masse_salariale": "1250000.00"
                            },
                            "operations": [
                                {
                                    "date": "2024-03-15T10:30:00Z",
                                    "action": "PROCESS",
                                    "utilisateur": "admin@company.com"
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Paramètres manquants ou invalides"),
            404: OpenApiResponse(description="Ressource non trouvée")
        }
    )
    async def get(self, request):
        """
        Récupère différents types de rapports d'audit.
        """
        try:
            report_type = request.query_params.get('report_type')

            if not report_type:
                return Response(
                    {'error': 'Le paramètre report_type est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if report_type == 'period':
                return await self._handle_period_report(request)
            if report_type == 'employee':
                return await self._handle_employee_report(request)
            if report_type == 'global':
                return await self._handle_global_report(request)

            return Response(
                {'error': f'Type de rapport non supporté: {report_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def _handle_period_report(self, request) -> Response:
        """Gère la génération d'un rapport de période."""
        periode_id = request.query_params.get('periode_id')

        if not periode_id:
            return Response(
                {'error': 'Le paramètre periode_id est requis pour un rapport de période'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            periode_id = int(periode_id)
            report = self.audit_service.generate_period_report(periode_id)
            return Response(report, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport de période: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def _handle_employee_report(self, request) -> Response:
        """Gère la génération d'un rapport d'employé."""
        employe_id = request.query_params.get('employe_id')

        if not employe_id:
            return Response(
                {'error': 'Le paramètre employe_id est requis pour un rapport d\'employé'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employe_id = int(employe_id)

            # Récupérer les dates optionnelles
            start_date = None
            end_date = None

            start_date_str = request.query_params.get('start_date')
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

            end_date_str = request.query_params.get('end_date')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            report = self.audit_service.generate_employee_history_report(
                employe_id, start_date, end_date
            )
            return Response(report, status=status.HTTP_200_OK)

        except ValueError as e:
            if 'Employé' in str(e):
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport d\'employé: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def _handle_global_report(self, request) -> Response:
        """Gère la génération d'un rapport global."""
        try:
            annee = request.query_params.get('annee')
            if annee:
                annee = int(annee)
            else:
                annee = datetime.now().year

            report = self.audit_service.generate_global_statistics_report(annee)
            return Response(report, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {'error': 'Format d\'année invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport global: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PeriodAuditReportView(APIView):
    """Vue spécialisée pour les rapports d'audit de période"""

    permission_classes = [IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.audit_service = AuditReportsService()

    async def get(self, request, periode_id: int):
        """Récupère le rapport d'audit pour une période spécifique."""
        try:
            report = self.audit_service.generate_period_report(periode_id)
            return Response(report, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmployeeAuditReportView(APIView):
    """Vue spécialisée pour les rapports d'audit d'employé"""

    permission_classes = [IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.audit_service = AuditReportsService()

    async def get(self, request, employe_id: int):
        """Récupère le rapport d'audit pour un employé spécifique."""
        try:
            # Récupérer les dates optionnelles
            start_date = None
            end_date = None

            start_date_str = request.query_params.get('start_date')
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

            end_date_str = request.query_params.get('end_date')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            report = self.audit_service.generate_employee_history_report(
                employe_id, start_date, end_date
            )
            return Response(report, status=status.HTTP_200_OK)

        except ValueError as e:
            if 'Employé' in str(e):
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                return Response(
                    {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GlobalStatisticsReportView(APIView):
    """Vue spécialisée pour les rapports de statistiques globales"""

    permission_classes = [IsAuthenticated]

    def __init__(self):
        super().__init__()
        self.audit_service = AuditReportsService()

    async def get(self, request):
        """Récupère les statistiques globales."""
        try:
            annee = request.query_params.get('annee')
            if annee:
                annee = int(annee)
            else:
                annee = datetime.now().year

            report = self.audit_service.generate_global_statistics_report(annee)
            return Response(report, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {'error': 'Format d\'année invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la génération du rapport: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
