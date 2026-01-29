from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import I_serviceSerializers
from user_app.models import service

class serviceAPIView(FlexFieldsModelViewSet):
    queryset = service.objects.all().order_by('-id')
    serializer_class = I_serviceSerializers 
    search_fields = ["titre"]