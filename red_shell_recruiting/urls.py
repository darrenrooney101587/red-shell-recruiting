from django.urls import path
from red_shell_recruiting import views
from red_shell_recruiting.views import CandidateSearch

urlpatterns = [
    path(
        '',
        views.CandidateEnter.as_view(),
        name='candidate-submit',
    ),
    path('candidate-search/', CandidateSearch.as_view(), name='candidate-search'),
]
