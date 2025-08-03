from django.urls import path

from red_shell_recruiting import views
from red_shell_recruiting.views import (
    CandidateSearch,
    CandidateDetail,
    ArchiveResume,
    UploadResume,
    UploadDocument,
    ArchiveDocument,
    client_placement_list,
    UploadCulinaryPortfolio,
    ArchiveCulinaryPortfolio,
    svg_showcase,
)

urlpatterns = [
    path("svg-showcase/", svg_showcase, name="svg_showcase"),
    path("candidate-submit/", views.CandidateInput.as_view(), name="candidate-submit"),
    path("candidate-search/", CandidateSearch.as_view(), name="candidate-search"),
    path(
        "candidate-detail/<int:candidate_id>/",
        CandidateDetail.as_view(),
        name="candidate-detail",
    ),
    path(
        "api/resume/archive/<int:resume_id>/",
        ArchiveResume.as_view(),
        name="archive-resume",
    ),
    path(
        "api/document/archive/<int:document_id>/",
        ArchiveDocument.as_view(),
        name="archive-document",
    ),
    path(
        "api/archive/culinary-portfolio/<int:portfolio_id>/",
        ArchiveCulinaryPortfolio.as_view(),
        name="archive-culinary-portfolio",
    ),
    path(
        "api/<int:candidate_id>/upload-resume/",
        UploadResume.as_view(),
        name="upload-resume",
    ),
    path(
        "api/<int:candidate_id>/upload-culinary-portfolio/",
        UploadCulinaryPortfolio.as_view(),
        name="upload-culinary-portfolio",
    ),
    path(
        "api/<int:candidate_id>/upload-document/",
        UploadDocument.as_view(),
        name="upload-document",
    ),
    path("api/client-placements/", client_placement_list, name="client-placement-list"),
    path(
        "api/candidate-titles/", views.candidate_title_list, name="candidate-title-list"
    ),
    path(
        "api/candidate-titles-filtered/",
        views.candidate_title_list_filtered,
        name="candidate-title-list-filtered",
    ),
    path(
        "api/candidate-sources/",
        views.candidate_source_list,
        name="candidate-source-list",
    ),
    path(
        "api/candidate-sources-filtered/",
        views.candidate_source_list_filtered,
        name="candidate-source-list-filtered",
    ),
    path(
        "api/candidate-ownerships/",
        views.candidate_ownership_list,
        name="candidate-ownership-list",
    ),
    path(
        "api/candidate-ownerships-filtered/",
        views.candidate_ownership_list_filtered,
        name="candidate-ownership-list-filtered",
    ),
    path(
        "api/journal_entries/<int:candidate_id>",
        views.JournalEntryView.as_view(),
        name="journal-entries",
    ),
    path(
        "api/placement_records/<int:candidate_id>/",
        views.PlacementRecordView.as_view(),
        name="placement-records",
    ),
]
