from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import redirect, render

from .forms import OrganizationForm
from .models import Organization
from .permissions import get_membership, get_organization_for_user

# Create your views here.


@login_required
def organization_list(request):
    organizations = (
        Organization.objects.visible_to(request.user)
        .annotate(project_count=Count("projects", distinct=True))
        .prefetch_related("memberships")
    )
    return render(
        request,
        "organizations/list.html",
        {"organizations": organizations},
    )


@login_required
def organization_detail(request, slug):
    organization = get_organization_for_user(request.user, slug)
    memberships = organization.memberships.select_related("user")
    projects = organization.projects.select_related("created_by").order_by("-updated_at")
    return render(
        request,
        "organizations/detail.html",
        {
            "organization": organization,
            "memberships": memberships,
            "projects": projects,
            "membership": get_membership(request.user, organization),
        },
    )


@user_passes_test(lambda user: user.is_staff)
def organization_create(request):
    form = OrganizationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        organization = Organization.objects.create_with_owner(
            owner=request.user,
            **form.cleaned_data,
        )
        messages.success(request, f"{organization.name} was created.")
        return redirect("organizations:detail", slug=organization.slug)
    return render(
        request,
        "organizations/form.html",
        {"form": form, "page_title": "Create organization"},
    )
