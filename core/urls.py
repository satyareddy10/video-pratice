from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import OrganizationListCreateView, TenantCheckView, LoginView

urlpatterns = [
    # Organization Management
    path('organizations/', OrganizationListCreateView.as_view(), name='organization-list'),
    
    # Tenant Identification (Frontend calls this first)
    path('check-tenant/', TenantCheckView.as_view(), name='check-tenant'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
