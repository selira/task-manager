import pytest
from django.urls import reverse

from apps.tasks.models import Task

pytestmark = pytest.mark.django_db


def task_url(name, organization, project, task=None):
    args = [organization.slug, project.slug]
    if task is not None:
        args.append(task.pk)
    return reverse(f"tasks:{name}", args=args)


def test_admin_can_create_task(client, admin_user, organization, project, member):
    client.force_login(admin_user)
    response = client.post(
        task_url("create", organization, project),
        {
            "title": "New task",
            "description": "New task description",
            "status": Task.Status.TODO,
            "priority": Task.Priority.URGENT,
            "assignee": member.pk,
            "due_date": "2026-12-10",
        },
    )

    assert response.status_code == 302
    task = Task.objects.get(title="New task")
    assert task.project == project
    assert task.created_by == admin_user


def test_member_cannot_create_task(client, member, organization, project):
    client.force_login(member)
    response = client.post(
        task_url("create", organization, project),
        {
            "title": "Forbidden task",
            "status": Task.Status.TODO,
            "priority": Task.Priority.MEDIUM,
        },
    )

    assert response.status_code == 403
    assert not Task.objects.filter(title="Forbidden task").exists()


def test_assigned_member_can_only_update_status(
    client,
    member,
    organization,
    project,
    task,
):
    client.force_login(member)
    response = client.post(
        task_url("update", organization, project, task),
        {"status": Task.Status.DONE, "title": "Tampered title"},
    )

    assert response.status_code == 302
    task.refresh_from_db()
    assert task.status == Task.Status.DONE
    assert task.title == "Assigned task"
    assert task.completed_at is not None


def test_unassigned_member_cannot_update_task(
    client,
    member,
    organization,
    project,
    task,
):
    task.assignee = None
    task.save()
    client.force_login(member)
    response = client.get(task_url("update", organization, project, task))

    assert response.status_code == 403


def test_owner_can_update_any_task(
    client,
    owner,
    organization,
    project,
    task,
    admin_user,
):
    client.force_login(owner)
    response = client.post(
        task_url("update", organization, project, task),
        {
            "title": "Manager update",
            "description": "Changed",
            "status": Task.Status.IN_PROGRESS,
            "priority": Task.Priority.LOW,
            "assignee": admin_user.pk,
            "due_date": "2026-12-20",
        },
    )

    assert response.status_code == 302
    task.refresh_from_db()
    assert task.title == "Manager update"
    assert task.assignee == admin_user


def test_outsider_cannot_view_task(
    client,
    outsider,
    organization,
    project,
    task,
):
    client.force_login(outsider)
    response = client.get(task_url("detail", organization, project, task))

    assert response.status_code == 404


def test_task_list_filters_and_searches(
    client,
    member,
    organization,
    project,
    task,
    owner,
):
    Task.objects.create(
        project=project,
        title="Unique planning note",
        status=Task.Status.DONE,
        priority=Task.Priority.LOW,
        created_by=owner,
    )
    client.force_login(member)
    url = reverse("tasks:list", args=[organization.slug])
    response = client.get(
        url,
        {
            "q": "Unique planning",
            "status": Task.Status.DONE,
            "priority": Task.Priority.LOW,
            "project": project.pk,
        },
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert "Unique planning note" in content
    assert task.title not in content


def test_task_list_filters_by_assignee(
    client,
    member,
    organization,
    task,
):
    client.force_login(member)
    response = client.get(
        reverse("tasks:list", args=[organization.slug]),
        {"assignee": member.pk},
    )

    assert task.title in response.content.decode()


def test_priority_ordering_puts_urgent_first(
    client,
    member,
    organization,
    project,
    task,
    owner,
):
    urgent = Task.objects.create(
        project=project,
        title="Urgent task",
        priority=Task.Priority.URGENT,
        created_by=owner,
    )
    client.force_login(member)
    response = client.get(
        reverse("tasks:list", args=[organization.slug]),
        {"ordering": "priority"},
    )

    assert list(response.context["tasks"])[0] == urgent


def test_htmx_filter_returns_task_list_partial(
    client,
    member,
    organization,
    task,
):
    client.force_login(member)
    response = client.get(
        reverse("tasks:list", args=[organization.slug]),
        HTTP_HX_REQUEST="true",
    )
    content = response.content.decode()

    assert response.status_code == 200
    assert 'id="task-list"' in content
    assert "<!doctype html>" not in content
