from django.db import models

class CandidateProfile(models.Model):
    name = models.CharField(max_length=255)
    current_location = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)  # Adjust based on phone format
    email = models.EmailField(unique=True)
    compensation = models.DecimalField(max_digits=10, decimal_places=2)  # Example compensation field
    notes = models.TextField(null=True, blank=True)
    open_to_relocation = models.BooleanField(default=False)
    currently_working = models.BooleanField(default=True)
    actively_looking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.name} - {self.job_title}"

    class Meta:
        managed = True
        db_table = 'candidate_profile'


class Resume(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Resume for {self.candidate.name}"

    class Meta:
        managed = True
        db_table = 'candidate_resume'
