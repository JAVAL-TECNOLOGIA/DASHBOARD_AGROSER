from django.urls import path

from .views import *

urlpatterns = [
    path('', PresupuestoLotesView.as_view(), name='presupuesto_agricola_lotes'),

    # API CRUD para lotes
    path('api/lotes/', PresupuestoLoteCRUDView.as_view(), name='presupuesto_agricola_lotes_api'),
    path('api/lotes/<int:id_lote>/', PresupuestoLoteCRUDView.as_view(), name='presupuesto_agricola_lotes_api_detail'),

]
