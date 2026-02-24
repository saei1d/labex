# labs/serializers.py
from rest_framework import serializers
from .models import Lab, LabSection, LabSession


class LabSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSession
        fields = ["id", "lab", "container_id", "status", "started_at"]


class LabSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSection
        fields = "__all__"


class LabSerializer(serializers.ModelSerializer):
    sections = LabSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Lab
        fields = "__all__"