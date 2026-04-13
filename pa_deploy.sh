#!/bin/bash

# Configuration
PROJECT_DIR=~/Wardrobe_Management
VENV_DIR=~/pa_venv

echo "--- Starting PythonAnywhere Deploy ---"

# 1. Pull latest code
cd $PROJECT_DIR
git pull origin main

# 2. Setup Virtual Environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# 3. Install requirements
source $VENV_DIR/bin/activate
pip install -r requirements.txt

# 4. Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate

echo "--- Deploy Finished! ---"
echo "Please remember to click 'Reload' on your Web tab in PythonAnywhere."
