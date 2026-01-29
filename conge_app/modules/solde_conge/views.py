from conge_app.models import solde_conge
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import J_solde_congeSerializers, I_solde_congeSerializers

class solde_congeAPIView(FlexFieldsModelViewSet):
    queryset = solde_conge.objects.all().order_by('-id')
    serializer_class_read = J_solde_congeSerializers
    serializer_class_write = I_solde_congeSerializers 
    filterset_fields = [
    'employe_id',
    'employe_id__poste_id',
    'employe_id__poste_id__service_id',
    'type_conge_id'
    ]
    
    permit_list_expands = [
    'employe_id',
    'employe_id.poste_id',
    'employe_id.poste_id.service_id',
    'type_conge_id'
    ]