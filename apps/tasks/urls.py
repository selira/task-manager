from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path(
        "organizations/<slug:organization_slug>/tasks/",
        views.task_list,
        name="list",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/tasks/new/",
        views.task_create,
        name="create",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/tasks/<int:task_id>/",
        views.task_detail,
        name="detail",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/tasks/<int:task_id>/edit/",
        views.task_update,
        name="update",
    ),
]
