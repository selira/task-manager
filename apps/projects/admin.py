from django.contrib import admin

from .models import Project

# Register your models here.


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status", "created_by", "updated_at")
    list_filter = ("status", "organization")
    search_fields = ("name", "description", "organization__name")
    autocomplete_fields = ("organization", "created_by")
    prepopulated_fields = {"slug": ("name",)}
