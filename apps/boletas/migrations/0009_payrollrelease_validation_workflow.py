from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def preserve_existing_releases(apps, schema_editor):
    PayrollRelease = apps.get_model("boletas", "PayrollRelease")
    for release in PayrollRelease.objects.all().iterator():
        release.validated_at = release.released_at
        release.validated_by_id = release.released_by_id
        release.save(update_fields=("validated_at", "validated_by"))


class Migration(migrations.Migration):
    dependencies = [("boletas", "0008_attendancemark")]

    operations = [
        migrations.AddField(
            model_name="payrollrelease",
            name="validated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="payrollrelease",
            name="validated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="validated_payroll_releases",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="payrollrelease",
            name="released_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="payrollrelease",
            name="released_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="released_payroll_releases",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(preserve_existing_releases, migrations.RunPython.noop),
    ]
