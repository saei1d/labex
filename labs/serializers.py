from rest_framework import serializers
from .models import Lab, LabSection, LabSession, LabTask, TaskAttempt, TaskValidationRule
from .services.image_resolver import UnknownLabImageKey, normalize_image_key, resolve_lab_image


class LabSessionSerializer(serializers.ModelSerializer):
    code_server_url = serializers.SerializerMethodField()

    class Meta:
        model = LabSession
        fields = [
            "id",
            "lab",
            "container_id",
            "status",
            "port",
            "code_server_url",
            "started_at",
            "expires_at",
        ]

    def get_code_server_url(self, obj):
        if not obj.port:
            return None
        return f"http://localhost:{obj.port}"


class LabSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSection
        fields = "__all__"


class TaskValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskValidationRule
        fields = "__all__"


class LabTaskSerializer(serializers.ModelSerializer):
    validation_rules = TaskValidationRuleSerializer(many=True, read_only=True)

    class Meta:
        model = LabTask
        fields = "__all__"


class LabSerializer(serializers.ModelSerializer):
    sections = LabSectionSerializer(many=True, read_only=True)
    tasks = LabTaskSerializer(many=True, read_only=True)

    def validate_docker_image(self, value):
        normalized_key = normalize_image_key(value)
        try:
            resolve_lab_image(normalized_key)
        except UnknownLabImageKey as exc:
            raise serializers.ValidationError(str(exc))
        return normalized_key

    class Meta:
        model = Lab
        fields = "__all__"


class TaskAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAttempt
        fields = "__all__"
        read_only_fields = ["attempt_no", "status", "score", "feedback"]
