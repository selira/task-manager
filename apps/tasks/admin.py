from django.contrib import admin

from .models import Task

# Register your models here.


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "project",
        "status",
        "priority",
        "assignee",
        "due_date",
        "updated_at",
    )
    list_filter = ("status", "priority", "project__organization", "project")
    search_fields = ("title", "description", "project__name", "assignee__email")
    autocomplete_fields = ("project", "assignee", "created_by")
