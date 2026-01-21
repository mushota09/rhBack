from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from adrf import routers
# from test_async_app.urls import router as test_async_app_router

router=routers.DefaultRouter()
# router.registry.extend(test_async_app_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    # path('', include('test_async_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)