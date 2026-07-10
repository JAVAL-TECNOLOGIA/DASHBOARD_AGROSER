from django.urls import path

from .views import *

urlpatterns = [
    path('', PresupuestoTipoPlantaView.as_view(), name='presupuesto_agricola_tipo_planta'),

    # API CRUD para tipo_planta
    path('api/tipo-planta/', PresupuestoTipoPlantaCRUDView.as_view(), name='presupuesto_agricola_tipo_planta_api'),
    path('api/tipo-planta/<int:id_tipo_planta>/', PresupuestoTipoPlantaCRUDView.as_view(), name='presupuesto_agricola_tipo_planta_api_detail'),

]