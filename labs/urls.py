from django.urls import path , include

urlpatterns = [
    path("", include('labs.admin.urls')),
]