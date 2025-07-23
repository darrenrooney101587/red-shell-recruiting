from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from app_admin.views import (
    privacy_policy,
    terms_of_service,
    healthcheck,
    force_404,
    force_500,
    StaticViewSitemap,
    LandingPageView,
)
from red_shell_recruiting.views import index


sitemaps_dict = {
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("/home", index, name="home"),
    path("", LandingPageView.as_view(), name="landing"),
    path("admin/", admin.site.urls),
    path("healthz/", healthcheck),
    path("mechanic/", include("mechanic.urls")),
    path("account/", include("account.urls")),
    path("candidate/", include("red_shell_recruiting.urls")),
    path("privacy_policy/", privacy_policy, name="privacy-policy"),
    path("terms_of_service/", terms_of_service, name="terms-of-service"),
    path("force-404/", force_404, name="force-404"),
    path("force-500/", force_500, name="force-500"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps_dict},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG and settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
