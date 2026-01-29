from user_app.models import historique_contrat
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import J_historique_contratSerializers, I_historique_contratSerializers

class historique_contratAPIView(FlexFieldsModelViewSet):
    queryset = historique_contrat.objects.all().order_by('-id')
    serializer_class_read = J_historique_contratSerializers
    serializer_class_write = I_historique_contratSerializers 
    filterset_fields = ['contrat_id',
    'contrat_id__employe_id',
    'contrat_id__employe_id__poste_id',
    'contrat_id__employe_id__poste_id__service_id',
    'contrat_id__employe_id__responsable_id',]
    search_fields = []
    permit_list_expands = [
    'contrat_id',
    'contrat_id.employe_id',
    'contrat_id.employe_id.poste_id',
    'contrat_id.employe_id.poste_id.service_id',
    'contrat_id.employe_id.responsable_id',
    'contrat_id.employe_id.responsable_id.poste_id',
    'contrat_id.employe_id.responsable_id.poste_id.service_id',
    ]

  