import traceback

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

from red_shell_recruiting.tasks import (
    update_resume_search_vector,
    update_document_search_vector,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db import IntegrityError, transaction

from red_shell_recruiting.models import (
    CandidateProfile,
    CandidateResume,
    CandidateDocument,
    CandidateClientPlacement,
    CandidateClientPlacementHistory,
    CandidateProfileTitle,
)


@login_required
def index(request):
    context = {}
    return render(request, "red_shell_recruiting/index.html", context)


def client_placement_list(request):
    placements = CandidateClientPlacement.objects.all().order_by("display_name")
    data = [{"id": p.id, "name": p.display_name} for p in placements]
    return JsonResponse(data, safe=False)


def candidate_title_list(request):
    titles = CandidateProfileTitle.objects.all().order_by("display_name")
    data = [{"id": t.id, "name": t.display_name} for t in titles]
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
        phone_number = request.POST.get("candidate-phone-number")
        email = request.POST.get("candidate-email")
        compensation = (
            str(request.POST.get("candidate-compensation")).replace(",", "") or 0
        )
        notes = request.POST.get("candidate-notes")
        candidate_state = request.POST.get("candidate-state")
        candidate_city = request.POST.get("candidate-city")
        actively_looking = bool(request.POST.get("candidate-looking"))
        open_to_relocation = bool(request.POST.get("candidate-relocation"))
        currently_working = bool(request.POST.get("candidate-working"))
        candidate_resume = request.FILES.get("candidate_resume")

        placement_id = request.POST.get("client-placement-id")
        placement_month = request.POST.get("client-placement-month")
        placement_year = request.POST.get("client-placement-year")

        try:
            with transaction.atomic():
                candidate = CandidateProfile.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    title=title_obj,
                    state=candidate_state,
                    city=candidate_city,
                    phone_number=phone_number,
                    email=email,
                    compensation=compensation,
                    notes=notes,
                    open_to_relocation=open_to_relocation,
                    currently_working=currently_working,
                    actively_looking=actively_looking,
                )

                if placement_id and placement_month and placement_year:
                    CandidateClientPlacementHistory.objects.create(
                        candidate=candidate,
                        placement_id=placement_id,
                        month=placement_month,
                        year=placement_year,
                    )

                if candidate_resume:
                    resume = CandidateResume.objects.create(
                        candidate=candidate, file=candidate_resume
                    )
                    update_resume_search_vector.delay(resume.id)
                else:
                    raise IntegrityError("Resume upload failed.")

        except IntegrityError as e:
            messages.error(request, f"Error saving candidate: {str(e)}")
            return redirect("candidate-submit")

        messages.success(request, f"{first_name} {last_name} has been added.")
        return redirect("candidate-submit")


class CandidateSearch(LoginRequiredMixin, TemplateView):
    template_name_desktop = "red_shell_recruiting/candidate_search_desktop.html"
    template_name_mobile = "red_shell_recruiting/candidate_search_mobile.html"

    def get_template_names(self):
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        if parse(user_agent).is_mobile:
            return [self.template_name_mobile]
        return [self.template_name_desktop]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        query = request.GET.get("q", "").strip()

        title_id = request.GET.get("title_id")
        all_titles = CandidateProfileTitle.objects.all().order_by("display_name")

        toggle_filters = {
            "actively_looking": request.GET.get("actively_looking"),
            "open_to_relocation": request.GET.get("open_to_relocation"),
            "currently_working": request.GET.get("currently_working"),
            "previously_placed": request.GET.get("previously_placed"),
        }
        toggles_active = any(toggle_filters.values())

        title_id = request.GET.get("title_id")
        query = request.GET.get("q", "").strip()

        candidates = CandidateProfile.objects.all()

        if title_id:
            candidates = candidates.filter(title_id=title_id)

        if query:
            candidates = (
                CandidateProfile.objects.extra(
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
                        """
                    ],
                    params=[query, query, query],
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
                            ), 0)
                        )
                        """,
                        (query, query, query),
                    )
                )
                .order_by("-rank")
                .distinct()
            )

        elif not (toggles_active or title_id):
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

        context["candidates"] = candidates
        context["query"] = query
        context["selected_count"] = candidates.count()
        context["total_count_profile"] = CandidateProfile.objects.count()
        context["total_count_resume"] = CandidateResume.objects.count()
        context["all_titles"] = all_titles
        context["selected_title_id"] = title_id

        return context


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
        return context

    def post(self, request, *args, **kwargs):
        candidate_id = self.kwargs.get("candidate_id")
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        candidate.first_name = request.POST.get("first-name", candidate.first_name)
        candidate.last_name = request.POST.get("last-name", candidate.last_name)
        candidate.state = request.POST.get("candidate-state", candidate.state)
        candidate.city = request.POST.get("candidate-city", candidate.city)
        candidate.phone_number = request.POST.get(
            "phone-number", candidate.phone_number
        )
        candidate.email = request.POST.get("email", candidate.email)
        candidate.compensation = str(
            request.POST.get("compensation", candidate.compensation)
        ).replace(",", "")
        candidate.notes = request.POST.get("notes", candidate.notes)
        candidate.open_to_relocation = request.POST.get("open-to-relocation") == "on"
        candidate.currently_working = request.POST.get("currently-working") == "on"
        candidate.actively_looking = request.POST.get("actively-looking") == "on"
        placement_id = request.POST.get("client-placement-id")
        month = request.POST.get("client-placement-month")
        year = request.POST.get("client-placement-year")

        if placement_id and month and year:
            try:
                record = CandidateClientPlacementHistory.objects.get(
                    id=placement_id, candidate=candidate
                )
                record.month = int(month)
                record.year = int(year)
                record.save()
            except CandidateClientPlacementHistory.DoesNotExist:
                pass

        placement_delete = request.POST.get("client-placement-delete") == "true"

        if placement_delete and placement_id:
            try:
                record = CandidateClientPlacementHistory.objects.get(
                    id=placement_id, candidate=candidate
                )
                record.delete()
            except CandidateClientPlacementHistory.DoesNotExist:
                pass

        title_id = request.POST.get("candidate-title-id")
        if title_id:
            title_obj = CandidateProfileTitle.objects.filter(id=title_id).first()
            if title_obj:
                candidate.title = title_obj

        candidate.save()

        uploaded_file = request.FILES.get("resume-file")
        if uploaded_file:
            CandidateResume.objects.create(candidate=candidate, file=uploaded_file)

        return redirect("candidate-detail", candidate_id=candidate.id)


class ArchiveResume(LoginRequiredMixin, View):
    def post(self, request, resume_id):
        resume = get_object_or_404(CandidateResume, id=resume_id)

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
                return render(
                    request,
                    "500.html",
                    {
                        "message": f"The resume could not be found in S3 at: {original_key}"
                    },
                    status=500,
                )
            return render(
                request,
                "500.html",
                {
                    "message": "An unexpected AWS error occurred while archiving the resume."
                },
                status=500,
            )
        except Exception:
            return render(
                request,
                "500.html",
                {"message": "An unexpected error occurred while archiving the resume."},
                status=500,
            )
        s3.delete_object(Bucket=bucket, Key=original_key)

        resume.archived = True
        resume.save(update_fields=["archived"])

        return redirect("candidate-detail", candidate_id=resume.candidate.id)


class ArchiveDocument(LoginRequiredMixin, View):
    def post(self, request, document_id):
        document = get_object_or_404(CandidateDocument, id=document_id)

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
                return render(
                    request,
                    "500.html",
                    {
                        "message": f"The document could not be found in S3 at: {original_key}"
                    },
                    status=500,
                )
            else:
                return render(
                    request,
                    "500.html",
                    {
                        "message": "An unexpected error occurred while archiving the document."
                    },
                    status=500,
                )
        except Exception:
            return render(
                request,
                "500.html",
                {
                    "message": "An unexpected error occurred while archiving the document."
                },
                status=500,
            )

        s3.delete_object(Bucket=bucket, Key=original_key)

        document.archived = True
        document.save(update_fields=["archived"])

        return redirect("candidate-detail", candidate_id=document.candidate.id)


class UploadResume(LoginRequiredMixin, View):
    def post(self, request, candidate_id):
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)
        uploaded_file = request.FILES.get("resume")

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
        uploaded_file = request.FILES.get("candidate_document")

        if uploaded_file:
            doc = CandidateDocument.objects.create(
                candidate=candidate, file=uploaded_file
            )
            # TODO may want to remove vectoring for documents
            update_document_search_vector.delay(doc.id)
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "No file uploaded"}, status=400)
