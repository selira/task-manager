from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.organizations.models import Membership, Organization
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User


class Command(BaseCommand):
    help = "Create a deterministic development dataset."

    def handle(self, *args, **options):
        call_command("flush", interactive=False, verbosity=0)

        users = {}
        user_data = [
            ("alex@example.com", "Alex Morgan", True),
            ("blair@example.com", "Blair Chen", False),
            ("casey@example.com", "Casey Rivera", False),
            ("devon@example.com", "Devon Patel", False),
        ]
        for email, name, is_staff in user_data:
            user, _ = User.objects.update_or_create(
                email=email,
                defaults={"name": name, "is_active": True, "is_staff": is_staff},
            )
            user.set_password("demo-pass-123")
            user.save(update_fields=["password"])
            users[email] = user

        acme, _ = Organization.objects.update_or_create(
            slug="acme-studio",
            defaults={"name": "Acme Studio"},
        )
        northstar, _ = Organization.objects.update_or_create(
            slug="northstar-labs",
            defaults={"name": "Northstar Labs"},
        )

        membership_data = [
            (acme, users["alex@example.com"], Membership.Role.OWNER),
            (acme, users["blair@example.com"], Membership.Role.ADMIN),
            (acme, users["casey@example.com"], Membership.Role.MEMBER),
            (northstar, users["devon@example.com"], Membership.Role.OWNER),
            (northstar, users["casey@example.com"], Membership.Role.MEMBER),
        ]
        for organization, user, role in membership_data:
            Membership.objects.update_or_create(
                organization=organization,
                user=user,
                defaults={"role": role},
            )

        website, _ = Project.objects.update_or_create(
            organization=acme,
            slug="website-redesign",
            defaults={
                "name": "Website Redesign",
                "description": "Refresh the public website and improve mobile navigation.",
                "status": Project.Status.ACTIVE,
                "created_by": users["alex@example.com"],
            },
        )
        onboarding, _ = Project.objects.update_or_create(
            organization=acme,
            slug="client-onboarding",
            defaults={
                "name": "Client Onboarding",
                "description": "Standardize the onboarding process for new clients.",
                "status": Project.Status.COMPLETED,
                "created_by": users["blair@example.com"],
            },
        )
        launch, _ = Project.objects.update_or_create(
            organization=northstar,
            slug="autumn-launch",
            defaults={
                "name": "Autumn Launch",
                "description": "Coordinate the autumn product release.",
                "status": Project.Status.ACTIVE,
                "created_by": users["devon@example.com"],
            },
        )

        task_data = [
            (
                website,
                "Fix mobile navigation",
                {
                    "description": "Resolve menu overflow and improve keyboard controls.",
                    "status": Task.Status.IN_PROGRESS,
                    "priority": Task.Priority.HIGH,
                    "assignee": users["casey@example.com"],
                    "created_by": users["alex@example.com"],
                    "due_date": date(2026, 10, 5),
                },
            ),
            (
                website,
                "Review homepage copy",
                {
                    "description": "Complete a final editorial review before publishing.",
                    "status": Task.Status.TODO,
                    "priority": Task.Priority.MEDIUM,
                    "assignee": users["blair@example.com"],
                    "created_by": users["alex@example.com"],
                    "due_date": date(2026, 10, 8),
                },
            ),
            (
                website,
                "Audit image sizes",
                {
                    "description": "Identify images that need responsive variants.",
                    "status": Task.Status.TODO,
                    "priority": Task.Priority.LOW,
                    "assignee": None,
                    "created_by": users["blair@example.com"],
                    "due_date": None,
                },
            ),
            (
                onboarding,
                "Publish kickoff checklist",
                {
                    "description": "Make the approved checklist available to the team.",
                    "status": Task.Status.DONE,
                    "priority": Task.Priority.HIGH,
                    "assignee": users["casey@example.com"],
                    "created_by": users["blair@example.com"],
                    "due_date": date(2026, 9, 15),
                },
            ),
            (
                launch,
                "Confirm release window",
                {
                    "description": "Get final release timing from all stakeholders.",
                    "status": Task.Status.IN_PROGRESS,
                    "priority": Task.Priority.URGENT,
                    "assignee": users["devon@example.com"],
                    "created_by": users["devon@example.com"],
                    "due_date": date(2026, 10, 1),
                },
            ),
            (
                launch,
                "Prepare support brief",
                {
                    "description": "Summarize launch changes for the support team.",
                    "status": Task.Status.TODO,
                    "priority": Task.Priority.MEDIUM,
                    "assignee": None,
                    "created_by": users["devon@example.com"],
                    "due_date": date(2026, 10, 10),
                },
            ),
        ]
        for project, title, defaults in task_data:
            Task.objects.update_or_create(
                project=project,
                title=title,
                defaults=defaults,
            )

        self.stdout.write(self.style.SUCCESS("Seed data is ready."))
        self.stdout.write("Log in with alex@example.com and demo-pass-123.")
