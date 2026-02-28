from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from courses.models import Course, CourseModule, PublishStatus
from labs.models import Lab, LabTask, TaskValidationRule, LabSession
from labs.serializers import LabSerializer
from labs.services.image_resolver import UnknownLabImageKey, normalize_image_key, resolve_lab_image
from progress.models import UserTaskProgress

User = get_user_model()


@override_settings(LAB_DOCKER_IMAGE_MAP={"python-dockerfile": "ghcr.io/acme/lab-python:1.0.0"})
def test_resolve_lab_image_success():
    assert resolve_lab_image(" python-dockerfile ") == "ghcr.io/acme/lab-python:1.0.0"
    assert normalize_image_key(" Python-Dockerfile ") == "python-dockerfile"


@override_settings(LAB_DOCKER_IMAGE_MAP={"python-dockerfile": "ghcr.io/acme/lab-python:1.0.0"})
def test_resolve_lab_image_unknown_key():
    with pytest.raises(UnknownLabImageKey):
        resolve_lab_image("unknown-key")


@pytest.mark.django_db
@override_settings(LAB_DOCKER_IMAGE_MAP={"python-dockerfile": "ghcr.io/acme/lab-python:1.0.0"})
def test_lab_serializer_rejects_unknown_docker_key():
    course = Course.objects.create(title="Python", slug="python-ser", description="d", level="beginner", status=PublishStatus.PUBLISHED)
    module = CourseModule.objects.create(course=course, title="M1", order=1)
    payload = {
        "module": module.id,
        "title": "Lab Serializer",
        "docker_image": "unknown-key",
        "difficulty": "easy",
        "status": PublishStatus.PUBLISHED,
        "time_limit_minutes": 90,
    }

    serializer = LabSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "docker_image" in serializer.errors


@pytest.mark.django_db
@override_settings(LAB_DOCKER_IMAGE_MAP={"python-dockerfile": "ghcr.io/acme/lab-python:1.0.0"})
def test_start_lab_creates_running_session():
    user = User.objects.create_user(email="student@test.com", password="12345678")
    client = APIClient()
    client.force_authenticate(user=user)

    course = Course.objects.create(title="Python", slug="python", description="d", level="beginner", status=PublishStatus.PUBLISHED)
    module = CourseModule.objects.create(course=course, title="M1", order=1)
    lab = Lab.objects.create(module=module, title="Lab 1", docker_image="python-dockerfile", difficulty="easy", status=PublishStatus.PUBLISHED)
    LabTask.objects.create(lab=lab, title="Task1", prompt_md="do", order=1)

    with patch("labs.views.runtime.create_session_container") as mocked_runtime:
        mocked_runtime.return_value.container_id = "c-1"
        mocked_runtime.return_value.port = 18080
        mocked_runtime.return_value.access_token = "token"
        mocked_runtime.return_value.workspace_path = "/tmp/w"
        response = client.post(reverse("start_lab", args=[lab.id]))

    assert response.status_code == 201
    mocked_runtime.assert_called_once_with(image="ghcr.io/acme/lab-python:1.0.0", session_key=f"{user.id}-{lab.id}")
    session = LabSession.objects.get(lab=lab, user=user)
    assert session.status == "running"
    progress = UserTaskProgress.objects.get(user=user, task__lab=lab, task__order=1)
    assert progress.is_unlocked is True


@pytest.mark.django_db
@override_settings(LAB_DOCKER_IMAGE_MAP={"python-dockerfile": "ghcr.io/acme/lab-python:1.0.0"})
def test_start_lab_rejects_unknown_docker_key():
    user = User.objects.create_user(email="student4@test.com", password="12345678")
    client = APIClient()
    client.force_authenticate(user=user)

    course = Course.objects.create(title="Python", slug="python-2", description="d", level="beginner", status=PublishStatus.PUBLISHED)
    module = CourseModule.objects.create(course=course, title="M1", order=1)
    lab = Lab.objects.create(module=module, title="Lab 2", docker_image="unknown-key", difficulty="easy", status=PublishStatus.PUBLISHED)
    LabTask.objects.create(lab=lab, title="Task1", prompt_md="do", order=1)

    with patch("labs.views.runtime.create_session_container") as mocked_runtime:
        response = client.post(reverse("start_lab", args=[lab.id]))

    assert response.status_code == 400
    assert "Unknown docker image key" in response.json()["error"]
    mocked_runtime.assert_not_called()


@pytest.mark.django_db
def test_validate_task_unlocks_next():
    user = User.objects.create_user(email="student2@test.com", password="12345678")
    client = APIClient()
    client.force_authenticate(user=user)

    course = Course.objects.create(title="Net", slug="net", description="d", level="beginner", status=PublishStatus.PUBLISHED)
    module = CourseModule.objects.create(course=course, title="M1", order=1)
    lab = Lab.objects.create(module=module, title="Lab 1", docker_image="python-dockerfile", difficulty="easy", status=PublishStatus.PUBLISHED)
    task1 = LabTask.objects.create(lab=lab, title="Task1", prompt_md="do", order=1)
    task2 = LabTask.objects.create(lab=lab, title="Task2", prompt_md="do", order=2)
    TaskValidationRule.objects.create(task=task1, type="command", config_json={"command": "echo ok"})

    session = LabSession.objects.create(
        user=user,
        lab=lab,
        container_id="c-1",
        status="running",
        workspace_path="/tmp",
        access_token="t",
        port=18080,
        expires_at=timezone.now() + timedelta(minutes=30),
    )
    UserTaskProgress.objects.create(user=user, task=task1, is_unlocked=True)

    with patch("labs.views.evaluate_task", return_value=(True, "ok")):
        response = client.post(reverse("validate_task", args=[session.id, task1.id]))

    assert response.status_code == 200
    assert response.json()["next_task_unlocked"] is True
    assert UserTaskProgress.objects.get(user=user, task=task1).completed is True
    assert UserTaskProgress.objects.get(user=user, task=task2).is_unlocked is True


@pytest.mark.django_db
def test_validate_task_fails_when_locked():
    user = User.objects.create_user(email="student3@test.com", password="12345678")
    client = APIClient()
    client.force_authenticate(user=user)

    course = Course.objects.create(title="Sec", slug="sec", description="d", level="beginner", status=PublishStatus.PUBLISHED)
    module = CourseModule.objects.create(course=course, title="M1", order=1)
    lab = Lab.objects.create(module=module, title="Lab 1", docker_image="python-dockerfile", difficulty="easy", status=PublishStatus.PUBLISHED)
    task1 = LabTask.objects.create(lab=lab, title="Task1", prompt_md="do", order=1)

    session = LabSession.objects.create(
        user=user,
        lab=lab,
        container_id="c-1",
        status="running",
        workspace_path="/tmp",
        access_token="t",
        port=18080,
        expires_at=timezone.now() + timedelta(minutes=30),
    )

    response = client.post(reverse("validate_task", args=[session.id, task1.id]))
    assert response.status_code == 403
