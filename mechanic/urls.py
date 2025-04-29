from django.urls import path
from mechanic import views
from mechanic.utilities import test_database_connection
from mechanic.views import redis_celery_connection

urlpatterns = [
    path("", views.index, name="mechanic-index"),
    path("test-db/", test_database_connection, name="test-database-connection"),
    path(
        "test-redis-celery-connection/",
        redis_celery_connection,
        name="test-redis-celery-connection",
    ),
]
