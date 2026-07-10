from django.urls import path

from .views import *

urlpatterns = [
    path('', parametro_costo_base.as_view(), name='presupuesto_agricola_parametro_costo_base'),
    path('api/parametro-costo/', ParametroCostoCRUDView.as_view(), name='presupuesto_agricola_parametro_costo_api'),
    path('api/parametro-costo/delete/<str:id_parametro>/', deleteParametroCosto,
         name='presupuesto_agricola_parametro_costo_api_delete'),
    path('api/parametro-costo/<str:id_parametro>/', ParametroCostoCRUDView.as_view(),
         name='presupuesto_agricola_parametro_costo_api_detail'),
]
