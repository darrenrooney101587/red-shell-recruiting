import os
import re

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from user_agents import parse
from django.db.models import F, Count, Q
from django.db.models.expressions import RawSQL
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpRequest
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, Page

from red_shell_recruiting.tasks import (
    update_resume_search_vector,
    update_document_search_vector,
    update_portfolio_search_vector,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError, transaction

from red_shell_recruiting.models import (
    CandidateProfile,
    CandidateResume,
    CandidateDocument,
    CandidateClientPlacement,
    CandidateClientPlacementHistory,
    CandidateProfileTitle,
    CandidateOwnership,
    CandidateCulinaryPortfolio,
    CandidateProfileSource,
    JournalEntry,
)


@login_required
def index(request):
    """Home page for logged-in users. Shows welcome message and last 5 candidates entered by the user."""
    context = {
        "user_name": request.user.username,
        "candidates": CandidateProfile.objects.filter(created_by=request.user).order_by(
            "-created_at"
        )[:5],
        "total_profiles": CandidateProfile.objects.count(),
        "total_resumes": CandidateResume.objects.count(),
        "total_documents": CandidateDocument.objects.count(),
        "total_culinary_portfolios": CandidateCulinaryPortfolio.objects.count(),
        "total_journal_entries": JournalEntry.objects.count(),
        "total_placement_histories": CandidateClientPlacementHistory.objects.count(),
        "titles_with_counts": CandidateProfileTitle.objects.annotate(
            candidate_count=Count("candidateprofile", distinct=True)
        ).order_by("-candidate_count", "display_name"),
        "ownerships_with_counts": CandidateOwnership.objects.annotate(
            candidate_count=Count("candidateprofile", distinct=True)
        ).order_by("-candidate_count", "display_name"),
        "sources_with_counts": CandidateProfileSource.objects.annotate(
            candidate_count=Count("candidateprofile", distinct=True)
        ).order_by("-candidate_count", "display_name"),
    }
    return render(request, "red_shell_recruiting/index.html", context)


def svg_showcase(request):
    template_path = os.path.join(
        settings.BASE_DIR,
        "red_shell_recruiting",
        "templates",
        "red_shell_recruiting",
        "components",
        "svg_components.html",
    )
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    svg_types = re.findall(r"elif type == ['\"]([a-zA-Z0-9_\-]+)['\"]", content)

    return render(
        request, "red_shell_recruiting/svg_showcase.html", {"svg_types": svg_types}
    )


def normalize_linkedin_url(url):
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def client_placement_list(request):
    placements = CandidateClientPlacement.objects.all().order_by("display_name")
    data = [{"id": p.id, "name": p.display_name} for p in placements]
    return JsonResponse(data, safe=False)


def candidate_title_list(request):
    titles = CandidateProfileTitle.objects.annotate(
        count=Count("candidateprofile", distinct=True)
    ).order_by("display_name")
    data = [{"id": t.id, "name": t.display_name, "count": t.count} for t in titles]
    return JsonResponse(data, safe=False)


def candidate_title_list_filtered(request):
    """Return title counts filtered by current search parameters."""
    candidates = CandidateProfile.objects.all()

    # Apply same filters as CandidateSearch view
    query = request.GET.get("q", "").strip()
    ownership_id = request.GET.get("ownership_id")
    source_id = request.GET.get("source_id")
    deep_search = request.GET.get("deep_search") == "on"  # Changed from "true" to "on"

    # Apply filters (excluding title_id to get counts for all titles)
    if ownership_id:
        candidates = candidates.filter(ownership_id=ownership_id)
    if source_id:
        candidates = candidates.filter(source_id=source_id)

    if query and "all" not in query:
        if deep_search:
            # Use same deep search logic as main view
            candidates = CandidateProfile.objects.extra(
                where=[
                    """
                    candidate_profile.search_document @@ plainto_tsquery(%s)
                    OR EXISTS (
                        SELECT 1 FROM candidate_resume
                        WHERE candidate_resume.candidate_id = candidate_profile.id
                        AND candidate_resume.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_document
                        WHERE candidate_document.candidate_id = candidate_profile.id
                        AND candidate_document.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_culinary_portfolio
                        WHERE candidate_culinary_portfolio.candidate_id = candidate_profile.id
                        AND candidate_culinary_portfolio.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_client_placement_history p
                        JOIN candidate_client_placement cp ON p.placement_id = cp.id
                        WHERE p.candidate_id = candidate_profile.id
                        AND cp.display_name ILIKE %s
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_journal_entry j
                        WHERE j.candidate_id = candidate_profile.id
                        AND j.notes ILIKE %s
                    )
                    """
                ],
                params=[query, query, query, query, f"%{query}%", f"%{query}%"],
            ).distinct()
        else:
            # Simple search
            search_query = Q()
            search_query |= Q(first_name__icontains=query)
            search_query |= Q(last_name__icontains=query)
            search_query |= Q(email__icontains=query)
            search_query |= Q(phone_number__icontains=query)
            search_query |= Q(city__icontains=query)
            search_query |= Q(state__icontains=query)
            search_query |= Q(entry_notes__icontains=query)
            search_query |= Q(linkedin_url__icontains=query)
            search_query |= Q(title__display_name__icontains=query)
            search_query |= Q(ownership__display_name__icontains=query)
            search_query |= Q(source__display_name__icontains=query)
            candidates = candidates.filter(search_query)

    # Apply toggle filters
    if request.GET.get("actively_looking"):
        candidates = candidates.filter(actively_looking=True)
    if request.GET.get("open_to_relocation"):
        candidates = candidates.filter(open_to_relocation=True)
    if request.GET.get("currently_working"):
        candidates = candidates.filter(currently_working=True)
    if request.GET.get("previously_placed"):
        candidates = candidates.filter(placement_record__isnull=False)

    # Get title counts from filtered candidates
    titles = (
        CandidateProfileTitle.objects.filter(candidateprofile__in=candidates)
        .annotate(count=Count("candidateprofile", distinct=True))
        .order_by("display_name")
    )

    data = [{"id": t.id, "name": t.display_name, "count": t.count} for t in titles]
    return JsonResponse(data, safe=False)


def candidate_source_list(request):
    sources = CandidateProfileSource.objects.annotate(
        count=Count("candidateprofile", distinct=True)
    ).order_by("display_name")
    data = [{"id": s.id, "name": s.display_name, "count": s.count} for s in sources]
    return JsonResponse(data, safe=False)


def candidate_source_list_filtered(request):
    """Return source counts filtered by current search parameters."""
    candidates = CandidateProfile.objects.all()

    # Apply same filters as CandidateSearch view (excluding source_id)
    query = request.GET.get("q", "").strip()
    title_id = request.GET.get("title_id")
    ownership_id = request.GET.get("ownership_id")
    deep_search = request.GET.get("deep_search") == "on"  # Changed from "true" to "on"

    if title_id:
        candidates = candidates.filter(title_id=title_id)
    if ownership_id:
        candidates = candidates.filter(ownership_id=ownership_id)

    if query and "all" not in query:
        if deep_search:
            # Use enhanced deep search logic including placement/journal
            candidates = CandidateProfile.objects.extra(
                where=[
                    """
                    candidate_profile.search_document @@ plainto_tsquery(%s)
                    OR EXISTS (
                        SELECT 1 FROM candidate_resume
                        WHERE candidate_resume.candidate_id = candidate_profile.id
                        AND candidate_resume.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_document
                        WHERE candidate_document.candidate_id = candidate_profile.id
                        AND candidate_document.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_culinary_portfolio
                        WHERE candidate_culinary_portfolio.candidate_id = candidate_profile.id
                        AND candidate_culinary_portfolio.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_client_placement_history p
                        JOIN candidate_client_placement cp ON p.placement_id = cp.id
                        WHERE p.candidate_id = candidate_profile.id
                        AND (
                            cp.display_name ILIKE %s
                            OR CAST(p.month AS TEXT) ILIKE %s
                            OR CAST(p.year AS TEXT) ILIKE %s
                            OR CAST(p.compensation AS TEXT) ILIKE %s
                        )
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_journal_entry j
                        WHERE j.candidate_id = candidate_profile.id
                        AND j.notes ILIKE %s
                    )
                    """
                ],
                params=[
                    query,
                    query,
                    query,
                    query,
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                ],
            ).distinct()
        else:
            # Simple search
            search_query = Q()
            search_query |= Q(first_name__icontains=query)
            search_query |= Q(last_name__icontains=query)
            search_query |= Q(email__icontains=query)
            search_query |= Q(phone_number__icontains=query)
            search_query |= Q(city__icontains=query)
            search_query |= Q(state__icontains=query)
            search_query |= Q(entry_notes__icontains=query)
            search_query |= Q(linkedin_url__icontains=query)
            search_query |= Q(title__display_name__icontains=query)
            search_query |= Q(ownership__display_name__icontains=query)
            search_query |= Q(source__display_name__icontains=query)
            candidates = candidates.filter(search_query)

    # Apply toggle filters
    if request.GET.get("actively_looking"):
        candidates = candidates.filter(actively_looking=True)
    if request.GET.get("open_to_relocation"):
        candidates = candidates.filter(open_to_relocation=True)
    if request.GET.get("currently_working"):
        candidates = candidates.filter(currently_working=True)
    if request.GET.get("previously_placed"):
        candidates = candidates.filter(placement_record__isnull=False)

    sources = (
        CandidateProfileSource.objects.filter(candidateprofile__in=candidates)
        .annotate(count=Count("candidateprofile", distinct=True))
        .order_by("display_name")
    )

    data = [{"id": s.id, "name": s.display_name, "count": s.count} for s in sources]
    return JsonResponse(data, safe=False)


def candidate_ownership_list(request):
    owners = CandidateOwnership.objects.annotate(
        count=Count("candidateprofile", distinct=True)
    ).order_by("display_name")
    data = [{"id": o.id, "name": o.display_name, "count": o.count} for o in owners]
    return JsonResponse(data, safe=False)


def candidate_ownership_list_filtered(request):
    """Return ownership counts filtered by current search parameters."""
    candidates = CandidateProfile.objects.all()

    # Apply same filters as CandidateSearch view (excluding ownership_id)
    query = request.GET.get("q", "").strip()
    title_id = request.GET.get("title_id")
    source_id = request.GET.get("source_id")
    deep_search = request.GET.get("deep_search") == "on"  # Changed from "true" to "on"

    if title_id:
        candidates = candidates.filter(title_id=title_id)
    if source_id:
        candidates = candidates.filter(source_id=source_id)

    if query and "all" not in query:
        if deep_search:
            candidates = CandidateProfile.objects.extra(
                where=[
                    """
                    candidate_profile.search_document @@ plainto_tsquery(%s)
                    OR EXISTS (
                        SELECT 1 FROM candidate_resume
                        WHERE candidate_resume.candidate_id = candidate_profile.id
                        AND candidate_resume.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_document
                        WHERE candidate_document.candidate_id = candidate_profile.id
                        AND candidate_document.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_culinary_portfolio
                        WHERE candidate_culinary_portfolio.candidate_id = candidate_profile.id
                        AND candidate_culinary_portfolio.search_document @@ plainto_tsquery(%s)
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_client_placement_history p
                        JOIN candidate_client_placement cp ON p.placement_id = cp.id
                        WHERE p.candidate_id = candidate_profile.id
                        AND (
                            cp.display_name ILIKE %s
                            OR CAST(p.month AS TEXT) ILIKE %s
                            OR CAST(p.year AS TEXT) ILIKE %s
                            OR CAST(p.compensation AS TEXT) ILIKE %s
                        )
                    )
                    OR EXISTS (
                        SELECT 1 FROM candidate_journal_entry j
                        WHERE j.candidate_id = candidate_profile.id
                        AND j.notes ILIKE %s
                    )
                    """
                ],
                params=[
                    query,
                    query,
                    query,
                    query,
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                    f"%{query}%",
                ],
            ).distinct()
        else:
            search_query = Q()
            search_query |= Q(first_name__icontains=query)
            search_query |= Q(last_name__icontains=query)
            search_query |= Q(email__icontains=query)
            search_query |= Q(phone_number__icontains=query)
            search_query |= Q(city__icontains=query)
            search_query |= Q(state__icontains=query)
            search_query |= Q(entry_notes__icontains=query)
            search_query |= Q(linkedin_url__icontains=query)
            search_query |= Q(title__display_name__icontains=query)
            search_query |= Q(ownership__display_name__icontains=query)
            search_query |= Q(source__display_name__icontains=query)
            candidates = candidates.filter(search_query)

    # Apply toggle filters
    if request.GET.get("actively_looking"):
        candidates = candidates.filter(actively_looking=True)
    if request.GET.get("open_to_relocation"):
        candidates = candidates.filter(open_to_relocation=True)
    if request.GET.get("currently_working"):
        candidates = candidates.filter(currently_working=True)
    if request.GET.get("previously_placed"):
        candidates = candidates.filter(placement_record__isnull=False)

    owners = (
        CandidateOwnership.objects.filter(candidateprofile__in=candidates)
        .annotate(count=Count("candidateprofile", distinct=True))
        .order_by("display_name")
    )

    data = [{"id": o.id, "name": o.display_name, "count": o.count} for o in owners]
    return JsonResponse(data, safe=False)


class CandidateInput(LoginRequiredMixin, View):
    template_name_desktop = "red_shell_recruiting/candidate_input_desktop.html"
    template_name_mobile = "red_shell_recruiting/candidate_input_mobile.html"

    def get_template_name(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if parse(user_agent).is_mobile:
            return self.template_name_mobile
        return self.template_name_desktop

    def get(self, request, *args, **kwargs):
        context = {"all_placements": CandidateClientPlacement.objects.all()}
        return render(request, self.get_template_name(request), context)

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get("candidate-first-name")
        last_name = request.POST.get("candidate-last-name")
        title_id = request.POST.get("candidate-title-id")
        title_obj = (
            CandidateProfileTitle.objects.filter(id=title_id).first()
            if title_id
            else None
        )
        source_id = request.POST.get("candidate-source-id")
        source_obj = (
            CandidateProfileSource.objects.filter(id=source_id).first()
            if source_id
            else None
        )
        phone_number = request.POST.get("candidate-phone-number")
        email = request.POST.get("candidate-email")
        compensation_from = (
            str(request.POST.get("candidate-compensation-from")).replace(",", "") or 0
        )
        compensation_to = (
            str(request.POST.get("candidate-compensation-to")).replace(",", "") or 0
        )
        notes = request.POST.get("candidate-notes")
        candidate_state = request.POST.get("candidate-state")
        candidate_city = request.POST.get("candidate-city")
        actively_looking = bool(request.POST.get("candidate-looking"))
        open_to_relocation = bool(request.POST.get("candidate-relocation"))
        currently_working = bool(request.POST.get("candidate-working"))
        candidate_resume = request.FILES.get("candidate_resume")
        raw_linkedin_url = request.POST.get("candidate-linkedin-url", "").strip()
        linkedin_url = normalize_linkedin_url(raw_linkedin_url)

        placement_id = request.POST.get("client-placement-id")
        placement_month = request.POST.get("client-placement-month")
        placement_year = request.POST.get("client-placement-year")
        placement_compensation = request.POST.get("client-placement-compensation")

        ownership_id = request.POST.get("candidate-ownership-id")
        ownership_obj = (
            CandidateOwnership.objects.filter(id=ownership_id).first()
            if ownership_id
            else None
        )

        try:
            with transaction.atomic():
                candidate = CandidateProfile.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    title=title_obj,
                    ownership=ownership_obj,
                    state=candidate_state,
                    city=candidate_city,
                    phone_number=phone_number,
                    email=email,
                    compensation_from=compensation_from,
                    compensation_to=compensation_to,
                    entry_notes=notes,
                    open_to_relocation=open_to_relocation,
                    currently_working=currently_working,
                    actively_looking=actively_looking,
                    linkedin_url=linkedin_url,
                    source=source_obj,
                    created_by=request.user,
                )

                if (
                    placement_id
                    and placement_month
                    and placement_year
                    and placement_compensation
                ):
                    placement_history = CandidateClientPlacementHistory.objects.create(
                        candidate=candidate,
                        placement_id=placement_id,
                        month=placement_month,
                        year=placement_year,
                        compensation=placement_compensation,
                    )

                    candidate.candidate_placement_history = placement_history
                    candidate.save(update_fields=["candidate_placement_history"])

                if candidate_resume:
                    resume = CandidateResume.objects.create(
                        candidate=candidate, file=candidate_resume
                    )
                    update_resume_search_vector.delay(resume.id)
                else:
                    raise IntegrityError("Resume upload failed.")

        except IntegrityError as e:
            if str(e).startswith("duplicate key"):
                messages.error(
                    request,
                    f"Looks like a candidate with that email already exists for {email}",
                )
                return redirect("candidate-submit")
            else:
                messages.error(request, f"Error saving candidate: {str(e)}")
                return redirect("candidate-submit")

        messages.success(request, f"{first_name} {last_name} has been added.")
        return redirect("candidate-submit")


class CandidateSearch(LoginRequiredMixin, TemplateView):
    """View for candidate search with desktop and mobile templates, supporting AJAX for all search/filter actions."""

    template_name_desktop = "red_shell_recruiting/candidate_search_desktop.html"
    template_name_mobile = "red_shell_recruiting/candidate_search_mobile.html"
    paginate_by = 10

    def get_template_names(self) -> list[str]:
        """Return the appropriate template name based on user agent."""
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        if parse(user_agent).is_mobile:
            return [self.template_name_mobile]
        return [self.template_name_desktop]

    def get_context_data(self, **kwargs) -> dict:
        """Get context data for candidate search, including dropdowns and filters."""
        context = super().get_context_data(**kwargs)
        request = self.request

        toggle_filters = {
            "actively_looking": request.GET.get("actively_looking"),
            "open_to_relocation": request.GET.get("open_to_relocation"),
            "currently_working": request.GET.get("currently_working"),
            "previously_placed": request.GET.get("previously_placed"),
        }
        toggles_active = any(toggle_filters.values())
        title_id = request.GET.get("title_id")
        ownership_id = request.GET.get("ownership_id")
        source_id = request.GET.get("source_id")
        query = request.GET.get("q", "").strip()
        deep_search = (
            request.GET.get("deep_search") == "on"
        )  # Changed from "true" to "on"
        candidates = CandidateProfile.objects.all()

        if "all" in query:
            candidates = candidates.order_by("-created_at")
            query = None
        else:
            if title_id:
                candidates = candidates.filter(title_id=title_id)
            if ownership_id:
                candidates = candidates.filter(ownership_id=ownership_id)
            if source_id:
                candidates = candidates.filter(source_id=source_id)
            if query:
                if deep_search:
                    # Enhanced deep search using PostgreSQL full-text search + ILIKE for placement/journal
                    # Apply to existing filtered queryset to preserve filters
                    candidates = (
                        candidates.extra(
                            where=[
                                """
                                candidate_profile.search_document @@ plainto_tsquery(%s)
                                OR EXISTS (
                                    SELECT 1 FROM candidate_resume
                                    WHERE candidate_resume.candidate_id = candidate_profile.id
                                    AND candidate_resume.search_document @@ plainto_tsquery(%s)
                                )
                                OR EXISTS (
                                    SELECT 1 FROM candidate_document
                                    WHERE candidate_document.candidate_id = candidate_profile.id
                                    AND candidate_document.search_document @@ plainto_tsquery(%s)
                                )
                                OR EXISTS (
                                    SELECT 1 FROM candidate_culinary_portfolio
                                    WHERE candidate_culinary_portfolio.candidate_id = candidate_profile.id
                                    AND candidate_culinary_portfolio.search_document @@ plainto_tsquery(%s)
                                )
                                OR EXISTS (
                                    SELECT 1 FROM candidate_client_placement_history p
                                    JOIN candidate_client_placement cp ON p.placement_id = cp.id
                                    WHERE p.candidate_id = candidate_profile.id
                                    AND (
                                        cp.display_name ILIKE %s
                                        OR CAST(p.month AS TEXT) ILIKE %s
                                        OR CAST(p.year AS TEXT) ILIKE %s
                                        OR CAST(p.compensation AS TEXT) ILIKE %s
                                    )
                                )
                                OR EXISTS (
                                    SELECT 1 FROM candidate_journal_entry j
                                    WHERE j.candidate_id = candidate_profile.id
                                    AND j.notes ILIKE %s
                                )
                                """
                            ],
                            params=[
                                query,
                                query,
                                query,
                                query,
                                f"%{query}%",
                                f"%{query}%",
                                f"%{query}%",
                                f"%{query}%",
                                f"%{query}%",
                            ],
                        )
                        .annotate(
                            rank=RawSQL(
                                """
                                GREATEST(
                                    ts_rank(candidate_profile.search_document, plainto_tsquery(%s)),
                                    COALESCE((
                                        SELECT MAX(ts_rank(candidate_resume.search_document, plainto_tsquery(%s)))
                                        FROM candidate_resume
                                        WHERE candidate_resume.candidate_id = candidate_profile.id
                                    ), 0),
                                    COALESCE((
                                        SELECT MAX(ts_rank(candidate_document.search_document, plainto_tsquery(%s)))
                                        FROM candidate_document
                                        WHERE candidate_document.candidate_id = candidate_profile.id
                                    ), 0),
                                    COALESCE((
                                        SELECT MAX(ts_rank(candidate_culinary_portfolio.search_document, plainto_tsquery(%s)))
                                        FROM candidate_culinary_portfolio
                                        WHERE candidate_culinary_portfolio.candidate_id = candidate_profile.id
                                    ), 0)
                                )
                                """,
                                (query, query, query, query),
                            )
                        )
                        .order_by("-rank")
                        .distinct()
                    )
                else:
                    # Simple search using ILIKE across candidate profile fields
                    candidates = self._perform_simple_search(candidates, query)
            elif not (toggles_active or title_id or ownership_id or source_id):
                candidates = CandidateProfile.objects.none()

            if toggle_filters["actively_looking"]:
                candidates = candidates.filter(actively_looking=True)
            if toggle_filters["open_to_relocation"]:
                candidates = candidates.filter(open_to_relocation=True)
            if toggle_filters["currently_working"]:
                candidates = candidates.filter(currently_working=True)
            if toggle_filters["previously_placed"]:
                candidates = candidates.filter(placement_record__isnull=False)
            candidates = candidates.annotate(resume_count=Count("resumes"))

        page_number = request.GET.get("page", 1)
        paginator = Paginator(candidates, self.paginate_by)
        page_obj = paginator.get_page(page_number)
        get_params = request.GET.copy()
        if "page" in get_params:
            get_params.pop("page")
        context["get_params"] = get_params.urlencode()
        context["candidates"] = page_obj.object_list
        context["page_obj"] = page_obj
        context["paginator"] = paginator
        context["query"] = query
        context["deep_search"] = deep_search
        context["selected_count"] = paginator.count
        context["total_count_profile"] = CandidateProfile.objects.count()
        context["total_count_resume"] = CandidateResume.objects.count()
        context["selected_ownership_id"] = ownership_id
        context["selected_source_id"] = source_id
        return context

    def _perform_simple_search(self, queryset, query: str):
        """Perform simple ILIKE search across candidate profile fields."""
        search_query = Q()

        # Search across text fields in candidate profile
        search_query |= Q(first_name__icontains=query)
        search_query |= Q(last_name__icontains=query)
        search_query |= Q(email__icontains=query)
        search_query |= Q(phone_number__icontains=query)
        search_query |= Q(city__icontains=query)
        search_query |= Q(state__icontains=query)
        search_query |= Q(entry_notes__icontains=query)
        search_query |= Q(linkedin_url__icontains=query)

        # Search in related fields
        search_query |= Q(title__display_name__icontains=query)
        search_query |= Q(ownership__display_name__icontains=query)
        search_query |= Q(source__display_name__icontains=query)

        return queryset.filter(search_query).order_by("-created_at", "-id").distinct()

    def render_to_response(self, context: dict, **response_kwargs) -> HttpResponse:
        """Render candidate cards only for AJAX requests (all search/filter actions), else full template."""
        request = self.request
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        if is_ajax:
            # Debug logging for pagination
            page_obj = context["page_obj"]
            candidates_queryset = context["candidates"]
            total_count = page_obj.paginator.count
            current_page_count = len(list(candidates_queryset))
            remaining_count = total_count - (page_obj.number * self.paginate_by)

            print(f"DEBUG: AJAX response - Current page: {page_obj.number}")
            print(f"DEBUG: AJAX response - Has next: {page_obj.has_next()}")
            print(f"DEBUG: AJAX response - Total pages: {page_obj.paginator.num_pages}")
            print(f"DEBUG: AJAX response - Total count: {total_count}")
            print(f"DEBUG: AJAX response - Page size: {self.paginate_by}")
            print(f"DEBUG: AJAX response - Objects on this page: {current_page_count}")
            print(f"DEBUG: AJAX response - Remaining count: {remaining_count}")
            print(f"DEBUG: Query params: {request.GET}")

            html = render_to_string(
                "red_shell_recruiting/components/candidate_cards_lazy.html",
                {
                    "candidates": context["candidates"],
                    "has_next": context["page_obj"].has_next(),
                    "total_count": total_count,
                    "remaining_count": max(0, remaining_count),
                },
                request=request,
            )
            return HttpResponse(html)
        return super().render_to_response(context, **response_kwargs)


class CandidateDetail(LoginRequiredMixin, TemplateView):
    template_name_desktop = "red_shell_recruiting/candidate_detail_desktop.html"
    template_name_mobile = "red_shell_recruiting/candidate_detail_mobile.html"

    def get_template_names(self):
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        if parse(user_agent).is_mobile:
            return [self.template_name_mobile]
        return [self.template_name_desktop]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate_id = self.kwargs.get("candidate_id")
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        context["candidate"] = candidate
        context["resumes"] = candidate.resumes.filter(archived=False)
        context["portfolios"] = candidate.culinary_portfolios.filter(archived=False)
        context["documents"] = candidate.documents.filter(archived=False)
        context["has_placement_records"] = candidate.placement_record.exists()
        return context

    def post(self, request, *args, **kwargs):
        candidate_id = self.kwargs.get("candidate_id")
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)

        # ----- Update candidate base info -----
        candidate.first_name = request.POST.get(
            "candidate-first-name", candidate.first_name
        )
        candidate.last_name = request.POST.get(
            "candidate-last-name", candidate.last_name
        )
        candidate.state = request.POST.get("candidate-state", candidate.state)
        candidate.city = request.POST.get("candidate-city", candidate.city)
        candidate.phone_number = request.POST.get(
            "candidate-phone-number", candidate.phone_number
        )
        candidate.email = request.POST.get("candidate-email", candidate.email)
        candidate.compensation_from = str(
            request.POST.get("candidate-compensation-from", candidate.compensation_from)
        ).replace(",", "")
        candidate.compensation_to = str(
            request.POST.get("candidate-compensation-to", candidate.compensation_to)
        ).replace(",", "")
        candidate.entry_notes = request.POST.get(
            "candidate-notes", candidate.entry_notes
        )
        candidate.open_to_relocation = (
            request.POST.get("candidate-open-to-relocation") == "on"
        )
        candidate.currently_working = (
            request.POST.get("candidate-currently-working") == "on"
        )
        candidate.actively_looking = (
            request.POST.get("candidate-actively-looking") == "on"
        )
        raw_linkedin_url = request.POST.get("candidate-linkedin-url", "").strip()
        candidate.linkedin_url = normalize_linkedin_url(raw_linkedin_url)

        title_id = request.POST.get("candidate-title-id")
        if title_id:
            title_obj = CandidateProfileTitle.objects.filter(id=title_id).first()
            if title_obj:
                candidate.title = title_obj

        owner_id = request.POST.get("candidate-ownership-id")
        if owner_id:
            owner_obj = CandidateOwnership.objects.filter(id=owner_id).first()
            if owner_obj:
                candidate.ownership = owner_obj

        source_id = request.POST.get("candidate-source-id")
        if source_id:
            source_obj = CandidateProfileSource.objects.filter(id=source_id).first()
            if source_obj:
                candidate.source = source_obj

        candidate.save()

        return redirect("candidate-detail", candidate_id=candidate.id)


class ArchiveResume(LoginRequiredMixin, View):
    def post(self, request, resume_id):
        try:
            resume = get_object_or_404(CandidateResume, id=resume_id)
        except:
            return JsonResponse(
                {"success": False, "error": "Resume not found"}, status=404
            )

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        original_key = resume.file.name
        archive_key = original_key.replace("resumes/", "resumes/archive/")

        try:
            s3.copy_object(
                Bucket=bucket,
                CopySource={"Bucket": bucket, "Key": original_key},
                Key=archive_key,
            )
            s3.delete_object(Bucket=bucket, Key=original_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"The resume could not be found in S3 at: {original_key}",
                    },
                    status=500,
                )
            return JsonResponse(
                {
                    "success": False,
                    "error": "An unexpected AWS error occurred while archiving the resume.",
                },
                status=500,
            )
        except Exception:
            return JsonResponse(
                {
                    "success": False,
                    "error": "An unexpected error occurred while archiving the resume.",
                },
                status=500,
            )

        resume.archived = True
        resume.save(update_fields=["archived"])

        return JsonResponse(
            {"success": True, "message": "Resume archived successfully"}
        )


class ArchiveDocument(LoginRequiredMixin, View):
    def post(self, request, document_id):
        try:
            document = get_object_or_404(CandidateDocument, id=document_id)
        except:
            return JsonResponse(
                {"success": False, "error": "Document not found"}, status=404
            )

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        original_key = document.file.name
        archive_key = original_key.replace("documents/", "documents/archive/")

        try:
            s3.copy_object(
                Bucket=bucket,
                CopySource={"Bucket": bucket, "Key": original_key},
                Key=archive_key,
            )
            s3.delete_object(Bucket=bucket, Key=original_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"The document could not be found in S3 at: {original_key}",
                    },
                    status=500,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "An unexpected error occurred while archiving the document.",
                    },
                    status=500,
                )
        except Exception:
            return JsonResponse(
                {
                    "success": False,
                    "error": "An unexpected error occurred while archiving the document.",
                },
                status=500,
            )

        document.archived = True
        document.save(update_fields=["archived"])

        return JsonResponse(
            {"success": True, "message": "Document archived successfully"}
        )


class ArchiveCulinaryPortfolio(LoginRequiredMixin, View):
    def post(self, request, portfolio_id):
        try:
            portfolio = get_object_or_404(CandidateCulinaryPortfolio, id=portfolio_id)
        except:
            return JsonResponse(
                {"success": False, "error": "Portfolio not found"}, status=404
            )

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        original_key = portfolio.file.name
        archive_key = original_key.replace("portfolios/", "portfolios/archive/")

        try:
            s3.copy_object(
                Bucket=bucket,
                CopySource={"Bucket": bucket, "Key": original_key},
                Key=archive_key,
            )
            s3.delete_object(Bucket=bucket, Key=original_key)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"The portfolio could not be found in S3 at: {original_key}",
                    },
                    status=500,
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "An unexpected error occurred while archiving the portfolio.",
                    },
                    status=500,
                )
        except Exception:
            return JsonResponse(
                {
                    "success": False,
                    "error": "An unexpected error occurred while archiving the portfolio.",
                },
                status=500,
            )

        portfolio.archived = True
        portfolio.file.name = archive_key
        portfolio.save(update_fields=["archived", "file"])

        return JsonResponse(
            {"success": True, "message": "Portfolio archived successfully"}
        )


class UploadResume(LoginRequiredMixin, View):
    def post(self, request, candidate_id):
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        uploaded_file = request.FILES.get("candidate-resume")

        if uploaded_file:
            resume = CandidateResume.objects.create(
                candidate=candidate, file=uploaded_file, archived=False
            )
            # TODO may want to remove vectoring for resumes
            update_resume_search_vector.delay(resume.id)

            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)


class UploadDocument(LoginRequiredMixin, View):
    def post(self, request, candidate_id):
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        uploaded_file = request.FILES.get("candidate-document")

        if uploaded_file:
            doc = CandidateDocument.objects.create(
                candidate=candidate, file=uploaded_file
            )
            # TODO may want to remove vectoring for documents
            update_document_search_vector.delay(doc.id)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)


class UploadCulinaryPortfolio(LoginRequiredMixin, View):
    def post(self, request, candidate_id):
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        uploaded_file = request.FILES.get("candidate-portfolio")

        if uploaded_file:
            portfolio = CandidateCulinaryPortfolio.objects.create(
                candidate=candidate, file=uploaded_file
            )
            update_portfolio_search_vector.delay(portfolio.id)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)


class JournalEntryView(View):
    """View for handling candidate journal entries (GET for list, POST for add)."""

    def get(self, request: HttpRequest, candidate_id: int) -> HttpResponse:
        """Return rendered HTML of all journal entries for a candidate, newest first."""
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        entries = JournalEntry.objects.filter(candidate=candidate).order_by(
            "-meeting_date", "-created_at"
        )
        context = {"entries": entries}
        html = render_to_string(
            "red_shell_recruiting/components/journal_entries_list.html",
            context,
            request=request,
        )
        return HttpResponse(html)

    def post(self, request: HttpRequest, candidate_id: int) -> HttpResponse:
        """Create a new journal entry for a candidate via AJAX POST."""
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        meeting_date = request.POST.get("meeting_date")
        notes = request.POST.get("notes")
        if not meeting_date or not notes:
            return HttpResponse("Missing meeting date or notes.", status=400)
        JournalEntry.objects.create(
            candidate=candidate,
            user=request.user,
            meeting_date=meeting_date,
            notes=notes,
        )
        return HttpResponse("OK")


class PlacementRecordView(View):
    """View for handling candidate placement records (GET for list, POST for add, DELETE for remove)."""

    def get(self, request: HttpRequest, candidate_id: int) -> HttpResponse:
        """Return rendered HTML of all placement records for a candidate, newest first."""
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        placements = CandidateClientPlacementHistory.objects.filter(
            candidate=candidate
        ).order_by("-year", "-month", "-created_at")
        context = {"placements": placements}
        html = render_to_string(
            "red_shell_recruiting/components/placement_records_list.html",
            context,
            request=request,
        )
        return HttpResponse(html)

    def post(self, request: HttpRequest, candidate_id: int) -> HttpResponse:
        """Create a new placement record for a candidate via AJAX POST."""
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        placement_id = request.POST.get("placement_id")
        month = request.POST.get("month")
        year = request.POST.get("year")
        compensation = request.POST.get("compensation")
        if not (placement_id and month and year and compensation):
            return HttpResponse("Missing placement data.", status=400)
        CandidateClientPlacementHistory.objects.create(
            candidate=candidate,
            placement_id=placement_id,
            month=month,
            year=year,
            compensation=compensation,
        )
        return HttpResponse("OK")

    def delete(self, request: HttpRequest, candidate_id: int) -> HttpResponse:
        """Remove a placement record for a candidate via AJAX DELETE."""
        placement_history_id = request.GET.get("placement_history_id")
        if not placement_history_id:
            return HttpResponse("Missing placement_history_id.", status=400)
        try:
            placement = CandidateClientPlacementHistory.objects.get(
                id=placement_history_id, candidate_id=candidate_id
            )
            placement.delete()
            return HttpResponse("OK")
        except CandidateClientPlacementHistory.DoesNotExist:
            return HttpResponse("Placement record not found.", status=404)
