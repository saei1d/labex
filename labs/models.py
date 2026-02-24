# labs/models.py
from django.db import models
from courses.models import CourseModule
from accounts.models import User


class Lab(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name="labs")
    title = models.CharField(max_length=255)
    docker_image = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50, choices=[
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ])

    def __str__(self):
        return self.title


class LabSection(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    content_md = models.TextField()  # markdown
    order = models.PositiveIntegerField(default=0)
    type = models.CharField(choices=[
        ("theory", "Theory"),
        ("task", "Task"),
        ("solution", "Solution"),
    ])

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.lab.title} - {self.title}"


class LabSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    container_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[
        ("running", "Running"),
        ("stopped", "Stopped"),
        ("finished", "Finished"),
    ])
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
