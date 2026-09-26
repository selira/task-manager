import pytest

from apps.tasks.forms import AssignedTaskStatusForm, TaskForm
from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def test_task_form_only_offers_organization_members(project, member, outsider):
    form = TaskForm(project=project)

    assert member in form.fields["assignee"].queryset
    assert outsider not in form.fields["assignee"].queryset


def test_task_form_rejects_invalid_date(project, member):
    form = TaskForm(
        data={
            "title": "Invalid date",
            "description": "",
            "status": Task.Status.TODO,
            "priority": Task.Priority.MEDIUM,
            "assignee": member.pk,
            "due_date": "not-a-date",
        },
        project=project,
    )

    assert not form.is_valid()
    assert "due_date" in form.errors


def test_assigned_member_form_only_exposes_status(task):
    form = AssignedTaskStatusForm(instance=task)

    assert list(form.fields) == ["status"]
