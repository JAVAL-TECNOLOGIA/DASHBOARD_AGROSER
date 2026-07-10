from django.contrib.auth.decorators import login_required

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    #DON LUIS 
     path('sst_presupuesto_dl/', presupuesto_dl.as_view(), name='sst_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('sst_servicios_totals_dl/', Costo_servicio_totals, name='sst_servicios_totals_dl'),
    path('sst_servicios_dl/', Costo_Servicios_dlView.as_view(), name='sst_servicios_dl'),
    path('sst_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='sst_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('sst_capex_totals_dl/', Costos_capex_totals, name='sst_capex_totals_dl'),

    path('sst_capex/', CapexView.as_view(), name='sst_capex'),
    path('sst_capex/<int:id>/', CapexView.as_view(), name='sst_capex_delete'),
    path('sst_capex/<int:id>/', CapexView.as_view(), name='sst_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('sst_suministros_totals_dl/', Costos_suministros_totals_dl, name='sst_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('sst_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='sst_combustibles_lubricantes'),
    path('sst_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='sst_combustibles_lubricantes_delete'),
    path('sst_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='sst_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('sst_utiles-oficina/', UtilesOficinaView.as_view(), name='sst_utiles_oficina'),
    path('sst_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='sst_utiles_oficina_delete'),
    path('sst_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='sst_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('sst_equipos-computo/', EquiposComputoView.as_view(), name='sst_equipos_computo'),
    path('sst_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='sst_equipos_computo_delete'),
    path('sst_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='sst_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('sst_otros-suministros/', OtrosSuministrosView.as_view(), name='sst_otros_suministros'),
    path('sst_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='sst_otros_suministros_delete'),   
    path('sst_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='sst_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('sst_material-construccion/', MaterialConstruccionView.as_view(), name='sst_material_construccion'),
    path('sst_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='sst_material_construccion_delete'),
    path('sst_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='sst_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('sst_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='sst_repuestos_accesorios'),
    path('sst_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='sst_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('sst_equipos-uit/', EquiposUITView.as_view(), name='sst_equipos_uit'),
    path('sst_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='sst_equipos_uit_delete'), 
    path('sst_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='sst_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('sst_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='sst_materiales_agricultura'),
    path('sst_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='sst_materiales_agricultura_delete'),
    path('sst_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='sst_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('sst_equipos-proteccion/', EquiposProteccionView.as_view(), name='sst_equipos_proteccion'),
    path('sst_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='sst_equipos_proteccion_delete'),
    path('sst_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='sst_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('sst_salarios_dl/', CostoSalariosView.as_view(), name='sst_salarios_dl'),
    path('sst_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='sst_salarios_dl_delete'),
    path('sst_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='sst_salarios_dl_detail'),
    path('sst_salario_mensual/', ApiMensualSalarios.as_view(), name='sst_salario_mensual'),
    
    
    path('sst_sueldos_dl/', CostoSueldosView.as_view(), name='sst_sueldos_dl'),
    path('sst_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='sst_sueldos_dl_delete'),
    path('sst_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='sst_sueldos_dl_detail'),
    path('sst_sueldo_mensual/', ApiMensualSueldos.as_view(), name='sst_sueldo_mensual'),

    
    
    #CAMPO VERDE
    
    path('sst_presupuesto_cv/', presupuesto_cv.as_view(), name='sst_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('sst_servicios_totals_cv/', Costo_servicio_totals_cv, name='sst_servicios_totals_cv'),
    path('sst_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='sst_servicios_cv'),
    path('sst_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='sst_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('sst_capex_totals_cv/', Costos_capex_totals_cv, name='sst_capex_totals_cv'),

    path('sst_capex_cv/', CapexView_cv.as_view(), name='sst_capex_cv'),
    path('sst_capex_cv/<int:id>/', CapexView_cv.as_view(), name='sst_capex_cv_delete'),
    path('sst_capex_cv/<int:id>/', CapexView_cv.as_view(), name='sst_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('sst_suministros_totals_cv/', Costos_suministros_totals_cv, name='sst_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('sst_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='sst_combustibles_lubricantes_cv'),
    path('sst_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='sst_combustibles_lubricantes_cv_delete'),
    path('sst_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='sst_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('sst_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='sst_utiles_oficina_cv'),
    path('sst_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='sst_utiles_oficina_cv_delete'),
    path('sst_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='sst_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('sst_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='sst_equipos_computo_cv'),
    path('sst_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='sst_equipos_computo_cv  _delete'),
    path('sst_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='sst_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('sst_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='sst_otros_suministros_cv'),
    path('sst_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='sst_otros_suministros_cv_delete'),   
    path('sst_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='sst_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('sst_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='sst_material_construccion_cv'),
    path('sst_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='sst_material_construccion_cv_delete'),
    path('sst_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='sst_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('sst_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='sst_repuestos_accesorios_cv'),
    path('sst_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='sst_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('sst_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='sst_equipos_uit_cv'),
    path('sst_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='sst_equipos_uit_cv_delete'), 
    path('sst_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='sst_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('sst_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='sst_materiales_agricultura_cv'),
    path('sst_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='sst_materiales_agricultura_cv_delete'),
    path('sst_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='sst_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('sst_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='sst_equipos_proteccion_cv'),
    path('sst_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='sst_equipos_proteccion_cv_delete'),
    path('sst_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='sst_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('sst_salarios_cv/', CostoSalariosView_cv.as_view(), name='sst_salarios_cv'),
    path('sst_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='sst_salarios_cv_delete'),
    path('sst_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='sst_salarios_cv_detail'),
    path('sst_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='sst_salario_mensual_cv'),
    
    
    path('sst_sueldos_cv/', CostoSueldosView_cv.as_view(), name='sst_sueldos_cv'),
    path('sst_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='sst_sueldos_cv_delete'),
    path('sst_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='sst_sueldos_cv_detail'),
    path('sst_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='sst_sueldo_mensual_cv'),

    
    # INVERSIONES AJS 
     path('sst_presupuesto_ajs/', presupuesto_ajs.as_view(), name='sst_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('sst_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='sst_servicios_totals_ajs'),
    path('sst_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='sst_servicios_ajs'),
    path('sst_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='sst_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('sst_capex_totals_ajs/', Costos_capex_totals_ajs, name='sst_capex_totals_ajs'),

    path('sst_capex_ajs/', CapexView_ajs.as_view(), name='sst_capex_ajs'),
    path('sst_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='sst_capex_ajs_delete'),
    path('sst_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='sst_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('sst_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='sst_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE INVERSIONES AJS
    path('sst_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='sst_combustibles_lubricantes_ajs'),
    path('sst_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='sst_combustibles_lubricantes_ajs_delete'),
    path('sst_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='sst_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE INVERSIONES AJS

    path('sst_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='sst_utiles_oficina_ajs'),
    path('sst_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='sst_utiles_oficina_ajs_delete'),
    path('sst_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='sst_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE INVERSIONES AJS
    path('sst_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='sst_equipos_computo_ajs'),
    path('sst_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='sst_equipos_computo_ajs  _delete'),
    path('sst_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='sst_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE INVERSIONES AJS
    path('sst_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='sst_otros_suministros_ajs'),
    path('sst_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='sst_otros_suministros_ajs_delete'),   
    path('sst_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='sst_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE INVERSIONES AJS
    path('sst_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='sst_material_construccion_ajs'),
    path('sst_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='sst_material_construccion_ajs_delete'),
    path('sst_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='sst_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE INVERSIONES AJS
    path('sst_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='sst_repuestos_accesorios_ajs'),
    path('sst_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='sst_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE INVERSIONES AJS
    path('sst_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='sst_equipos_uit_ajs'),
    path('sst_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='sst_equipos_uit_ajs_delete'), 
    path('sst_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='sst_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE INVERSIONES AJS
    path('sst_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='sst_materiales_agricultura_ajs'),
    path('sst_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='sst_materiales_agricultura_ajs_delete'),
    path('sst_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='sst_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE INVERSIONES AJS
    path('sst_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='sst_equipos_proteccion_ajs'),
    path('sst_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='sst_equipos_proteccion_ajs_delete'),
    path('sst_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='sst_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('sst_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='sst_salarios_ajs'),
    path('sst_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='sst_salarios_ajs_delete'),
    path('sst_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='sst_salarios_ajs_detail'),
    path('sst_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='sst_salario_mensual_ajs'),
    
    
    path('sst_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='sst_sueldos_ajs'),
    path('sst_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='sst_sueldos_ajs_delete'),
    path('sst_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='sst_sueldos_ajs_detail'),
    path('sst_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='sst_sueldo_mensual_ajs'),

]