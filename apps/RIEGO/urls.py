from django.contrib.auth.decorators import login_required

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('riego_presupuesto_dl/', presupuesto_dl.as_view(), name='riego_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('riego_servicios_totals_dl/', Costo_servicio_totals, name='riego_servicios_totals_dl'),
    path('riego_servicios_dl/', Costo_Servicios_dlView.as_view(), name='riego_servicios_dl'),
    path('riego_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='riego_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('riego_capex_totals_dl/', Costos_capex_totals, name='riego_capex_totals_dl'),

    path('riego_capex/', CapexView.as_view(), name='riego_capex'),
    path('riego_capex/<int:id>/', CapexView.as_view(), name='riego_capex_delete'),
    path('riego_capex/<int:id>/', CapexView.as_view(), name='riego_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('riego_suministros_totals_dl/', Costos_suministros_totals_dl, name='riego_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('riego_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='riego_combustibles_lubricantes'),
    path('riego_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='riego_combustibles_lubricantes_delete'),
    path('riego_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='riego_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('riego_utiles-oficina/', UtilesOficinaView.as_view(), name='riego_utiles_oficina'),
    path('riego_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='riego_utiles_oficina_delete'),
    path('riego_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='riego_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('riego_equipos-computo/', EquiposComputoView.as_view(), name='riego_equipos_computo'),
    path('riego_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='riego_equipos_computo_delete'),
    path('riego_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='riego_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('riego_otros-suministros/', OtrosSuministrosView.as_view(), name='riego_otros_suministros'),
    path('riego_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='riego_otros_suministros_delete'),   
    path('riego_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='riego_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('riego_material-construccion/', MaterialConstruccionView.as_view(), name='riego_material_construccion'),
    path('riego_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='riego_material_construccion_delete'),
    path('riego_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='riego_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('riego_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='riego_repuestos_accesorios'),
    path('riego_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='riego_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('riego_equipos-uit/', EquiposUITView.as_view(), name='riego_equipos_uit'),
    path('riego_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='riego_equipos_uit_delete'), 
    path('riego_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='riego_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('riego_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='riego_materiales_agricultura'),
    path('riego_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='riego_materiales_agricultura_delete'),
    path('riego_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='riego_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('riego_equipos-proteccion/', EquiposProteccionView.as_view(), name='riego_equipos_proteccion'),
    path('riego_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='riego_equipos_proteccion_delete'),
    path('riego_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='riego_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('riego_salarios_dl/', CostoSalariosView.as_view(), name='riego_salarios_dl'),
    path('riego_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='riego_salarios_dl_delete'),
    path('riego_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='riego_salarios_dl_detail'),
    path('riego_salario_mensual/', ApiMensualSalarios.as_view(), name='riego_salario_mensual'),
    
    
    path('riego_sueldos_dl/', CostoSueldosView.as_view(), name='riego_sueldos_dl'),
    path('riego_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='riego_sueldos_dl_delete'),
    path('riego_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='riego_sueldos_dl_detail'),
    path('riego_sueldo_mensual/', ApiMensualSueldos.as_view(), name='riego_sueldo_mensual'),

    #====================================================================================================================
    #PRESUPUESTO DE FERTILIZACION
    #====================================================================================================================

    #RESUMEN DE FERTILIZACION
    # path('api/riego_presupuesto_fertilizacion_dl/', ResumenFertilizacionView.as_view(), name='api_riego_presupuesto_fertilizacion_dl'), 
    # path('api/riego_presupuesto_fertilizacion_dl/<int:id>/', ResumenFertilizacionView.as_view(), name='api_riego_presupuesto_fertilizacion_dl_detail'),

    # #DETALLE DE FERTILIZACION
    # path('api/riego_dprefertilizacion/', DetallePreFertilizacionView.as_view(), name='api_riego_dprefertilizacion'),
    # path('api/riego_dprefertilizacion/<int:id>/', DetallePreFertilizacionView.as_view(), name='api_riego_dprefertilizacion_detail'),
    
    
    #====================================================================================================================
    #MATERIA ORGANICA - DON LUIS
    #====================================================================================================================

    #RESUMEN DE MATERIA ORGANICA
    path('api/materia_organica_dl/', OrgResumenMateriaOrganicaView.as_view(), name='api_materia_organica_dl'), 
    path('api/materia_organica_dl/<int:id>/', OrgResumenMateriaOrganicaView.as_view(), name='api_materia_organica_dl_detail'),

    #DETALLE DE MATERIA ORGANICA
    path('api/organica_materia/', OrgDetalleMateriaOrganicaView.as_view(), name='api_organica_materia'),
    path('api/organica_materia/<int:id>/', OrgDetalleMateriaOrganicaView.as_view(), name='api_organica_materia_detail'),
    
    #====================================================================================================================
    #MATERIA ORGANICA - CAMPO VERDE
    #====================================================================================================================

    #RESUMEN DE MATERIA ORGANICA
    path('api/materia_organica_cv/', OrgResumenMateriaOrganicaCVView.as_view(), name='api_materia_organica_cv'), 
    path('api/materia_organica_cv/<int:id>/', OrgResumenMateriaOrganicaCVView.as_view(), name='api_materia_organica_cv_detail'),

    #DETALLE DE MATERIA ORGANICA
    path('api/organica_materia_cv/', OrgDetalleMateriaOrganicaCVView.as_view(), name='api_organica_materia_cv'),
    path('api/organica_materia_cv/<int:id>/', OrgDetalleMateriaOrganicaCVView.as_view(), name='api_organica_materia_cv_detail'),
    
    #====================================================================================================================
    #MATERIA ORGANICA - INVERSIONES AJS 
    #====================================================================================================================

    #RESUMEN DE MATERIA ORGANICA
    path('api/materia_organica_ajs/', OrgResumenMateriaOrganicaAJSView.as_view(), name='api_materia_organica_ajs'), 
    path('api/materia_organica_ajs/<int:id>/', OrgResumenMateriaOrganicaAJSView.as_view(), name='api_materia_organica_ajs_detail'),

    #DETALLE DE MATERIA ORGANICA
    path('api/organica_materia_ajs/', OrgDetalleMateriaOrganicaAJSView.as_view(), name='api_organica_materia_ajs'),
    path('api/organica_materia_ajs/<int:id>/', OrgDetalleMateriaOrganicaAJSView.as_view(), name='api_organica_materia_ajs_detail'),
    
    
    # # API PARA OBTENER LOTES
    # path('api/lotes_variedad/', LotesVariedadView.as_view(), name='api_lotes_variedad'),

    #====================================================================================================================
    #EVALUACION DE DESEMPEÑO
    #====================================================================================================================

    path('riego_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='riego_evaluacion_desempeño'),



    # API PARA OBTENER DATOS DE EVALUACIONES DE OBJETIVOS
    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='detalles_objetivos_detail'),

    path('resumen_evaluacion_desempeño/', ResumenRRHHObjetivosView.as_view(), name='resumen_evaluacion_desempeño'),
    
    path('detalles_competencias/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias'),
    path('detalles_competencias/<int:id>/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias_detail'),

    path('resumen_competencias/', ResumenCompetenciasView.as_view(), name='resumen_competencias'),
    
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



    path('riego_presupuesto_cv/', presupuesto_cv.as_view(), name='riego_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('riego_servicios_totals_cv/', Costo_servicio_totals_cv, name='riego_servicios_totals_cv'),
    path('riego_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='riego_servicios_cv'),
    path('riego_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='riego_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('riego_capex_totals_cv/', Costos_capex_totals_cv, name='riego_capex_totals_cv'),

    path('riego_capex_cv/', CapexView_cv.as_view(), name='riego_capex_cv'),
    path('riego_capex_cv/<int:id>/', CapexView_cv.as_view(), name='riego_capex_cv_delete'),
    path('riego_capex_cv/<int:id>/', CapexView_cv.as_view(), name='riego_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('riego_suministros_totals_cv/', Costos_suministros_totals_cv, name='riego_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('riego_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='riego_combustibles_lubricantes_cv'),
    path('riego_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='riego_combustibles_lubricantes_cv_delete'),
    path('riego_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='riego_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('riego_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='riego_utiles_oficina_cv'),
    path('riego_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='riego_utiles_oficina_cv_delete'),
    path('riego_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='riego_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('riego_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='riego_equipos_computo_cv'),
    path('riego_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='riego_equipos_computo_cv  _delete'),
    path('riego_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='riego_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('riego_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='riego_otros_suministros_cv'),
    path('riego_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='riego_otros_suministros_cv_delete'),   
    path('riego_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='riego_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('riego_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='riego_material_construccion_cv'),
    path('riego_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='riego_material_construccion_cv_delete'),
    path('riego_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='riego_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('riego_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='riego_repuestos_accesorios_cv'),
    path('riego_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='riego_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('riego_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='riego_equipos_uit_cv'),
    path('riego_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='riego_equipos_uit_cv_delete'), 
    path('riego_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='riego_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('riego_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='riego_materiales_agricultura_cv'),
    path('riego_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='riego_materiales_agricultura_cv_delete'),
    path('riego_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='riego_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('riego_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='riego_equipos_proteccion_cv'),
    path('riego_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='riego_equipos_proteccion_cv_delete'),
    path('riego_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='riego_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('riego_salarios_cv/', CostoSalariosView_cv.as_view(), name='riego_salarios_cv'),
    path('riego_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='riego_salarios_cv_delete'),
    path('riego_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='riego_salarios_cv_detail'),
    path('riego_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='riego_salario_mensual_cv'),
    
    
    path('riego_sueldos_cv/', CostoSueldosView_cv.as_view(), name='riego_sueldos_cv'),
    path('riego_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='riego_sueldos_cv_delete'),
    path('riego_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='riego_sueldos_cv_detail'),
    path('riego_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='riego_sueldo_mensual_cv'),




    #====================================================================================================================
    #PRESUPUESTO DE FERTILIZACION
    #====================================================================================================================

    #RESUMEN DE FERTILIZACION
    path('api/riego_presupuesto_fertilizacion_cv/', ResumenFertilizacionCVView.as_view(), name='api_riego_presupuesto_fertilizacion_dl'), 
    path('api/riego_presupuesto_fertilizacion_cv/<int:id>/', ResumenFertilizacionCVView.as_view(), name='api_riego_presupuesto_fertilizacion_dl_detail'),

    #DETALLE DE FERTILIZACION
    path('api/riego_dprefertilizacion_cv/', DetallePreFertilizacionCVView.as_view(), name='api_riego_dprefertilizacion_cv'),
    path('api/riego_dprefertilizacion_cv/<int:id>/', DetallePreFertilizacionCVView.as_view(), name='api_riego_dprefertilizacion_cv_detail'),
    
    # API PARA OBTENER LOTES
    path('api/lotes_variedad/', LotesVariedadView.as_view(), name='api_lotes_variedad'),

    #====================================================================================================================
    #PRESUPUESTO DE FERTILIZACION
    #====================================================================================================================

    #RESUMEN DE FERTILIZACION
    path('api/riego_presupuesto_fertilizacion_ajs/', ResumenFertilizacionAJSView.as_view(), name='api_riego_presupuesto_fertilizacion_ajs'), 
    path('api/riego_presupuesto_fertilizacion_ajs/<int:id>/', ResumenFertilizacionAJSView.as_view(), name='api_riego_presupuesto_fertilizacion_ajs_detail'),

    #DETALLE DE FERTILIZACION
    path('api/riego_dprefertilizacion_ajs/', DetallePreFertilizacionAJSView.as_view(), name='api_riego_dprefertilizacion_ajs'),
    path('api/riego_dprefertilizacion_ajs/<int:id>/', DetallePreFertilizacionAJSView.as_view(), name='api_riego_dprefertilizacion_ajs_detail'),       

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



    path('riego_presupuesto_ajs/', presupuesto_ajs.as_view(), name='riego_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('riego_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='riego_servicios_totals_ajs'),
    path('riego_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='riego_servicios_ajs'),
    path('riego_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='riego_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('riego_capex_totals_ajs/', Costos_capex_totals_ajs, name='riego_capex_totals_ajs'),

    path('riego_capex_ajs/', CapexView_ajs.as_view(), name='riego_capex_ajs'),
    path('riego_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='riego_capex_ajs_delete'),
    path('riego_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='riego_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('riego_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='riego_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('riego_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='riego_combustibles_lubricantes_ajs'),
    path('riego_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='riego_combustibles_lubricantes_ajs_delete'),
    path('riego_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='riego_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('riego_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='riego_utiles_oficina_ajs'),
    path('riego_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='riego_utiles_oficina_ajs_delete'),
    path('riego_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='riego_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('riego_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='riego_equipos_computo_ajs'),
    path('riego_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='riego_equipos_computo_ajs  _delete'),
    path('riego_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='riego_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('riego_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='riego_otros_suministros_ajs'),
    path('riego_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='riego_otros_suministros_ajs_delete'),   
    path('riego_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='riego_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('riego_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='riego_material_construccion_ajs'),
    path('riego_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='riego_material_construccion_ajs_delete'),
    path('riego_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='riego_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('riego_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='riego_repuestos_accesorios_ajs'),
    path('riego_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='riego_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('riego_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='riego_equipos_uit_ajs'),
    path('riego_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='riego_equipos_uit_ajs_delete'), 
    path('riego_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='riego_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('riego_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='riego_materiales_agricultura_ajs'),
    path('riego_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='riego_materiales_agricultura_ajs_delete'),
    path('riego_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='riego_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('riego_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='riego_equipos_proteccion_ajs'),
    path('riego_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='riego_equipos_proteccion_ajs_delete'),
    path('riego_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='riego_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('riego_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='riego_salarios_ajs'),
    path('riego_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='riego_salarios_ajs_delete'),
    path('riego_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='riego_salarios_ajs_detail'),
    path('riego_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='riego_salario_mensual_ajs'),
    
    path('riego_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='riego_sueldos_ajs'),
    path('riego_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='riego_sueldos_ajs_delete'),
    path('riego_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='riego_sueldos_ajs_detail'),
    path('riego_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='riego_sueldo_mensual_ajs'),

    # RESUMEN DE MATERIA AGRICOLA - DON LUIS
    path('api/materia_agricola_dl/', ResumenMaterialAgricolaView.as_view(), name='api_materia_agricola_dl'), 
    path('api/materia_agricola_dl/<int:id>/', ResumenMaterialAgricolaView.as_view(), name='api_materia_agricola_dl_detail'),

    path('api_productos_agricolas/', ApiproductosAgricolas.as_view(), name='api_productos_agricolas'),
    path('api/suministro_agricola/', SuministroAgricolaListView.as_view(), name='api_suministro_agricola'),
    path('api/suministro_agricola/<int:id>/', SuministroAgricolaDetailView.as_view(), name='api_suministro_agricola_detail'),


    # RESUMEN DE MATERIA AGRICOLA - CAMPO VERDE
    path('api/materia_agricola_cv/', ResumenMaterialAgricolaCVView.as_view(), name='api_materia_agricola_cv'), 
    path('api/materia_agricola_cv/<int:id>/', ResumenMaterialAgricolaCVView.as_view(), name='api_materia_agricola_cv_detail'),

    path('api/suministro_agricola_cv/', SuministroAgricolaListCVView.as_view(), name='api_suministro_agricola_cv'),
    path('api/suministro_agricola_cv/<int:id>/', SuministroAgricolaDetailCVView.as_view(), name='api_suministro_agricola_cv_detail'),

    # RESUMEN DE MATERIA AGRICOLA - INVERSIONES AJS
    path('api/materia_agricola_ajs/', ResumenMaterialAgricolaAJSView.as_view(), name='api_materia_agricola_ajs'), 
    path('api/materia_agricola_ajs/<int:id>/', ResumenMaterialAgricolaAJSView.as_view(), name='api_materia_agricola_ajs_detail'),

    path('api/suministro_agricola_ajs/', SuministroAgricolaListAJSView.as_view(), name='api_suministro_agricola_ajs'),
    path('api/suministro_agricola_ajs/<int:id>/', SuministroAgricolaDetailAJSView.as_view(), name='api_suministro_agricola_ajs_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

