from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.forms.models import model_to_dict
from .models import Organization
from .context import set_current_tenant, clear_current_tenant

class TenantMiddleware:
    """
    Zero-DB Hit Middleware with JSON error responses for APIs.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Bypass for internal Django Admin or static files
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)

        # 2. Bypass for OPTIONS (CORS Preflight)
        if request.method == 'OPTIONS':
            return self.get_response(request)

        # 3. Mandatory Tenant Header for all other API requests
        host = request.headers.get('X-Tenant-Domain')
        
        if not host:
            return JsonResponse({
                "status": "error",
                "code": "tenant_header_missing",
                "message": "The 'X-Tenant-Domain' header is required for all API requests."
            }, status=400)
        
        # Strip port if present
        host = host.split(':')[0]
        
        print(f"--- [Middleware] GATEWAY: {host} (Path: {request.path}) ---")
        # 1. Bypass for main domain
        if host == getattr(settings, 'TENANT_MAIN_DOMAIN', None):
            request.organization = None
            set_current_tenant(None)
            return self.get_response(request)

        # 2. Check Cache for FULL DICTIONARY
        cache_key = f"tenant_data_{host}"
        org_data = cache.get(cache_key)

        if org_data:
            org = Organization(**org_data)
        else:
            try:
                org = Organization.objects.get(domain=host)
            except Organization.DoesNotExist:
                return JsonResponse({
                    "status": "error",
                    "code": "tenant_not_found",
                    "message": "Domain not configured. Please contact the administrator.",
                    "domain": host
                }, status=404)
            
            if not org.is_active:
                cache.set(cache_key, model_to_dict(org), 3600)
                return JsonResponse({
                    "status": "error",
                    "code": "organization_inactive",
                    "message": "This organization is currently inactive. Please contact support."
                }, status=403)
            
            cache.set(cache_key, model_to_dict(org), 3600)

        # Success: Set the organization and the context
        request.organization = org
        # set_current_tenant(org)
        
        response = self.get_response(request)
        
        # CLEAR context after request
        # clear_current_tenant()
        return response
