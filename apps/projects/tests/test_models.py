import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_project_slug_is_unique_within_organization(project, organization, owner):
    with pytest.raises(IntegrityError):
        Project.objects.create(
            organization=organization,
            name="Duplicate",
            slug=project.slug,
            created_by=owner,
        )


def test_same_project_slug_is_allowed_in_different_organizations(
    project,
    other_organization,
    outsider,
):
    second = Project.objects.create(
        organization=other_organization,
        name="Another Main Project",
        slug=project.slug,
        created_by=outsider,
    )

    assert second.pk


def test_project_creator_must_belong_to_organization(
    organization,
    outsider,
):
    project = Project(
        organization=organization,
        name="Invalid",
        slug="invalid",
        created_by=outsider,
    )

    with pytest.raises(ValidationError, match="creator"):
        project.full_clean()


def test_project_queryset_enforces_organization_visibility(
    project,
    member,
    outsider,
):
    assert project in Project.objects.visible_to(member)
    assert project not in Project.objects.visible_to(outsider)
