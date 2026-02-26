from django.urls import include, path
from rest_framework.routers import DefaultRouter
from labs.views import LabPublicViewSet, LabSectionPublicViewSet, LabTaskPublicViewSet

router = DefaultRouter()
router.register("labs", LabPublicViewSet)
router.register("lab-sections", LabSectionPublicViewSet)
router.register("lab-tasks", LabTaskPublicViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include("labs.api_client.urls")),
    path("admin/", include("labs.api_admin.urls")),
]
