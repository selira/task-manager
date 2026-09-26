import pytest
from django.urls import reverse

from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_member_can_view_project_list_and_detail(
    client,
    member,
    organization,
    project,
):
    client.force_login(member)

    list_response = client.get(reverse("projects:list", args=[organization.slug]))
    detail_response = client.get(reverse("projects:detail", args=[organization.slug, project.slug]))

    assert list_response.status_code == 200
    assert project.name in list_response.content.decode()
    assert detail_response.status_code == 200
    assert project.description in detail_response.content.decode()


def test_member_cannot_create_project(client, member, organization):
    client.force_login(member)
    response = client.post(
        reverse("projects:create", args=[organization.slug]),
        {"name": "Forbidden", "slug": "forbidden", "status": Project.Status.ACTIVE},
    )

    assert response.status_code == 403
    assert not Project.objects.filter(slug="forbidden").exists()


def test_admin_can_create_project(client, admin_user, organization):
    client.force_login(admin_user)
    response = client.post(
        reverse("projects:create", args=[organization.slug]),
        {
            "name": "New Project",
            "slug": "new-project",
            "description": "A useful project",
            "status": Project.Status.ACTIVE,
        },
    )

    assert response.status_code == 302
    project = Project.objects.get(slug="new-project")
    assert project.organization == organization
    assert project.created_by == admin_user


def test_owner_can_update_project(client, owner, organization, project):
    client.force_login(owner)
    response = client.post(
        reverse("projects:update", args=[organization.slug, project.slug]),
        {
            "name": "Renamed Project",
            "slug": project.slug,
            "description": project.description,
            "status": Project.Status.COMPLETED,
        },
    )

    assert response.status_code == 302
    project.refresh_from_db()
    assert project.name == "Renamed Project"
    assert project.status == Project.Status.COMPLETED


def test_outsider_cannot_view_project(client, outsider, organization, project):
    client.force_login(outsider)
    response = client.get(reverse("projects:detail", args=[organization.slug, project.slug]))

    assert response.status_code == 404


def test_duplicate_slug_returns_form_error(client, owner, organization, project):
    client.force_login(owner)
    response = client.post(
        reverse("projects:create", args=[organization.slug]),
        {
            "name": "Duplicate",
            "slug": project.slug,
            "status": Project.Status.ACTIVE,
        },
    )

    assert response.status_code == 200
    assert "already exists" in response.content.decode()
