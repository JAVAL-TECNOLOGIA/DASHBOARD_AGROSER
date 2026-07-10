from django.db import models

# Create your models here.
class LegalPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            #PERMISSIONS PARA EL LEGAL               
            ('modulo_legal', 'modulo_legal'),
            ('modulo_legal_dl','modulo_legal_dl'),
            ('modulo_legal_cv','modulo_legal_cv'),
            ('modulo_legal_ajs','modulo_legal_ajs'),
                
            #PERMISO DE ACCESO ESTANDAR AL MODULO CONTABILIDAD
            ('legal_item','legal_item'),
                
            #PERMISO SECCION PRESUPUESTO DE CONTABILIDAD
            ('legal_presupuesto','legal_presupuesto'),
                
            #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
            ('legal_costos','legal_costos'),

        ]
        verbose_name = 'Permisos_Legal'
        verbose_name_plural = 'Permisos_Legal'