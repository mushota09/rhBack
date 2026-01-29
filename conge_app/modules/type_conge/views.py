from conge_app.models import type_conge
from .serializers import I_type_congeSerializers
from adrf_flex_fields.views import FlexFieldsModelViewSet

class type_congeAPIView(FlexFieldsModelViewSet):
    queryset = type_conge.objects.all().order_by('-id')
    serializer_class = I_type_congeSerializers 

  