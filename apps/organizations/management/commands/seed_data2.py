from datetime import date, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.organizations.models import Membership, Organization
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.users.models import User


class Command(BaseCommand):
    help = "Replace the database contents with a larger UI test dataset."

    def handle(self, *args, **options):
        call_command("flush", interactive=False, verbosity=0)

        password = "load-test-pass-123"
        users = []
        for number in range(1, 21):
            user = User.objects.create_user(
                email=f"user{number:02d}@example.com",
                name=f"Demo User {number:02d}",
                password=password,
                is_staff=number == 1,
            )
            users.append(user)

        owner = users[0]
        organizations = [
            Organization.objects.create_with_owner(
                owner=owner,
                name="UI Load Test Organization",
                slug="ui-load-test",
            )
        ]
        for number in range(2, 21):
            organizations.append(
                Organization.objects.create_with_owner(
                    owner=owner,
                    name=f"Demo Organization {number:02d}",
                    slug=f"demo-organization-{number:02d}",
                )
            )

        primary_organization = organizations[0]
        for number, user in enumerate(users[1:], start=2):
            role = Membership.Role.ADMIN if number <= 5 else Membership.Role.MEMBER
            Membership.objects.create(
                organization=primary_organization,
                user=user,
                role=role,
            )

        projects = []
        for number in range(1, 21):
            project = Project.objects.create(
                organization=primary_organization,
                name=f"Demo Project {number:02d}",
                slug=f"demo-project-{number:02d}",
                description=(
                    f"Project {number:02d} exercises card layouts, status badges, "
                    "navigation, and longer descriptive content in the user interface."
                ),
                status=(Project.Status.COMPLETED if number % 5 == 0 else Project.Status.ACTIVE),
                created_by=owner,
            )
            projects.append(project)

        statuses = [
            Task.Status.TODO,
            Task.Status.IN_PROGRESS,
            Task.Status.DONE,
        ]
        priorities = [
            Task.Priority.LOW,
            Task.Priority.MEDIUM,
            Task.Priority.HIGH,
            Task.Priority.URGENT,
        ]
        task_names = [
            "Review account navigation and responsive sidebar behavior",
            "Validate form errors with unusually long submitted values",
            "Confirm task filtering and ordering combinations",
            "Prepare the next stakeholder progress update",
            "Check status and priority badge alignment",
        ]
        for number in range(1, 21):
            Task.objects.create(
                project=projects[0],
                title=f"Task {number:02d}: {task_names[(number - 1) % len(task_names)]}",
                description=(
                    f"This is load-test task {number:02d}. It provides enough descriptive "
                    "content to exercise wrapping, spacing, detail views, and table rows."
                ),
                status=statuses[(number - 1) % len(statuses)],
                priority=priorities[(number - 1) % len(priorities)],
                assignee=None if number % 5 == 0 else users[(number - 1) % len(users)],
                created_by=owner,
                due_date=date(2026, 10, 1) + timedelta(days=number - 1),
            )

        self.stdout.write(self.style.SUCCESS("Large seed dataset is ready."))
        self.stdout.write(f"Created {User.objects.count()} users.")
        self.stdout.write(f"Created {Organization.objects.count()} organizations.")
        self.stdout.write(f"Created {Project.objects.count()} projects.")
        self.stdout.write(f"Created {Task.objects.count()} tasks.")
        self.stdout.write(f"Log in with {owner.email} and {password}.")
