from django.contrib import admin
from .models import CandidateProfile, Resume

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'job_title', 'email', 'city', 'state', 'created_at', 'updated_at')
    search_fields = ('last_name', 'email', 'city', 'state')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'file', 'created_at', 'updated_at')
    search_fields = ('candidate__last_name',)
