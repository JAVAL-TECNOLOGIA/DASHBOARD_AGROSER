from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import apps.tic_assets.models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=40, unique=True, verbose_name="Código patrimonial")),
                ("category", models.CharField(choices=[("PHONE", "Celular"), ("LAPTOP", "Laptop"), ("PC", "PC"), ("OTHER", "Otro")], db_index=True, max_length=12, verbose_name="Categoría")),
                ("brand", models.CharField(max_length=80, verbose_name="Marca")),
                ("model", models.CharField(max_length=100, verbose_name="Modelo")),
                ("serial_number", models.CharField(blank=True, db_index=True, max_length=100, verbose_name="Serie")),
                ("imei", models.CharField(blank=True, max_length=30, verbose_name="IMEI")),
                ("phone_number", models.CharField(blank=True, max_length=30, verbose_name="Número celular")),
                ("status", models.CharField(choices=[("NEW", "Nuevo"), ("AVAILABLE", "Disponible"), ("ASSIGNED", "Asignado"), ("MAINTENANCE", "Mantenimiento"), ("RETIRED", "Baja"), ("LOST", "Perdido")], db_index=True, default="NEW", max_length=15, verbose_name="Estado")),
                ("condition", models.CharField(default="BUENO", max_length=30, verbose_name="Condición")),
                ("accessories", models.TextField(blank=True, verbose_name="Accesorios")),
                ("notes", models.TextField(blank=True, verbose_name="Observaciones")),
                ("purchase_date", models.DateField(blank=True, null=True, verbose_name="Fecha de compra")),
                ("current_holder_document", models.CharField(blank=True, max_length=20)),
                ("current_holder_name", models.CharField(blank=True, max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="tic_assets_created", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("category", "code"), "permissions": (("manage_tic_assets", "Puede administrar inventario y asignaciones TIC"),)},
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("movement_type", models.CharField(choices=[("DELIVERY", "Asignación"), ("RETURN", "Devolución"), ("MAINTENANCE_IN", "Ingreso a mantenimiento"), ("MAINTENANCE_OUT", "Salida de mantenimiento"), ("RETIRE", "Baja")], default="DELIVERY", max_length=20)),
                ("worker_document", models.CharField(blank=True, max_length=20, verbose_name="Documento")), ("worker_name", models.CharField(blank=True, max_length=180, verbose_name="Trabajador")), ("worker_email", models.EmailField(blank=True, max_length=254, verbose_name="Correo")), ("worker_phone", models.CharField(blank=True, max_length=30, verbose_name="Celular")),
                ("observations", models.TextField(blank=True, verbose_name="Observaciones")),
                ("signature", models.ImageField(blank=True, null=True, upload_to=apps.tic_assets.models.assignment_upload)), ("evidence", models.ImageField(blank=True, null=True, upload_to=apps.tic_assets.models.assignment_upload)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("asset", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movements", to="tic_assets.asset")),
                ("registered_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ], options={"ordering": ("-created_at",)},
        ),
    ]
