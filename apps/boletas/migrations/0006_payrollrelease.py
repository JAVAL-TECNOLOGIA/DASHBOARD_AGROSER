from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("boletas", "0005_workeraccessrestriction")]

    operations = [
        migrations.CreateModel(
            name="PayrollRelease",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payroll_type", models.CharField(max_length=10)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("released_at", models.DateTimeField(auto_now_add=True)),
                ("released_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Publicación de boleta", "verbose_name_plural": "Publicaciones de boletas"},
        ),
        migrations.AddConstraint(
            model_name="payrollrelease",
            constraint=models.UniqueConstraint(fields=("payroll_type", "period_start", "period_end"), name="boletas_release_scope_unique"),
        ),
    ]
