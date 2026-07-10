from django.db import models


# Create your models here.
class PDFFile(models.Model):
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
    
class RRHHPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
                #PERMISOS PRINCIPALES PARA EL RRHH Y POR EMPRESA                
                ('modulo_rrhh', 'modulo_rrhh'),
                ('modulo_rrhh_dl','modulo_rrhh_dl'),
                ('modulo_rrhh_cv','modulo_rrhh_cv'),
                ('modulo_rrhh_ajs','modulo_rrhh_ajs'),
                
                #PERMISO DE ACCESO A SECCIONES ESPECIFICAS DE MODULO RRHH
                ('RRHH_DL_INGRESO_INFORMACION','RRHH_DL_INGRESO_INFORMACION'),
                ('RRHH_DL_EVALUACION_DESEMPENO','RRHH_DL_EVALUACION_DESEMPENO'),
                ('RRHH_DL_REPORTE_UTILIDADES','RRHH_DL_REPORTE_UTILIDADES'),
                ('RRHH_REPORTE_CAMPANA_PODA_AMARRE','RRHH_REPORTE_CAMPANA_PODA_AMARRE'),
                ('RRHH_CV_REPORTE_UTILIDADES','RRHH_CV_REPORTE_UTILIDADES'),
                ('RRHH_presupuesto','RRHH_presupuesto'),




                #PERMISO DE ACCESO A SECCIONES ESPECIFICAS DE MODULO RRHH
                ('RRHH_item_publico','RRHH_item_publico'),
                
                
                #PERMISO SECCION PRESUPUESTO DE RRHH
                
                
                #PERMISO EXCLUSIVO PARA EL ANALISIS DE COSTOS
                ('RRHH_costos','RRHH_costos'),

        ]
        verbose_name = 'Permisos_RRHH'
        verbose_name_plural = 'Permisos_RRHH'
