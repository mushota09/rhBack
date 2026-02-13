from adrf.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import I_serviceSerializers
from user_app.models import service


class ServiceViewSet(ModelViewSet):
    """
    ViewSet for Service management
    """
    queryset = service.objects.all().order_by('-id')
    serializer_class = I_serviceSerializers

    # Filtering and search configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["titre"]
    filterset_fields = ['titre']
    ordering_fields = ['id', 'titre']
    ordering = ['-id']
