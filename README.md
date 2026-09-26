# Task Manager

Task Manager is a server-rendered Django application for organizing projects and tasks within organizations. It provides email-based authentication, organization roles, project and task workflows, filtering, search, and an HTMX-enhanced interface.

## Requirements

- Python 3.12
- SQLite

## Setup

Create a virtual environment and install the project:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Create the database and optional sample data:

```bash
python manage.py migrate
python manage.py seed_data
```

Start the development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The seed command creates a staff owner account with:

- Email: `alex@example.com`
- Password: `demo-pass-123`

The command also prints these credentials and is safe to run repeatedly.

## Roles

- Owners manage projects, tasks, and organization users.
- Admins manage projects, tasks, and organization users.
- Members view organization data and update the status of tasks assigned to them.
- Staff users can create organizations and become their first owner.

Accounts are created by an organization owner or admin. New organization accounts can receive the Admin or Member role.

## Development

Run the test suite:

```bash
pytest
```

Run lint checks:

```bash
ruff check .
```

Check for model changes and validate the Django configuration:

```bash
python manage.py makemigrations --check
python manage.py check
```

The development configuration uses `config.settings.development`. Tests use `config.settings.test`.
