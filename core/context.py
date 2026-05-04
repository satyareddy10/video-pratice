import threading
from contextlib import contextmanager

_thread_locals = threading.local()

# --- ORGANIZATION CONTEXT ---

def set_current_tenant(organization):
    _thread_locals.organization = organization

def get_current_tenant():
    return getattr(_thread_locals, 'organization', None)

def is_tenant_filtering_disabled():
    return getattr(_thread_locals, 'tenant_filtering_disabled', False)

def clear_current_tenant():
    if hasattr(_thread_locals, 'organization'):
        del _thread_locals.organization
    _thread_locals.tenant_filtering_disabled = False

# --- OVERRIDE CONTEXT (The Master Key) ---

@contextmanager
def tenant_context_disabled():
    """
    Usage:
    with tenant_context_disabled():
        # Filtering is temporarily turned off here
        all_data = MyModel.objects.all()
    """
    previous_state = getattr(_thread_locals, 'tenant_filtering_disabled', False)
    _thread_locals.tenant_filtering_disabled = True
    try:
        yield
    finally:
        _thread_locals.tenant_filtering_disabled = previous_state
