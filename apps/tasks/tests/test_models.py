import pytest
from django.core.exceptions import ValidationError

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def test_marking_task_done_sets_completion_timestamp(task):
    task.status = Task.Status.DONE
    task.save()

    assert task.completed_at is not None


def test_saving_done_task_preserves_completion_timestamp(task):
    task.status = Task.Status.DONE
    task.save()
    completed_at = task.completed_at
    task.title = "Updated title"
    task.save()

    assert task.completed_at == completed_at


def test_moving_task_out_of_done_clears_completion_timestamp(task):
    task.status = Task.Status.DONE
    task.save()
    task.status = Task.Status.IN_PROGRESS
    task.save()

    assert task.completed_at is None


def test_assignee_must_belong_to_project_organization(task, outsider):
    task.assignee = outsider

    with pytest.raises(ValidationError, match="assignee"):
        task.full_clean()


def test_task_queryset_enforces_organization_visibility(task, member, outsider):
    assert task in Task.objects.visible_to(member)
    assert task not in Task.objects.visible_to(outsider)
