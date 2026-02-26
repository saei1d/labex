from django.db import models
from courses.models import Course
from accounts.models import User
from labs.models import Lab, LabTask


class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percent = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "course"], name="uniq_user_course_progress")]


class UserLabProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "lab"], name="uniq_user_lab_progress")]


class UserTaskProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(LabTask, on_delete=models.CASCADE)
    is_unlocked = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    last_score = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "task"], name="uniq_user_task_progress")]
