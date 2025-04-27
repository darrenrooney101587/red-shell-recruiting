from django.urls import path
from red_shell_recruiting import views

urlpatterns = [
    path(
        'enter',
        views.CandidateEnter.as_view(),
        name='candidate-enter',
    ),
    path(
        'submit',
        views.CandidateSubmit.as_view(),
        name='candidate-submit',
    )
]
