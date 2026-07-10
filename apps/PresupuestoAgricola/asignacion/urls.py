from django.urls import path

from apps.PresupuestoAgricola.asignacion.views import IngenierosListView, AsignacionLoteCRUDView, AsignacionListView, \
    asignacion_ingenieros
from apps.PresupuestoAgricola.mapeo.views import FundosPorUsuarioCampaniaAPI

urlpatterns = [
    path('', asignacion_ingenieros.as_view(), name='presupuesto_agricola_asignacion_ingenieros'),

    # API para obtener ingenieros
    path('api/ingenieros/', IngenierosListView.as_view(), name='ingenieros_list'),
    # API CRUD AsignacionLote (SQL Server directo)
    path('api/asignacion_lote/', AsignacionLoteCRUDView.as_view(), name='asignacion_lote_list_create'),
    path('api/asignacion_lote/<int:id_asignacion>/', AsignacionLoteCRUDView.as_view(), name='asignacion_lote_detail'),
    # API CRUD para asignación de ingenieros
    path('api/asignaciones/', AsignacionListView.as_view(), name='asignacion_list'),  # GET lista, POST crear
    path('api/fundos_por_usuario/', FundosPorUsuarioCampaniaAPI.as_view(), name='presupuesto_agricola_fundos_usuario'),

]
