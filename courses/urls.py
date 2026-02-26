from django.urls import include, path
from rest_framework.routers import DefaultRouter
from courses.views import CoursePublicViewSet, CourseModulePublicViewSet

router = DefaultRouter()
router.register("courses", CoursePublicViewSet)
router.register("modules", CourseModulePublicViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", include("courses.api_admin.urls")),
]
