from django.urls import path

from .views import *

urlpatterns = [
     path('', tipo_calculo.as_view(), name='presupuesto_agricola_tipo_calculo'),
     path('api/tipo-calculo/', TipoCalculoCRUDView.as_view(), name='presupuesto_agricola_tipo_calculo_api'),
     path('api/tipo-calculo/delete/<str:id_tipo_calculo>/', deleteTipoCalculo,
          name='presupuesto_agricola_tipo_calculo_api_delete'),
     path('api/tipo-calculo/<str:id_tipo_calculo>/', TipoCalculoCRUDView.as_view(),
           name='presupuesto_agricola_tipo_calculo_api_detail'),
]
