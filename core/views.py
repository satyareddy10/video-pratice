from django.conf import settings
from rest_framework import permissions, status, views, response
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Organization
from .permissions import IsPlatformSuperAdmin
from .serializers import OrganizationSerializer, CustomTokenObtainPairSerializer

class OrganizationListCreateView(views.APIView):
    permission_classes = [IsPlatformSuperAdmin]

    def get(self, request):
        orgs = Organization.objects.all()
        serializer = OrganizationSerializer(orgs, many=True)
        return response.Response(serializer.data)

    def post(self, request):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TenantCheckView(views.APIView):
    """
    The 'Initialization' API. 
    The frontend calls this FIRST to know what to display.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        org = getattr(request, 'organization', None)
        host = request.get_host().split(':')[0]
        main_domain = settings.TENANT_MAIN_DOMAIN
        
        if org is None:
            # Check if this is exactly the main platform domain
            if host == main_domain:
                return response.Response({
                    "tenant_type": "PLATFORM",
                    "show_marketing": True,
                    "domain": host
                })
            else:
                # Security: This is a subdomain we don't recognize
                return response.Response({
                    "status": "error",
                    "code": "tenant_not_found",
                    "message": "Domain not configured. Please contact the administrator.",
                    "domain": host
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Case 2: Valid Tenant
        return response.Response({
            "tenant_type": "ORGANIZATION",
            "organization_name": org.name,
            "show_login": True,
            "domain": org.domain
        })

class LoginView(TokenObtainPairView):
    """
    Secure Login API.
    Uses JWT and enforces tenant isolation.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
