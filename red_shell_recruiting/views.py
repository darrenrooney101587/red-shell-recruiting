from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.views.generic import TemplateView

from red_shell_recruiting.tasks import update_resume_search_vector
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.db import IntegrityError, transaction

from red_shell_recruiting.models import CandidateProfile, Resume


def index(request):
    context = {}
    return render(request, 'red_shell_recruiting/index.html', context)


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

        try:
            with transaction.atomic():
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
                    resume = Resume.objects.create(
                        candidate=candidate,
                        file=candidate_resume
                    )

                    update_resume_search_vector.delay(resume.id) # async
                else:
                    raise IntegrityError("Resume upload failed.")

        except IntegrityError as e:
            messages.error(request, f"Error saving candidate: {str(e)}")
            return redirect('candidate-submit')

        messages.success(request, f"{first_name} {last_name} has been added.")
        return redirect('candidate-submit')



class CandidateSearch(TemplateView):
    template_name = 'red_shell_recruiting/candidate_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        candidates = CandidateProfile.objects.all()

        if query:
            search_query = SearchQuery(query)
            candidates = candidates.annotate(
                rank=SearchRank(SearchVector('search_document'), search_query)
            ).filter(
                search_document=search_query
            ).order_by('-rank')

        if self.request.GET.get('candidate-looking'):
            candidates = candidates.filter(actively_looking=True)

        if self.request.GET.get('candidate-relocation'):
            candidates = candidates.filter(open_to_relocation=True)

        if self.request.GET.get('currently-working'):
            candidates = candidates.filter(currently_working=True)

        context['candidates'] = candidates
        context['query'] = query
        return context
