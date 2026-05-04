from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Organization

@receiver(post_save, sender=Organization)
@receiver(post_delete, sender=Organization)
def invalidate_tenant_cache(sender, instance, **kwargs):
    """
    Deletes the tenant cache whenever an Organization is created, updated, or deleted.
    This ensures that changes to domains or active status are reflected immediately
    in the middleware.
    """
    cache_key = f"tenant_data_{instance.domain}"
    cache.delete(cache_key)
