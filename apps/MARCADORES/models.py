
from django.db import models

# Permisos para el módulo Marcadores
class MarcadoresPermission(models.Model):
	class Meta:
		managed = False  # No se creará una tabla en la base de datos
		default_permissions = ()
		permissions = [
			('modulo_marcadores', 'modulo_marcadores'),
			
		]
		verbose_name = 'Permisos_Marcadores'
		verbose_name_plural = 'Permisos_Marcadores'