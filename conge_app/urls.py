
from adrf import routers
from django.urls import path
from conge_app.modules.type_conge.views import type_congeAPIView
from conge_app.modules.type_conge.views import type_congeAPIView
from conge_app.modules.solde_conge.views import solde_congeAPIView
from conge_app.modules.demande_conge.views import demande_congeAPIView
from conge_app.modules.historique_conge.views import historique_congeAPIView

router=routers.DefaultRouter()
router.register("type_conge",type_congeAPIView,basename="type_congeAPIView")
router.register("demande_conge",demande_congeAPIView,basename="demande_congeAPIView")
router.register("historique_conge",historique_congeAPIView,basename="historique_congeAPIView")
router.register("solde_conge",solde_congeAPIView,basename="solde_congeAPIView")

urlpatterns = []