from django.db import models
from courses.models import Course
from accounts.models import User
from labs.models import Lab


# Create your models here.
class UserCourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percent = models.FloatField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class UserLabProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.FloatField(default=0)
