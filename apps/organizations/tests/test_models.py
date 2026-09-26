import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.organizations.models import Membership, Organization

pytestmark = pytest.mark.django_db


def test_create_with_owner_adds_owner_membership(owner):
    organization = Organization.objects.create_with_owner(
        owner=owner,
        name="New Organization",
        slug="new-organization",
    )

    assert organization.memberships.get(user=owner).role == Membership.Role.OWNER


def test_membership_is_unique_per_user_and_organization(organization, member):
    with pytest.raises(IntegrityError):
        Membership.objects.create(
            organization=organization,
            user=member,
            role=Membership.Role.ADMIN,
        )


def test_visible_to_only_returns_joined_organizations(
    organization,
    other_organization,
    member,
):
    visible = Organization.objects.visible_to(member)

    assert organization in visible
    assert other_organization not in visible


def test_last_owner_cannot_be_demoted(organization, owner):
    membership = Membership.objects.get(organization=organization, user=owner)
    membership.role = Membership.Role.ADMIN

    with pytest.raises(ValidationError, match="must have an owner"):
        membership.full_clean()


def test_last_owner_cannot_be_deleted(organization, owner):
    membership = Membership.objects.get(organization=organization, user=owner)

    with pytest.raises(ValidationError, match="must have an owner"):
        membership.delete()
