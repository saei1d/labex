from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from ..models import Lab, LabSection, LabSession, LabSubmission, TestCase, TestResult
from ..serializers import (
    LabSerializer, LabSectionSerializer, LabSessionSerializer,
    LabSubmissionSerializer, TestCaseSerializer, TestResultSerializer
)
from docker_manager.manager import DockerManager
from validators.code_validator import CodeValidator
from tasks.lab_tasks import validate_submission


class LabSessionViewSet(viewsets.ModelViewSet):
    serializer_class = LabSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LabSession.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a lab session."""
        try:
            lab = Lab.objects.get(id=pk)
            docker_manager = DockerManager()
            
            session_info = docker_manager.start_lab_session(request.user, lab)
            
            return Response(session_info, status=status.HTTP_201_CREATED)
            
        except Lab.DoesNotExist:
            return Response(
                {'error': 'Lab not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop a lab session."""
        try:
            session = self.get_object()
            docker_manager = DockerManager()
            docker_manager.stop_lab_session(session)
            
            return Response({'message': 'Session stopped successfully'})
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get session status and container info."""
        try:
            session = self.get_object()
            
            # Check if session is expired
            if session.expires_at and session.expires_at < timezone.now():
                if session.status == 'running':
                    docker_manager = DockerManager()
                    docker_manager.stop_lab_session(session)
            
            serializer = self.get_serializer(session)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LabSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = LabSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LabSubmission.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def submit_code(self, request):
        """Submit code for validation."""
        try:
            lab_section_id = request.data.get('lab_section_id')
            code = request.data.get('code')
            
            if not lab_section_id or not code:
                return Response(
                    {'error': 'lab_section_id and code are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            lab_section = LabSection.objects.get(id=lab_section_id)
            
            # Create submission
            submission = LabSubmission.objects.create(
                user=request.user,
                lab_section=lab_section,
                code=code
            )
            
            # Validate asynchronously
            validate_submission.delay(submission.id)
            
            return Response({
                'submission_id': submission.id,
                'message': 'Code submitted for validation'
            }, status=status.HTTP_201_CREATED)
            
        except LabSection.DoesNotExist:
            return Response(
                {'error': 'Lab section not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get validation results for a submission."""
        try:
            submission = self.get_object()
            test_results = TestResult.objects.filter(submission=submission)
            
            total_points = sum(tc.points for tc in submission.lab_section.test_cases.all())
            earned_points = sum(tr.points_earned for tr in test_results)
            
            return Response({
                'submission_id': submission.id,
                'total_points': total_points,
                'earned_points': earned_points,
                'percentage': (earned_points / total_points * 100) if total_points > 0 else 0,
                'test_results': TestResultSerializer(test_results, many=True).data,
                'passed_all': all(tr.passed for tr in test_results)
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = TestCaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        lab_section_id = self.request.query_params.get('lab_section_id')
        if lab_section_id:
            return TestCase.objects.filter(lab_section_id=lab_section_id)
        return TestCase.objects.all()
