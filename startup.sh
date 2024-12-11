#!/bin/bash

# Define the path to your virtual environment and Django project
VENV_PATH="/home/fpf/env"
PROJECT_PATH="/home/fpf/FarmInsight-FPF-Backend/django_server"

# Activate the virtual environment
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated."
else
    echo "Virtual environment not found. Make sure the path is correct."
    exit 1
fi

# Navigate to your Django project directory
if [ -d "$PROJECT_PATH" ]; then
    cd "$PROJECT_PATH"
else
    echo "Django project directory not found. Make sure the path is correct."
    exit 1
fi

# Start the Django development server
python manage.py runserver

# Deactivate the virtual environment when done (optional)
deactivate