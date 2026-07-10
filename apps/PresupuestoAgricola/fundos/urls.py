from django.urls import path

from .views import *

urlpatterns = [
    path('', PresupuestoFundosView.as_view(), name='presupuesto_agricola_fundos'),

    # API CRUD para fundos
    path('api/fundos/', PresupuestoFundoCRUDView.as_view(), name='presupuesto_agricola_fundos_api'),
    path('api/fundos/<str:id_fundo>/', PresupuestoFundoCRUDView.as_view(),
         name='presupuesto_agricola_fundos_api_detail'),

]
