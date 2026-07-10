from django.db import models


class ScriptPermission(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        permissions = [
            #PERMISSIONS PARA EL ALMACEN
            ('puede_ver_logistica', 'puede ver logistica'),
            ('puede_ver_ti', 'puede ver ti'),
            ('puede_ver_informes_bi', 'puede ver informes bi'),

            # PERMISOS PARA EL MODULO DE APROBACIONES
            ('MODULO_APROBACIONES', 'MODULO_APROBACIONES'),

            # PERMISOS PARA EL MODULO DE APROBACIONES DONLUIS
            

            ('MODULO_APROBACIONES_DONLUIS', 'MODULO_APROBACIONES_DONLUIS'),
            ('MODULO_APROBACIONES_DONLUIS_FITOSANIDAD', 'MODULO_APROBACIONES_DONLUIS_FITOSANIDAD'),
            ('MODULO_APROBACIONES_DONLUIS_REQUERIMIENTOS', 'MODULO_APROBACIONES_DONLUIS_REQUERIMIENTOS'),
            ('MODULO_APROBACIONES_DONLUIS_PEDIDOS', 'MODULO_APROBACIONES_DONLUIS_PEDIDOS'),
            ('MODULO_APROBACIONES_DONLUIS_APROBACION_ORDENES', 'MODULO_APROBACIONES_DONLUIS_APROBACION_ORDENES'),


            # PERMISOS PARA EL MODULO DE APROBACIONES DONLUIS PEDIDOS
            ('MODULO_APROBACIONES_DONLUIS_PEDIDOS_COMPRAS', 'MODULO_APROBACIONES_DONLUIS_PEDIDOS_COMPRAS'),
            ('MODULO_APROBACIONES_DONLUIS_PEDIDOS_SERVICIOS', 'MODULO_APROBACIONES_DONLUIS_PEDIDOS_SERVICIOS'),
            
            ######################################################################################################

            # PERMISOS PARA EL MODULO DE APROBACIONES AJS
            ('MODULO_APROBACIONES_AJS', 'MODULO_APROBACIONES_AJS'),
            ('MODULO_APROBACIONES_AJS_FITOSANIDAD', 'MODULO_APROBACIONES_AJS_FITOSANIDAD'),
            ('MODULO_APROBACIONES_AJS_REQUERIMIENTOS', 'MODULO_APROBACIONES_AJS_REQUERIMIENTOS'),
            ('MODULO_APROBACIONES_AJS_PEDIDOS', 'MODULO_APROBACIONES_AJS_PEDIDOS'),
            ('MODULO_APROBACIONES_AJS_APROBACION_ORDENES', 'MODULO_APROBACIONES_AJS_APROBACION_ORDENES'),

            # PERMISOS PARA EL MODULO DE APROBACIONES AJS PEDIDOS
            ('MODULO_APROBACIONES_AJS_PEDIDOS_COMPRAS', 'MODULO_APROBACIONES_AJS_PEDIDOS_COMPRAS'),
            ('MODULO_APROBACIONES_AJS_PEDIDOS_SERVICIOS', 'MODULO_APROBACIONES_AJS_PEDIDOS_SERVICIOS'),

            ####################################################################################################

            # PERMISOS PARA EL MODULO DE APROBACIONES CV
            ('MODULO_APROBACIONES_CV', 'MODULO_APROBACIONES_CV'),
            ('MODULO_APROBACIONES_CV_FITOSANIDAD', 'MODULO_APROBACIONES_CV_FITOSANIDAD'),
            ('MODULO_APROBACIONES_CV_REQUERIMIENTOS', 'MODULO_APROBACIONES_CV_REQUERIMIENTOS'),
            ('MODULO_APROBACIONES_CV_PEDIDOS', 'MODULO_APROBACIONES_CV_PEDIDOS'),
            ('MODULO_APROBACIONES_CV_APROBACION_ORDENES', 'MODULO_APROBACIONES_CV_APROBACION_ORDENES'),

            # PERMISOS PARA EL MODULO DE APROBACIONES CV PEDIDOS
            ('MODULO_APROBACIONES_CV_PEDIDOS_COMPRAS', 'MODULO_APROBACIONES_CV_PEDIDOS_COMPRAS'),
            ('MODULO_APROBACIONES_CV_PEDIDOS_SERVICIOS', 'MODULO_APROBACIONES_CV_PEDIDOS_SERVICIOS'),

            ####################################################################################################





            
             # PERMISOS PARA LOGISTICA
            ("ver_logistica_dl", "ver_logistica_dl"),
            ("ver_logistica_cv", "ver_logistica_cv"),
            ("ver_logistica_ajs", "ver_logistica_ajs"),

            # PERMISOS PARA CONTABILIDAD
            ("ver_contabilidad ", "ver_contabilidad"),

            # PERMISOS PARA SPACE
            ("ver_reportes_space", "ver_reportes_space"),
            ("ver_space_calidad", "ver_space_calidad"),
            ("ver_space_evaluacion", "ver_space_evaluacion"),
            ("ver_space_riego", "ver_space_riego"),
            
            # PERMISOS PARA  APROBACIONES
            ("aei_approve_orders", "aei_approve_orders"),

            
            
            
        ]
