import os

import boto3
from django.conf import settings
from django.db import models
from django.db.models import ForeignKey
from django.utils.timezone import now
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex


def resume_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = now().strftime("%Y_%m_%d_%H%M%S")
    return f"resumes/{instance.candidate.id}/{base}_{timestamp}{ext}"


def document_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = now().strftime("%Y_%m_%d_%H%M%S")
    return f"documents/{instance.candidate.id}/{base}_{timestamp}{ext}"


class CandidateProfileTitle(models.Model):
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidate_profile_title"
        managed = True
        verbose_name_plural = "Candidate Profile Titles"
        verbose_name = "Candidate Profile Title"


class CandidateClientPlacement(models.Model):
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "candidate_client_placement"
        managed = True
        verbose_name_plural = "Candidate Placements"
        verbose_name = "Candidate Placement"


class CandidateOwnerShip(models.Model):
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "candidate_ownership"
        verbose_name_plural = "Candidate Ownerships"
        verbose_name = "Candidate Ownership"


class CandidateProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    title = models.ForeignKey(
        "CandidateProfileTitle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="candidates",
    )
    ownership = models.ForeignKey(
        CandidateOwnerShip, on_delete=models.PROTECT, default=None
    )
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    compensation_from = models.DecimalField(max_digits=10, decimal_places=2)
    compensation_to = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    open_to_relocation = models.BooleanField(default=False)
    currently_working = models.BooleanField(default=True)
    actively_looking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_document = SearchVectorField(null=True)
    candidate_placement_history = models.ForeignKey(
        "CandidateClientPlacementHistory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="currently_active_for",
    )

    @property
    def previously_placed(self):
        return self.placement_record.exists()

    def __str__(self):
        return (
            f"CandidateProfile("
            f"id={self.id}, "
            f"first_name={self.first_name}, "
            f"last_name={self.last_name}, "
            f"state={self.state}, "
            f"city={self.city}, "
            f"title={self.title.display_name if self.title else 'None'}, "
            f"ownership={self.ownership.display_name if self.ownership else 'None'}, "
            f"phone={self.phone_number}, "
            f"email={self.email}, "
            f"comp_from={self.compensation_from}, "
            f"comp_to={self.compensation_to}, "
            f"notes={(self.notes[:30] + '...') if self.notes and len(self.notes) > 30 else self.notes}, "
            f"open_to_relocation={self.open_to_relocation}, "
            f"currently_working={self.currently_working}, "
            f"actively_looking={self.actively_looking}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}, "
            f"placement_history_id={self.candidate_placement_history_id}"
            f")"
        )

    def update_search_document(self):
        self.search_document = (
            SearchVector("first_name", weight="A")
            + SearchVector("last_name", weight="A")
            + SearchVector("city", weight="B")
            + SearchVector("state", weight="B")
            + SearchVector("email", weight="C")
            + SearchVector("notes", weight="D")
            + SearchVector("title__display_name", weight="B")
        )
        self.save(update_fields=["search_document"])

    class Meta:
        managed = True
        db_table = "candidate_profile"
        indexes = [
            GinIndex(fields=["search_document"]),
        ]
        verbose_name_plural = "Candidate Profiles"
        verbose_name = "Candidate Profile"


class CandidateClientPlacementHistory(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="placement_record"
    )
    placement = models.ForeignKey(
        CandidateClientPlacement, on_delete=models.PROTECT, related_name="placements"
    )
    month = models.IntegerField()
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "candidate_client_placement_history"
        managed = True
        verbose_name_plural = "Candidate Placement Histories"
        verbose_name = "Candidate Placement History"


class CandidateDocument(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="documents"
    )
    file = models.FileField(upload_to=document_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extracted_text = models.TextField(null=True, blank=True)
    search_document = SearchVectorField(null=True)
    archived = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "candidate_document"
        indexes = [GinIndex(fields=["search_document"])]
        verbose_name_plural = "Candidate Documents"
        verbose_name = "Candidate Document"

    def __str__(self):
        return f"Document for {self.candidate}"


class CandidateResume(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile, on_delete=models.CASCADE, related_name="resumes"
    )
    file = models.FileField(upload_to=resume_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extracted_text = models.TextField(null=True, blank=True)
    search_document = SearchVectorField(null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return f"Resume for {self.candidate.first_name} {self.candidate.last_name}"

    def get_signed_url(self, expiration=3600):
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        object_key = self.file.name

        signed_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
        )
        return signed_url

    class Meta:
        managed = True
        db_table = "candidate_resume"
        indexes = [
            GinIndex(fields=["search_document"]),
        ]
        verbose_name_plural = "Candidate Resumes"
        verbose_name = "Candidate Resume"


class SearchVectorProcessingLog(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("resume", "Resume"),
        ("profile", "Candidate Profile"),
        ("document", "Candidate Document"),
    ]

    resume = models.ForeignKey(
        "red_shell_recruiting.CandidateResume",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    document = models.ForeignKey(
        "red_shell_recruiting.CandidateDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(max_length=50)
    message = models.TextField(null=True, blank=True)
    attempts = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "search_vector_processing_log"
        indexes = [
            models.Index(fields=["resume", "document_type", "status"]),
            models.Index(fields=["document"]),
        ]
        verbose_name_plural = "Candidate Vector Processing Logs"
        verbose_name = "Candidate Vector Processing Log"

    def __str__(self):
        return f"{self.resume} - {self.document_type} - {self.status}"
