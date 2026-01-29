
"""
URL configuration for user_app
"""
from adrf import routers
from django.urls import path, include
from user_app.modules.user.views import (
    LoginView, ProtectedView, RefreshTokenView, userAPIView, LogoutView
)
from user_app.modules.poste.views import posteAPIView
from user_app.modules.service.views import serviceAPIView
from user_app.modules.contrat.views import contratAPIView
from user_app.modules.employe.views import employeAPIView
from user_app.modules.document.views import documentAPIView
from user_app.modules.audit_log.views import audit_logAPIView
from user_app.modules.historique_contrat.views import historique_contratAPIView

router = routers.DefaultRouter()
router.register("service", serviceAPIView, basename="serviceAPIView")
router.register("poste", posteAPIView, basename="posteAPIView")
router.register("user", userAPIView, basename="userAPIView")
router.register("audit_log", audit_logAPIView, basename="audit_logAPIView")
router.register("contrat", contratAPIView, basename="contratAPIView")
router.register("document", documentAPIView, basename="documentAPIView")
router.register("employe", employeAPIView, basename="employeAPIView")
router.register(
    "historique_contrat",
    historique_contratAPIView,
    basename="historique_contratAPIView"
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
]

