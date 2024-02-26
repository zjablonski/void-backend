#!/bin/bash

# Start the Flask app in the background
gunicorn main:app &

# Start the Celery worker
celery -A main.celery worker --loglevel=info