
from django.db import models

# Permisos para el módulo Presupuesto Agrícola
class PresupuestoAgricolaPermission(models.Model):
	class Meta:
		managed = False  # No se creará una tabla en la base de datos
		default_permissions = ()
		permissions = [
			('modulo_presupuesto_agricola', 'modulo_presupuesto_agricola'),
			('presupuesto_agricola_lotes', 'presupuesto_agricola_lotes'),
			('presupuesto_agricola_fundos', 'presupuesto_agricola_fundos'),
			('presupuesto_agricola_asignacion_ingenieros', 'presupuesto_agricola_asignacion_ingenieros'),
		]
		verbose_name = 'Permisos_Presupuesto_Agricola'
		verbose_name_plural = 'Permisos_Presupuesto_Agricola'