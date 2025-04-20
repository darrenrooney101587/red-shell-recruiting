from django.contrib import admin
from django.urls import path, include

from red_shell_recruiting.views import index
from red_shell_recruiting.views import healthcheck

urlpatterns = [
    path('', index, name='home'),
    path("admin/", admin.site.urls),
    path("healthz/", healthcheck),
    path("mechanic/", include("mechanic.urls")),
    path("account/", include("account.urls"))
]
