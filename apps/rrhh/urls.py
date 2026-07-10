from django.contrib.auth.decorators import login_required,  permission_required

from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from .views import eliminar_pdf


urlpatterns = [


    # REPORTE
    path('rrhh_reporte/', reporte_rrhh.as_view(), name='rrhh_reporte'),

    path('recursos_humanos/', Recursos_humanos.as_view(), name='recursos_humanos'),
    path('eliminar/<int:pdf_id>/', eliminar_pdf, name='eliminar_pdf'),
    


    # PRESUPUESTO
    path('rrhh_presupuesto_dl/', presupuesto_dl.as_view(), name='rrhh_presupuesto_dl'),

    # EVALUACION DE DESEMPEÑO
    path('rrhh_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='rrhh_evaluacion_desempeño'),






    #=============================================================================
    # SERVICIOS
    #=========================================================================
    path('rrhh_servicios_totals_dl/', Costo_servicio_totals, name='rrhh_servicios_totals_dl'),
    path('rrhh_servicios_dl/', Costo_Servicios_dlView.as_view(), name='rrhh_servicios_dl'),
    path('rrhh_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='rrhh_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('rrhh_capex_totals_dl/', Costos_capex_totals, name='rrhh_capex_totals_dl'),

    path('rrhh_capex/', CapexView.as_view(), name='rrhh_capex'),
    path('rrhh_capex/<int:id>/', CapexView.as_view(), name='rrhh_capex_delete'),
    path('rrhh_capex/<int:id>/', CapexView.as_view(), name='rrhh_capex_detail'),

    #================================================
    # SUMINISTROS
    #===============================================
    path('rrhh_suministros_totals_dl/', Costos_suministros_totals_dl, name='rrhh_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('rrhh_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='rrhh_combustibles_lubricantes'),
    path('rrhh_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='rrhh_combustibles_lubricantes_delete'),
    path('rrhh_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='rrhh_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('rrhh_utiles-oficina/', UtilesOficinaView.as_view(), name='rrhh_utiles_oficina'),
    path('rrhh_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='rrhh_utiles_oficina_delete'),
    path('rrhh_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='rrhh_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('rrhh_equipos-computo/', EquiposComputoView.as_view(), name='rrhh_equipos_computo'),
    path('rrhh_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='rrhh_equipos_computo_delete'),
    path('rrhh_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='rrhh_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('rrhh_otros-suministros/', OtrosSuministrosView.as_view(), name='rrhh_otros_suministros'),
    path('rrhh_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='rrhh_otros_suministros_delete'),   
    path('rrhh_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='rrhh_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('rrhh_material-construccion/', MaterialConstruccionView.as_view(), name='rrhh_material_construccion'),
    path('rrhh_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='rrhh_material_construccion_delete'),
    path('rrhh_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='rrhh_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('rrhh_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='rrhh_repuestos_accesorios'),
    path('rrhh_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='rrhh_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('rrhh_equipos-uit/', EquiposUITView.as_view(), name='rrhh_equipos_uit'),
    path('rrhh_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='rrhh_equipos_uit_delete'), 
    path('rrhh_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='rrhh_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('rrhh_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='rrhh_materiales_agricultura'),
    path('rrhh_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='rrhh_materiales_agricultura_delete'),
    path('rrhh_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='rrhh_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('rrhh_equipos-proteccion/', EquiposProteccionView.as_view(), name='rrhh_equipos_proteccion'),
    path('rrhh_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='rrhh_equipos_proteccion_delete'),
    path('rrhh_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='rrhh_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('rrhh_salarios_dl/', CostoSalariosView.as_view(), name='rrhh_salarios_dl'),
    path('rrhh_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='rrhh_salarios_dl_delete'),
    path('rrhh_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='rrhh_salarios_dl_detail'),
    path('rrhh_salario_mensual/', ApiMensualSalarios.as_view(), name='rrhh_salario_mensual'),
    
    
    path('rrhh_sueldos_dl/', CostoSueldosView.as_view(), name='rrhh_sueldos_dl'),
    path('rrhh_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='rrhh_sueldos_dl_delete'),
    path('rrhh_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='rrhh_sueldos_dl_detail'),
    path('rrhh_sueldo_mensual/', ApiMensualSueldos.as_view(), name='rrhh_sueldo_mensual'),



    #####################################################################################################
    # UTILIDADES
    #####################################################################################################

    #CONSULTA DE UTILIDADES
    path('rrhh_consulta_utilidades/', consulta_utilidades.as_view(), name='rrhh_consulta_utilidades'),

    path('consulta_utilidades_DON_LUIS/', ConsultaUtilidadesPublicaView.as_view(), name='consulta_utilidades_DON_LUIS'),

    # CONSULTA API DE UTILIDADES
    path('rrhh_personal_general/', PersonalGeneralAPI.as_view(), name='personal_general'),
    # API PARA BUSCAR EMPLEADOS EN UTILIDADES
    
    # Añadir después de la línea 370
    path('certificado_utilidades/', CertificadoUtilidadesView.as_view(), name='certificado_utilidades'),

    # Añadir esta línea en el arreglo urlpatterns
    path('utilidades_empleados/', UtilidadesEmpleadosView.as_view(), name='utilidades_empleados'),
    
    
   
    # API PARA OBTENER DATOS PERSONALES POR DNI
    path('datos_personal_por_dni/', DatosPersonalPorDNIView.as_view(), name='datos_personal_por_dni'),

    # API PARA OBTENER DATOS DE USUARIOS
    path('usuarios/', UsuariosView.as_view(), name='usuarios'),

    
    #REPORTE DE UTILIDADES
    path('rrhh_reporte_utilidades/', reporte_utilidades.as_view(), name='rrhh_reporte_utilidades'),
    
    path('lista_utilidades_empleados/', UtilidadesEmpleadosListView.as_view(), name='lista_utilidades_empleados'),


    ###########################################################################################################
    # FORMULARIOS
    ###########################################################################################################

    #CAMPAÑA DE PODA Y AMARRE
    path('registro_campana_poda_amarre/', RegistroCampanaPodaAmarreView.as_view(), name='registro_campana_poda_amarre'),
    path('api/registro_campana_poda_amarre/', RegistroCampanaPodaAmarreAPIView.as_view(), name='api_registro_campana_poda_amarre'),
    
    path('reporte_campana_poda_amarre/', reporte_campana_poda_amarre.as_view(), name='reporte_campana_poda_amarre'),
    
    ##REPORTE DE EVALUACION DE DESEMPEÑO GENERAL 
                    
     path('resumen_evaluacion_desempeño/', ResumenRRHHObjetivosView.as_view(), name='resumen_evaluacion_desempeño'),


     # ENCUESTA DE CAPACITACION DE HABILIDADES BLANDAS

     path('encuesta_capacitacion_habilidades_blandas/', EncuestaCapacitacionHabilidadesBlandasView.as_view(), name='encuesta_capacitacion_habilidades_blandas'),
     path('encuesta_dia_de_la_madre/', EncuestaDiaMadre.as_view(), name='encuesta_dia_de_la_madre'),
     path('encuesta_dia_del_padre/', EncuestaDiaPadre.as_view(), name='encuesta_dia_del_padre'),
     path('encuesta_de_fiestas_patrias/', EncuestaFiestasPatrias.as_view(), name='encuesta_de_fiestas_patrias'),
     path('encuesta_del_reinado/', EncuestaReinado.as_view(), name='encuesta_del_reinado'),
     path('encuesta_del_halloween/', EncuestaHalloween.as_view(), name='encuesta_del_halloween'),
     path('encuesta_voley_mixto/', EncuestaVoleyMixto.as_view(), name='encuesta_voley_mixto'),
     path('encuesta_juegos_integracion/', EncuestaJuegosIntegracion.as_view(), name='encuesta_juegos_integracion'),   

    #==============================================================================================
    # EVALUACION DE DESEMPEÑO
    #==============================================================================================
    
    path('rrhh_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='rrhh_evaluacion_desempeño'),
    path('evaluaciones/', EvaluacionDesempenoView.as_view(), name='evaluaciones'),
    path('evaluaciones/<int:id>/', EvaluacionDesempenoView.as_view(), name='evaluaciones_detail'),
    

    # API para obtener datos maestros
    path('areas/', AreasView.as_view(), name='areas'),
    path('categorias/', CategoriasView.as_view(), name='categorias'),
    path('preguntas/', PreguntasView.as_view(), name='preguntas'),
    



    # API PARA OBTENER DATOS DE USUARIOS AREAS Y ROLES 
    path('usuario-area/', UsuarioAreaConsultaView.as_view(), name='usuario_area'),
    path('rrhh_evaluaciones/', RRHH_EvaluacionesView.as_view(), name='rrhh_evaluaciones'),
    path('evaluaciones-general/', EvaluacionesGeneralView.as_view(), name='evaluaciones_general'),

    # API PARA OBTENER DATOS DE EVALUADOS GENERAL
    path('rpt_rrhh_evaluados/', RPT_RRHH_EvaluadosView.as_view(), name='rpt_rrhh_evaluados'),
    


    # API PARA OBTENER DATOS DE EVALUACIONES DE OBJETIVOS
    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='detalles_objetivos_detail'),
    
    # API PARA OBTENER EL RESUMEN DE COMPETENCIAS DE EVALUACION
    path('resumen_competencias/', ResumenCompetenciasView.as_view(), name='resumen_competencias'),
    



    # API PARA OBTENER DATOS DE COMPETENCIAS DE EVALUACION
    path('detalles_competencias/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias'),
    path('detalles_competencias/<int:id>/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias_detail'),
    path('enviar_evaluacion_correo/', enviar_evaluacion_correo, name='enviar_evaluacion_correo'),

    # API PARA OBTENER DATOS DE USUARIOS DE JERARQUIA
    path('usuarios-jerarquia/', UsuariosJerarquiaView.as_view(), name='usuarios_jerarquia'),

    #====================================================================================================================
    # VISUALIZACION DE DATOS DE EVALUACION DE DESEMPEÑO
    #====================================================================================================================
    path('api/rrhh_ev_datos/<int:id_evaluacion>/', EvaluacionCompletaView.as_view(), name='api/rrhh_ev_datos'),

    #====================================================================================================================
    # API para la fase intermedia de evaluaciones
    #====================================================================================================================
    
    path('api/fase-intermedia/', FaseIntermediaEvaluacionesView.as_view(), name='fase_intermedia_evaluaciones'),
    path('api/fase-intermedia/<int:id_evaluacion>/', FaseIntermediaEvaluacionesView.as_view(), name='fase_intermedia_evaluacion_detalle'),
    
    #api para los detalles de la fase intermedia
    
    
    # En tu archivo urls.py
    path('api/detalles-evaluacion/', DetallesEvaluacionModalView.as_view(), name='detalles_evaluacion_modal'),
    
    
    
    #=====================================================================================================================
    # API PARA LOS DETALLES DE LA FASE INTERMEDIA
    #=====================================================================================================================
    
    
    #====================================================================================================================
    # API para la fase FINAL de evaluaciones
    #====================================================================================================================
    
    path('api/fase-final/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluaciones'),
    path('api/fase-final/<int:id_evaluacion>/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluacion_detalle'),
    
    #api para los detalles de la fase final
    path('api/detalles-evaluacion-final/', DetallesEvaluacionFinalModalView.as_view(), name='detalles_evaluacion_final_modal'),
    
    
    
    #=====================================================================================================================
    # API PARA LOS DETALLES DE LA FASE FINAL
    #=====================================================================================================================
    
    
    
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



    path('rrhh_presupuesto_cv/', presupuesto_cv.as_view(), name='rrhh_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('rrhh_servicios_totals_cv/', Costo_servicio_totals_cv, name='rrhh_servicios_totals_cv'),
    path('rrhh_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='rrhh_servicios_cv'),
    path('rrhh_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='rrhh_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('rrhh_capex_totals_cv/', Costos_capex_totals_cv, name='rrhh_capex_totals_cv'),

    path('rrhh_capex_cv/', CapexView_cv.as_view(), name='rrhh_capex_cv'),
    path('rrhh_capex_cv/<int:id>/', CapexView_cv.as_view(), name='rrhh_capex_cv_delete'),
    path('rrhh_capex_cv/<int:id>/', CapexView_cv.as_view(), name='rrhh_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('rrhh_suministros_totals_cv/', Costos_suministros_totals_cv, name='rrhh_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('rrhh_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='rrhh_combustibles_lubricantes_cv'),
    path('rrhh_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='rrhh_combustibles_lubricantes_cv_delete'),
    path('rrhh_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='rrhh_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('rrhh_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='rrhh_utiles_oficina_cv'),
    path('rrhh_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='rrhh_utiles_oficina_cv_delete'),
    path('rrhh_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='rrhh_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('rrhh_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='rrhh_equipos_computo_cv'),
    path('rrhh_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='rrhh_equipos_computo_cv  _delete'),
    path('rrhh_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='rrhh_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('rrhh_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='rrhh_otros_suministros_cv'),
    path('rrhh_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='rrhh_otros_suministros_cv_delete'),   
    path('rrhh_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='rrhh_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('rrhh_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='rrhh_material_construccion_cv'),
    path('rrhh_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='rrhh_material_construccion_cv_delete'),
    path('rrhh_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='rrhh_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('rrhh_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='rrhh_repuestos_accesorios_cv'),
    path('rrhh_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='rrhh_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('rrhh_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='rrhh_equipos_uit_cv'),
    path('rrhh_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='rrhh_equipos_uit_cv_delete'), 
    path('rrhh_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='rrhh_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('rrhh_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='rrhh_materiales_agricultura_cv'),
    path('rrhh_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='rrhh_materiales_agricultura_cv_delete'),
    path('rrhh_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='rrhh_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('rrhh_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='rrhh_equipos_proteccion_cv'),
    path('rrhh_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='rrhh_equipos_proteccion_cv_delete'),
    path('rrhh_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='rrhh_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('rrhh_salarios_cv/', CostoSalariosView_cv.as_view(), name='rrhh_salarios_cv'),
    path('rrhh_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='rrhh_salarios_cv_delete'),
    path('rrhh_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='rrhh_salarios_cv_detail'),
    path('rrhh_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='rrhh_salario_mensual_cv'),
    
    
    path('rrhh_sueldos_cv/', CostoSueldosView_cv.as_view(), name='rrhh_sueldos_cv'),
    path('rrhh_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='rrhh_sueldos_cv_delete'),
    path('rrhh_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='rrhh_sueldos_cv_detail'),
    path('rrhh_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='rrhh_sueldo_mensual_cv'),



    #====================================================================================================================
    # UTILIDADES CAMPOS VERDE
    #====================================================================================================================

    path('rrhh_consulta_utilidades_cv/', consulta_utilidades_cv.as_view(), name='rrhh_consulta_utilidades_cv'),

    # CONSULTA API DE UTILIDADES
    path('personal_general_cv/', PersonalGeneralAPI_cv.as_view(), name='personal_general_cv'),
    # API PARA BUSCAR EMPLEADOS EN UTILIDADES
    
    # Añadir después de la línea 370
    path('certificado_utilidades_cv/', CertificadoUtilidadesView_cv.as_view(), name='certificado_utilidades_cv'),

    # Añadir esta línea en el arreglo urlpatterns
    path('utilidades_empleados_cv/', UtilidadesEmpleadosView_cv.as_view(), name='utilidades_empleados_cv'),
    
    
   
    # API PARA OBTENER DATOS PERSONALES POR DNI
    path('datos_personal_por_dni_cv/', DatosPersonalPorDNIView_cv.as_view(), name='datos_personal_por_dni_cv'),




    #REPORTE DE UTILIDADES
    path('rrhh_reporte_utilidades_cv/', reporte_utilidades_cv.as_view(), name='rrhh_reporte_utilidades_cv'),
    
    path('lista_utilidades_empleados_cv/', UtilidadesEmpleadosListView_cv.as_view(), name='lista_utilidades_empleados_cv'),



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



    path('rrhh_presupuesto_ajs/', presupuesto_ajs.as_view(), name='rrhh_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('rrhh_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='rrhh_servicios_totals_ajs'),
    path('rrhh_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='rrhh_servicios_ajs'),
    path('rrhh_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='rrhh_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('rrhh_capex_totals_ajs/', Costos_capex_totals_ajs, name='rrhh_capex_totals_ajs'),

    path('rrhh_capex_ajs/', CapexView_ajs.as_view(), name='rrhh_capex_ajs'),
    path('rrhh_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='rrhh_capex_ajs_delete'),
    path('rrhh_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='rrhh_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('rrhh_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='rrhh_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('rrhh_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='rrhh_combustibles_lubricantes_ajs'),
    path('rrhh_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='rrhh_combustibles_lubricantes_ajs_delete'),
    path('rrhh_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='rrhh_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('rrhh_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='rrhh_utiles_oficina_ajs'),
    path('rrhh_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='rrhh_utiles_oficina_ajs_delete'),
    path('rrhh_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='rrhh_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('rrhh_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='rrhh_equipos_computo_ajs'),
    path('rrhh_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='rrhh_equipos_computo_ajs  _delete'),
    path('rrhh_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='rrhh_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('rrhh_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='rrhh_otros_suministros_ajs'),
    path('rrhh_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='rrhh_otros_suministros_ajs_delete'),   
    path('rrhh_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='rrhh_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('rrhh_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='rrhh_material_construccion_ajs'),
    path('rrhh_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='rrhh_material_construccion_ajs_delete'),
    path('rrhh_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='rrhh_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('rrhh_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='rrhh_repuestos_accesorios_ajs'),
    path('rrhh_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='rrhh_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('rrhh_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='rrhh_equipos_uit_ajs'),
    path('rrhh_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='rrhh_equipos_uit_ajs_delete'), 
    path('rrhh_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='rrhh_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('rrhh_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='rrhh_materiales_agricultura_ajs'),
    path('rrhh_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='rrhh_materiales_agricultura_ajs_delete'),
    path('rrhh_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='rrhh_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('rrhh_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='rrhh_equipos_proteccion_ajs'),
    path('rrhh_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='rrhh_equipos_proteccion_ajs_delete'),
    path('rrhh_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='rrhh_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('rrhh_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='rrhh_salarios_ajs'),
    path('rrhh_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='rrhh_salarios_ajs_delete'),
    path('rrhh_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='rrhh_salarios_ajs_detail'),
    path('rrhh_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='rrhh_salario_mensual_ajs'),
    
    
    path('rrhh_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='rrhh_sueldos_ajs'),
    path('rrhh_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='rrhh_sueldos_ajs_delete'),
    path('rrhh_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='rrhh_sueldos_ajs_detail'),
    path('rrhh_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='rrhh_sueldo_mensual_ajs'),

    


    # path("api/consolidado-mensual/", consolidado_mensual_api, name="consolidado-mensual"),

   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

