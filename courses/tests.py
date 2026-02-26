import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from courses.models import Course, PublishStatus

User = get_user_model()


@pytest.mark.django_db
def test_public_courses_only_show_published(client):
    Course.objects.create(title="draft", slug="draft", description="d", level="beginner", status=PublishStatus.DRAFT)
    Course.objects.create(title="pub", slug="pub", description="d", level="beginner", status=PublishStatus.PUBLISHED)

    response = client.get("/api/courses/")
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_admin_courses_requires_role(client):
    user = User.objects.create_user(email="student@test.com", password="12345678", role="student")
    client.force_login(user)
    response = client.get("/api/admin/courses/")
    assert response.status_code == 403
