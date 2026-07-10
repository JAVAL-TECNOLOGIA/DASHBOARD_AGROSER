from django.contrib import admin
from .models import Fundo

@admin.register(Fundo)
class FundoAdmin(admin.ModelAdmin):
	list_display = ('id_fundo', 'descripcion', 'id_empresa')
