from user_app.models import contrat
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import J_contratSerializers,I_contratSerializers

class contratAPIView(FlexFieldsModelViewSet):
    queryset = contrat.objects.all().order_by('-id')
    serializer_class_read = J_contratSerializers
    serializer_class_write = I_contratSerializers 
    filterset_fields = ['employe_id','employe_id__poste_id','employe_id__poste_id__service_id',]
    permit_list_expands = ['employe_id','employe_id.poste_id','employe_id.poste_id.service_id']