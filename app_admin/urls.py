from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app_admin.views import privacy_policy, terms_of_service, healthcheck
from red_shell_recruiting.views import index

urlpatterns = [
    path('', index, name='home'),
    path("admin/", admin.site.urls),
    path("healthz/", healthcheck),
    path("mechanic/", include("mechanic.urls")),
    path("account/", include("account.urls")),
    path("candidate/", include("red_shell_recruiting.urls")),
    path('privacy_policy/', privacy_policy, name='privacy-policy'),
    path('terms_of_service/', terms_of_service, name='terms-of-service'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
