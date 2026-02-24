# labs/views.py
from rest_framework.viewsets import ModelViewSet
from ..models import Lab, LabSection, LabSession
from ..serializers import LabSerializer, LabSectionSerializer, LabSessionSerializer


class LabViewSet(ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer


class LabSectionViewSet(ModelViewSet):
    queryset = LabSection.objects.all()
    serializer_class = LabSectionSerializer

