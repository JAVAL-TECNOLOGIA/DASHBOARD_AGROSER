from django.urls import path

from .views import *

urlpatterns = [
    path('', PresupuestoTipoTrabajoView.as_view(), name='presupuesto_agricola_tipo_trabajo'),

    # API CRUD para tipo_trabajo
    path('api/tipo-trabajo/', PresupuestoTipoTrabajoCRUDView.as_view(), name='presupuesto_agricola_tipo_trabajo_api'),
    path('api/tipo-trabajo/<int:id_tipo_trabajo>/', PresupuestoTipoTrabajoCRUDView.as_view(), name='presupuesto_agricola_tipo_trabajo_api_detail'),

]