import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_admin.settings')
app = Celery('app_admin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
