from django.urls import path
from .views import Fito_apl_diario,Fito_apl_diario_script,Fito_apl_diario_detalles

urlpatterns = [
    path('fitosanidad_apl_diario/', Fito_apl_diario.as_view(), name='fitosanidad_apl_diario'),
    path('fitosanidad_apl_diario_data/', Fito_apl_diario_script.as_view(), name='fitosanidad_apl_diario_data'),
    path('fitosanidad_apl_diario_data_detalle/<str:identificador>/', Fito_apl_diario_detalles.as_view(), name='fitosanidad_apl_diario_data_detalle')
]

