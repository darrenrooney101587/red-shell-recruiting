#!/bin/bash
poetry run python manage.py migrate || { echo 'Migration failed!'; }

echo 'Collecting static files...(this may start the application be default)'
# Use --clear to clear out the existing files and then collect static files
# adding  /dev/null 2>&1 to suppress printouts
poetry run python manage.py collectstatic --noinput --clear || { echo 'Failed to clear static files!'; }
echo 'Done collecting static files....'

chmod -R a+rX /app/staticfiles || { echo 'Failed to set static file permissions!'; }

echo "Starting Gunicorn..."
exec poetry run gunicorn app_admin.wsgi \
    --name admin \
    --bind unix:/app/admin.sock \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-config config/gunicorn_logging.conf \
    --log-level=info
