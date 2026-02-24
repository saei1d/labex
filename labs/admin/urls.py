# labs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .labs import LabViewSet, LabSectionViewSet
from .session_views import LabSessionViewSet, LabSubmissionViewSet, TestCaseViewSet

router = DefaultRouter()
router.register("labs", LabViewSet)
router.register("lab-sections", LabSectionViewSet)
router.register("sessions", LabSessionViewSet, basename='labsession')
router.register("submissions", LabSubmissionViewSet, basename='labsubmission')
router.register("test-cases", TestCaseViewSet, basename='testcase')

urlpatterns = [
    path("", include(router.urls)),
]