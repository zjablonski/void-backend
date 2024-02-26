#!/bin/bash

# Start the Celery worker in the background
celery -A main.celery worker --loglevel=info &
# Start the Flask app in the background
gunicorn main:app