from user_app.models import document as document
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import J_documentSerializers, I_documentSerializers

class documentAPIView(FlexFieldsModelViewSet):
    queryset = document.objects.all().order_by('-id')
    serializer_class_read = J_documentSerializers
    serializer_class_write = I_documentSerializers 
    filterset_fields = ['employe_id',"employe_id__poste_id","employe_id__poste_id__service_id"]
    search_fields = []
    permit_list_expands = ["employe_id","employe_id.poste_id","employe_id.poste_id.service_id"]

  