from conge_app.models import historique_conge
from adrf.viewsets import ModelViewSet
from .serializers import J_historique_congeSerializers,I_historique_congeSerializers

class historique_congeAPIView(ModelViewSet):
    queryset = historique_conge.objects.all().order_by('-id')
    serializer_class_read = J_historique_congeSerializers
    serializer_class_write = I_historique_congeSerializers
    filterset_fields = [
    'demande_conge_id',
    'demande_conge_id__employe_id',
    'demande_conge_id__employe_id__poste_id',
    'demande_conge_id__employe_id__poste_id__service_id',
    'poste_valideur_id',
    'poste_valideur_id__service_id',
    ]

    permit_list_expands = [
    'demande_conge_id',
    'demande_conge_id.employe_id',
    'demande_conge_id.employe_id.poste_id',
    'demande_conge_id.employe_id.poste_id.service_id',

    'poste_valideur_id',
    'poste_valideur_id.service_id',
    ]
