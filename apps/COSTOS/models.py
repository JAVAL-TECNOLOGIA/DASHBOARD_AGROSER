from django.db import models
from django.contrib.auth.models import Permission
from django.db import models
from decimal import Decimal

# Create your models here.

class COSTOSPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL COSTOS
                      
            ("ver_costos", "ver_costos"),

            #PERMISOS PARA VISUALIZAR LAS EMPRESAS
            ('modulo_costos_dl','modulo_costos_dl'),
            ('modulo_costos_cv','modulo_costos_cv'),
            ('modulo_costos_ajs','modulo_costos_ajs'),
            ('costos_evaluacion_desempeno','costos_evaluacion_desempeno'),

            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('costos_item','costos_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('costos_presupuesto','costos_presupuesto'),
]


