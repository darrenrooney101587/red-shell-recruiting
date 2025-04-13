from django.http import JsonResponse
from django.shortcuts import render
from django.contrib import messages


def index(request):
    context = {}
    return render(request, 'red_shell_recruiting/index.html', context)

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
