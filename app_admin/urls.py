from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app_admin.views import privacy_policy, terms_of_service, healthcheck, force_404, force_500
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
    path('force-404/', force_404, name='force-404'),
    path('force-500/', force_500, name='force-500'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
