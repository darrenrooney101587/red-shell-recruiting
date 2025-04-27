from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.contrib import messages

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
    return render(request, "500.html", status=500)
