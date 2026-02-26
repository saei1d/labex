from django.urls import path
from .start_lab import start_lab, stop_session, session_detail, validate_task

urlpatterns = [
    path("labs/<int:lab_id>/start/", start_lab, name="start_lab"),
    path("sessions/<int:session_id>/", session_detail, name="session_detail"),
    path("sessions/<int:session_id>/stop/", stop_session, name="stop_session"),
    path("sessions/<int:session_id>/tasks/<int:task_id>/validate/", validate_task, name="validate_task"),
]
