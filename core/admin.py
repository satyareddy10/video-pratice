from django.contrib import admin
from django.apps import apps

# Get all models from the current app ('core')
app_models = apps.get_app_config('core').get_models()

for model in app_models:
    try:
        # Register the model if it's not already registered
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
