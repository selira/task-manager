from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from apps.organizations.models import Membership

from .models import User


class LoginForm(AuthenticationForm):
    pass


class OrganizationUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[
            (Membership.Role.ADMIN, Membership.Role.ADMIN.label),
            (Membership.Role.MEMBER, Membership.Role.MEMBER.label),
        ]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "name", "role")

    def __init__(self, *args, organization, **kwargs):
        self.organization = organization
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Membership.objects.create(
                organization=self.organization,
                user=user,
                role=self.cleaned_data["role"],
            )
        return user
