from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Membership, Organization

MANAGER_ROLES = (Membership.Role.OWNER, Membership.Role.ADMIN)


def get_organization_for_user(user, slug):
    return get_object_or_404(Organization.objects.visible_to(user), slug=slug)


def get_membership(user, organization):
    return Membership.objects.filter(user=user, organization=organization).first()


def require_manager(user, organization):
    membership = get_membership(user, organization)
    if membership is None or membership.role not in MANAGER_ROLES:
        raise PermissionDenied
    return membership
