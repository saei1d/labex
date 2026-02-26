from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .labs import LabViewSet, LabSectionViewSet, LabTaskViewSet, TaskValidationRuleViewSet

router = DefaultRouter()
router.register("labs", LabViewSet)
router.register("lab-sections", LabSectionViewSet)
router.register("lab-tasks", LabTaskViewSet)
router.register("validation-rules", TaskValidationRuleViewSet)

urlpatterns = [path("", include(router.urls))]
