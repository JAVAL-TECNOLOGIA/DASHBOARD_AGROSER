from django.db import models

# Create your models here.
class SeguridadPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
                    #PERMISSIONS PARA EL SEGURIDAD               
                ('modulo_seguridad', 'modulo_seguridad'),
                
                ('modulo_seguridad_dl','modulo_seguridad_dl'),
                ('modulo_seguridad_cv','modulo_seguridad_cv'),
                ('modulo_seguridad_ajs','modulo_seguridad_ajs'),
                
                #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
                ('seguridad_item','seguridad_item'),
                
                #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
                ('seguridad_presupuesto','seguridad_presupuesto'),
                
                #PERMISO SECCION EVALUACION DE DESPEÑO DE CONTABILIDAD
                ('seguridad_evaluacion_desempeno','seguridad_evaluacion_desempeno'),
                
                #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
                ('seguridad_costos','seguridad_costos'),

        ]
        verbose_name = 'Permisos_Seguridad'
        verbose_name_plural = 'Permisos_Seguridad'