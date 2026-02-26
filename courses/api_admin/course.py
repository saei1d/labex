from rest_framework.viewsets import ModelViewSet
from common.permissions import IsAdminOrInstructor
from courses.models import Course, CourseModule
from courses.serializers import CourseSerializer, CourseModuleSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrInstructor]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class CourseModuleViewSet(ModelViewSet):
    queryset = CourseModule.objects.select_related("course").all()
    serializer_class = CourseModuleSerializer
    permission_classes = [IsAdminOrInstructor]
