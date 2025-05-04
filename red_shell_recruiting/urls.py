from django.urls import path
from red_shell_recruiting import views
from red_shell_recruiting.views import (
    CandidateSearch,
    CandidateDetail,
    ArchiveResume,
    UploadResume,
    UploadDocument,
    ArchiveDocument,
)

urlpatterns = [
    path(
        "",
        views.CandidateEnter.as_view(),
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
        "candidate/<int:candidate_id>/upload-resume/",
        UploadResume.as_view(),
        name="upload-resume",
    ),
    path(
        "candidate/<int:candidate_id>/upload-document/",
        UploadDocument.as_view(),
        name="upload-document",
    ),
]
