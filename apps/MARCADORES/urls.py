from django.urls import path
from .views import *

urlpatterns = [
    # Vista principal: Cards de sedes
    path('', marcadores.as_view(), name='marcadores'),
    
    # Vista de marcaciones por sede
    path('sede/<int:id_sede>/', marcaciones_sede.as_view(), name='marcaciones_sede'),
    
    # Escáner de códigos de barras por sede
    path('sede/<int:id_sede>/escaner/', marcador_escaner, name='marcador_escaner'),
    
    # Vista de administración
    path('administracion/', administracion_marcadores.as_view(), name='administracion_marcadores'),
    
    # APIs para procesar asistencias
    path('api/health/', marcadores_health, name='marcadores_health'),
    path('api/procesar-marcacion/', procesar_marcacion, name='procesar_marcacion'),
    path('api/asistencias/', obtener_asistencias, name='obtener_asistencias'),
    path('api/exportar-txt/', exportar_txt_nisira, name='exportar_txt_nisira'),
    
    # APIs para gestión de sedes
    path('api/sedes/', sedes_list_api, name='sedes_list_api'),
    path('api/sedes/crud/', SedesCRUDView.as_view(), name='sedes_crud'),
    path('api/sedes/estadisticas/', estadisticas_sede, name='estadisticas_sede'),
    
    # Exportación a Excel
    path('api/exportar-excel/', exportar_excel, name='exportar_excel'),
    
    # Actualización manual de estados
    path('api/actualizar-estados/', actualizar_estados_manual, name='actualizar_estados_manual'),
    
    # Verificar estados actuales (para debug)
    path('api/verificar-estados/', verificar_estados_debug, name='verificar_estados_debug'),
    
    # APIs para administración
    path('api/eliminar-marcaciones/', eliminar_marcaciones, name='eliminar_marcaciones'),
    path('api/estadisticas-rango/', estadisticas_rango, name='estadisticas_rango'),
]
