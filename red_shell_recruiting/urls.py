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
    path(
        "candidate-submit/",
        views.CandidateInput.as_view(),
        name="candidate-submit",
    ),
    path("candidate-search/", CandidateSearch.as_view(), name="candidate-search"),
    path("<int:candidate_id>/", CandidateDetail.as_view(), name="candidate-detail"),
    path(
        "resume/archive/<int:resume_id>/",
        ArchiveResume.as_view(),
        name="archive-resume",
    ),
    path(
        "document/archive/<int:document_id>/",
        ArchiveDocument.as_view(),
        name="archive-document",
    ),
    path(
        "candidate/culinary-portfolio/<int:portfolio_id>/archive/",
        ArchiveCulinaryPortfolio.as_view(),
        name="archive-culinary-portfolio",
    ),
    path(
        "candidate/<int:candidate_id>/upload-resume/",
        UploadResume.as_view(),
        name="upload-resume",
    ),
    path(
        "candidate/<int:candidate_id>/upload-culinary-portfolio/",
        UploadCulinaryPortfolio.as_view(),
        name="upload-culinary-portfolio",
    ),
    path(
        "candidate/<int:candidate_id>/upload-document/",
        UploadDocument.as_view(),
        name="upload-document",
    ),
    path("api/client-placements/", client_placement_list, name="client-placement-list"),
    path(
        "api/candidate-titles/", views.candidate_title_list, name="candidate-title-list"
    ),
    path(
        "api/candidate-sources/",
        views.candidate_source_list,
        name="candidate-source-list",
    ),
    path(
        "api/candidate-ownership/",
        views.candidate_ownership_list,
        name="candidate-ownership-list",
    ),
    path(
        "candidate/<int:candidate_id>/journal_entries/",
        views.JournalEntryView.as_view(),
        name="journal-entries",
    ),
    path(
        "candidate/<int:candidate_id>/placement_records/",
        views.PlacementRecordView.as_view(),
        name="placement-records",
    ),
]
