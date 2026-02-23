import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_login_user(client):
    # create user
    User.objects.create_user(
        email="login@test.com",
        password="12345678"
    )

    url = reverse("login")
    data = {
        "email": "login@test.com",
        "password": "12345678"
    }

    response = client.post(url, data, content_type="application/json")

    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()


@pytest.mark.django_db
def test_login_invalid_password(client):
    User.objects.create_user(
        email="login2@test.com",
        password="correctpass"
    )

    url = reverse("login")
    data = {
        "email": "login2@test.com",
        "password": "wrongpass"
    }

    response = client.post(url, data, content_type="application/json")

    assert response.status_code == 400