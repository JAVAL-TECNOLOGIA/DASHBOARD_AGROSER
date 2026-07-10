from django.urls import path
from . import views
from .views import compras_lotes_api

urlpatterns = [
    path('', views.evaluacion_fertilidad, name='presupuesto_agricola_consolidados'),
    path('api/compras/lotes/', compras_lotes_api, name='compras_lotes_api')
]
