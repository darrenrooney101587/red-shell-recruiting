from django.db import migrations, models
import django.db.models.deletion


def create_default_ownership(apps, schema_editor):
    CandidateOwnerShip = apps.get_model("red_shell_recruiting", "CandidateOwnerShip")
    CandidateOwnerShip.objects.get_or_create(display_name="Unassigned")


def set_default_ownership_fk(apps, schema_editor):
    CandidateOwnerShip = apps.get_model("red_shell_recruiting", "CandidateOwnerShip")
    default_record = CandidateOwnerShip.objects.get(display_name="Unassigned")

    # Set all nulls to the new default
    CandidateProfile = apps.get_model("red_shell_recruiting", "CandidateProfile")
    CandidateProfile.objects.filter(owner_ship__isnull=True).update(
        owner_ship=default_record.id
    )


class Migration(migrations.Migration):

    dependencies = [
        ("red_shell_recruiting", "0015_candidateprofiletitleadmin"),
    ]

    operations = [
        migrations.CreateModel(
            name="CandidateOwnerShip",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "candidate_owner_ship",
                "managed": True,
            },
        ),
        migrations.DeleteModel(
            name="CandidateProfileTitleAdmin",
        ),
        migrations.RunPython(create_default_ownership),
        migrations.AddField(
            model_name="candidateprofile",
            name="owner_ship",
            field=models.ForeignKey(
                default=1,  # Placeholder; will be fixed by the actual object
                on_delete=django.db.models.deletion.PROTECT,
                to="red_shell_recruiting.candidateownership",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_ownership_fk),
    ]
