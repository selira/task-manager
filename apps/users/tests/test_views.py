import pytest
from django.urls import reverse

from apps.organizations.models import Membership
from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_login_page_renders(client):
    response = client.get(reverse("users:login"))

    assert response.status_code == 200
    assert "Log in to Task Manager" in response.content.decode()


def test_login_authenticates_by_email(client, owner):
    response = client.post(
        reverse("users:login"),
        {"username": owner.email, "password": "test-pass-123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("organizations:list")


def test_anonymous_user_is_redirected_from_dashboard(client):
    response = client.get(reverse("organizations:list"))

    assert response.status_code == 302
    assert reverse("users:login") in response.url


def test_owner_can_create_admin_for_organization(client, owner, organization):
    client.force_login(owner)
    response = client.post(
        reverse("organizations:user-create", args=[organization.slug]),
        {
            "email": "new-admin@example.com",
            "name": "New Admin",
            "role": Membership.Role.ADMIN,
            "password1": "secure-pass-456",
            "password2": "secure-pass-456",
        },
    )

    assert response.status_code == 302
    user = User.objects.get(email="new-admin@example.com")
    assert (
        Membership.objects.get(user=user, organization=organization).role == Membership.Role.ADMIN
    )


def test_member_cannot_create_users(client, member, organization):
    client.force_login(member)
    response = client.get(reverse("organizations:user-create", args=[organization.slug]))

    assert response.status_code == 403


def test_existing_email_is_rejected(client, owner, organization, outsider):
    client.force_login(owner)
    response = client.post(
        reverse("organizations:user-create", args=[organization.slug]),
        {
            "email": outsider.email,
            "name": outsider.name,
            "role": Membership.Role.MEMBER,
            "password1": "secure-pass-456",
            "password2": "secure-pass-456",
        },
    )

    assert response.status_code == 200
    assert "already exists" in response.content.decode()
    assert not Membership.objects.filter(user=outsider, organization=organization).exists()
