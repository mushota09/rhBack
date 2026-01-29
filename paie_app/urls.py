
"""
URLs pour l'application paie.
"""
from django.urls import path, include
from adrf import routers
from paie_app.modules.entree_paie.views import EntreePaieAPIView
from paie_app.modules.periode_paie.views import PeriodePaieAPIView
from paie_app.modules.retenue_employe.views import RetenueEmployeAPIView

router = routers.DefaultRouter()
router.register("periode_paie", PeriodePaieAPIView, basename="periode_paie")
router.register("entree_paie", EntreePaieAPIView, basename="entree_paie")
router.register("retenue_employe", RetenueEmployeAPIView, basename="retenue_employe")

urlpatterns = [
    # Audit reports URLs
    path('audit/', include('paie_app.modules.audit_reports.urls')),
    # API router URLs
    path('', include(router.urls)),
]
