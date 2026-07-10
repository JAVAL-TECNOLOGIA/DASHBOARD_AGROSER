from django.contrib.auth.decorators import login_required

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    path('produccionpalta_presupuesto_dl/', presupuesto_dl.as_view(), name='produccionpalta_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('produccionpalta_servicios_totals_dl/', Costo_servicio_totals, name='produccionpalta_servicios_totals_dl'),
    path('produccionpalta_servicios_dl/', Costo_Servicios_dlView.as_view(), name='produccionpalta_servicios_dl'),
    path('produccionpalta_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='produccionpalta_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('produccionpalta_capex_totals_dl/', Costos_capex_totals, name='produccionpalta_capex_totals_dl'),

    path('produccionpalta_capex/', CapexView.as_view(), name='produccionpalta_capex'),
    path('produccionpalta_capex/<int:id>/', CapexView.as_view(), name='produccionpalta_capex_delete'),
    path('produccionpalta_capex/<int:id>/', CapexView.as_view(), name='produccionpalta_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('produccionpalta_suministros_totals_dl/', Costos_suministros_totals_dl, name='produccionpalta_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('produccionpalta_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='produccionpalta_combustibles_lubricantes'),
    path('produccionpalta_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='produccionpalta_combustibles_lubricantes_delete'),
    path('produccionpalta_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='produccionpalta_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('produccionpalta_utiles-oficina/', UtilesOficinaView.as_view(), name='produccionpalta_utiles_oficina'),
    path('produccionpalta_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='produccionpalta_utiles_oficina_delete'),
    path('produccionpalta_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='produccionpalta_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('produccionpalta_equipos-computo/', EquiposComputoView.as_view(), name='produccionpalta_equipos_computo'),
    path('produccionpalta_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='produccionpalta_equipos_computo_delete'),
    path('produccionpalta_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='produccionpalta_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('produccionpalta_otros-suministros/', OtrosSuministrosView.as_view(), name='produccionpalta_otros_suministros'),
    path('produccionpalta_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='produccionpalta_otros_suministros_delete'),   
    path('produccionpalta_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='produccionpalta_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('produccionpalta_material-construccion/', MaterialConstruccionView.as_view(), name='produccionpalta_material_construccion'),
    path('produccionpalta_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='produccionpalta_material_construccion_delete'),
    path('produccionpalta_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='produccionpalta_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('produccionpalta_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='produccionpalta_repuestos_accesorios'),
    path('produccionpalta_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='produccionpalta_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('produccionpalta_equipos-uit/', EquiposUITView.as_view(), name='produccionpalta_equipos_uit'),
    path('produccionpalta_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='produccionpalta_equipos_uit_delete'), 
    path('produccionpalta_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='produccionpalta_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('produccionpalta_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='produccionpalta_materiales_agricultura'),
    path('produccionpalta_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='produccionpalta_materiales_agricultura_delete'),
    path('produccionpalta_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='produccionpalta_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('produccionpalta_equipos-proteccion/', EquiposProteccionView.as_view(), name='produccionpalta_equipos_proteccion'),
    path('produccionpalta_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='produccionpalta_equipos_proteccion_delete'),
    path('produccionpalta_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='produccionpalta_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('produccionpalta_salarios_dl/', CostoSalariosView.as_view(), name='produccionpalta_salarios_dl'),
    path('produccionpalta_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='produccionpalta_salarios_dl_delete'),
    path('produccionpalta_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='produccionpalta_salarios_dl_detail'),
    path('produccionpalta_salario_mensual/', ApiMensualSalarios.as_view(), name='produccionpalta_salario_mensual'),
    
    
    path('produccionpalta_sueldos_dl/', CostoSueldosView.as_view(), name='produccionpalta_sueldos_dl'),
    path('produccionpalta_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='produccionpalta_sueldos_dl_delete'),
    path('produccionpalta_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='produccionpalta_sueldos_dl_detail'),
    path('produccionpalta_sueldo_mensual/', ApiMensualSueldos.as_view(), name='produccionpalta_sueldo_mensual'),


    #====================================================================================================================
    #EVALUACION DE DESEMPEÑO
    #====================================================================================================================

    path('produccionpalta_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='produccionpalta_evaluacion_desempeño'),



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
    #CAMPO VERDE - TECNOLOGIA DE LA INFORMACION
    #====================================================================================================================

    #=================================================================================================================
    #MODULO PRESUPUESTOS
    #AUTOR: JHON GUTIERREZ
    #FECHA: 06/01/2025
    #MODIFICACIONES: 
    # 10/01/2025: Se crea el modulo de presupuestos
    #=================================================================================================================



    path('produccionpalta_presupuesto_cv/', presupuesto_cv.as_view(), name='produccionpalta_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('produccionpalta_servicios_totals_cv/', Costo_servicio_totals_cv, name='produccionpalta_servicios_totals_cv'),
    path('produccionpalta_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='produccionpalta_servicios_cv'),
    path('produccionpalta_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='produccionpalta_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('produccionpalta_capex_totals_cv/', Costos_capex_totals_cv, name='produccionpalta_capex_totals_cv'),

    path('produccionpalta_capex_cv/', CapexView_cv.as_view(), name='produccionpalta_capex_cv'),
    path('produccionpalta_capex_cv/<int:id>/', CapexView_cv.as_view(), name='produccionpalta_capex_cv_delete'),
    path('produccionpalta_capex_cv/<int:id>/', CapexView_cv.as_view(), name='produccionpalta_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('produccionpalta_suministros_totals_cv/', Costos_suministros_totals_cv, name='produccionpalta_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('produccionpalta_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='produccionpalta_combustibles_lubricantes_cv'),
    path('produccionpalta_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='produccionpalta_combustibles_lubricantes_cv_delete'),
    path('produccionpalta_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='produccionpalta_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('produccionpalta_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='produccionpalta_utiles_oficina_cv'),
    path('produccionpalta_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='produccionpalta_utiles_oficina_cv_delete'),
    path('produccionpalta_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='produccionpalta_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('produccionpalta_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='produccionpalta_equipos_computo_cv'),
    path('produccionpalta_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='produccionpalta_equipos_computo_cv  _delete'),
    path('produccionpalta_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='produccionpalta_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('produccionpalta_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='produccionpalta_otros_suministros_cv'),
    path('produccionpalta_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='produccionpalta_otros_suministros_cv_delete'),   
    path('produccionpalta_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='produccionpalta_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('produccionpalta_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='produccionpalta_material_construccion_cv'),
    path('produccionpalta_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='produccionpalta_material_construccion_cv_delete'),
    path('produccionpalta_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='produccionpalta_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('produccionpalta_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='produccionpalta_repuestos_accesorios_cv'),
    path('produccionpalta_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='produccionpalta_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('produccionpalta_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='produccionpalta_equipos_uit_cv'),
    path('produccionpalta_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='produccionpalta_equipos_uit_cv_delete'), 
    path('produccionpalta_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='produccionpalta_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('produccionpalta_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='produccionpalta_materiales_agricultura_cv'),
    path('produccionpalta_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='produccionpalta_materiales_agricultura_cv_delete'),
    path('produccionpalta_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='produccionpalta_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('produccionpalta_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='produccionpalta_equipos_proteccion_cv'),
    path('produccionpalta_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='produccionpalta_equipos_proteccion_cv_delete'),
    path('produccionpalta_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='produccionpalta_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('produccionpalta_salarios_cv/', CostoSalariosView_cv.as_view(), name='produccionpalta_salarios_cv'),
    path('produccionpalta_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='produccionpalta_salarios_cv_delete'),
    path('produccionpalta_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='produccionpalta_salarios_cv_detail'),
    path('produccionpalta_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='produccionpalta_salario_mensual_cv'),
    
    
    path('produccionpalta_sueldos_cv/', CostoSueldosView_cv.as_view(), name='produccionpalta_sueldos_cv'),
    path('produccionpalta_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='produccionpalta_sueldos_cv_delete'),
    path('produccionpalta_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='produccionpalta_sueldos_cv_detail'),
    path('produccionpalta_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='produccionpalta_sueldo_mensual_cv'),


    # API PARA OBTENER LOTES
    path('api/lotes_variedad/', LotesVariedadView.as_view(), name='api_lotes_variedad'),

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
    path('api/materia_organica_ajs/<int:id>/', OrgResumenMateriaOrganicaCVView.as_view(), name='api_materia_organica_ajs_detail'),

    #DETALLE DE MATERIA ORGANICA
    path('api/organica_materia_ajs/', OrgDetalleMateriaOrganicaAJSView.as_view(), name='api_organica_materia_ajs'),
    path('api/organica_materia_ajs/<int:id>/', OrgDetalleMateriaOrganicaAJSView.as_view(), name='api_organica_materia_ajs_detail'),
    
    



    

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



    path('produccionpalta_presupuesto_ajs/', presupuesto_ajs.as_view(), name='produccionpalta_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('produccionpalta_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='produccionpalta_servicios_totals_ajs'),
    path('produccionpalta_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='produccionpalta_servicios_ajs'),
    path('produccionpalta_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='produccionpalta_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('produccionpalta_capex_totals_ajs/', Costos_capex_totals_ajs, name='produccionpalta_capex_totals_ajs'),

    path('produccionpalta_capex_ajs/', CapexView_ajs.as_view(), name='produccionpalta_capex_ajs'),
    path('produccionpalta_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='produccionpalta_capex_ajs_delete'),
    path('produccionpalta_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='produccionpalta_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('produccionpalta_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='produccionpalta_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('produccionpalta_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='produccionpalta_combustibles_lubricantes_ajs'),
    path('produccionpalta_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='produccionpalta_combustibles_lubricantes_ajs_delete'),
    path('produccionpalta_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='produccionpalta_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('produccionpalta_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='produccionpalta_utiles_oficina_ajs'),
    path('produccionpalta_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='produccionpalta_utiles_oficina_ajs_delete'),
    path('produccionpalta_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='produccionpalta_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('produccionpalta_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='produccionpalta_equipos_computo_ajs'),
    path('produccionpalta_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='produccionpalta_equipos_computo_ajs  _delete'),
    path('produccionpalta_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='produccionpalta_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('produccionpalta_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='produccionpalta_otros_suministros_ajs'),
    path('produccionpalta_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='produccionpalta_otros_suministros_ajs_delete'),   
    path('produccionpalta_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='produccionpalta_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('produccionpalta_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='produccionpalta_material_construccion_ajs'),
    path('produccionpalta_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='produccionpalta_material_construccion_ajs_delete'),
    path('produccionpalta_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='produccionpalta_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('produccionpalta_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='produccionpalta_repuestos_accesorios_ajs'),
    path('produccionpalta_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='produccionpalta_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('produccionpalta_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='produccionpalta_equipos_uit_ajs'),
    path('produccionpalta_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='produccionpalta_equipos_uit_ajs_delete'), 
    path('produccionpalta_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='produccionpalta_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('produccionpalta_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='produccionpalta_materiales_agricultura_ajs'),
    path('produccionpalta_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='produccionpalta_materiales_agricultura_ajs_delete'),
    path('produccionpalta_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='produccionpalta_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('produccionpalta_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='produccionpalta_equipos_proteccion_ajs'),
    path('produccionpalta_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='produccionpalta_equipos_proteccion_ajs_delete'),
    path('produccionpalta_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='produccionpalta_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('produccionpalta_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='produccionpalta_salarios_ajs'),
    path('produccionpalta_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='produccionpalta_salarios_ajs_delete'),
    path('produccionpalta_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='produccionpalta_salarios_ajs_detail'),
    path('produccionpalta_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='produccionpalta_salario_mensual_ajs'),
    
    
    path('produccionpalta_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='produccionpalta_sueldos_ajs'),
    path('produccionpalta_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='produccionpalta_sueldos_ajs_delete'),
    path('produccionpalta_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='produccionpalta_sueldos_ajs_detail'),
    path('produccionpalta_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='produccionpalta_sueldo_mensual_ajs'),

    
    # RESUMEN DE MATERIA AGRICOLA - DON LUIS
    path('api/materia_agricola_palta/', ResumenMaterialAgricolaView.as_view(), name='api_materia_agricola_palta'), 
    path('api/materia_agricola_palta/<int:id>/', ResumenMaterialAgricolaView.as_view(), name='api_materia_agricola_palta_detail'),

    path('api_productos_agricolas_palta/', ApiproductosAgricolas.as_view(), name='api_productos_agricolas_palta'),
    path('api/suministro_agricola_palta/', SuministroAgricolaListView.as_view(), name='api_suministro_agricola_palta'),
    path('api/suministro_agricola_palta/<int:id>/', SuministroAgricolaDetailView.as_view(), name='api_suministro_agricola_palta_detail'),


    # RESUMEN DE MATERIA AGRICOLA - CAMPO VERDE
    path('api/materia_agricola_palta_cv/', ResumenMaterialAgricolaCVView.as_view(), name='api_materia_agricola_palta_cv'), 
    path('api/materia_agricola_palta_cv/<int:id>/', ResumenMaterialAgricolaCVView.as_view(), name='api_materia_agricola_palta_cv_detail'),

    path('api/suministro_agricola_palta_cv/', SuministroAgricolaListCVView.as_view(), name='api_suministro_agricola_palta_cv'),
    path('api/suministro_agricola_palta_cv/<int:id>/', SuministroAgricolaDetailCVView.as_view(), name='api_suministro_agricola_palta_cv_detail'),

    # RESUMEN DE MATERIA AGRICOLA - INVERSIONES AJS
    path('api/materia_agricola_palta_ajs/', ResumenMaterialAgricolaAJSView.as_view(), name='api_materia_agricola_palta_ajs'), 
    path('api/materia_agricola_palta_ajs/<int:id>/', ResumenMaterialAgricolaAJSView.as_view(), name='api_materia_agricola_palta_ajs_detail'),

    path('api/suministro_agricola_palta_ajs/', SuministroAgricolaListAJSView.as_view(), name='api_suministro_agricola_palta_ajs'),
    path('api/suministro_agricola_palta_ajs/<int:id>/', SuministroAgricolaDetailAJSView.as_view(), name='api_suministro_agricola_palta_ajs_detail'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

