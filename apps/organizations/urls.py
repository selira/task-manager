from django.urls import path

from apps.users.views import organization_user_create

from . import views

app_name = "organizations"

urlpatterns = [
    path("", views.organization_list, name="list"),
    path("new/", views.organization_create, name="create"),
    path("<slug:slug>/", views.organization_detail, name="detail"),
    path("<slug:organization_slug>/users/new/", organization_user_create, name="user-create"),
]
