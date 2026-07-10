from django.db import models


# Permisos para el módulo Cartillas Agrícolas (preparado para Fase 3+)
class CartillasAgricolaPermission(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ('modulo_cartillas_agricola', 'modulo_cartillas_agricola'),
            ('cartillas_evaluaciones', 'cartillas_evaluaciones'),
        ]
        verbose_name = 'Permisos_Cartillas_Agricola'
        verbose_name_plural = 'Permisos_Cartillas_Agricola'
