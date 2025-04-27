import os
import tempfile

from celery import shared_task
from celery.exceptions import Ignore
import boto3
import textract
from django.conf import settings
from django.contrib.postgres.search import SearchVector
from red_shell_recruiting.models import Resume, CandidateProfile, SearchVectorProcessingLog

@shared_task(bind=True)
def update_resume_search_vector(self, resume_id):
    try:
        resume = Resume.objects.get(id=resume_id)
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=resume.file.name)
        file_bytes = obj['Body'].read()
        extension = resume.file.name.split('.')[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            extracted_text = textract.process(temp_file_path).decode('utf-8')
        finally:
            os.remove(temp_file_path)

        if extracted_text.strip():
            resume.extracted_text = extracted_text
            resume.save(update_fields=['extracted_text'])

            Resume.objects.filter(id=resume.id).update(
                search_document=SearchVector('extracted_text', weight='D')
            )

            SearchVectorProcessingLog.objects.create(
                resume=resume,
                document_type='resume',
                status='success',
                message='Resume processed successfully.',
                attempts=self.request.retries,
            )

            candidate = resume.candidate
            CandidateProfile.objects.filter(id=candidate.id).update(
                search_document=(
                        SearchVector('first_name', weight='A') +
                        SearchVector('last_name', weight='A') +
                        SearchVector('job_title', weight='B') +
                        SearchVector('city', weight='C') +
                        SearchVector('state', weight='C') +
                        SearchVector('notes', weight='D') +
                        SearchVector('email', weight='A')
                )
            )

            SearchVectorProcessingLog.objects.create(
                resume=resume,
                document_type='profile',
                status='success',
                message='CandidateProfile processed successfully.',
                attempts=self.request.retries,
            )
        else:
            SearchVectorProcessingLog.objects.create(
                resume=resume,
                document_type='resume',
                status='ignored',
                message='No extracted text found in resume.',
                attempts=self.request.retries,
            )
            raise Ignore()

    except Resume.DoesNotExist:
        SearchVectorProcessingLog.objects.create(
            resume_id=resume_id,
            document_type='resume',
            status='failed',
            message='Resume not found.',
            attempts=self.request.retries,
        )
        raise Ignore()

    except Exception as e:
        SearchVectorProcessingLog.objects.create(
            resume_id=resume_id,
            document_type='resume',
            status='failed',
            message=str(e),
            attempts=self.request.retries,
        )
        raise self.retry(exc=e, countdown=60, max_retries=3)
