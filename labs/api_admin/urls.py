# labs/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .labs import LabViewSet, LabSectionViewSet, start_lab

router = DefaultRouter()
router.register("labs", LabViewSet)
router.register("lab-sections", LabSectionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("labs/<uuid:lab_id>/start/", start_lab, name="start_lab"),
]