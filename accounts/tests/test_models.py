import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email="test@example.com",
        password="12345678",

    )

    assert user.email == "test@example.com"
    assert user.check_password("12345678")
    assert user.role == "student"


@pytest.mark.django_db
def test_create_superuser():
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="admin123"
    )

    assert admin.is_staff
    assert admin.is_superuser