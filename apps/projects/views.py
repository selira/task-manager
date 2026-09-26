from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.organizations.permissions import (
    get_membership,
    get_organization_for_user,
    require_manager,
)

from .forms import ProjectForm
from .models import Project

# Create your views here.


@login_required
def project_list(request, organization_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    projects = Project.objects.visible_to(request.user).filter(organization=organization)
    return render(
        request,
        "projects/list.html",
        {
            "organization": organization,
            "projects": projects,
            "membership": get_membership(request.user, organization),
        },
    )


@login_required
def project_detail(request, organization_slug, project_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    project = get_object_or_404(
        Project.objects.visible_to(request.user),
        organization=organization,
        slug=project_slug,
    )
    tasks = project.tasks.select_related("assignee").order_by("-updated_at")
    return render(
        request,
        "projects/detail.html",
        {
            "organization": organization,
            "project": project,
            "tasks": tasks,
            "membership": get_membership(request.user, organization),
        },
    )


@login_required
def project_create(request, organization_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    require_manager(request.user, organization)
    form = ProjectForm(request.POST or None, organization=organization)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.organization = organization
        project.created_by = request.user
        project.save()
        messages.success(request, f"{project.name} was created.")
        return redirect(
            "projects:detail",
            organization_slug=organization.slug,
            project_slug=project.slug,
        )
    return render(
        request,
        "projects/form.html",
        {
            "organization": organization,
            "form": form,
            "page_title": "Create project",
        },
    )


@login_required
def project_update(request, organization_slug, project_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    require_manager(request.user, organization)
    project = get_object_or_404(
        Project.objects.visible_to(request.user),
        organization=organization,
        slug=project_slug,
    )
    form = ProjectForm(
        request.POST or None,
        instance=project,
        organization=organization,
    )
    if request.method == "POST" and form.is_valid():
        project = form.save()
        messages.success(request, f"{project.name} was updated.")
        return redirect(
            "projects:detail",
            organization_slug=organization.slug,
            project_slug=project.slug,
        )
    return render(
        request,
        "projects/form.html",
        {
            "organization": organization,
            "project": project,
            "form": form,
            "page_title": "Edit project",
        },
    )
