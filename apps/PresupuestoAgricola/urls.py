from django.urls import path, include

from .views import *

urlpatterns = [
    path('lotes/', include('apps.PresupuestoAgricola.lotes.urls')),
    path('fundos/', include('apps.PresupuestoAgricola.fundos.urls')),
    path('tipo-planta/', include('apps.PresupuestoAgricola.tipo_planta.urls')),
    path('tipo-trabajo/', include('apps.PresupuestoAgricola.tipo_trabajo.urls')),
    path('unidad-medida/', include('apps.PresupuestoAgricola.unidad_medida.urls')),
    path('asignacion/', include('apps.PresupuestoAgricola.asignacion.urls')),
    path('mapeo/', include('apps.PresupuestoAgricola.mapeo.urls')),
    path('produccion_uva/', include('apps.PresupuestoAgricola.produccion.urls')),
    path('tipo_calculo/', include('apps.PresupuestoAgricola.tipo_calculo.urls')),
    path('config_tipo_trabajo/', include('apps.PresupuestoAgricola.config_tipo_trabajo.urls')),
    path('parametro_costo_base/', include('apps.PresupuestoAgricola.parametro_costo_base.urls')),
    path('tipo_costo_base/', include('apps.PresupuestoAgricola.tipo_costo_base.urls')),
    path('presupuesto/', include('apps.PresupuestoAgricola.presupuesto.urls')),
    path('consolidado/', include('apps.PresupuestoAgricola.consolidado.urls')),
    path('plantillas/', include('apps.PresupuestoAgricola.TestPlantillas.urls')),
    path('plantillas_offline/', include('apps.PresupuestoAgricola.TestPlantillasOffline.urls')),

]
