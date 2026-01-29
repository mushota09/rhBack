from conge_app.models import type_conge
from adrf_flex_fields import FlexFieldsModelSerializer

class I_type_congeSerializers(FlexFieldsModelSerializer):
    class Meta:
        model=type_conge
        fields="__all__"