from django.db import models

# Create your models here.
class EvaluacionesPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_evaluaciones', 'modulo_evaluaciones'),
            ('modulo_evaluaciones_dl','modulo_evaluaciones_dl'),
            ('modulo_evaluaciones_cv','modulo_evaluaciones_cv'),
            ('modulo_evaluaciones_ajs','modulo_evaluaciones_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('evaluaciones_item','evaluaciones_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('evaluaciones_presupuesto','evaluaciones_presupuesto'),
            ('evaluaciones_evaluacion_desempeno','evaluaciones_evaluacion_desempeno'),
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('evaluaciones_costos','evaluaciones_costos'),

        ]
        verbose_name = 'Permisos_Evaluaciones'
        verbose_name_plural = 'Permisos_Evaluaciones'