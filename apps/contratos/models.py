from django.db import models


class ContratoPermission(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("gestionar_contratos", "Puede generar y administrar contratos"),
        )
