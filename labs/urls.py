from django.urls import path , include

urlpatterns = [
    path("", include('labs.api_admin.urls')),
]