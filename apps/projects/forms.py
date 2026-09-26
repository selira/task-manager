from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "slug", "description", "status")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def __init__(self, *args, organization, **kwargs):
        self.organization = organization
        super().__init__(*args, **kwargs)
        self.instance.organization = organization

    def clean_slug(self):
        slug = self.cleaned_data["slug"]
        projects = Project.objects.filter(organization=self.organization, slug=slug)
        if self.instance.pk:
            projects = projects.exclude(pk=self.instance.pk)
        if projects.exists():
            raise forms.ValidationError(
                "A project with this slug already exists in the organization."
            )
        return slug
