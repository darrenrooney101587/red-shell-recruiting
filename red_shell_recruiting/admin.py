from django.contrib import admin
from .models import (
    CandidateProfile,
    CandidateResume,
    SearchVectorProcessingLog,
    CandidateClientPlacement,
    CandidateProfileTitle,
)


@admin.register(CandidateProfileTitle)
class CandidateProfileTitleAdmin(admin.ModelAdmin):
    list_display = ("display_name",)
    search_fields = ("display_name",)


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "get_title",
        "email",
        "city",
        "state",
        "created_at",
        "updated_at",
    )
    search_fields = ("last_name", "email", "city", "state")

    def get_title(self, obj):
        return obj.title.display_name if obj.title else "-"

    get_title.short_description = "Title"
    get_title.admin_order_field = "title__display_name"


@admin.register(CandidateResume)
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


@admin.register(CandidateClientPlacement)
class CandidateClientPlacementAdmin(admin.ModelAdmin):
    list_display = ("display_name", "created_at", "updated_at")
    search_fields = ("display_name",)
    ordering = ("display_name",)
