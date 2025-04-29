import traceback

from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.contrib import messages
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def terms_of_service(request):
    return render(request, "terms_of_service.html")


def healthcheck(request):
    return JsonResponse({"status": "ok"})


def custom_403_view(request, exception=None):
    """
    Custom 403 handler to extract permission error messages
    and render the standalone 403.html page.
    """
    permission_error = None
    storage = messages.get_messages(request)
    for message in storage:
        if "permission" in str(message).lower():
            permission_error = message
            break

    return render(
        request, "403.html", {"permission_error": permission_error}, status=403
    )


def force_404(request):
    """Force a 404 error manually."""
    raise Http404("This page does not exist.")


def force_500(request):
    """Render 500 error template manually for testing."""
    try:
        raise Exception("This is a test 500 error.")
    except Exception:
        context = {"stacktrace": traceback.format_exc()}
        return render(request, "500.html", context=context, status=500)


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["home", "privacy-policy", "terms-of-service"]

    def location(self, item):
        return reverse(item)
