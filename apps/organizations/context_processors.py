from .models import Organization


def organization_navigation(request):
    if not request.user.is_authenticated:
        return {"navigation_organizations": []}
    return {
        "navigation_organizations": Organization.objects.visible_to(request.user).only(
            "name",
            "slug",
        )
    }
