from django.contrib import admin
from .models import CandidateProfile, Resume, SearchVectorProcessingLog


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "job_title",
        "email",
        "city",
        "state",
        "created_at",
        "updated_at",
    )
    search_fields = ("last_name", "email", "city", "state")


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("candidate", "file", "created_at", "updated_at")
    search_fields = ("candidate__last_name",)


@admin.register(SearchVectorProcessingLog)
class SearchVectorProcessingLogAdmin(admin.ModelAdmin):
    list_display = (
        "resume",
        "document",
        "document_type",
        "status",
        "attempts",
        "short_message",
        "created_at",
    )
    list_filter = ("document_type", "status", "created_at")
    search_fields = (
        "resume__candidate__first_name",
        "resume__candidate__last_name",
        "message",
    )
    readonly_fields = (
        "resume",
        "document_type",
        "status",
        "message",
        "attempts",
        "created_at",
    )
    ordering = ("-created_at",)

    def short_message(self, obj):
        return (
            (obj.message[:75] + "...")
            if obj.message and len(obj.message) > 75
            else obj.message
        )

    short_message.short_description = "Message"
