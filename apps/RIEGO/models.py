from django.db import models

# Create your models here.
class RiegoPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_riego', 'modulo_riego'),
            ('modulo_riego_dl','modulo_riego_dl'),
            ('modulo_riego_cv','modulo_riego_cv'),
            ('modulo_riego_ajs','modulo_riego_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('riego_item','riego_item'),
            ('RIEGO_PRODUCCION_UVA','RIEGO_PRODUCCION_UVA'),
            ('RIEGO_FERTIRRIEGO_UVA','RIEGO_FERTIRRIEGO_UVA'),


            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('RIEGO_PRODUCCION_UVA_SECCION_CONSOLIDADO','RIEGO_PRODUCCION_UVA_SECCION_CONSOLIDADO'),
            ('RIEGO_PRODUCCION_UVA_SECCION_SUELDOS','RIEGO_PRODUCCION_UVA_SECCION_SUELDOS'),
            ('RIEGO_PRODUCCION_UVA_SECCION_SERVICIOS','RIEGO_PRODUCCION_UVA_SECCION_SERVICIOS'),
            ('RIEGO_PRODUCCION_UVA_SECCION_MATERIALES','RIEGO_PRODUCCION_UVA_SECCION_MATERIALES'),
            ('RIEGO_PRODUCCION_UVA_SECCION_CAPEX','RIEGO_PRODUCCION_UVA_SECCION_CAPEX'),
            ('RIEGO_PRODUCCION_UVA_SECCION_FERTILIZACION','RIEGO_PRODUCCION_UVA_SECCION_FERTILIZACION'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('riego_presupuesto','riego_presupuesto'),
            ('riego_evaluacion_desempeno','riego_evaluacion_desempeno'),
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('riego_costos','riego_costos'),

        ]
        verbose_name = 'Permisos_Riego'
        verbose_name_plural = 'Permisos_Riego'