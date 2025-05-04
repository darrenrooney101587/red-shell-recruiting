import os

import boto3
from django.conf import settings
from django.db import models
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


class CandidateProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    compensation = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(null=True, blank=True)
    open_to_relocation = models.BooleanField(default=False)
    currently_working = models.BooleanField(default=True)
    actively_looking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_document = SearchVectorField(null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_title}"

    def update_search_document(self):
        self.search_document = (
            SearchVector("first_name", weight="A")
            + SearchVector("last_name", weight="A")
            + SearchVector("city", weight="B")
            + SearchVector("state", weight="B")
            + SearchVector("job_title", weight="B")
            + SearchVector("email", weight="C")
            + SearchVector("notes", weight="D")
        )
        self.save(update_fields=["search_document"])

    class Meta:
        managed = True
        db_table = "candidate_profile"
        indexes = [
            GinIndex(fields=["search_document"]),
        ]


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

    def __str__(self):
        return f"Document for {self.candidate}"


class Resume(models.Model):
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


class SearchVectorProcessingLog(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("resume", "Resume"),
        ("profile", "Candidate Profile"),
        ("document", "Candidate Document"),
    ]

    resume = models.ForeignKey(
        "red_shell_recruiting.Resume", on_delete=models.CASCADE, null=True, blank=True
    )
    document = models.ForeignKey(
        "red_shell_recruiting.CandidateDocument",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(max_length=50)  # 'success', 'ignored', 'failed'
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

    def __str__(self):
        return f"{self.resume} - {self.document_type} - {self.status}"
