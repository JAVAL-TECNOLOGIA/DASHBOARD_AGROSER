from django.contrib.auth.decorators import login_required

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    #DON LUIS 
     path('salud_presupuesto_dl/', presupuesto_dl.as_view(), name='salud_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('salud_servicios_totals_dl/', Costo_servicio_totals, name='salud_servicios_totals_dl'),
    path('salud_servicios_dl/', Costo_Servicios_dlView.as_view(), name='salud_servicios_dl'),
    path('salud_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='salud_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('salud_capex_totals_dl/', Costos_capex_totals, name='salud_capex_totals_dl'),

    path('salud_capex/', CapexView.as_view(), name='salud_capex'),
    path('salud_capex/<int:id>/', CapexView.as_view(), name='salud_capex_delete'),
    path('salud_capex/<int:id>/', CapexView.as_view(), name='salud_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('salud_suministros_totals_dl/', Costos_suministros_totals_dl, name='salud_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('salud_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='salud_combustibles_lubricantes'),
    path('salud_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='salud_combustibles_lubricantes_delete'),
    path('salud_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='salud_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('salud_utiles-oficina/', UtilesOficinaView.as_view(), name='salud_utiles_oficina'),
    path('salud_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='salud_utiles_oficina_delete'),
    path('salud_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='salud_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('salud_equipos-computo/', EquiposComputoView.as_view(), name='salud_equipos_computo'),
    path('salud_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='salud_equipos_computo_delete'),
    path('salud_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='salud_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('salud_otros-suministros/', OtrosSuministrosView.as_view(), name='salud_otros_suministros'),
    path('salud_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='salud_otros_suministros_delete'),   
    path('salud_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='salud_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('salud_material-construccion/', MaterialConstruccionView.as_view(), name='salud_material_construccion'),
    path('salud_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='salud_material_construccion_delete'),
    path('salud_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='salud_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('salud_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='salud_repuestos_accesorios'),
    path('salud_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='salud_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('salud_equipos-uit/', EquiposUITView.as_view(), name='salud_equipos_uit'),
    path('salud_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='salud_equipos_uit_delete'), 
    path('salud_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='salud_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('salud_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='salud_materiales_agricultura'),
    path('salud_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='salud_materiales_agricultura_delete'),
    path('salud_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='salud_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('salud_equipos-proteccion/', EquiposProteccionView.as_view(), name='salud_equipos_proteccion'),
    path('salud_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='salud_equipos_proteccion_delete'),
    path('salud_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='salud_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('salud_salarios_dl/', CostoSalariosView.as_view(), name='salud_salarios_dl'),
    path('salud_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='salud_salarios_dl_delete'),
    path('salud_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='salud_salarios_dl_detail'),
    path('salud_salario_mensual/', ApiMensualSalarios.as_view(), name='salud_salario_mensual'),
    
    
    path('salud_sueldos_dl/', CostoSueldosView.as_view(), name='salud_sueldos_dl'),
    path('salud_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='salud_sueldos_dl_delete'),
    path('salud_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='salud_sueldos_dl_detail'),
    path('salud_sueldo_mensual/', ApiMensualSueldos.as_view(), name='salud_sueldo_mensual'),

    
    
    #CAMPO VERDE
    
    path('salud_presupuesto_cv/', presupuesto_cv.as_view(), name='salud_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('salud_servicios_totals_cv/', Costo_servicio_totals_cv, name='salud_servicios_totals_cv'),
    path('salud_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='salud_servicios_cv'),
    path('salud_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='salud_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('salud_capex_totals_cv/', Costos_capex_totals_cv, name='salud_capex_totals_cv'),

    path('salud_capex_cv/', CapexView_cv.as_view(), name='salud_capex_cv'),
    path('salud_capex_cv/<int:id>/', CapexView_cv.as_view(), name='salud_capex_cv_delete'),
    path('salud_capex_cv/<int:id>/', CapexView_cv.as_view(), name='salud_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('salud_suministros_totals_cv/', Costos_suministros_totals_cv, name='salud_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('salud_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='salud_combustibles_lubricantes_cv'),
    path('salud_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='salud_combustibles_lubricantes_cv_delete'),
    path('salud_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='salud_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('salud_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='salud_utiles_oficina_cv'),
    path('salud_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='salud_utiles_oficina_cv_delete'),
    path('salud_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='salud_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('salud_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='salud_equipos_computo_cv'),
    path('salud_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='salud_equipos_computo_cv  _delete'),
    path('salud_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='salud_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('salud_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='salud_otros_suministros_cv'),
    path('salud_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='salud_otros_suministros_cv_delete'),   
    path('salud_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='salud_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('salud_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='salud_material_construccion_cv'),
    path('salud_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='salud_material_construccion_cv_delete'),
    path('salud_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='salud_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('salud_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='salud_repuestos_accesorios_cv'),
    path('salud_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='salud_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('salud_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='salud_equipos_uit_cv'),
    path('salud_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='salud_equipos_uit_cv_delete'), 
    path('salud_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='salud_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('salud_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='salud_materiales_agricultura_cv'),
    path('salud_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='salud_materiales_agricultura_cv_delete'),
    path('salud_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='salud_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('salud_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='salud_equipos_proteccion_cv'),
    path('salud_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='salud_equipos_proteccion_cv_delete'),
    path('salud_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='salud_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('salud_salarios_cv/', CostoSalariosView_cv.as_view(), name='salud_salarios_cv'),
    path('salud_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='salud_salarios_cv_delete'),
    path('salud_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='salud_salarios_cv_detail'),
    path('salud_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='salud_salario_mensual_cv'),
    
    
    path('salud_sueldos_cv/', CostoSueldosView_cv.as_view(), name='salud_sueldos_cv'),
    path('salud_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='salud_sueldos_cv_delete'),
    path('salud_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='salud_sueldos_cv_detail'),
    path('salud_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='salud_sueldo_mensual_cv'),

]