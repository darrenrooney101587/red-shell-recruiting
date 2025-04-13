from django.urls import path
from mechanic import views
from mechanic.utilities import test_database_connection

urlpatterns = [
    path('', views.index, name='mechanic-index'),
    path("test-db/", test_database_connection, name="test-database-connection"),
]
