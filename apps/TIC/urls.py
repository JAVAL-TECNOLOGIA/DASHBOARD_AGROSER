from django.urls import path
from .views import *


urlpatterns = [

    # PROCESOS TIC - MANEJO DE PDFs
    path('procesos_tic/', tic.as_view(), name='procesos_tic'),
    path('eliminar/<int:pdf_id>/', eliminar_pdf_tic, name='eliminar_pdf_tic'),

    # VISTA DE LINEAS CELULARES
    path('api-linea-celulares/', LineaCelularesView.as_view(), name='api_linea_celulares'),
    path('api-linea-celulares/<int:id>/', LineaCelularesView.as_view(), name='api_linea_celulares_detail'),
    path('lineas-celulares/', LineaCelularesTemplateView.as_view(), name='lineas_celulares'),
    
    #SECCIONES DEL MODULO TIC
    path('tic_presupuesto_dl/', Tic_presupuesto_dl.as_view(), name='tic_presupuesto_dl'),
    path('Tic_Costos_Don_luis/',Tic_costos_dl_view.as_view(), name ='tic_costos_dl'),
    path('Tic_Mantenimiento_dl/',Tic_mantenimiento_dl_view.as_view(), name ='tic_mantenimiento_dl'),


    #VISTA PARA EL PRESUPUESTO - TOTALES  DE DON LUIS
    path('api_suministros_totales/', get_suministros_totals, name='api_suministros_totales'),
    
    path('api_sueldos_totales/', get_sueldos_totals, name='api_sueldos_totales'),
    
    
    path('api_salarios_totales/', get_salarios_totals, name='api_salarios_totales'),
    

    path('api_servicios_totales/', get_tic_servicio_totals, name='api_servicios_totales'),
    
    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    


    path('material-oficina/', MaterialOficinaView.as_view(), name='material_oficina'),
    path('api_productos/', Apiproductos.as_view(), name='api_productos'),
    path('material-oficina/<int:id>/', MaterialOficinaView.as_view(), name='material_oficina_delete'),
    path('material-oficina/<int:id>/', MaterialOficinaView.as_view(), name='material_oficina_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('utiles-oficina/', UtilesOficinaView.as_view(), name='utiles_oficina'),
    path('api_productos_utiles/', ApiProductosUtiles.as_view(), name='api_productos_utiles'),
    path('utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='utiles_oficina_delete'),
    path('utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('equipos-computo/', EquiposComputoView.as_view(), name='equipos_computo'),
    path('api_productos_computo/', ApiProductosComputo.as_view(), name='api_productos_computo'),
    path('equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='equipos_computo_delete'),
    path('equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('otros-suministros/', OtrosSuministrosView.as_view(), name='otros_suministros'),
    path('api_productos_otros_suministros/', ApiProductosOtrosSuministros.as_view(), name='api_productos_otros_suministros'),
    path('otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='otros_suministros_delete'),   
    path('otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('material-construccion/', MaterialConstruccionView.as_view(), name='material_construccion'),
    path('api_productos_material_construccion/', ApiProductosMaterialConstruccion.as_view(), name='api_productos_material_construccion'),
    path('material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='material_construccion_delete'),
    path('material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='repuestos_accesorios'),
    path('api_productos_repuestos_accesorios/', ApiProductosRepuestosAccesorios.as_view(), name='api_productos_repuestos_accesorios'),
    path('repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('equipos-uit/', EquiposUITView.as_view(), name='equipos_uit'),
    path('api_productos_equipos_uit/', ApiProductosEquiposUIT.as_view(), name='api_productos_equipos_uit'),
    path('equipos-uit/<int:id>/', EquiposUITView.as_view(), name='equipos_uit_delete'), 
    path('equipos-uit/<int:id>/', EquiposUITView.as_view(), name='equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='materiales_agricultura'),
    path('api_productos_materiales_agricultura/', ApiProductosMaterialesAgricultura.as_view(), name='api_productos_materiales_agricultura'),
    path('materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='materiales_agricultura_delete'),
    path('materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('equipos-proteccion/', EquiposProteccionView.as_view(), name='equipos_proteccion'),
    path('api_productos_equipos_proteccion/', ApiProductosEquiposProteccion.as_view(), name='api_productos_equipos_proteccion'),
    path('equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='equipos_proteccion_delete'),
    path('equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='equipos_proteccion_detail'),


    #PRESUPUESTO - SUELDOS Y SALARIOS
    path('api_sueldos/', ApiSueldos.as_view(), name='api_sueldos'),
    path('sueldos/', SueldosView.as_view(), name='sueldos'),
    path('sueldos/<int:id>/', SueldosView.as_view(), name='sueldos_detail'),
    path('api_sueldo_mensual/', ApiSueldoMensual.as_view(), name='api_sueldo_mensual'),


    path('api_salarios/', ApiSalarios.as_view(), name='api_salarios'),
    path('salarios/', SalariosView.as_view(), name='salarios'),
    path('salarios/<int:id>/', SalariosView.as_view(), name='salarios_detail'),
    path('api_salario_mensual/', ApiSalarioMensual.as_view(), name='api_salario_mensual'),

    #CONFIGURACIONES
    path('configuraciones-sueldos-salarios/', ConfiguracionesSueldosSalariosView.as_view(), name='configuraciones_sueldos_salarios'),
    path('configuraciones-sueldos-salarios/<int:id>/', ConfiguracionesSueldosSalariosView.as_view(), name='configuraciones_sueldos_salarios_detail'),

    #CAPEX
    path('api_capex_totales/', get_capex_totals, name='api_capex_totales'),
    path('capex/', CapexView.as_view(), name='capex'),
    path('api_capex/', ApiCapex.as_view(), name='api_capex'),
    path('capex/<int:id>/', CapexView.as_view(), name='capex_delete'),
    path('capex/<int:id>/', CapexView.as_view(), name='capex_detail'),

    #SERVICIOS
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('servicios/<int:id>/', ServiciosView.as_view(), name='servicios_delete'),
    path('servicios/<int:id>/', ServiciosView.as_view(), name='servicios_detail'),
    path('api_subgrupos_servicios/<str:grupo_id>/', ApiSubgruposServicios.as_view(), name='api_subgrupos_servicios'),
    path('api_descripciones_servicios/', ApiDescripcionesServicios.as_view(), name='api_descripciones_servicios'),


    
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



    path('tic_presupuesto_cv/', presupuesto_cv.as_view(), name='tic_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('tic_servicios_totals_cv/', Costo_servicio_totals_cv, name='tic_servicios_totals_cv'),
    path('tic_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='tic_servicios_cv'),
    path('tic_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='tic_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('tic_capex_totals_cv/', Costos_capex_totals_cv, name='tic_capex_totals_cv'),

    path('tic_capex_cv/', CapexView_cv.as_view(), name='tic_capex_cv'),
    path('tic_capex_cv/<int:id>/', CapexView_cv.as_view(), name='tic_capex_cv_delete'),
    path('tic_capex_cv/<int:id>/', CapexView_cv.as_view(), name='tic_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('tic_suministros_totals_cv/', Costos_suministros_totals_cv, name='tic_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('tic_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='tic_combustibles_lubricantes_cv'),
    path('tic_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='tic_combustibles_lubricantes_cv_delete'),
    path('tic_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='tic_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('tic_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='tic_utiles_oficina_cv'),
    path('tic_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='tic_utiles_oficina_cv_delete'),
    path('tic_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='tic_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('tic_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='tic_equipos_computo_cv'),
    path('tic_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='tic_equipos_computo_cv  _delete'),
    path('tic_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='tic_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('tic_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='tic_otros_suministros_cv'),
    path('tic_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='tic_otros_suministros_cv_delete'),   
    path('tic_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='tic_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('tic_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='tic_material_construccion_cv'),
    path('tic_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='tic_material_construccion_cv_delete'),
    path('tic_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='tic_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('tic_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='tic_repuestos_accesorios_cv'),
    path('tic_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='tic_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('tic_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='tic_equipos_uit_cv'),
    path('tic_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='tic_equipos_uit_cv_delete'), 
    path('tic_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='tic_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('tic_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='tic_materiales_agricultura_cv'),
    path('tic_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='tic_materiales_agricultura_cv_delete'),
    path('tic_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='tic_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('tic_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='tic_equipos_proteccion_cv'),
    path('tic_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='tic_equipos_proteccion_cv_delete'),
    path('tic_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='tic_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('tic_salarios_cv/', CostoSalariosView_cv.as_view(), name='tic_salarios_cv'),
    path('tic_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='tic_salarios_cv_delete'),
    path('tic_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='tic_salarios_cv_detail'),
    path('tic_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='tic_salario_mensual_cv'),
    
    
    path('tic_sueldos_cv/', CostoSueldosView_cv.as_view(), name='tic_sueldos_cv'),
    path('tic_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='tic_sueldos_cv_delete'),
    path('tic_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='tic_sueldos_cv_detail'),
    path('tic_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='tic_sueldo_mensual_cv'),


    
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



    path('tic_presupuesto_ajs/', presupuesto_ajs.as_view(), name='tic_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('tic_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='tic_servicios_totals_ajs'),
    path('tic_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='tic_servicios_ajs'),
    path('tic_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='tic_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('tic_capex_totals_ajs/', Costos_capex_totals_ajs, name='tic_capex_totals_ajs'),

    path('tic_capex_ajs/', CapexView_ajs.as_view(), name='tic_capex_ajs'),
    path('tic_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='tic_capex_ajs_delete'),
    path('tic_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='tic_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('tic_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='tic_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('tic_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='tic_combustibles_lubricantes_ajs'),
    path('tic_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='tic_combustibles_lubricantes_ajs_delete'),
    path('tic_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='tic_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('tic_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='tic_utiles_oficina_ajs'),
    path('tic_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='tic_utiles_oficina_ajs_delete'),
    path('tic_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='tic_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('tic_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='tic_equipos_computo_ajs'),
    path('tic_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='tic_equipos_computo_ajs  _delete'),
    path('tic_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='tic_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('tic_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='tic_otros_suministros_ajs'),
    path('tic_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='tic_otros_suministros_ajs_delete'),   
    path('tic_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='tic_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('tic_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='tic_material_construccion_ajs'),
    path('tic_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='tic_material_construccion_ajs_delete'),
    path('tic_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='tic_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('tic_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='tic_repuestos_accesorios_ajs'),
    path('tic_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='tic_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('tic_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='tic_equipos_uit_ajs'),
    path('tic_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='tic_equipos_uit_ajs_delete'), 
    path('tic_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='tic_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('tic_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='tic_materiales_agricultura_ajs'),
    path('tic_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='tic_materiales_agricultura_ajs_delete'),
    path('tic_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='tic_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('tic_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='tic_equipos_proteccion_ajs'),
    path('tic_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='tic_equipos_proteccion_ajs_delete'),
    path('tic_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='tic_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('tic_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='tic_salarios_ajs'),
    path('tic_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='tic_salarios_ajs_delete'),
    path('tic_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='tic_salarios_ajs_detail'),
    path('tic_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='tic_salario_mensual_ajs'),
    
    
    path('tic_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='tic_sueldos_ajs'),
    path('tic_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='tic_sueldos_ajs_delete'),
    path('tic_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='tic_sueldos_ajs_detail'),
    path('tic_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='tic_sueldo_mensual_ajs'),



    #=====================================================================================================================
    #GESTION TIC
    #=====================================================================================================================

    path('mantenimiento_user/', MantenimientoUserDlView.as_view(), name='mantenimiento_user_dl'),
    path('mantenimiento_user/<int:id>/', MantenimientoUserDlView.as_view(), name='mantenimiento_user_dl_detail'),
    #API PARA EL MANEJO DE USUARIOS DE TIC
    path('api_mantenimiento_usuarios_dl/', ApiUsuariosDL.as_view(), name='api_mantenimiento_usuarios_dl'),

    #GESTION DE TIC - TRABAJADORES
    
     # Nuevas rutas para la gestión de trabajadores
    path('trabajador/', TrabajadorView.as_view(), name='trabajador'),
    path('trabajador/<int:id>/', TrabajadorView.as_view(), name='trabajador_detail'),
    
    # APIs para los selectores
    path('api/cargos/', ApiCargosView.as_view(), name='api_cargos'),
    path('api/areas/', ApiAreasView.as_view(), name='api_areas'),
    path('api/gerencias/', ApiGerenciasView.as_view(), name='api_gerencias'),
    path('api/sedes/', ApiSedesView.as_view(), name='api_sedes'),
    path('api/empresas/', ApiEmpresasView.as_view(), name='api_empresas'),


    #========================================================================
    # APIS CAMPO VERDE 
    #========================================================================

    #APIS DE SUELDOS Y SALARIOS
     path('api_salarios_cv/', ApiSalarios_cv.as_view(), name='api_salarios_cv'),
    path('api_sueldos_cv/', ApiSueldos_cv.as_view(), name='api_sueldos_cv'),


    #========================================================================
    # APIS CAMPO VERDE 
    #========================================================================

    #APIS DE SUELDOS Y SALARIOS
    path('api_salarios_ajs/', ApiSalarios_ajs.as_view(), name='api_salarios_ajs'),
    path('api_sueldos_ajs/', ApiSueldos_ajs.as_view(), name='api_sueldos_ajs'),

    #APIS DE EVALUACION DE DESEMPEÑO
    path('tic_evaluacion_desempeño/', Tic_evaluacion_desempeño.as_view(), name='tic_evaluacion_desempeño'),
    
    
    path('tic_evaluaciones-general/', EvaluacionesGeneralView.as_view(), name='evaluaciones_general'),



    #==============================================================================
    # EVALACUACIONES | OBJTIVOS Y DESEMPEÑO
    #==============================================================================
    
   

    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='tic_objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='tic_objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='tic_detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='tic_detalles_objetivos_detail'),

    # API PARA OBTENER EL RESUMEN DE COMPETENCIAS DE EVALUACION (filtrado por id_area=4)
    path('resumen_competencias/', ResumenCompetenciasView.as_view(), name='tic_resumen_competencias'),
    
    path('detalles_competencias/', CompetenciasEvaluacionDetailView.as_view(), name='tic_detalles_competencias'),
    path('detalles_competencias/<int:id>/', CompetenciasEvaluacionDetailView.as_view(), name='tic_detalles_competencias_detail'),


]



