# 🚀 PythonAnywhere Deployment Guide

Follow these steps to host your **Wardrobe Management** system on PythonAnywhere.

## 1. Upload Your Code
1. Log in to [PythonAnywhere](https://www.pythonanywhere.com/).
2. Go to the **Files** tab.
3. Open the /home/yourusername/ directory.
4. Upload your project folder (you can zip it first, upload, and unzip using the **Consoles** tab with `unzip filename.zip`).

## 2. Set Up the Virtual Environment
Open a **Bash Console** and run these commands:

```bash
# Go to your project directory
cd Wardrobe_Management

# Create a virtual environment (use Python 3.10+)
mkvirtualenv --python=/usr/bin/python3.10 wardrobe-env

# Install the dependencies
pip install -r requirements.txt
```

## 3. Configure the Web Tab
Go to the **Web** tab on PythonAnywhere:
1. Click **Add a new web app**.
2. Choose **Manual Configuration** (do NOT choose the Django option, as we have a customized setup).
3. Select **Python 3.10**.
4. In the **Virtualenv** section, enter: `/home/yourusername/.virtualenvs/wardrobe-env`.
5. In the **Code** section:
   - **Source code**: `/home/yourusername/Wardrobe_Management`
   - **Working directory**: `/home/yourusername/Wardrobe_Management`

## 4. Edit the WSGI Configuration
In the **Web** tab, click the link to your **WSGI configuration file**. Replace its content with:

```python
import os
import sys

# Add your project directory to sys.path
path = '/home/yourusername/Wardrobe_Management'
if path not in sys.path:
    sys.path.insert(0, path)

# Add the apps directory to sys.path
apps_path = os.path.join(path, 'apps')
if apps_path not in sys.path:
    sys.path.insert(0, apps_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'main.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 5. Static & Media Files
Under the **Static files** section of the **Web** tab, add these mappings:
- **URL**: `/static/`  -> **Path**: `/home/yourusername/Wardrobe_Management/staticfiles`
- **URL**: `/media/`   -> **Path**: `/home/yourusername/Wardrobe_Management/media`

## 6. Final Steps (Console)
Go back to your **Bash Console** and run:

```bash
# Prepare static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

## 7. Environment Variables
If you are using a `.env` file for your `SECRET_KEY` or AI API keys, make sure to upload it to your project root on PythonAnywhere.

---
**Done!** Hit the **Reload** button on the Web tab, and your site should be live at `yourusername.pythonanywhere.com`.
