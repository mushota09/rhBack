from adrf import routers
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from user_app.urls import router as user_app_router
from paie_app.urls import router as paie_app_router
from conge_app.urls import router as conge_app_router

router = routers.DefaultRouter()
router.registry.extend(user_app_router.registry)
router.registry.extend(paie_app_router.registry)
router.registry.extend(conge_app_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Routes
    path('api/', include(router.urls)),
    path('api/user/', include('user_app.urls')),
    path('api/paie/', include('paie_app.urls')),
    path('api/conge/', include('conge_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
