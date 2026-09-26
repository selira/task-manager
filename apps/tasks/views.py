from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Case, F, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render

from apps.organizations.permissions import (
    MANAGER_ROLES,
    get_membership,
    get_organization_for_user,
    require_manager,
)
from apps.projects.models import Project

from .forms import AssignedTaskStatusForm, TaskFilterForm, TaskForm
from .models import Task

# Create your views here.


@login_required
def task_list(request, organization_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    tasks = (
        Task.objects.visible_to(request.user)
        .filter(project__organization=organization)
        .select_related("project", "assignee")
    )
    form = TaskFilterForm(request.GET or None, organization=organization)
    if form.is_valid():
        filters = form.cleaned_data
        if filters["q"]:
            tasks = tasks.filter(
                Q(title__icontains=filters["q"])
                | Q(description__icontains=filters["q"])
                | Q(project__name__icontains=filters["q"])
            )
        if filters["status"]:
            tasks = tasks.filter(status=filters["status"])
        if filters["priority"]:
            tasks = tasks.filter(priority=filters["priority"])
        if filters["project"]:
            tasks = tasks.filter(project=filters["project"])
        if filters["assignee"]:
            tasks = tasks.filter(assignee=filters["assignee"])
        ordering = filters["ordering"] or "-created_at"
        if ordering == "priority":
            tasks = tasks.annotate(
                priority_order=Case(
                    When(priority=Task.Priority.URGENT, then=Value(0)),
                    When(priority=Task.Priority.HIGH, then=Value(1)),
                    When(priority=Task.Priority.MEDIUM, then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            ).order_by("priority_order", "due_date")
        elif ordering == "due_date":
            tasks = tasks.order_by(F("due_date").asc(nulls_last=True), "-created_at")
        else:
            tasks = tasks.order_by(ordering)
    context = {
        "organization": organization,
        "tasks": tasks,
        "filter_form": form,
        "membership": get_membership(request.user, organization),
    }
    if request.headers.get("HX-Request") == "true":
        return render(request, "tasks/_task_list.html", context)
    return render(request, "tasks/list.html", context)


@login_required
def task_detail(request, organization_slug, project_slug, task_id):
    organization = get_organization_for_user(request.user, organization_slug)
    task = get_object_or_404(
        Task.objects.visible_to(request.user).select_related(
            "project",
            "assignee",
            "created_by",
        ),
        pk=task_id,
        project__organization=organization,
        project__slug=project_slug,
    )
    return render(
        request,
        "tasks/detail.html",
        {
            "organization": organization,
            "project": task.project,
            "task": task,
            "membership": get_membership(request.user, organization),
        },
    )


@login_required
def task_create(request, organization_slug, project_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    require_manager(request.user, organization)
    project = get_object_or_404(
        Project.objects.visible_to(request.user),
        organization=organization,
        slug=project_slug,
    )
    form = TaskForm(request.POST or None, project=project)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        messages.success(request, f"{task.title} was created.")
        return redirect(
            "tasks:detail",
            organization_slug=organization.slug,
            project_slug=project.slug,
            task_id=task.pk,
        )
    return render(
        request,
        "tasks/form.html",
        {
            "organization": organization,
            "project": project,
            "form": form,
            "page_title": "Create task",
        },
    )


@login_required
def task_update(request, organization_slug, project_slug, task_id):
    organization = get_organization_for_user(request.user, organization_slug)
    task = get_object_or_404(
        Task.objects.visible_to(request.user).select_related("project"),
        pk=task_id,
        project__organization=organization,
        project__slug=project_slug,
    )
    membership = get_membership(request.user, organization)
    is_manager = membership.role in MANAGER_ROLES
    if not is_manager and task.assignee_id != request.user.pk:
        raise PermissionDenied
    form_class = TaskForm if is_manager else AssignedTaskStatusForm
    form_kwargs = {"data": request.POST or None, "instance": task}
    if is_manager:
        form_kwargs["project"] = task.project
    form = form_class(**form_kwargs)
    if request.method == "POST" and form.is_valid():
        task = form.save()
        messages.success(request, f"{task.title} was updated.")
        return redirect(
            "tasks:detail",
            organization_slug=organization.slug,
            project_slug=task.project.slug,
            task_id=task.pk,
        )
    return render(
        request,
        "tasks/form.html",
        {
            "organization": organization,
            "project": task.project,
            "task": task,
            "form": form,
            "page_title": "Update task",
            "status_only": not is_manager,
        },
    )
