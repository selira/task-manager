import pytest
from django.urls import reverse

from apps.organizations.models import Membership, Organization

pytestmark = pytest.mark.django_db


def test_dashboard_lists_only_joined_organizations(
    client,
    member,
    organization,
    other_organization,
):
    client.force_login(member)
    response = client.get(reverse("organizations:list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert organization.name in content
    assert other_organization.name not in content


def test_organization_detail_rejects_outsider(client, outsider, organization):
    client.force_login(outsider)
    response = client.get(reverse("organizations:detail", args=[organization.slug]))

    assert response.status_code == 404


def test_organization_detail_renders_members_and_projects(
    client,
    owner,
    organization,
    project,
):
    client.force_login(owner)
    response = client.get(reverse("organizations:detail", args=[organization.slug]))
    content = response.content.decode()

    assert response.status_code == 200
    assert project.name in content
    assert "Member User" in content


def test_staff_can_create_organization_and_becomes_owner(client, owner):
    owner.is_staff = True
    owner.save(update_fields=["is_staff"])
    client.force_login(owner)
    response = client.post(
        reverse("organizations:create"),
        {"name": "Staff Organization", "slug": "staff-organization"},
    )

    assert response.status_code == 302
    organization = Organization.objects.get(slug="staff-organization")
    assert (
        Membership.objects.get(organization=organization, user=owner).role == Membership.Role.OWNER
    )


def test_non_staff_cannot_create_organization(client, member):
    client.force_login(member)
    response = client.post(
        reverse("organizations:create"),
        {"name": "Forbidden", "slug": "forbidden"},
    )

    assert response.status_code == 302
    assert not Organization.objects.filter(slug="forbidden").exists()
