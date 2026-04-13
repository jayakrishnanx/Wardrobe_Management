import os
import sys

# Add project root and apps to path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

apps_path = os.path.join(path, 'apps')
if apps_path not in sys.path:
    sys.path.insert(0, apps_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
