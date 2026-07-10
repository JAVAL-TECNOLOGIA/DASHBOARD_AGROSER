from django.contrib.auth.decorators import login_required

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('aplicaciones_presupuesto_dl/', presupuesto_dl.as_view(), name='aplicaciones_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('aplicaciones_servicios_totals_dl/', Costo_servicio_totals, name='aplicaciones_servicios_totals_dl'),
    path('aplicaciones_servicios_dl/', Costo_Servicios_dlView.as_view(), name='aplicaciones_servicios_dl'),
    path('aplicaciones_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='aplicaciones_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('aplicaciones_capex_totals_dl/', Costos_capex_totals, name='aplicaciones_capex_totals_dl'),

    path('aplicaciones_capex/', CapexView.as_view(), name='aplicaciones_capex'),
    path('aplicaciones_capex/<int:id>/', CapexView.as_view(), name='aplicaciones_capex_delete'),
    path('aplicaciones_capex/<int:id>/', CapexView.as_view(), name='aplicaciones_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('aplicaciones_suministros_totals_dl/', Costos_suministros_totals_dl, name='aplicaciones_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('aplicaciones_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='aplicaciones_combustibles_lubricantes'),
    path('aplicaciones_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='aplicaciones_combustibles_lubricantes_delete'),
    path('aplicaciones_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='aplicaciones_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('aplicaciones_utiles-oficina/', UtilesOficinaView.as_view(), name='aplicaciones_utiles_oficina'),
    path('aplicaciones_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='aplicaciones_utiles_oficina_delete'),
    path('aplicaciones_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='aplicaciones_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('aplicaciones_equipos-computo/', EquiposComputoView.as_view(), name='aplicaciones_equipos_computo'),
    path('aplicaciones_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='aplicaciones_equipos_computo_delete'),
    path('aplicaciones_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='aplicaciones_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('aplicaciones_otros-suministros/', OtrosSuministrosView.as_view(), name='aplicaciones_otros_suministros'),
    path('aplicaciones_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='aplicaciones_otros_suministros_delete'),   
    path('aplicaciones_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='aplicaciones_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('aplicaciones_material-construccion/', MaterialConstruccionView.as_view(), name='aplicaciones_material_construccion'),
    path('aplicaciones_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='aplicaciones_material_construccion_delete'),
    path('aplicaciones_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='aplicaciones_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('aplicaciones_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='aplicaciones_repuestos_accesorios'),
    path('aplicaciones_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='aplicaciones_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('aplicaciones_equipos-uit/', EquiposUITView.as_view(), name='aplicaciones_equipos_uit'),
    path('aplicaciones_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='aplicaciones_equipos_uit_delete'), 
    path('aplicaciones_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='aplicaciones_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('aplicaciones_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='aplicaciones_materiales_agricultura'),
    path('aplicaciones_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='aplicaciones_materiales_agricultura_delete'),
    path('aplicaciones_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='aplicaciones_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('aplicaciones_equipos-proteccion/', EquiposProteccionView.as_view(), name='aplicaciones_equipos_proteccion'),
    path('aplicaciones_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='aplicaciones_equipos_proteccion_delete'),
    path('aplicaciones_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='aplicaciones_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('aplicaciones_salarios_dl/', CostoSalariosView.as_view(), name='aplicaciones_salarios_dl'),
    path('aplicaciones_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='aplicaciones_salarios_dl_delete'),
    path('aplicaciones_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='aplicaciones_salarios_dl_detail'),
    path('aplicaciones_salario_mensual/', ApiMensualSalarios.as_view(), name='aplicaciones_salario_mensual'),
    
    
    path('aplicaciones_sueldos_dl/', CostoSueldosView.as_view(), name='aplicaciones_sueldos_dl'),
    path('aplicaciones_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='aplicaciones_sueldos_dl_delete'),
    path('aplicaciones_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='aplicaciones_sueldos_dl_detail'),
    path('aplicaciones_sueldo_mensual/', ApiMensualSueldos.as_view(), name='aplicaciones_sueldo_mensual'),



    #=================================================================================================================
    # PRESUPUESTO APLICACIONES FITOSANITARIAS 
    #=================================================================================================================


    
    # API para VARIEDAD
    path('api/variedad/', ApiVariedad.as_view(), name='api_variedad'),

    # API para FACECULTIVO
    path('api/facecultivo/', ApiFaceCultivo.as_view(), name='api_facecultivo'),

    # API para Lotes
    

    path('programas/', ProgramaAaplView.as_view(), name='programas'),
    path('programas/<int:id>/', ProgramaAaplView.as_view(), name='programas_detail'),

    path('programas/detalles/', DetalleProgramaAaplView.as_view(), name='programa_detalles'),
    path('programas/detalles/<int:id>/', DetalleProgramaAaplView.as_view(), name='programa_detalles_crud'),
    path('programas/<int:programa_id>/detalles/', DetalleProgramaAaplView.as_view(), name='programa_detalles_by_programa'),
        
    path('subgrupos/', ApiSubgruposView.as_view(), name='subgrupos'),
    path('productos/', ApiProductosView.as_view(), name='api_productos'),
    path('api/objetivos-apl/', ApiObjetivosAplView.as_view(), name='api_objetivos_apl'),
    path('aplproductos/', AplApiProductosView.as_view(), name='aplproductos'),


    #=================================================================================================================
    # PRESUPUESTO APLICACIONES FITOSANITARIAS - CAMPO VERDE
    #=================================================================================================================
    
    path('programas_cv/', ProgramaAaplCVView.as_view(), name='programas_cv'),
    path('programas_cv/<int:id>/', ProgramaAaplCVView.as_view(), name='programas_detail_cv'),
    
    path('programas_cv/detalles/', DetalleProgramaAaplCVView.as_view(), name='programa_detalles_cv'),
    path('programas_cv/detalles/<int:id>/', DetalleProgramaAaplCVView.as_view(), name='programa_detalles_crud_cv'),
    path('programas_cv/<int:programa_id>/detalles/', DetalleProgramaAaplCVView.as_view(), name='programa_detalles_by_programa_cv'),

    #=================================================================================================================
    # PRESUPUESTO APLICACIONES FITOSANITARIAS - INVERSIONES AJS
    #=================================================================================================================
    
    path('programas_ajs/', ProgramaAaplAJSView.as_view(), name='programas_ajs'),
    path('programas_ajs/<int:id>/', ProgramaAaplAJSView.as_view(), name='programas_detail_ajs'),
    
    path('programas_ajs/detalles/', DetalleProgramaAaplAJSView.as_view(), name='programa_detalles_ajs'),
    path('programas_ajs/detalles/<int:id>/', DetalleProgramaAaplAJSView.as_view(), name='programa_detalles_crud_ajs'),
    path('programas_ajs/<int:programa_id>/detalles/', DetalleProgramaAaplAJSView.as_view(), name='programa_detalles_by_programa_ajs'),

    
    #====================================================================================================================
    #EVALUACION DE DESEMPEÑO
    #====================================================================================================================

    path('aplicaciones_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='aplicaciones_evaluacion_desempeño'),



    # API PARA OBTENER DATOS DE EVALUACIONES DE OBJETIVOS
    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='detalles_objetivos_detail'),

    path('resumen_competencias/', ResumenCompetenciasView.as_view(), name='aplicaciones_resumen_competencias'),
    
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
    # API para la fase final de evaluaciones
    #====================================================================================================================
    
    path('api/fase-final/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluaciones'),
    path('api/fase-final/<int:id_evaluacion>/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluacion_detalle'),
    
    # API para los detalles de la fase final
    path('api/detalles-evaluacion-final/', DetallesEvaluacionFinalModalView.as_view(), name='detalles_evaluacion_final_modal'),


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



    path('aplicaciones_presupuesto_cv/', presupuesto_cv.as_view(), name='aplicaciones_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('aplicaciones_servicios_totals_cv/', Costo_servicio_totals_cv, name='aplicaciones_servicios_totals_cv'),
    path('aplicaciones_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='aplicaciones_servicios_cv'),
    path('aplicaciones_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='aplicaciones_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('aplicaciones_capex_totals_cv/', Costos_capex_totals_cv, name='aplicaciones_capex_totals_cv'),

    path('aplicaciones_capex_cv/', CapexView_cv.as_view(), name='aplicaciones_capex_cv'),
    path('aplicaciones_capex_cv/<int:id>/', CapexView_cv.as_view(), name='aplicaciones_capex_cv_delete'),
    path('aplicaciones_capex_cv/<int:id>/', CapexView_cv.as_view(), name='aplicaciones_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('aplicaciones_suministros_totals_cv/', Costos_suministros_totals_cv, name='aplicaciones_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('aplicaciones_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='aplicaciones_combustibles_lubricantes_cv'),
    path('aplicaciones_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='aplicaciones_combustibles_lubricantes_cv_delete'),
    path('aplicaciones_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='aplicaciones_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('aplicaciones_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='aplicaciones_utiles_oficina_cv'),
    path('aplicaciones_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='aplicaciones_utiles_oficina_cv_delete'),
    path('aplicaciones_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='aplicaciones_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('aplicaciones_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='aplicaciones_equipos_computo_cv'),
    path('aplicaciones_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='aplicaciones_equipos_computo_cv  _delete'),
    path('aplicaciones_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='aplicaciones_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('aplicaciones_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='aplicaciones_otros_suministros_cv'),
    path('aplicaciones_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='aplicaciones_otros_suministros_cv_delete'),   
    path('aplicaciones_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='aplicaciones_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('aplicaciones_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='aplicaciones_material_construccion_cv'),
    path('aplicaciones_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='aplicaciones_material_construccion_cv_delete'),
    path('aplicaciones_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='aplicaciones_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('aplicaciones_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='aplicaciones_repuestos_accesorios_cv'),
    path('aplicaciones_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='aplicaciones_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('aplicaciones_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='aplicaciones_equipos_uit_cv'),
    path('aplicaciones_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='aplicaciones_equipos_uit_cv_delete'), 
    path('aplicaciones_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='aplicaciones_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('aplicaciones_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='aplicaciones_materiales_agricultura_cv'),
    path('aplicaciones_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='aplicaciones_materiales_agricultura_cv_delete'),
    path('aplicaciones_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='aplicaciones_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('aplicaciones_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='aplicaciones_equipos_proteccion_cv'),
    path('aplicaciones_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='aplicaciones_equipos_proteccion_cv_delete'),
    path('aplicaciones_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='aplicaciones_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('aplicaciones_salarios_cv/', CostoSalariosView_cv.as_view(), name='aplicaciones_salarios_cv'),
    path('aplicaciones_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='aplicaciones_salarios_cv_delete'),
    path('aplicaciones_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='aplicaciones_salarios_cv_detail'),
    path('aplicaciones_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='aplicaciones_salario_mensual_cv'),
    
    
    path('aplicaciones_sueldos_cv/', CostoSueldosView_cv.as_view(), name='aplicaciones_sueldos_cv'),
    path('aplicaciones_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='aplicaciones_sueldos_cv_delete'),
    path('aplicaciones_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='aplicaciones_sueldos_cv_detail'),
    path('aplicaciones_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='aplicaciones_sueldo_mensual_cv'),

    #====================================================================================================================
    # MODULO PRESUPUESTO FITOSANITARIO CAMPOS VERDE
    #====================================================================================================================

    #RESUMEN
    path('programas_cv/', ProgramaAaplView_CV.as_view(), name='programas_cv'),
    path('programas_cv/<int:id>/', ProgramaAaplView_CV.as_view(), name='programas_cv_detail'),

    # DETALLES
    path('programas_cv/detalles/', DetalleProgramaAaplView_CV.as_view(), name='programa_detalles'),
    path('programas_cv/detalles/<int:id>/', DetalleProgramaAaplView_CV.as_view(), name='programa_detalles_crud'),
    path('programas_cv/<int:programa_id>/detalles/', DetalleProgramaAaplView_CV.as_view(), name='programa_detalles_by_programa'),
      




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



    path('aplicaciones_presupuesto_ajs/', presupuesto_ajs.as_view(), name='aplicaciones_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('aplicaciones_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='aplicaciones_servicios_totals_ajs'),
    path('aplicaciones_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='aplicaciones_servicios_ajs'),
    path('aplicaciones_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='aplicaciones_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('aplicaciones_capex_totals_ajs/', Costos_capex_totals_ajs, name='aplicaciones_capex_totals_ajs'),

    path('aplicaciones_capex_ajs/', CapexView_ajs.as_view(), name='aplicaciones_capex_ajs'),
    path('aplicaciones_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='aplicaciones_capex_ajs_delete'),
    path('aplicaciones_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='aplicaciones_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('aplicaciones_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='aplicaciones_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('aplicaciones_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='aplicaciones_combustibles_lubricantes_ajs'),
    path('aplicaciones_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='aplicaciones_combustibles_lubricantes_ajs_delete'),
    path('aplicaciones_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='aplicaciones_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('aplicaciones_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='aplicaciones_utiles_oficina_ajs'),
    path('aplicaciones_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='aplicaciones_utiles_oficina_ajs_delete'),
    path('aplicaciones_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='aplicaciones_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('aplicaciones_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='aplicaciones_equipos_computo_ajs'),
    path('aplicaciones_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='aplicaciones_equipos_computo_ajs  _delete'),
    path('aplicaciones_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='aplicaciones_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('aplicaciones_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='aplicaciones_otros_suministros_ajs'),
    path('aplicaciones_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='aplicaciones_otros_suministros_ajs_delete'),   
    path('aplicaciones_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='aplicaciones_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('aplicaciones_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='aplicaciones_material_construccion_ajs'),
    path('aplicaciones_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='aplicaciones_material_construccion_ajs_delete'),
    path('aplicaciones_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='aplicaciones_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('aplicaciones_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='aplicaciones_repuestos_accesorios_ajs'),
    path('aplicaciones_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='aplicaciones_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('aplicaciones_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='aplicaciones_equipos_uit_ajs'),
    path('aplicaciones_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='aplicaciones_equipos_uit_ajs_delete'), 
    path('aplicaciones_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='aplicaciones_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('aplicaciones_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='aplicaciones_materiales_agricultura_ajs'),
    path('aplicaciones_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='aplicaciones_materiales_agricultura_ajs_delete'),
    path('aplicaciones_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='aplicaciones_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('aplicaciones_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='aplicaciones_equipos_proteccion_ajs'),
    path('aplicaciones_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='aplicaciones_equipos_proteccion_ajs_delete'),
    path('aplicaciones_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='aplicaciones_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('aplicaciones_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='aplicaciones_salarios_ajs'),
    path('aplicaciones_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='aplicaciones_salarios_ajs_delete'),
    path('aplicaciones_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='aplicaciones_salarios_ajs_detail'),
    path('aplicaciones_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='aplicaciones_salario_mensual_ajs'),
    
    
    path('aplicaciones_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='aplicaciones_sueldos_ajs'),
    path('aplicaciones_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='aplicaciones_sueldos_ajs_delete'),
    path('aplicaciones_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='aplicaciones_sueldos_ajs_detail'),
    path('aplicaciones_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='aplicaciones_sueldo_mensual_ajs'),


    #====================================================================================================================
    # MODULO PRESUPUESTO FITOSANITARIO INVERSIONES AJS
    #====================================================================================================================

    #RESUMEN
    path('programas_ajs/', ProgramaAaplView_AJS.as_view(), name='programas_ajs'),
    path('programas_ajs/<int:id>/', ProgramaAaplView_AJS.as_view(), name='programas_ajs_detail'),
    
    # DETALLES
    path('programas_ajs/detalles/', DetalleProgramaAaplView_AJS.as_view(), name='programa_detalles'),
    path('programas_ajs/detalles/<int:id>/', DetalleProgramaAaplView_AJS.as_view(), name='programa_detalles_crud'),
    path('programas_ajs/<int:programa_id>/detalles/', DetalleProgramaAaplView_AJS.as_view(), name='programa_detalles_by_programa'),
      

        
    #====================================================================================================================
    # API para la fase FINAL de evaluaciones
    #====================================================================================================================
    
    path('api/fase-final/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluaciones'),
    path('api/fase-final/<int:id_evaluacion>/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluacion_detalle'),
    
    #api para los detalles de la fase final
    path('api/detalles-evaluacion-final/', DetallesEvaluacionFinalModalView.as_view(), name='detalles_evaluacion_final_modal'),
    
    
    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

