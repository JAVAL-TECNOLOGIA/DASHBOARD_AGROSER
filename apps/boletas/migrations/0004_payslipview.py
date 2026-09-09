from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("boletas", "0003_workeridentityprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="PayslipView",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("worker_document", models.CharField(db_index=True, max_length=20)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("payslip_hash", models.CharField(max_length=64, unique=True)),
                ("first_viewed_at", models.DateTimeField(auto_now_add=True)),
                ("last_viewed_at", models.DateTimeField(auto_now=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=300)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payslip_views", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-last_viewed_at",), "verbose_name": "Visualización de boleta", "verbose_name_plural": "Visualizaciones de boletas"},
        ),
    ]
