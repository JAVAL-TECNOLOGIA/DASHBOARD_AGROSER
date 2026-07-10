from django.db import models

# Create your models here.



class ContabilidadPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
                #PERMISSIONS PARA EL CONTABILIDAD               
                ('modulo_contabilidad', 'modulo_contabilidad'),

                ('modulo_contabilidad_dl','modulo_contabilidad_dl'),
                ('modulo_contabilidad_cv','modulo_contabilidad_cv'),
                ('modulo_contabilidad_ajs','modulo_contabilidad_ajs'),
                
                #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
                ('contabilidad_item','contabilidad_item'),
                
                #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
                ('contabilidad_presupuesto','contabilidad_presupuesto'),
                ('contabilidad_evaluacion_desempeno','contabilidad_evaluacion_desempeno'),
                
                #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
                ('contabilidad_costos','contabilidad_costos'),
        ]
        verbose_name = 'Permisos_Contabilidad'
        verbose_name_plural = 'Permisos_Contabilidad'