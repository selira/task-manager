from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

# Create your models here.


class OrganizationQuerySet(models.QuerySet):
    def visible_to(self, user):
        if not user.is_authenticated:
            return self.none()
        return self.filter(memberships__user=user).distinct()


class OrganizationManager(models.Manager.from_queryset(OrganizationQuerySet)):
    @transaction.atomic
    def create_with_owner(self, *, owner, **organization_fields):
        organization = self.create(**organization_fields)
        Membership.objects.create(
            organization=organization,
            user=owner,
            role=Membership.Role.OWNER,
        )
        return organization


class Organization(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OrganizationManager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MembershipQuerySet(models.QuerySet):
    def managers(self):
        return self.filter(role__in=[Membership.Role.OWNER, Membership.Role.ADMIN])


class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MembershipQuerySet.as_manager()

    class Meta:
        ordering = ["organization__name", "user__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_organization_membership",
            )
        ]
        indexes = [models.Index(fields=["organization", "role"])]

    def __str__(self):
        return f"{self.user} · {self.organization} · {self.get_role_display()}"

    def clean(self):
        super().clean()
        if not self.pk:
            return
        previous_role = type(self).objects.filter(pk=self.pk).values_list("role", flat=True).first()
        if (
            previous_role == self.Role.OWNER
            and self.role != self.Role.OWNER
            and not type(self)
            .objects.filter(organization=self.organization, role=self.Role.OWNER)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError({"role": "An organization must have an owner."})

    def delete(self, *args, **kwargs):
        if (
            self.role == self.Role.OWNER
            and not type(self)
            .objects.filter(organization=self.organization, role=self.Role.OWNER)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("An organization must have an owner.")
        return super().delete(*args, **kwargs)
