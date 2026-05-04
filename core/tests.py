from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory

from core.models import Organization
from core.permissions import IsPlatformSuperAdmin


TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}


@override_settings(CACHES=TEST_CACHES)
class IsPlatformSuperAdminTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = IsPlatformSuperAdmin()
        self.organization = Organization.objects.create(
            name="Acme",
            domain="acme.localhost",
            is_active=True,
        )

    def _build_request(self, *, organization=None, auth=None):
        request = self.factory.get("/api/organizations/")
        request.auth = auth
        request.organization = organization
        return request

    def test_allows_platform_superadmin_with_matching_claims(self):
        request = self._build_request(
            auth={"role": "superadmin", "org_id": None},
        )

        self.assertTrue(self.permission.has_permission(request, view=None))

    def test_denies_superadmin_when_token_has_tenant_claim(self):
        request = self._build_request(
            auth={"role": "superadmin", "org_id": self.organization.id},
        )

        self.assertFalse(self.permission.has_permission(request, view=None))

    def test_denies_superadmin_when_token_role_is_not_superadmin(self):
        request = self._build_request(
            auth={"role": "admin", "org_id": None},
        )

        self.assertFalse(self.permission.has_permission(request, view=None))

    def test_denies_superadmin_on_tenant_request(self):
        request = self._build_request(
            organization=self.organization,
            auth={"role": "superadmin", "org_id": None},
        )

        self.assertFalse(self.permission.has_permission(request, view=None))

    def test_denies_request_when_claims_are_missing(self):
        request = self._build_request(auth=None)

        self.assertFalse(self.permission.has_permission(request, view=None))
