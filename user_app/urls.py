
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

router = routers.DefaultRouter()
# Register all user management ViewSets
router.register("group", GroupViewSet, basename="GroupViewSet")
router.register("user-group", UserGroupViewSet, basename="UserGroupViewSet")
router.register("group-permission", GroupPermissionViewSet,
                basename="GroupPermissionViewSet")
router.register("permission", PermissionViewSet, basename="PermissionViewSet")

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    # Include router URLs
    path('', include(router.urls)),
]

