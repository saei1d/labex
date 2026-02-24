# labs/serializers.py
from rest_framework import serializers
from .models import Lab, LabSection, LabSession, LabSubmission, TestCase, TestResult


class LabSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSection
        fields = "__all__"


class LabSerializer(serializers.ModelSerializer):
    sections = LabSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Lab
        fields = "__all__"


class LabSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSession
        fields = "__all__"
        read_only_fields = ["container_id", "container_port", "access_token"]


class LabSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSubmission
        fields = "__all__"
        read_only_fields = ["user", "submitted_at"]


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = "__all__"


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = "__all__"
        read_only_fields = ["submission"]