from rest_framework.viewsets import ReadOnlyModelViewSet
from courses.models import Course, CourseModule, PublishStatus
from courses.serializers import CourseSerializer, CourseModuleSerializer


class CoursePublicViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.filter(status=PublishStatus.PUBLISHED)
    serializer_class = CourseSerializer


class CourseModulePublicViewSet(ReadOnlyModelViewSet):
    queryset = CourseModule.objects.select_related("course").filter(course__status=PublishStatus.PUBLISHED)
    serializer_class = CourseModuleSerializer
