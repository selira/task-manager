from datetime import date

import pytest

from apps.organizations.models import Membership, Organization
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User


@pytest.fixture
def user_factory(db):
    def create_user(email, name=None, password="test-pass-123", **kwargs):
        return User.objects.create_user(
            email=email,
            name=name or email.split("@")[0].title(),
            password=password,
            **kwargs,
        )

    return create_user


@pytest.fixture
def owner(user_factory):
    return user_factory("owner@example.com", "Owner User")


@pytest.fixture
def admin_user(user_factory):
    return user_factory("admin@example.com", "Admin User")


@pytest.fixture
def member(user_factory):
    return user_factory("member@example.com", "Member User")


@pytest.fixture
def outsider(user_factory):
    return user_factory("outsider@example.com", "Outside User")


@pytest.fixture
def organization(owner, admin_user, member):
    organization = Organization.objects.create_with_owner(
        owner=owner,
        name="Example Organization",
        slug="example",
    )
    Membership.objects.create(
        organization=organization,
        user=admin_user,
        role=Membership.Role.ADMIN,
    )
    Membership.objects.create(
        organization=organization,
        user=member,
        role=Membership.Role.MEMBER,
    )
    return organization


@pytest.fixture
def other_organization(outsider):
    return Organization.objects.create_with_owner(
        owner=outsider,
        name="Other Organization",
        slug="other",
    )


@pytest.fixture
def project(organization, owner):
    return Project.objects.create(
        organization=organization,
        name="Main Project",
        slug="main-project",
        description="Primary project",
        created_by=owner,
    )


@pytest.fixture
def task(project, owner, member):
    return Task.objects.create(
        project=project,
        title="Assigned task",
        description="Work to complete",
        priority=Task.Priority.HIGH,
        assignee=member,
        created_by=owner,
        due_date=date(2026, 12, 1),
    )
