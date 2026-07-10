from django.db import models

# Create your models here.
class ProduccionUVA2Permission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_produccion_uva_2', 'modulo_produccion_uva_2'),
            ('modulo_produccion_uva_2_dl','modulo_produccion_uva_2_dl'),
            ('modulo_produccion_uva_2_cv','modulo_produccion_uva_2_cv'),
            ('modulo_produccion_uva_2_ajs','modulo_produccion_uva_2_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('produccion_uva_2_item','produccion_uva_2_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('produccion_uva_2_presupuesto','produccion_uva_2_presupuesto'),
            ('produccion_uva_2_evaluacion_desempeno','produccion_uva_2_evaluacion_desempeno'),    
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('produccion_uva_2_costos','produccion_uva_2_costos'),

        ]
        verbose_name = 'Permisos_Produccion_Uva_2'
        verbose_name_plural = 'Permisos_Produccion_Uva_2'