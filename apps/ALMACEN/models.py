from django.db import models

# Create your models here.
class AlmacenPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            
            #PERMISSIONS PARA EL RRHH               
            ('modulo_almacen', 'modulo_almacen'),

            #PERMISOS PARA VISUALIZAR LAS EMPRESAS
            ('modulo_almacen_dl','modulo_almacen_dl'),
            ('modulo_almacen_cv','modulo_almacen_cv'),
            ('modulo_almacen_ajs','modulo_almacen_ajs'),     

            #PERMISO DE ACCESO ESTANDAR AL MODULO ALMACEN
            ('almacen_item','almacen_item'),
                
            #PERMISO SECCION PRESUPUESTO DE ALMACEN
            ('almacen_presupuesto','almacen_presupuesto'),
            ('almacen_evaluacion_desempeno','almacen_evaluacion_desempeno'),
            ('almacen_req_internos','almacen_req_internos'),
            
            #PERMISO SECCION COSTOS DE ALMACEN
            ('almacen_costos','almacen_costos'),
        ]
        verbose_name = 'Permisos_Almacen'
        verbose_name_plural = 'Permisos_Almacen'