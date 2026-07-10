from django.db import models

# Create your models here.
class AplicacionesPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_aplicaciones', 'modulo_aplicaciones'),
            ('modulo_aplicaciones_dl','modulo_aplicaciones_dl'),
            ('modulo_aplicaciones_cv','modulo_aplicaciones_cv'),
            ('modulo_aplicaciones_ajs','modulo_aplicaciones_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('aplicaciones_item','aplicaciones_item'),

            #PERMISO SECCION PRESUPUESTO DE APLICACIONES
            ('aplicaciones_presupuesto_resumen','aplicaciones_presupuesto_resumen'),
            ('aplicaciones_presupuesto_sueldos','aplicaciones_presupuesto_sueldos'),
            ('aplicaciones_presupuesto_servicios','aplicaciones_presupuesto_servicios'),
            ('aplicaciones_presupuesto_materiales','aplicaciones_presupuesto_materiales'),
            ('aplicaciones_presupuesto_capex','aplicaciones_presupuesto_capex'),
            ('aplicaciones_fito','aplicaciones_fito'),
            ('aplicaciones_evaluacion_desempeno','aplicaciones_evaluacion_desempeno'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('aplicaciones_presupuesto','aplicaciones_presupuesto'),    
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('aplicaciones_costos','aplicaciones_costos'),

        ]
        verbose_name = 'Permisos_Aplicaciones'
        verbose_name_plural = 'Permisos_Aplicaciones'