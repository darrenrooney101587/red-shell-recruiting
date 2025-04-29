#!/bin/bash

echo "Starting Celery worker..."
celery -A app_admin worker --loglevel=info
