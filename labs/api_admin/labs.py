from rest_framework.viewsets import ModelViewSet
from common.permissions import IsAdminOrInstructor
from labs.models import Lab, LabSection, LabTask, TaskValidationRule
from labs.serializers import LabSerializer, LabSectionSerializer, LabTaskSerializer, TaskValidationRuleSerializer


class LabViewSet(ModelViewSet):
    queryset = Lab.objects.select_related("module", "module__course").all()
    serializer_class = LabSerializer
    permission_classes = [IsAdminOrInstructor]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class LabSectionViewSet(ModelViewSet):
    queryset = LabSection.objects.select_related("lab").all()
    serializer_class = LabSectionSerializer
    permission_classes = [IsAdminOrInstructor]


class LabTaskViewSet(ModelViewSet):
    queryset = LabTask.objects.select_related("lab", "section").all()
    serializer_class = LabTaskSerializer
    permission_classes = [IsAdminOrInstructor]


class TaskValidationRuleViewSet(ModelViewSet):
    queryset = TaskValidationRule.objects.select_related("task").all()
    serializer_class = TaskValidationRuleSerializer
    permission_classes = [IsAdminOrInstructor]
