from django.db import models
from django.conf import settings


class BoletaPermission(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("visualizar_boletas", "Puede visualizar boletas"),
        ]
        verbose_name = "Permiso de boletas"
        verbose_name_plural = "Permisos de boletas"


class PayslipAcknowledgement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payslip_acknowledgements",
    )
    worker_document = models.CharField(max_length=20, db_index=True)
    period_start = models.DateField()
    period_end = models.DateField()
    payroll_code = models.CharField(max_length=20, blank=True)
    payslip_hash = models.CharField(max_length=64, unique=True)
    signer_name = models.CharField(max_length=160)
    confirmed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ("-confirmed_at",)
        verbose_name = "Conformidad de boleta"
        verbose_name_plural = "Conformidades de boletas"


class PayrollRelease(models.Model):
    payroll_type = models.CharField(max_length=10)
    period_start = models.DateField()
    period_end = models.DateField()
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="validated_payroll_releases",
    )
    released_at = models.DateTimeField(null=True, blank=True)
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="released_payroll_releases",
    )

    @property
    def status(self):
        if self.released_at:
            return "authorized"
        if self.validated_at:
            return "validated"
        return "pending"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("payroll_type", "period_start", "period_end"),
                name="boletas_release_scope_unique",
            )
        ]
        verbose_name = "Publicación de boleta"
        verbose_name_plural = "Publicaciones de boletas"


class WorkerIdentityProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="worker_identity_profile",
    )
    worker_document = models.CharField(max_length=20, unique=True, db_index=True)
    signature = models.FileField(upload_to="boletas/identidad/firmas/")
    photo = models.FileField(upload_to="boletas/identidad/fotos/")
    consent_accepted = models.BooleanField(default=False)
    consent_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Identidad del trabajador"
        verbose_name_plural = "Identidades de trabajadores"


class PayslipView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payslip_views",
    )
    worker_document = models.CharField(max_length=20, db_index=True)
    period_start = models.DateField()
    period_end = models.DateField()
    payslip_hash = models.CharField(max_length=64, unique=True)
    first_viewed_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ("-last_viewed_at",)
        verbose_name = "Visualización de boleta"
        verbose_name_plural = "Visualizaciones de boletas"


class WorkerAccessRestriction(models.Model):
    worker_document = models.CharField(max_length=20, unique=True, db_index=True)
    disabled = models.BooleanField(default=True)
    reason = models.CharField(max_length=200, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="worker_access_updates",
    )

    class Meta:
        verbose_name = "Restricción de acceso del trabajador"
        verbose_name_plural = "Restricciones de acceso de trabajadores"


class PortalContent(models.Model):
    KIND_RIT = "RIT"
    KIND_NOTICE = "NOTICE"
    kind = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    file = models.FileField(upload_to="boletas/portal/", blank=True)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)


class AttendanceMark(models.Model):
    worker_document = models.CharField(max_length=20, db_index=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    client_event_id = models.CharField(max_length=64, unique=True, null=True, blank=True)
    action = models.CharField(max_length=10, choices=(("IN", "Ingreso"), ("OUT", "Salida")), default="IN")
    source = models.CharField(max_length=20, default="QR")
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        ordering = ("-marked_at",)
