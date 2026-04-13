import os
import sys

# Add project root and apps to path
# Vercel's root is the folder containing vercel.json
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.insert(0, path)

# Add apps folder
apps_path = os.path.join(path, 'apps')
if apps_path not in sys.path:
    sys.path.insert(0, apps_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise e
