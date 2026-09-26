import pytest

from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_create_user_uses_email_as_identity():
    user = User.objects.create_user(
        email="person@EXAMPLE.COM",
        name="Person",
        password="strong-pass-123",
    )

    assert user.email == "person@example.com"
    assert user.check_password("strong-pass-123")
    assert user.get_username() == "person@example.com"


def test_create_user_requires_email():
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user(email="", name="Person")


def test_create_superuser_sets_required_flags():
    user = User.objects.create_superuser(
        email="staff@example.com",
        name="Staff",
        password="strong-pass-123",
    )

    assert user.is_staff
    assert user.is_superuser
