from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path(
        "organizations/<slug:organization_slug>/projects/",
        views.project_list,
        name="list",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/new/",
        views.project_create,
        name="create",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/",
        views.project_detail,
        name="detail",
    ),
    path(
        "organizations/<slug:organization_slug>/projects/<slug:project_slug>/edit/",
        views.project_update,
        name="update",
    ),
]
