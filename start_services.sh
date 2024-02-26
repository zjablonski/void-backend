#!/bin/bash

# Start the Flask app in the background
gunicorn main:app &

# Start the Celery worker
celery -A yourapp.celery worker --loglevel=info