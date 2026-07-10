from django.db import models

# Create your models here.
class CalidadPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_calidad', 'modulo_calidad'),
            ('modulo_calidad_dl','modulo_calidad_dl'),
            ('modulo_calidad_cv','modulo_calidad_cv'),
            ('modulo_calidad_ajs','modulo_calidad_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('calidad_item','calidad_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('calidad_presupuesto','calidad_presupuesto'),
            ('calidad_evaluacion_desempeno','calidad_evaluacion_desempeno'),    
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('calidad_costos','calidad_costos'),

        ]
        verbose_name = 'Permisos_Calidad'
        verbose_name_plural = 'Permisos_Calidad'