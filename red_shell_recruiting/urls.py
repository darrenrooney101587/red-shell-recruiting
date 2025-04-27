from django.urls import path
from red_shell_recruiting import views

urlpatterns = [
    path(
        '',
        views.CandidateEnter.as_view(),
        name='candidate-submit',
    )
]
