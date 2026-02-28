from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from courses.models import PublishStatus
from labs.models import Lab, LabSection, LabTask, LabSession, TaskAttempt
from labs.serializers import LabSerializer, LabSectionSerializer, LabTaskSerializer, LabSessionSerializer
from labs.services.container_runtime import RuntimeErrorException, runtime
from labs.services.grader import evaluate_task
from labs.services.image_resolver import UnknownLabImageKey, resolve_lab_image
from progress.models import UserTaskProgress


class LabPublicViewSet(ReadOnlyModelViewSet):
    queryset = Lab.objects.select_related("module", "module__course").filter(status=PublishStatus.PUBLISHED)
    serializer_class = LabSerializer


class LabSectionPublicViewSet(ReadOnlyModelViewSet):
    queryset = LabSection.objects.select_related("lab").filter(lab__status=PublishStatus.PUBLISHED)
    serializer_class = LabSectionSerializer


class LabTaskPublicViewSet(ReadOnlyModelViewSet):
    queryset = LabTask.objects.select_related("lab").filter(lab__status=PublishStatus.PUBLISHED)
    serializer_class = LabTaskSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_lab(request, lab_id):
    try:
        lab = Lab.objects.get(id=lab_id, status=PublishStatus.PUBLISHED)
    except Lab.DoesNotExist:
        return Response({"error": "Lab not found or not published"}, status=status.HTTP_404_NOT_FOUND)

    try:
        resolved_image = resolve_lab_image(lab.docker_image)
    except UnknownLabImageKey as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        runtime_container = runtime.create_session_container(image=resolved_image, session_key=f"{request.user.id}-{lab.id}")
    except RuntimeErrorException as exc:
        return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    session = LabSession.objects.create(
        user=request.user,
        lab=lab,
        container_id=runtime_container.container_id,
        workspace_path=runtime_container.workspace_path,
        port=runtime_container.port,
        access_token=runtime_container.access_token,
        expires_at=LabSession.default_expiry(minutes=lab.time_limit_minutes),
        status="running",
    )

    first_task = lab.tasks.order_by("order").first()
    if first_task:
        UserTaskProgress.objects.get_or_create(
            user=request.user,
            task=first_task,
            defaults={"is_unlocked": True},
        )

    serializer = LabSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def stop_session(request, session_id):
    session = LabSession.objects.filter(id=session_id, user=request.user).first()
    if not session:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        runtime.stop_container(session.container_id)
        runtime.destroy_container(session.container_id)
    except RuntimeErrorException:
        pass

    session.mark_finished(status="stopped")
    return Response({"status": "stopped"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def session_detail(request, session_id):
    session = LabSession.objects.filter(id=session_id, user=request.user).first()
    if not session:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    if session.is_expired() and session.status == "running":
        session.mark_finished(status="expired")

    serializer = LabSessionSerializer(session)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_task(request, session_id, task_id):
    session = LabSession.objects.select_related("lab").filter(id=session_id, user=request.user).first()
    if not session:
        return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)

    if session.is_expired() or session.status != "running":
        return Response({"error": "Session is not active"}, status=status.HTTP_400_BAD_REQUEST)

    task = LabTask.objects.filter(id=task_id, lab=session.lab).first()
    if not task:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    task_progress, _ = UserTaskProgress.objects.get_or_create(user=request.user, task=task)
    if not task_progress.is_unlocked:
        return Response({"error": "Task is locked"}, status=status.HTTP_403_FORBIDDEN)

    attempt_count = TaskAttempt.objects.filter(session=session, task=task).count()
    if attempt_count >= task.max_attempts:
        return Response({"error": "Maximum attempts reached"}, status=status.HTTP_400_BAD_REQUEST)

    is_passed, feedback = evaluate_task(session=session, task=task)
    attempt = TaskAttempt.objects.create(
        session=session,
        task=task,
        attempt_no=attempt_count + 1,
        status="passed" if is_passed else "failed",
        score=100 if is_passed else 0,
        feedback=feedback,
    )

    next_task_unlocked = False
    if is_passed:
        task_progress.completed = True
        task_progress.last_score = 100
        task_progress.save(update_fields=["completed", "last_score", "updated_at"])
        next_task = LabTask.objects.filter(lab=session.lab, order__gt=task.order).order_by("order").first()
        if next_task:
            next_progress, _ = UserTaskProgress.objects.get_or_create(user=request.user, task=next_task)
            if not next_progress.is_unlocked:
                next_progress.is_unlocked = True
                next_progress.save(update_fields=["is_unlocked", "updated_at"])
                next_task_unlocked = True

    return Response(
        {
            "attempt_id": attempt.id,
            "status": attempt.status,
            "feedback": attempt.feedback,
            "next_task_unlocked": next_task_unlocked,
        }
    )
