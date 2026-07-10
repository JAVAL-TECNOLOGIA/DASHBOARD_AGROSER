from django.db import models

# Create your models here.


class GerenciaPermissionProduccion(models.Model):
    class Meta:
        managed = False  # No se creará una tabla en la base de datos
        default_permissions = ()
        permissions = [
            ('modulo_gerencia_produccion', 'modulo_gerencia_produccion'),
            ('gerencia_produccion_ev_competencias', 'gerencia_produccion_ev_competencias'),
        ]   
        verbose_name = 'Permisos_Gerencia_Produccion'
        verbose_name_plural = 'Permisos_Gerencia_Produccion'


class Fundo(models.Model):
    id_fundo = models.AutoField(db_column='ID_FUNDO', primary_key=True)
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=255)
    id_empresa = models.IntegerField(db_column='ID_EMPRESA')

    class Meta:
        managed = False   # No se creará una tabla en la base de datos
        db_table = 'FUNDO'  
        app_label = 'GERENCIA_PRODUCCION'

