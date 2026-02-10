from conge_app.models import demande_conge
from adrf.viewsets import ModelViewSet
from .serializers import J_demande_congeSerializers, I_demande_congeSerializers

class demande_congeAPIView(ModelViewSet):
    queryset = demande_conge.objects.all().order_by('-id')
    serializer_class_read = J_demande_congeSerializers
    serializer_class_write = I_demande_congeSerializers
    filterset_fields = [
    'employe_id',
    'employe_id__poste_id',
    'employe_id__poste_id__service_id',

    'approuve_par_id',
    'approuve_par_id__poste_id',
    'approuve_par_id__poste_id__service_id',
    'type_conge_id'
    ]

    permit_list_expands = [
    'employe_id',
    'employe_id.poste_id',
    'employe_id.poste_id.service_id',

    'approuve_par_id',
    'approuve_par_id.poste_id',
    'approuve_par_id.poste_id.service_id',
    'type_conge_id'
    ]
