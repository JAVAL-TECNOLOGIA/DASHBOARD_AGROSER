from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('evaluaciones_presupuesto_dl/', presupuesto_dl.as_view(), name='evaluaciones_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('evaluaciones_servicios_totals_dl/', Costo_servicio_totals, name='evaluaciones_servicios_totals_dl'),
    path('evaluaciones_servicios_dl/', Costo_Servicios_dlView.as_view(), name='evaluaciones_servicios_dl'),
    path('evaluaciones_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='evaluaciones_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('evaluaciones_capex_totals_dl/', Costos_capex_totals, name='evaluaciones_capex_totals_dl'),

    path('evaluaciones_capex/', CapexView.as_view(), name='evaluaciones_capex'),
    path('evaluaciones_capex/<int:id>/', CapexView.as_view(), name='evaluaciones_capex_delete'),
    path('evaluaciones_capex/<int:id>/', CapexView.as_view(), name='evaluaciones_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('evaluaciones_suministros_totals_dl/', Costos_suministros_totals_dl, name='evaluaciones_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('evaluaciones_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='evaluaciones_combustibles_lubricantes'),
    path('evaluaciones_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='evaluaciones_combustibles_lubricantes_delete'),
    path('evaluaciones_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='evaluaciones_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('evaluaciones_utiles-oficina/', UtilesOficinaView.as_view(), name='evaluaciones_utiles_oficina'),
    path('evaluaciones_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='evaluaciones_utiles_oficina_delete'),
    path('evaluaciones_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='evaluaciones_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('evaluaciones_equipos-computo/', EquiposComputoView.as_view(), name='evaluaciones_equipos_computo'),
    path('evaluaciones_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='evaluaciones_equipos_computo_delete'),
    path('evaluaciones_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='evaluaciones_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('evaluaciones_otros-suministros/', OtrosSuministrosView.as_view(), name='evaluaciones_otros_suministros'),
    path('evaluaciones_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='evaluaciones_otros_suministros_delete'),   
    path('evaluaciones_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='evaluaciones_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('evaluaciones_material-construccion/', MaterialConstruccionView.as_view(), name='evaluaciones_material_construccion'),
    path('evaluaciones_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='evaluaciones_material_construccion_delete'),
    path('evaluaciones_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='evaluaciones_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('evaluaciones_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='evaluaciones_repuestos_accesorios'),
    path('evaluaciones_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='evaluaciones_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('evaluaciones_equipos-uit/', EquiposUITView.as_view(), name='evaluaciones_equipos_uit'),
    path('evaluaciones_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='evaluaciones_equipos_uit_delete'), 
    path('evaluaciones_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='evaluaciones_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('evaluaciones_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='evaluaciones_materiales_agricultura'),
    path('evaluaciones_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='evaluaciones_materiales_agricultura_delete'),
    path('evaluaciones_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='evaluaciones_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('evaluaciones_equipos-proteccion/', EquiposProteccionView.as_view(), name='evaluaciones_equipos_proteccion'),
    path('evaluaciones_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='evaluaciones_equipos_proteccion_delete'),
    path('evaluaciones_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='evaluaciones_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('evaluaciones_salarios_dl/', CostoSalariosView.as_view(), name='evaluaciones_salarios_dl'),
    path('evaluaciones_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='evaluaciones_salarios_dl_delete'),
    path('evaluaciones_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='evaluaciones_salarios_dl_detail'),
    path('evaluaciones_salario_mensual/', ApiMensualSalarios.as_view(), name='evaluaciones_salario_mensual'),
    
    
    path('evaluaciones_sueldos_dl/', CostoSueldosView.as_view(), name='evaluaciones_sueldos_dl'),
    path('evaluaciones_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='evaluaciones_sueldos_dl_delete'),
    path('evaluaciones_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='evaluaciones_sueldos_dl_detail'),
    path('evaluaciones_sueldo_mensual/', ApiMensualSueldos.as_view(), name='evaluaciones_sueldo_mensual'),


    #====================================================================================================================
    #EVALUACION DE DESEMPEÑO
    #====================================================================================================================

    path('evaluaciones_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='evaluaciones_evaluacion_desempeño'),



    # API PARA OBTENER DATOS DE EVALUACIONES DE OBJETIVOS
    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='detalles_objetivos_detail'),

    # API PARA OBTENER EL RESUMEN DE COMPETENCIAS DE EVALUACION (filtrado por id_area=9)
    path('resumen_competencias/', ResumenCompetenciasView.as_view(), name='evaluaciones_resumen_competencias'),
    
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
    #CAMPO VERDE - TECNOLOGIA DE LA INFORMACION
    #====================================================================================================================

    #=================================================================================================================
    #MODULO PRESUPUESTOS
    #AUTOR: JHON GUTIERREZ
    #FECHA: 06/01/2025
    #MODIFICACIONES: 
    # 10/01/2025: Se crea el modulo de presupuestos
    #=================================================================================================================



    path('evaluaciones_presupuesto_cv/', presupuesto_cv.as_view(), name='evaluaciones_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('evaluaciones_servicios_totals_cv/', Costo_servicio_totals_cv, name='evaluaciones_servicios_totals_cv'),
    path('evaluaciones_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='evaluaciones_servicios_cv'),
    path('evaluaciones_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='evaluaciones_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('evaluaciones_capex_totals_cv/', Costos_capex_totals_cv, name='evaluaciones_capex_totals_cv'),

    path('evaluaciones_capex_cv/', CapexView_cv.as_view(), name='evaluaciones_capex_cv'),
    path('evaluaciones_capex_cv/<int:id>/', CapexView_cv.as_view(), name='evaluaciones_capex_cv_delete'),
    path('evaluaciones_capex_cv/<int:id>/', CapexView_cv.as_view(), name='evaluaciones_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('evaluaciones_suministros_totals_cv/', Costos_suministros_totals_cv, name='evaluaciones_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('evaluaciones_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='evaluaciones_combustibles_lubricantes_cv'),
    path('evaluaciones_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='evaluaciones_combustibles_lubricantes_cv_delete'),
    path('evaluaciones_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='evaluaciones_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('evaluaciones_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='evaluaciones_utiles_oficina_cv'),
    path('evaluaciones_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='evaluaciones_utiles_oficina_cv_delete'),
    path('evaluaciones_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='evaluaciones_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('evaluaciones_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='evaluaciones_equipos_computo_cv'),
    path('evaluaciones_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='evaluaciones_equipos_computo_cv  _delete'),
    path('evaluaciones_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='evaluaciones_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('evaluaciones_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='evaluaciones_otros_suministros_cv'),
    path('evaluaciones_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='evaluaciones_otros_suministros_cv_delete'),   
    path('evaluaciones_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='evaluaciones_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('evaluaciones_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='evaluaciones_material_construccion_cv'),
    path('evaluaciones_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='evaluaciones_material_construccion_cv_delete'),
    path('evaluaciones_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='evaluaciones_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('evaluaciones_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='evaluaciones_repuestos_accesorios_cv'),
    path('evaluaciones_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='evaluaciones_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('evaluaciones_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='evaluaciones_equipos_uit_cv'),
    path('evaluaciones_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='evaluaciones_equipos_uit_cv_delete'), 
    path('evaluaciones_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='evaluaciones_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('evaluaciones_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='evaluaciones_materiales_agricultura_cv'),
    path('evaluaciones_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='evaluaciones_materiales_agricultura_cv_delete'),
    path('evaluaciones_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='evaluaciones_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('evaluaciones_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='evaluaciones_equipos_proteccion_cv'),
    path('evaluaciones_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='evaluaciones_equipos_proteccion_cv_delete'),
    path('evaluaciones_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='evaluaciones_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('evaluaciones_salarios_cv/', CostoSalariosView_cv.as_view(), name='evaluaciones_salarios_cv'),
    path('evaluaciones_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='evaluaciones_salarios_cv_delete'),
    path('evaluaciones_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='evaluaciones_salarios_cv_detail'),
    path('evaluaciones_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='evaluaciones_salario_mensual_cv'),
    
    
    path('evaluaciones_sueldos_cv/', CostoSueldosView_cv.as_view(), name='evaluaciones_sueldos_cv'),
    path('evaluaciones_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='evaluaciones_sueldos_cv_delete'),
    path('evaluaciones_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='evaluaciones_sueldos_cv_detail'),
    path('evaluaciones_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='evaluaciones_sueldo_mensual_cv'),





    

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



    path('evaluaciones_presupuesto_ajs/', presupuesto_ajs.as_view(), name='evaluaciones_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('evaluaciones_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='evaluaciones_servicios_totals_ajs'),
    path('evaluaciones_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='evaluaciones_servicios_ajs'),
    path('evaluaciones_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='evaluaciones_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('evaluaciones_capex_totals_ajs/', Costos_capex_totals_ajs, name='evaluaciones_capex_totals_ajs'),

    path('evaluaciones_capex_ajs/', CapexView_ajs.as_view(), name='evaluaciones_capex_ajs'),
    path('evaluaciones_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='evaluaciones_capex_ajs_delete'),
    path('evaluaciones_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='evaluaciones_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('evaluaciones_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='evaluaciones_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('evaluaciones_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='evaluaciones_combustibles_lubricantes_ajs'),
    path('evaluaciones_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='evaluaciones_combustibles_lubricantes_ajs_delete'),
    path('evaluaciones_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='evaluaciones_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('evaluaciones_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='evaluaciones_utiles_oficina_ajs'),
    path('evaluaciones_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='evaluaciones_utiles_oficina_ajs_delete'),
    path('evaluaciones_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='evaluaciones_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('evaluaciones_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='evaluaciones_equipos_computo_ajs'),
    path('evaluaciones_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='evaluaciones_equipos_computo_ajs  _delete'),
    path('evaluaciones_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='evaluaciones_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('evaluaciones_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='evaluaciones_otros_suministros_ajs'),
    path('evaluaciones_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='evaluaciones_otros_suministros_ajs_delete'),   
    path('evaluaciones_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='evaluaciones_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('evaluaciones_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='evaluaciones_material_construccion_ajs'),
    path('evaluaciones_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='evaluaciones_material_construccion_ajs_delete'),
    path('evaluaciones_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='evaluaciones_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('evaluaciones_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='evaluaciones_repuestos_accesorios_ajs'),
    path('evaluaciones_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='evaluaciones_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('evaluaciones_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='evaluaciones_equipos_uit_ajs'),
    path('evaluaciones_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='evaluaciones_equipos_uit_ajs_delete'), 
    path('evaluaciones_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='evaluaciones_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('evaluaciones_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='evaluaciones_materiales_agricultura_ajs'),
    path('evaluaciones_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='evaluaciones_materiales_agricultura_ajs_delete'),
    path('evaluaciones_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='evaluaciones_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('evaluaciones_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='evaluaciones_equipos_proteccion_ajs'),
    path('evaluaciones_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='evaluaciones_equipos_proteccion_ajs_delete'),
    path('evaluaciones_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='evaluaciones_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('evaluaciones_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='evaluaciones_salarios_ajs'),
    path('evaluaciones_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='evaluaciones_salarios_ajs_delete'),
    path('evaluaciones_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='evaluaciones_salarios_ajs_detail'),
    path('evaluaciones_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='evaluaciones_salario_mensual_ajs'),
    
    
    path('evaluaciones_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='evaluaciones_sueldos_ajs'),
    path('evaluaciones_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='evaluaciones_sueldos_ajs_delete'),
    path('evaluaciones_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='evaluaciones_sueldos_ajs_detail'),
    path('evaluaciones_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='evaluaciones_sueldo_mensual_ajs'),






] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

