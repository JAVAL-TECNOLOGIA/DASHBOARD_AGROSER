from django.conf import settings
from django.db import models


class Asset(models.Model):
    class Category(models.TextChoices):
        PHONE = "PHONE", "Celular"
        LAPTOP = "LAPTOP", "Laptop"
        PC = "PC", "PC"
        OTHER = "OTHER", "Otro"

    class Status(models.TextChoices):
        NEW = "NEW", "Nuevo"
        AVAILABLE = "AVAILABLE", "Disponible"
        ASSIGNED = "ASSIGNED", "Asignado"
        MAINTENANCE = "MAINTENANCE", "Mantenimiento"
        RETIRED = "RETIRED", "Baja"
        LOST = "LOST", "Perdido"

    code = models.CharField("Código patrimonial", max_length=40, unique=True)
    category = models.CharField("Categoría", max_length=12, choices=Category.choices, db_index=True)
    brand = models.CharField("Marca", max_length=80)
    model = models.CharField("Modelo", max_length=100)
    serial_number = models.CharField("Serie", max_length=100, blank=True, db_index=True)
    imei = models.CharField("IMEI", max_length=30, blank=True)
    phone_number = models.CharField("Número celular", max_length=30, blank=True)
    status = models.CharField("Estado", max_length=15, choices=Status.choices, default=Status.NEW, db_index=True)
    condition = models.CharField("Condición", max_length=30, default="BUENO")
    accessories = models.TextField("Accesorios", blank=True)
    notes = models.TextField("Observaciones", blank=True)
    purchase_date = models.DateField("Fecha de compra", null=True, blank=True)
    current_holder_document = models.CharField(max_length=20, blank=True)
    current_holder_name = models.CharField(max_length=180, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tic_assets_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("category", "code")
        permissions = (("manage_tic_assets", "Puede administrar inventario y asignaciones TIC"),)

    def __str__(self):
        return f"{self.code} - {self.brand} {self.model}"


def assignment_upload(instance, filename):
    return f"tic/asignaciones/{instance.asset.code}/{filename}"


class Assignment(models.Model):
    class Type(models.TextChoices):
        DELIVERY = "DELIVERY", "Asignación"
        RETURN = "RETURN", "Devolución"
        MAINTENANCE_IN = "MAINTENANCE_IN", "Ingreso a mantenimiento"
        MAINTENANCE_OUT = "MAINTENANCE_OUT", "Salida de mantenimiento"
        RETIRE = "RETIRE", "Baja"

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=Type.choices, default=Type.DELIVERY)
    worker_document = models.CharField("Documento", max_length=20, blank=True)
    worker_name = models.CharField("Trabajador", max_length=180, blank=True)
    worker_email = models.EmailField("Correo", blank=True)
    worker_phone = models.CharField("Celular", max_length=30, blank=True)
    observations = models.TextField("Observaciones", blank=True)
    signature = models.ImageField(upload_to=assignment_upload, blank=True, null=True)
    evidence = models.ImageField(upload_to=assignment_upload, blank=True, null=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.asset.code}"
