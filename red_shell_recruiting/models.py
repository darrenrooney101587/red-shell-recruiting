import os

from django.db import models
from django.utils.timezone import now


def resume_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    timestamp = now().strftime('%Y_%m_%d_%H%M%S')
    return f"resumes/{instance.candidate.id}/{base}_{timestamp}{ext}"

class CandidateProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
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

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_title}"

    class Meta:
        managed = True
        db_table = 'candidate_profile'


class Resume(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to=resume_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.candidate.name}"

    class Meta:
        managed = True
        db_table = 'candidate_resume'
