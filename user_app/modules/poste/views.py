from user_app.models import poste
from adrf.viewsets import ModelViewSet
from .serializers import J_posteSerializers, I_posteSerializers

class posteAPIView(ModelViewSet):
    queryset = poste.objects.all().order_by('-id')
    serializer_class_read = J_posteSerializers
    serializer_class_write = I_posteSerializers
    filterset_fields = ['service_id']
    search_fields = ["titre","service_id__titre"]
    permit_list_expands = ["service_id"]

