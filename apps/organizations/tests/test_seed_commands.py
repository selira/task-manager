import pytest
from django.core.management import call_command

from apps.organizations.models import Membership, Organization
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User

pytestmark = pytest.mark.django_db(transaction=True)


def test_seed_data_replaces_existing_data():
    User.objects.create_user(
        email="stale@example.com",
        name="Stale User",
        password="stale-password",
    )

    call_command("seed_data", verbosity=0)

    assert not User.objects.filter(email="stale@example.com").exists()
    assert User.objects.count() == 4
    assert Organization.objects.count() == 2
    assert Project.objects.count() == 3
    assert Task.objects.count() == 6


def test_seed_data2_creates_large_visible_collections():
    call_command("seed_data2", verbosity=0)

    owner = User.objects.get(email="user01@example.com")
    primary_organization = Organization.objects.get(slug="ui-load-test")
    first_project = Project.objects.get(
        organization=primary_organization,
        slug="demo-project-01",
    )

    assert User.objects.count() == 20
    assert Organization.objects.count() == 20
    assert Project.objects.count() == 20
    assert Task.objects.count() == 20
    assert Membership.objects.filter(user=owner).count() == 20
    assert primary_organization.memberships.count() == 20
    assert first_project.tasks.count() == 20
