from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from django.db.models.functions import Cast
from django.db.models import TextField
from red_shell_recruiting.models import CandidateProfile

"""
    be sure to add the fields you are including into the task.pv profile 
"""
SEARCHABLE_FIELDS = [
    ('first_name', 'A', False),
    ('last_name', 'A', False),
    ('job_title', 'B', False),
    ('city', 'C', False),
    ('state', 'C', False),
    ('notes', 'D', False),
    ('email', 'A', False),
    ('phone_number', 'B', False),
    ('compensation', 'C', True),
]

class Command(BaseCommand):
    help = 'Rebuild search_document for all CandidateProfiles'

    def handle(self, *args, **options):
        candidates = CandidateProfile.objects.all()
        count = 0

        for candidate in candidates:
            search_vector = None
            for field_name, weight, needs_cast in SEARCHABLE_FIELDS:
                if needs_cast:
                    vector = SearchVector(Cast(field_name, TextField()), weight=weight)
                else:
                    vector = SearchVector(field_name, weight=weight)

                if search_vector is None:
                    search_vector = vector
                else:
                    search_vector += vector

            CandidateProfile.objects.filter(id=candidate.id).update(
                search_document=search_vector
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully revectorized {count} candidate profiles."))
