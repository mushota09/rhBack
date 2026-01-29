"""
URLs pour les rapports d'audit.
"""
from django.urls import path
from .views import (
    AuditReportsAPIView,
    PeriodAuditReportView,
    EmployeeAuditReportView,
    GlobalStatisticsReportView
)

urlpatterns = [
    # API générale pour tous les types de rapports
    path('reports/', AuditReportsAPIView.as_view(), name='audit-reports'),

    # APIs spécialisées
    path('reports/period/<int:periode_id>/', PeriodAuditReportView.as_view(), name='period-audit-report'),
    path('reports/employee/<int:employe_id>/', EmployeeAuditReportView.as_view(), name='employee-audit-report'),
    path('reports/global/', GlobalStatisticsReportView.as_view(), name='global-statistics-report'),
]
