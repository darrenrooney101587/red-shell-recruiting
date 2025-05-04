#!/bin/bash
poetry run python manage.py migrate || { echo 'Migration failed!'; }

echo 'Collecting static files...(this may start the application be default)'
# Use --clear to clear out the existing files and then collect static files
# adding  /dev/null 2>&1 to suppress printouts
poetry run python manage.py collectstatic --noinput --clear || { echo 'Failed to clear static files!'; }
echo 'Done collecting static files....'

chmod -R a+rX /app/staticfiles || { echo 'Failed to set static file permissions!'; }


BIND_ADDRESS=${BIND_ADDRESS:-0.0.0.0:5000}

echo "Starting Gunicorn..."
exec poetry run gunicorn app_admin.wsgi \
    --name reporting-sync-server \
    --bind ${BIND_ADDRESS} \
    --bind unix:/app/reporting-sync-server.sock \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-config config/gunicorn_logging.conf \
    --log-level=info
