from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class Organization(models.Model):
    """
    The tenant model. Represents a single customer/organization.
    """
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True, help_text="The domain name used by this tenant to access the system (e.g. learn.client.com).")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

from .context import get_current_tenant, is_tenant_filtering_disabled

class TenantManager(models.Manager):
    def get_queryset(self):
        # 1. Master Key: If filtering is disabled, show EVERYTHING
        if is_tenant_filtering_disabled():
            return super().get_queryset()

        # 2. Get current tenant
        org = get_current_tenant()
        
        # 3. If a tenant is set, show THEIR data + GLOBAL data (org=None)
        if org:
            return super().get_queryset().filter(
                models.Q(organization=org) | models.Q(organization__isnull=True)
            )
            
        # 4. Main Platform: ONLY show Global data
        return super().get_queryset().filter(organization__isnull=True)

class TenantAwareModel(models.Model):
    """
    Abstract base class for all tenant-specific models.
    """
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name="%(app_label)s_%(class)s_related",
        null=True, 
        blank=True
    )

    # objects = TenantManager() # THE MAGIC HAPPENS HERE

    class Meta:
        abstract = True

class CustomUserManager(UserManager):
    """
    Custom manager that handles Email-only uniqueness. 
    Usernames are generated but do not need to be unique.
    """
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        # Auto-generate username from names (does not need to be unique)
        if not extra_fields.get('username'):
            first = extra_fields.get('first_name', '').lower().replace(' ', '')
            last = extra_fields.get('last_name', '').lower().replace(' ', '')
            extra_fields['username'] = f"{first}{last}"

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        if self.filter(role='superadmin').exists():
            raise ValueError('A Super Admin already exists. Only one is allowed for this platform.')

        extra_fields.setdefault('role', 'superadmin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('organization', None)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser, TenantAwareModel):
    """
    LMS User model where only Email is unique.
    Username is kept for compatibility but is non-unique.
    """
    # Override username to allow duplicates
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    ROLES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('learner', 'Learner'),
    )
    
    role = models.CharField(max_length=20, choices=ROLES, default='learner')
    
    # Use email for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} ({self.organization or 'Platform'})"
