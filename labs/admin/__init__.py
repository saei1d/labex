from django.contrib import admin

from ..models import Lab, LabSection, LabSession


class LabSectionInline(admin.TabularInline):
    model = LabSection
    extra = 1


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "difficulty", "order")
    list_filter = ("difficulty", "module")
    search_fields = ("title",)
    inlines = [LabSectionInline]


@admin.register(LabSection)
class LabSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "lab", "order")
    ordering = ("lab", "order")


@admin.register(LabSession)
class LabSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "lab", "status", "started_at")
    list_filter = ("status",)
