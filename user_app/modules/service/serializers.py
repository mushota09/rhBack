from user_app.models import service
from adrf_flex_fields import FlexFieldsModelSerializer

class I_serviceSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=service
        fields="__all__"