from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .course import CourseViewSet, CourseModuleViewSet

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("modules", CourseModuleViewSet)

urlpatterns = [path("", include(router.urls))]
