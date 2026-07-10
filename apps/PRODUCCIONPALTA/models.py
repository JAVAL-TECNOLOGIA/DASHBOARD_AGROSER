from django.db import models

# Create your models here.
class ProduccionPaltaPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_produccion_palta', 'modulo_produccion_palta'),
            ('modulo_produccion_palta_dl','modulo_produccion_palta_dl'),
            ('modulo_produccion_palta_cv','modulo_produccion_palta_cv'),
            ('modulo_produccion_palta_ajs','modulo_produccion_palta_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('produccion_palta_item','produccion_palta_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('produccion_palta_presupuesto','produccion_palta_presupuesto'),
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('produccion_palta_costos','produccion_palta_costos'),

        ]
        verbose_name = 'Permisos_Produccion_Palta'
        verbose_name_plural = 'Permisos_Produccion_Palta'