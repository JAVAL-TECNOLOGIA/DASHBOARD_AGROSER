from django.db import models

# Create your models here.

class GerenciaPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            ('modulo_gerencia', 'modulo_gerencia'),
            ('gerencia_ev_competencias', 'gerencia_ev_competencias'),
        ]   
        verbose_name = 'Permisos_Gerencia'
        verbose_name_plural = 'Permisos_Gerencia'

