from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("boletas", "0002_payslipacknowledgement"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkerIdentityProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("worker_document", models.CharField(db_index=True, max_length=20, unique=True)),
                ("signature", models.FileField(upload_to="boletas/identidad/firmas/")),
                ("photo", models.FileField(upload_to="boletas/identidad/fotos/")),
                ("consent_accepted", models.BooleanField(default=False)),
                ("consent_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(auto_now_add=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=300)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="worker_identity_profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "Identidad del trabajador", "verbose_name_plural": "Identidades de trabajadores"},
        ),
    ]
