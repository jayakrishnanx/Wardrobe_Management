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

app = None
try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception:
    import traceback
    error_msg = traceback.format_exc()
    
    def error_app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        html = f"""
        <html>
        <head><title>Vercel Rescue: Startup Error</title></head>
        <body style="font-family: sans-serif; padding: 20px; line-height: 1.5;">
            <h1 style="color: #e11d48;">⚠️ Django Startup Failed</h1>
            <p>This page is a debug wrapper. The error below is why your site is showing a 500 error:</p>
            <pre style="background: #f4f4f5; padding: 15px; border-radius: 8px; overflow-x: auto; border: 1px solid #e4e4e7;">{error_msg}</pre>
        </body>
        </html>
        """
        return [html.encode('utf-8')]
    
    app = error_app
