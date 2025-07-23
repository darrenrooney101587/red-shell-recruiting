import os
import re
import traceback

from django.conf import settings
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.contrib import messages
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.views.generic import TemplateView

from red_shell_recruiting.models import (
    CandidateProfile,
    CandidateResume,
    CandidateCulinaryPortfolio,
)


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def terms_of_service(request):
    return render(request, "terms_of_service.html")


def healthcheck(request):
    return JsonResponse({"status": "ok"})


class LandingPageView(TemplateView):
    """
    Landing page view for the recruitment application.
    """

    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_count"] = CandidateProfile.objects.count()
        context["resume_count"] = CandidateResume.objects.count()
        context["portfolio_count"] = CandidateCulinaryPortfolio.objects.count()

        return context


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
        return ["landing", "privacy-policy", "terms-of-service"]

    def location(self, item):
        return reverse(item)
