# courses/views.py
from rest_framework.viewsets import ModelViewSet
from ..models import Course, CourseModule
from ..serializers import CourseSerializer, CourseModuleSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseModuleViewSet(ModelViewSet):
    queryset = CourseModule.objects.all()
    serializer_class = CourseModuleSerializer