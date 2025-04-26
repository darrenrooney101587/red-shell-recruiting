#!/bin/bash
poetry run python manage.py migrate || { echo 'Migration failed!'; }

echo 'Collecting static files...(this may start the application be default)'
# Use --clear to clear out the existing files and then collect static files
# adding  /dev/null 2>&1 to suppress printouts
poetry run python manage.py collectstatic --noinput --clear || { echo 'Failed to clear static files!'; }
echo 'Done collecting static files....'

#PORT=${PORT:-5000}
#echo "Using PORT: $PORT"
#sed -i "s/__PORT__/$PORT/g" /etc/nginx/sites-available/django_nginx.conf

#cat /etc/nginx/sites-available/django_nginx.conf
#
## Start Gunicorn processes
#echo 'Starting nginx...'
#nginx -g "daemon on;"
#if [ $? -eq 0 ]; then
#    echo 'Nginx started successfully...'
#else
#    echo 'Failed to start Nginx...'
#    exit 1
#fi

echo "Starting Gunicorn..."
exec poetry run gunicorn app_admin.wsgi \
    --name reporting-sync-server \
    --bind unix:/app/reporting-sync-server.sock \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    --log-config config/gunicorn_logging.conf \
    --log-level=info
