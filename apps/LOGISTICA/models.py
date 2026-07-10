from django.db import models

# Create your models here.
class LogisticaPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
                    #PERMISSIONS PARA EL LOGISTICA               
                ('modulo_logistica', 'modulo_logistica'),
                
                ('modulo_logistica_dl','modulo_logistica_dl'),
                ('modulo_logistica_cv','modulo_logistica_cv'),
                ('modulo_logistica_ajs','modulo_logistica_ajs'),
                
                #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
                ('logistica_item','logistica_item'),
                ('logistica_evaluacion_desempeno','logistica_evaluacion_desempeno'),
                
                #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
                ('logistica_presupuesto','logistica_presupuesto'),
                
                #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
                ('logistica_costos','logistica_costos'),

        ]
        verbose_name = 'Permisos_Logistica'
        verbose_name_plural = 'Permisos_Logistica'