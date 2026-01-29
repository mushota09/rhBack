from user_app.models import audit_log
from adrf_flex_fields.views import FlexFieldsModelViewSet
from .serializers import J_audit_logSerializers, I_audit_logSerializers


class audit_logAPIView(FlexFieldsModelViewSet):
    queryset = audit_log.objects.all().order_by('-id')
    serializer_class_read = J_audit_logSerializers
    serializer_class_write = I_audit_logSerializers 
    filterset_fields = ["user_id"]
    search_fields = []
    permit_list_expands = ["user_id"]