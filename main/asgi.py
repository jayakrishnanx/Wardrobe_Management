"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import sys

from django.core.asgi import get_asgi_application

# Add 'apps' to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

application = get_asgi_application()
