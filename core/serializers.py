from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'domain', 'is_active']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT response to include user details and organization info.
    """
    def validate(self, attrs):
        # The base validate() handles email/password check
        data = super().validate(attrs)
        
        user = self.user
        request = self.context.get('request')
        current_org = getattr(request, 'organization', None)

        # SECURITY: Tenant Isolation Check
        if user.role == 'superadmin':
            # Superadmins ONLY allowed on the Main Platform
            if current_org is not None:
                raise serializers.ValidationError(
                    "Super Admins are only allowed to log in through the Main Platform portal."
                )
        else:
            # If we are on a subdomain, user MUST belong to that specific organization
            if current_org and user.organization != current_org:
                raise serializers.ValidationError(
                    "You do not have access to this organization portal."
                )
            
            # If we are on the main platform, user MUST have organization=None
            if not current_org and user.organization is not None:
                raise serializers.ValidationError(
                    "Please log in through your specific organization subdomain."
                )

        # Add custom data to the response
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.role,
            'organization': user.organization.name if user.organization else "Platform"
        }
        
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims into the token payload (visible when decoded)
        token['role'] = user.role
        token['org_id'] = user.organization.id if user.organization else None
        
        return token
