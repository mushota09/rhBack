from adrf import routers
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from user_app.urls import router as user_app_router

router=routers.DefaultRouter()
router.registry.extend(user_app_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('', include('user_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)