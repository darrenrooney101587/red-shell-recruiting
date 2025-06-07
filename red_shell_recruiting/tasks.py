import os
import tempfile

from celery import shared_task
from celery.exceptions import Ignore
import boto3
import textract
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db.models import Value

from red_shell_recruiting.models import (
    CandidateResume,
    CandidateProfile,
    SearchVectorProcessingLog,
    CandidateDocument,
)


@shared_task(bind=True)
def update_document_search_vector(self, document_id):
    try:
        document = CandidateDocument.objects.get(id=document_id)
        s3 = boto3.client("s3")
        obj = s3.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=document.file.name
        )
        file_bytes = obj["Body"].read()
        extension = document.file.name.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{extension}"
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            extracted_text = textract.process(temp_file_path).decode("utf-8")
        except Exception as textract_error:
            SearchVectorProcessingLog.objects.create(
                document=document,
                document_type="document",
                status="failed",
                message=f"Textract error: {str(textract_error)}",
                attempts=self.request.retries,
            )
            raise self.retry(exc=textract_error, countdown=60, max_retries=3)

        if extracted_text.strip():
            document.extracted_text = extracted_text
            document.save(update_fields=["extracted_text"])

            CandidateDocument.objects.filter(id=document.id).update(
                search_document=SearchVector("extracted_text", weight="D")
            )

            SearchVectorProcessingLog.objects.create(
                document=document,
                document_type="document",
                status="success",
                message="Document processed successfully.",
                attempts=self.request.retries,
            )
        else:
            SearchVectorProcessingLog.objects.create(
                document=document,
                document_type="document",
                status="ignored",
                message="No extracted text found in document.",
                attempts=self.request.retries,
            )
            return

    except CandidateDocument.DoesNotExist:
        SearchVectorProcessingLog.objects.create(
            document_id=document_id,
            document_type="document",
            status="failed",
            message="Document not found.",
            attempts=self.request.retries,
        )
        raise Ignore()

    except Exception as e:
        SearchVectorProcessingLog.objects.create(
            document_id=document_id,
            document_type="document",
            status="failed",
            message=str(e),
            attempts=self.request.retries,
        )
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True)
def update_resume_search_vector(self, resume_id):
    try:
        resume = CandidateResume.objects.get(id=resume_id)
        s3 = boto3.client("s3")
        obj = s3.get_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=resume.file.name
        )
        file_bytes = obj["Body"].read()
        extension = resume.file.name.split(".")[-1].lower()
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{extension}"
        ) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            extracted_text = textract.process(temp_file_path).decode("utf-8")
        finally:
            os.remove(temp_file_path)

        if extracted_text.strip():
            resume.extracted_text = extracted_text
            resume.save(update_fields=["extracted_text"])

            CandidateResume.objects.filter(id=resume.id).update(
                search_document=SearchVector("extracted_text", weight="D")
            )

            SearchVectorProcessingLog.objects.create(
                resume=resume,
                document_type="resume",
                status="success",
                message="Resume processed successfully.",
                attempts=self.request.retries,
            )

            candidate = CandidateProfile.objects.select_related("title").get(
                id=resume.candidate_id
            )
            combined_vector = (
                SearchVector(Value(candidate.first_name), weight="A")
                + SearchVector(Value(candidate.last_name), weight="A")
                + SearchVector(
                    Value(candidate.title.display_name if candidate.title else ""),
                    weight="B",
                )
                + SearchVector(Value(candidate.city), weight="C")
                + SearchVector(Value(candidate.state), weight="C")
                + SearchVector(Value(candidate.notes or ""), weight="D")
                + SearchVector(Value(candidate.email), weight="A")
            )

            CandidateProfile.objects.filter(id=candidate.id).update(
                search_document=combined_vector
            )

            SearchVectorProcessingLog.objects.create(
                resume=resume,
                document_type="profile",
                status="success",
                message="CandidateProfile processed successfully.",
                attempts=self.request.retries,
            )
        else:
            SearchVectorProcessingLog.objects.create(
                resume=resume,
                document_type="resume",
                status="ignored",
                message="No extracted text found in resume.",
                attempts=self.request.retries,
            )
            raise Ignore()

    except CandidateResume.DoesNotExist:
        SearchVectorProcessingLog.objects.create(
            resume_id=resume_id,
            document_type="resume",
            status="failed",
            message="Resume not found.",
            attempts=self.request.retries,
        )
        raise Ignore()

    except Exception as e:
        SearchVectorProcessingLog.objects.create(
            resume_id=resume_id,
            document_type="resume",
            status="failed",
            message=str(e),
            attempts=self.request.retries,
        )
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task
def test_redis_celery_connection():
    return "Redis and Celery are connected!"
