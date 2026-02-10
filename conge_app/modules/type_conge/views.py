from conge_app.models import type_conge
from .serializers import I_type_congeSerializers
from adrf.viewsets import ModelViewSet

class type_congeAPIView(ModelViewSet):
    queryset = type_conge.objects.all().order_by('-id')
    serializer_class = I_type_congeSerializers

