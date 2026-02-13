"""
URL configuration for ServiceGroup module
"""
from adrf import routers
from .views import ServiceGroupViewSet

router = routers.DefaultRouter()
router.register('service-group', ServiceGroupViewSet, basename='ServiceGroupViewSet')

urlpatterns = router.urls
