# subforum/admin.py
from django.contrib import admin
from .models import Projects  # Import your model(s)

# Register the model to appear in the admin interface
admin.site.register(Projects)
