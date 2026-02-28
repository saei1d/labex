
from django.contrib import admin
from .models import Course, CourseModule


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "is_published", "created_at")
    list_filter = ['level', 'status']  # به جای is_published از status استفاده کنید
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseModuleInline]


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    ordering = ("course", "order")