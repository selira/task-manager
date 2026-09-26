from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from apps.organizations.permissions import get_organization_for_user, require_manager

from .forms import LoginForm, OrganizationUserCreationForm

# Create your views here.


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    pass


@login_required
def organization_user_create(request, organization_slug):
    organization = get_organization_for_user(request.user, organization_slug)
    require_manager(request.user, organization)
    form = OrganizationUserCreationForm(
        request.POST or None,
        organization=organization,
    )
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"{user.name} was added to {organization.name}.")
        return redirect("organizations:detail", slug=organization.slug)
    return render(
        request,
        "users/create.html",
        {"form": form, "organization": organization},
    )
