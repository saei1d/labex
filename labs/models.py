import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from courses.models import CourseModule, PublishStatus
from accounts.models import User


class Lab(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name="labs")
    title = models.CharField(max_length=255)
    docker_image = models.CharField(max_length=255)
    difficulty = models.CharField(
        max_length=50,
        choices=[("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
    )
    status = models.CharField(max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    time_limit_minutes = models.PositiveIntegerField(default=90)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_labs")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_labs")

    def __str__(self):
        return self.title


class LabSection(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    content_md = models.TextField()
    order = models.PositiveIntegerField(default=0)
    type = models.CharField(
        max_length=20,
        choices=[("theory", "Theory"), ("task", "Task"), ("solution", "Solution")],
    )

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["lab", "order"], name="uniq_lab_section_order")]

    def __str__(self):
        return f"{self.lab.title} - {self.title}"


class LabTask(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="tasks")
    section = models.ForeignKey(LabSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    title = models.CharField(max_length=255)
    prompt_md = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    max_attempts = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["lab", "order"], name="uniq_lab_task_order")]

    def __str__(self):
        return f"{self.lab.title} - {self.title}"


class TaskValidationRule(models.Model):
    task = models.ForeignKey(LabTask, on_delete=models.CASCADE, related_name="validation_rules")
    type = models.CharField(
        max_length=20,
        choices=[("command", "Command"), ("script", "Script"), ("http", "HTTP")],
        default="command",
    )
    config_json = models.JSONField(default=dict)
    timeout_seconds = models.PositiveIntegerField(default=15)


class LabSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[("running", "Running"), ("stopped", "Stopped"), ("finished", "Finished"), ("expired", "Expired")],
    )
    workspace_path = models.CharField(max_length=255, blank=True)
    port = models.PositiveIntegerField(null=True, blank=True)
    access_token = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def mark_finished(self, status="finished"):
        self.status = status
        self.ended_at = timezone.now()
        self.save(update_fields=["status", "ended_at", "last_activity_at"])

    @classmethod
    def default_expiry(cls, minutes):
        return timezone.now() + timedelta(minutes=minutes)


class TaskAttempt(models.Model):
    session = models.ForeignKey(LabSession, on_delete=models.CASCADE, related_name="attempts")
    task = models.ForeignKey(LabTask, on_delete=models.CASCADE, related_name="attempts")
    attempt_no = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=[("passed", "Passed"), ("failed", "Failed")])
    score = models.FloatField(default=0)
    feedback = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]
