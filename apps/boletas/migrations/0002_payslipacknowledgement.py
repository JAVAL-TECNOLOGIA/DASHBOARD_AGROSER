from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("boletas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PayslipAcknowledgement",
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
                ("worker_document", models.CharField(db_index=True, max_length=20)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("payroll_code", models.CharField(blank=True, max_length=20)),
                ("payslip_hash", models.CharField(max_length=64, unique=True)),
                ("signer_name", models.CharField(max_length=160)),
                ("confirmed_at", models.DateTimeField(auto_now_add=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=300)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payslip_acknowledgements",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Conformidad de boleta",
                "verbose_name_plural": "Conformidades de boletas",
                "ordering": ("-confirmed_at",),
            },
        ),
    ]
