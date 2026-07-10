from django.urls import path
from .views import *



urlpatterns = [

    # PRESUPUESTO DE DON LUIS - COSTOS
    path('presupuesto_dl/', presupuesto_dl.as_view(), name='presupuesto_dl'),


    
    #================================================
    # SERVICIOS
    #================================================
    path('costo_servicios_totals_dl/', Costo_servicio_totals, name='costo_servicios_totals_dl'),
    path('costo_servicios_dl/', Costo_Servicios_dlView.as_view(), name='costo_servicios_dl'),
    path('costo_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='costo_servicios_dl_detail'),
    
    #================================================
    # SUMINISTROS
    #================================================
    path('costo_suministros_totals_dl/', Costos_suministros_totals_dl, name='costo_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('costos_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='costos_combustibles_lubricantes'),
    path('costos_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='costos_combustibles_lubricantes_delete'),
    path('costos_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='costos_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('costos_utiles-oficina/', UtilesOficinaView.as_view(), name='costos_utiles_oficina'),
    path('costos_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='costos_utiles_oficina_delete'),
    path('costos_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='costos_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('costos_equipos-computo/', EquiposComputoView.as_view(), name='costos_equipos_computo'),
    path('costos_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='costos_equipos_computo_delete'),
    path('costos_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='costos_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('costos_otros-suministros/', OtrosSuministrosView.as_view(), name='costos_otros_suministros'),
    path('costos_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='costos_otros_suministros_delete'),   
    path('costos_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='costos_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('costos_material-construccion/', MaterialConstruccionView.as_view(), name='costos_material_construccion'),
    path('costos_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='costos_material_construccion_delete'),
    path('costos_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='costos_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('costos_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='costos_repuestos_accesorios'),
    path('costos_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='costos_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('costos_equipos-uit/', EquiposUITView.as_view(), name='costos_equipos_uit'),
    path('costos_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='costos_equipos_uit_delete'), 
    path('costos_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='costos_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('costos_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='costos_materiales_agricultura'),
    path('costos_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='costos_materiales_agricultura_delete'),
    path('costos_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='costos_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('costos_equipos-proteccion/', EquiposProteccionView.as_view(), name='costos_equipos_proteccion'),
    path('costos_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='costos_equipos_proteccion_delete'),
    path('costos_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='costos_equipos_proteccion_detail'),

    #================================================
    # CAPEX
    #================================================

    path('costos_capex_totals_dl/', Costos_capex_totals, name='costos_capex_totals_dl'),

    path('capex/', CapexView.as_view(), name='capex'),
    path('capex/<int:id>/', CapexView.as_view(), name='capex_delete'),
    path('capex/<int:id>/', CapexView.as_view(), name='capex_detail'),


    #================================================
    # REMUNERACION
    #================================================
    path('costo_salarios_dl/', CostoSalariosView.as_view(), name='costo_salarios_dl'),
    path('costo_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='costo_salarios_dl_delete'),
    path('costo_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='costo_salarios_dl_detail'),
    path('costo_salario_mensual/', ApiMensualSalarios.as_view(), name='costo_salario_mensual'),
    
    
    path('costo_sueldos_dl/', CostoSueldosView.as_view(), name='costo_sueldos_dl'),
    path('costo_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='costo_sueldos_dl_delete'),
    path('costo_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='costo_sueldos_dl_detail'),
    path('costo_sueldo_mensual/', ApiMensualSueldos.as_view(), name='costo_sueldo_mensual'),




    #====================================================================================================================
    #EVALUACION DE DESEMPEÑO
    #====================================================================================================================

    path('costos_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='costos_evaluacion_desempeño'),



    # API PARA OBTENER DATOS DE EVALUACIONES DE OBJETIVOS
    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='detalles_objetivos_detail'),

    
    path('detalles_competencias/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias'),
    path('detalles_competencias/<int:id>/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias_detail'),

    #====================================================================================================================
    # API para la fase intermedia de evaluaciones
    #====================================================================================================================
    
    path('api/fase-intermedia/', FaseIntermediaEvaluacionesView.as_view(), name='fase_intermedia_evaluaciones'),
    path('api/fase-intermedia/<int:id_evaluacion>/', FaseIntermediaEvaluacionesView.as_view(), name='fase_intermedia_evaluacion_detalle'),
    
    #api para los detalles de la fase intermedia
    
    
    # En tu archivo urls.py
    path('api/detalles-evaluacion/', DetallesEvaluacionModalView.as_view(), name='detalles_evaluacion_modal'),

    #====================================================================================================================
    #REPORTES
    #====================================================================================================================


    path('costos_rpt_horas_personal/', ReporteResumenHorasViewTemplate.as_view(), name='costos_rpt_horas_personal'),
    path('costos_rpt_horas_personal_api/', ReporteResumenHorasViewApi.as_view(), name='costos_rpt_horas_personal_api'),

    #====================================================================================================================
    #CAMPO VERDE - TECNOLOGIA DE LA INFORMACION
    #====================================================================================================================

    #=================================================================================================================
    #MODULO PRESUPUESTOS
    #AUTOR: JHON GUTIERREZ
    #FECHA: 06/01/2025
    #MODIFICACIONES: 
    # 10/01/2025: Se crea el modulo de presupuestos
    #=================================================================================================================


    path('costos_presupuesto_cv/', presupuesto_cv.as_view(), name='costos_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('costos_servicios_totals_cv/', Costo_servicio_totals_cv, name='costos_servicios_totals_cv'),
    path('costos_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='costos_servicios_cv'),
    path('costos_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='costos_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('costos_capex_totals_cv/', Costos_capex_totals_cv, name='costos_capex_totals_cv'),

    path('costos_capex_cv/', CapexView_cv.as_view(), name='costos_capex_cv'),
    path('costos_capex_cv/<int:id>/', CapexView_cv.as_view(), name='costos_capex_cv_delete'),
    path('costos_capex_cv/<int:id>/', CapexView_cv.as_view(), name='costos_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('costos_suministros_totals_cv/', Costos_suministros_totals_cv, name='costos_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('costos_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='costos_combustibles_lubricantes_cv'),
    path('costos_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='costos_combustibles_lubricantes_cv_delete'),
    path('costos_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='costos_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('costos_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='costos_utiles_oficina_cv'),
    path('costos_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='costos_utiles_oficina_cv_delete'),
    path('costos_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='costos_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('costos_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='costos_equipos_computo_cv'),
    path('costos_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='costos_equipos_computo_cv_delete'),
    path('costos_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='costos_equipos_computo_cv_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('costos_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='costos_otros_suministros_cv'),
    path('costos_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='costos_otros_suministros_cv_delete'),   
    path('costos_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='costos_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('costos_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='costos_material_construccion_cv'),
    path('costos_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='costos_material_construccion_cv_delete'),
    path('costos_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='costos_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('costos_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='costos_repuestos_accesorios_cv'),
    path('costos_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='costos_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('costos_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='costos_equipos_uit_cv'),
    path('costos_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='costos_equipos_uit_cv_delete'), 
    path('costos_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='costos_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('costos_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='costos_materiales_agricultura_cv'),
    path('costos_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='costos_materiales_agricultura_cv_delete'),
    path('costos_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='costos_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('costos_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='costos_equipos_proteccion_cv'),
    path('costos_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='costos_equipos_proteccion_cv_delete'),
    path('costos_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='costos_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('costos_salarios_cv/', CostoSalariosView_cv.as_view(), name='costos_salarios_cv'),
    path('costos_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='costos_salarios_cv_delete'),
    path('costos_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='costos_salarios_cv_detail'),
    path('costos_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='costos_salario_mensual_cv'),
    
    
    path('costos_sueldos_cv/', CostoSueldosView_cv.as_view(), name='costos_sueldos_cv'),
    path('costos_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='costos_sueldos_cv_delete'),
    path('costos_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='costos_sueldos_cv_detail'),
    path('costos_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='costos_sueldo_mensual_cv'),





    
#====================================================================================================================
    # INVERSIONES AJS - TECNOLOGIA DE LA INFORMACION
    #====================================================================================================================

    #=================================================================================================================
    #MODULO PRESUPUESTOS
    #AUTOR: JHON GUTIERREZ
    #FECHA: 06/01/2025
    #MODIFICACIONES: 
    # 10/01/2025: Se crea el modulo de presupuestos
    #=================================================================================================================



    path('costos_presupuesto_ajs/', presupuesto_ajs.as_view(), name='costos_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('costos_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='costos_servicios_totals_ajs'),
    path('costos_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='costos_servicios_ajs'),
    path('costos_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='costos_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('costos_capex_totals_ajs/', Costos_capex_totals_ajs, name='costos_capex_totals_ajs'),

    path('costos_capex_ajs/', CapexView_ajs.as_view(), name='costos_capex_ajs'),
    path('costos_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='costos_capex_ajs_delete'),
    path('costos_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='costos_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('costos_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='costos_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('costos_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='costos_combustibles_lubricantes_ajs'),
    path('costos_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='costos_combustibles_lubricantes_ajs_delete'),
    path('costos_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='costos_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('costos_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='costos_utiles_oficina_ajs'),
    path('costos_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='costos_utiles_oficina_ajs_delete'),
    path('costos_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='costos_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('costos_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='costos_equipos_computo_ajs'),
    path('costos_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='costos_equipos_computo_ajs  _delete'),
    path('costos_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='costos_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('costos_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='costos_otros_suministros_ajs'),
    path('costos_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='costos_otros_suministros_ajs_delete'),   
    path('costos_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='costos_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('costos_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='costos_material_construccion_ajs'),
    path('costos_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='costos_material_construccion_ajs_delete'),
    path('costos_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='costos_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('costos_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='costos_repuestos_accesorios_ajs'),
    path('costos_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='costos_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('costos_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='costos_equipos_uit_ajs'),
    path('costos_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='costos_equipos_uit_ajs_delete'), 
    path('costos_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='costos_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('costos_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='costos_materiales_agricultura_ajs'),
    path('costos_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='costos_materiales_agricultura_ajs_delete'),
    path('costos_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='costos_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('costos_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='costos_equipos_proteccion_ajs'),
    path('costos_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='costos_equipos_proteccion_ajs_delete'),
    path('costos_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='costos_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('costos_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='costos_salarios_ajs'),
    path('costos_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='costos_salarios_ajs_delete'),
    path('costos_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='costos_salarios_ajs_detail'),
    path('costos_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='costos_salario_mensual_ajs'),
    
    
    path('costos_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='costos_sueldos_ajs'),
    path('costos_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='costos_sueldos_ajs_delete'),
    path('costos_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='costos_sueldos_ajs_detail'),
    path('costos_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='costos_sueldo_mensual_ajs'),





    #path('distribucion_costos_detallado/', Distribucion_costo.as_view(), name='distribucion_costos_detallado'),
	#path('distribucion_costos_detallado_script/', Distribucion_costo_script.as_view(), name='distribucion_costos_detallado_script'),
    
	#DISTRIBUCION COSTOS  CAMPOVERDE
    #path('distribucion_costos_detallado_CV/', Distribucion_costo_cv.as_view(), name='distribucion_costos_detallado_CV'),
    #path('distribucion_costos_detallado_CV_script/', Distribucion_costo_cv_script.as_view(), name='distribucion_costos_detallado_CV_script'),
    
	#DISTRIBUCION COSTOS  INVERSIONES AJS
    #path('distribucion_costos_detallado_AJS/', Distribucion_costo_ajs.as_view(), name='distribucion_costos_detallado_AJS'),
	#path('distribucion_costos_detallado_AJS_script/', Distribucion_costo_ajs_script.as_view(), name='distribucion_costos_detallado_AJS_script'),





]




