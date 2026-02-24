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
    order = models.PositiveIntegerField(default=0)

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
    container_port = models.IntegerField(null=True, blank=True)
    access_token = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ("running", "Running"),
        ("stopped", "Stopped"),
        ("finished", "Finished"),
    ])
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.lab.title}"


class LabSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab_section = models.ForeignKey(LabSection, on_delete=models.CASCADE)
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.lab_section.title}"


class TestCase(models.Model):
    lab_section = models.ForeignKey(
        LabSection, on_delete=models.CASCADE, related_name="test_cases"
    )
    input_data = models.TextField(blank=True, null=True)
    expected_output = models.TextField()
    test_code = models.TextField()  # pytest test code
    points = models.FloatField(default=10.0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Test for {self.lab_section.title}"


class TestResult(models.Model):
    submission = models.ForeignKey(
        LabSubmission, on_delete=models.CASCADE, related_name="test_results"
    )
    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE)
    passed = models.BooleanField(default=False)
    actual_output = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    execution_time = models.FloatField(null=True, blank=True)
    points_earned = models.FloatField(default=0.0)

    def __str__(self):
        return f"Result for {self.submission} - {self.test_case}"