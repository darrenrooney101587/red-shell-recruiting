#!/bin/bash
poetry run python manage.py migrate || { echo 'Migration failed!'; }

echo 'Collecting static files...(this may start the application by default)'
poetry run python manage.py collectstatic --noinput --clear || { echo 'Failed to clear static files!'; }
echo 'Done collecting static files....'

chmod -R a+rX /app/staticfiles || { echo 'Failed to set static file permissions!'; }

# Create Django superuser if not exists using environment variables
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_PASSWORD=admin1234!
poetry run python manage.py createsuperuser --noinput || true

echo "Starting Gunicorn for local/dev..."
exec poetry run gunicorn app_admin.wsgi \
    --name admin \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-config config/gunicorn_logging.conf \
    --log-level=info
