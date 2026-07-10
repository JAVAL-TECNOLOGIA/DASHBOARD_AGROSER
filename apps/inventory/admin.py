from django.contrib import admin
from .models import *

# Register your models here.
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'fecha_creacion','fecha_actualizacion')

admin.site.register(Sucursal, SucursalAdmin)

class AreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'fecha_creacion','fecha_actualizacion')

admin.site.register(Area, AreaAdmin)

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descripcion', 'fecha_creacion','fecha_actualizacion')

admin.site.register(Categoria, CategoriaAdmin)

class ProcesadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'gama','generacion','frecuencia', 'fecha_creacion','fecha_actualizacion')

admin.site.register(Procesador, ProcesadorAdmin)

class RamAdmin(admin.ModelAdmin):
    list_display = ('id', 'tamaño', 'fecha_creacion','fecha_actualizacion')

admin.site.register(Ram, RamAdmin)


class DiscoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tamaño','tipo', 'fecha_creacion','fecha_actualizacion')

admin.site.register(Disco, DiscoAdmin)

class CPUAdmin(admin.ModelAdmin):
    list_display = ('id', 'procesador','ram','disco')

admin.site.register(CPU, CPUAdmin)

