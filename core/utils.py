import os

def tenant_directory_path(instance, filename):
    """
    Organizes file uploads into tenant-specific folders.
    Format: uploads/tenant_<id>/<model_name>/<filename>
    """
    tenant_id = "global"
    if hasattr(instance, 'organization') and instance.organization:
        tenant_id = f"tenant_{instance.organization.id}"
    
    model_name = instance.__class__.__name__.lower()
    return os.path.join('uploads', tenant_id, model_name, filename)
