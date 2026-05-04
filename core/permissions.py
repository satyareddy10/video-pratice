from rest_framework.permissions import BasePermission


class IsPlatformSuperAdmin(BasePermission):
    """
    Allows access only to authenticated platform-level superadmins.
    """

    message = "Only platform superadmins can access this endpoint."

    def has_permission(self, request, view):
        token = getattr(request, "auth", None)
        if not token:
            return False

        token_role = token.get("role")
        token_org_id = token.get("org_id")

        is_platform_request = getattr(request, "organization", None) is None
        return (
            is_platform_request
            and token_role == "superadmin"
            and token_org_id is None
        )
