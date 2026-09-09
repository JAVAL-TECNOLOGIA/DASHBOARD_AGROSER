from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("boletas", "0004_payslipview"),
    ]
    operations = [
        migrations.CreateModel(
            name="WorkerAccessRestriction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("worker_document", models.CharField(db_index=True, max_length=20, unique=True)),
                ("disabled", models.BooleanField(default=True)),
                ("reason", models.CharField(blank=True, max_length=200)),
                ("disabled_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="worker_access_updates", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Restricción de acceso del trabajador", "verbose_name_plural": "Restricciones de acceso de trabajadores"},
        ),
    ]
