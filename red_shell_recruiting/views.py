from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView

from red_shell_recruiting.models import CandidateProfile, Resume


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


class CandidateEnter(View):
    template_name = 'red_shell_recruiting/candidate_input.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get('candidate-first-name')
        last_name = request.POST.get('candidate-last-name')
        job_title = request.POST.get('candidate-job-title')
        phone_number = request.POST.get('candidate-phone-number')
        email = request.POST.get('candidate-email')
        compensation = request.POST.get('candidate-compensation') or 0
        notes = request.POST.get('candidate-notes')
        candidate_state = request.POST.get('candidate-state')
        candidate_city = request.POST.get('candidate-city')
        actively_looking = bool(request.POST.get('candidate-looking'))
        open_to_relocation = bool(request.POST.get('candidate-relocation'))
        currently_working = bool(request.POST.get('candidate-working'))
        candidate_resume = request.FILES.get('candidate_resume')
        candidate = CandidateProfile.objects.create(
            first_name=first_name,
            last_name=last_name,
            state=candidate_state,
            city=candidate_city,
            job_title=job_title,
            phone_number=phone_number,
            email=email,
            compensation=compensation,
            notes=notes,
            open_to_relocation=open_to_relocation,
            currently_working=currently_working,
            actively_looking=actively_looking
        )

        if candidate_resume:
            Resume.objects.create(
                candidate=candidate,
                file=candidate_resume
            )

        return redirect('candidate-submit')
