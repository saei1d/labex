from django.contrib import admin

from .models import UserCourseProgress, UserLabProgress


@admin.register(UserCourseProgress)
class UserCourseProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "progress_percent", "updated_at")
    search_fields = ("user__email", "course__title")


@admin.register(UserLabProgress)
class UserLabProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lab", "completed", "score")
    list_filter = ("completed",)
    search_fields = ("user__email", "lab__title")
