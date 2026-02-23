# labs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .labs import LabViewSet, LabSectionViewSet

router = DefaultRouter()
router.register("labs", LabViewSet)
router.register("lab-sections", LabSectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]