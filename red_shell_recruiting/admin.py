from django.contrib import admin
from .models import CandidateProfile, Resume

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_title', 'email', 'current_location', 'created_at', 'updated_at')
    search_fields = ('name', 'email')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'file', 'created_at', 'updated_at')
    search_fields = ('candidate__name',)
