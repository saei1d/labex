import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_register_user(client):
    url = reverse("register")

    data = {
        "email": "newuser@test.com",
        "password": "StrongPass123",
        "password2": "StrongPass123"
    }

    response = client.post(url, data, content_type="application/json")

    assert response.status_code == 201
    assert User.objects.filter(email="newuser@test.com").exists()