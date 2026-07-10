from django.db import models

# Create your models here.
class ProduccionUVA1Permission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_produccion_uva_1', 'modulo_produccion_uva_1'),
            ('modulo_produccion_uva_1_dl','modulo_produccion_uva_1_dl'),
            ('modulo_produccion_uva_1_cv','modulo_produccion_uva_1_cv'),
            ('modulo_produccion_uva_1_ajs','modulo_produccion_uva_1_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('produccion_uva_1_item','produccion_uva_1_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('produccion_uva_1_presupuesto','produccion_uva_1_presupuesto'),
            ('produccion_uva_1_evaluacion_desempeno','produccion_uva_1_evaluacion_desempeno'),
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('produccion_uva_1_costos','produccion_uva_1_costos'),

        ]
        verbose_name = 'Permisos_Produccion_Uva_1'
        verbose_name_plural = 'Permisos_Produccion_Uva_1'