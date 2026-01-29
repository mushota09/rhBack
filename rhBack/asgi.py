"""
ASGI config for rhBack project.
"""

import os
from django.core.asgi import get_asgi_application

# Import Celery app to ensure it's loaded
from .celery import app as celery_app

__all__ = ('celery_app',)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rhBack.settings')

application = get_asgi_application()
