from django import forms

from apps.projects.models import Project
from apps.users.models import User

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "status", "priority", "assignee", "due_date")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, project, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.project = project
        self.fields["assignee"].queryset = User.objects.filter(
            memberships__organization=project.organization
        )


class AssignedTaskStatusForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("status",)


class TaskFilterForm(forms.Form):
    ORDERING_CHOICES = [
        ("-created_at", "Newest"),
        ("-updated_at", "Recently updated"),
        ("due_date", "Due date"),
        ("priority", "Priority"),
    ]

    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All statuses"), *Task.Status.choices],
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[("", "All priorities"), *Task.Priority.choices],
    )
    project = forms.ModelChoiceField(
        required=False,
        queryset=Project.objects.none(),
        empty_label="All projects",
    )
    assignee = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.none(),
        empty_label="All assignees",
    )
    ordering = forms.ChoiceField(choices=ORDERING_CHOICES, required=False)

    def __init__(self, *args, organization, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = organization.projects.all()
        self.fields["assignee"].queryset = User.objects.filter(
            memberships__organization=organization
        )
