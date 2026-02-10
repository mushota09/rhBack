
"""
URL configuration for user_app
"""
from adrf import routers
from django.urls import path, include
from user_app.modules.user.views import (
    LoginView, ProtectedView, RefreshTokenView, userAPIView, LogoutView
)
from user_app.modules.group.views import GroupViewSet
from user_app.modules.user_group.views import UserGroupViewSet
from user_app.modules.permission.views import (
    GroupPermissionViewSet, PermissionViewSet
)
from user_app.modules.employe.views import employeAPIView
from user_app.modules.contrat.views import contratAPIView
from user_app.modules.document.views import documentAPIView

router = routers.DefaultRouter()
# Register all user management ViewSets
router.register("group", GroupViewSet, basename="GroupViewSet")
router.register("user-group", UserGroupViewSet, basename="UserGroupViewSet")
router.register("group-permission", GroupPermissionViewSet,
                basename="GroupPermissionViewSet")
router.register("permission", PermissionViewSet, basename="PermissionViewSet")

# Register HR management ViewSets
router.register("employees", employeAPIView, basename="employeAPIView")
router.register("contracts", contratAPIView, basename="contratAPIView")
router.register("documents", documentAPIView, basename="documentAPIView")

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    # Include router URLs
    path('', include(router.urls)),
]

