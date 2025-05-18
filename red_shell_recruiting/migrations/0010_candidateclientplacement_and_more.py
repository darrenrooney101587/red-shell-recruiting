from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def create_default_client_placement(apps, schema_editor):
    CandidateClientPlacement = apps.get_model(
        "red_shell_recruiting", "CandidateClientPlacement"
    )
    default = CandidateClientPlacement.objects.create(
        display_name="Default Placement", month=12, year=2019, created_at=timezone.now()
    )

    CandidateProfile = apps.get_model("red_shell_recruiting", "CandidateProfile")
    # Use model field name, not 'fieldname_id'
    CandidateProfile.objects.all().update(candidate_placement=default)


def remove_default_client_placement(apps, schema_editor):
    CandidateClientPlacement = apps.get_model(
        "red_shell_recruiting", "CandidateClientPlacement"
    )
    CandidateClientPlacement.objects.filter(display_name="Default Placement").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("red_shell_recruiting", "0009_searchvectorprocessinglog_document_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CandidateClientPlacement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("display_name", models.CharField(max_length=100)),
                ("month", models.IntegerField()),
                ("year", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "candidate_client_placement",
                "managed": True,
            },
        ),
        migrations.AddField(
            model_name="candidateprofile",
            name="candidate_placement",
            field=models.ForeignKey(
                to="red_shell_recruiting.candidateclientplacement",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="client_placement",
                null=True,  # temporarily nullable
            ),
        ),
        migrations.RunPython(
            create_default_client_placement,
            reverse_code=remove_default_client_placement,
        ),
        migrations.AlterField(
            model_name="candidateprofile",
            name="candidate_placement",
            field=models.ForeignKey(
                to="red_shell_recruiting.candidateclientplacement",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="client_placement",
            ),
        ),
    ]
