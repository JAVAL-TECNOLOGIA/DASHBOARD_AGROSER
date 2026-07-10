from django.urls import path
from .views import *
#from .views_api_reqinterno import ProcesarRequerimientoInternoAPI


urlpatterns = [
    

    path('almacen_presupuesto_dl/', presupuesto_dl.as_view(), name='almacen_presupuesto_dl'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('almacen_servicios_totals_dl/', Costo_servicio_totals, name='almacen_servicios_totals_dl'),
    path('almacen_servicios_dl/', Costo_Servicios_dlView.as_view(), name='almacen_servicios_dl'),
    path('almacen_servicios_dl/<int:id>/', Costo_Servicios_dlView.as_view(), name='almacen_servicios_dl_detail'),

    

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('almacen_capex_totals_dl/', Costos_capex_totals, name='almacen_capex_totals_dl'),

    path('almacen_capex/', CapexView.as_view(), name='almacen_capex'),
    path('almacen_capex/<int:id>/', CapexView.as_view(), name='almacen_capex_delete'),
    path('almacen_capex/<int:id>/', CapexView.as_view(), name='almacen_capex_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('almacen_suministros_totals_dl/', Costos_suministros_totals_dl, name='almacen_suministros_totals_dl'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('almacen_combustibles-lubricantes/', CombustiblesLubricantesView.as_view(), name='almacen_combustibles_lubricantes'),
    path('almacen_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='almacen_combustibles_lubricantes_delete'),
    path('almacen_combustibles-lubricantes/<int:id>/', CombustiblesLubricantesView.as_view(), name='almacen_combustibles_lubricantes_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('almacen_utiles-oficina/', UtilesOficinaView.as_view(), name='almacen_utiles_oficina'),
    path('almacen_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='almacen_utiles_oficina_delete'),
    path('almacen_utiles-oficina/<int:id>/', UtilesOficinaView.as_view(), name='almacen_utiles_oficina_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('almacen_equipos-computo/', EquiposComputoView.as_view(), name='almacen_equipos_computo'),
    path('almacen_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='almacen_equipos_computo_delete'),
    path('almacen_equipos-computo/<int:id>/', EquiposComputoView.as_view(), name='almacen_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('almacen_otros-suministros/', OtrosSuministrosView.as_view(), name='almacen_otros_suministros'),
    path('almacen_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='almacen_otros_suministros_delete'),   
    path('almacen_otros-suministros/<int:id>/', OtrosSuministrosView.as_view(), name='almacen_otros_suministros_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('almacen_material-construccion/', MaterialConstruccionView.as_view(), name='almacen_material_construccion'),
    path('almacen_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='almacen_material_construccion_delete'),
    path('almacen_material-construccion/<int:id>/', MaterialConstruccionView.as_view(), name='almacen_material_construccion_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('almacen_repuestos-accesorios/', RepuestosAccesoriosView.as_view(), name='almacen_repuestos_accesorios'),
    path('almacen_repuestos-accesorios/<int:id>/', RepuestosAccesoriosView.as_view(), name='almacen_repuestos_accesorios_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('almacen_equipos-uit/', EquiposUITView.as_view(), name='almacen_equipos_uit'),
    path('almacen_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='almacen_equipos_uit_delete'), 
    path('almacen_equipos-uit/<int:id>/', EquiposUITView.as_view(), name='almacen_equipos_uit_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('almacen_materiales-agricultura/', MaterialesAgriculturaView.as_view(), name='almacen_materiales_agricultura'),
    path('almacen_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='almacen_materiales_agricultura_delete'),
    path('almacen_materiales-agricultura/<int:id>/', MaterialesAgriculturaView.as_view(), name='almacen_materiales_agricultura_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('almacen_equipos-proteccion/', EquiposProteccionView.as_view(), name='almacen_equipos_proteccion'),
    path('almacen_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='almacen_equipos_proteccion_delete'),
    path('almacen_equipos-proteccion/<int:id>/', EquiposProteccionView.as_view(), name='almacen_equipos_proteccion_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('almacen_salarios_dl/', CostoSalariosView.as_view(), name='almacen_salarios_dl'),
    path('almacen_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='almacen_salarios_dl_delete'),
    path('almacen_salarios_dl/<int:id>/', CostoSalariosView.as_view(), name='almacen_salarios_dl_detail'),
    path('almacen_salario_mensual/', ApiMensualSalarios.as_view(), name='almacen_salario_mensual'),
    
    
    path('almacen_sueldos_dl/', CostoSueldosView.as_view(), name='almacen_sueldos_dl'),
    path('almacen_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='almacen_sueldos_dl_delete'),
    path('almacen_sueldos_dl/<int:id>/', CostoSueldosView.as_view(), name='almacen_sueldos_dl_detail'),
    path('almacen_sueldo_mensual/', ApiMensualSueldos.as_view(), name='almacen_sueldo_mensual'),




    #====================================================================================================================
    #EVALUACION DE DESEMPEÑO
    #====================================================================================================================

    path('almacen_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='almacen_evaluacion_desempeño'),



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
    # REQ. INTERNOS - DON LUIS
    #====================================================================================================================

    #template
    #path('almacen_req_interno_dl/', req_internos_dl.as_view(), name='almacen_req_interno_dl'),
    path('almacen_prueba/', req_internos_don_luis.as_view(), name='almacen_prueba'),

    #api
    path('api/req_interno_dl/', RequerimientosInternosView.as_view(), name='api/req_interno_dl'), 
    path('api/req_internoDetalle_dl/<str:idreqinterno>/', DetalleRequerimientoInternoAPI.as_view(), name='api/req_internoDetalle_dl'),
    # Agregar esta línea en tu urlpatterns
    path('api/stock_producto/<str:idproducto>/', ConsultaStockProductoAPI.as_view(), name='api_stock_producto'),

    
    #====================================================================================================================
    # REQ. INTERNOS - CAMPO VERDE
    #====================================================================================================================

    # #template

    path('almacen_prueba_cv/', req_internos_campo_verde.as_view(), name='almacen_prueba_cv'),

    # #api
    path('api/req_interno_cv/', RequerimientosInternosViewCV.as_view(), name='api/req_interno_cv'), 
    path('api/req_internoDetalle_cv/<str:idreqinterno>/', DetalleRequerimientoInternoAPICV.as_view(), name='api/req_internoDetalle_cv'),
    
    # # Agregar esta línea en tu urlpatterns
    path('api/stock_producto_cv/<str:idproducto>/', ConsultaStockProductoAPICV.as_view(), name='api_stock_producto_cv'),


    #====================================================================================================================
    # REQ. INTERNOS - INVERSIONES AJS
    #====================================================================================================================

    #template
    #path('almacen_req_interno_ajs/', req_internos_dl.as_view(), name='almacen_req_interno_ajs'),
    path('almacen_prueba_ajs/', req_internos_ajs.as_view(), name='almacen_prueba_ajs'),

    #api
    path('api/req_interno_ajs/', RequerimientosInternosViewAJS.as_view(), name='api/req_interno_ajs'), 
    path('api/req_internoDetalle_ajs/<str:idreqinterno>/', DetalleRequerimientoInternoAPIAJS.as_view(), name='api/req_internoDetalle_ajs'),
    # Agregar esta línea en tu urlpatterns
    path('api/stock_producto_ajs/<str:idproducto>/', ConsultaStockProductoAPIAJS.as_view(), name='api_stock_producto_ajs'),

    #====================================================================================================================
    # SALIDAS INTERNAS - DON LUIS
    #====================================================================================================================


    path('salida-interna/', SalidaInternaView.as_view(), name='salida_interna'),
    path('salida-interna/<str:id>/', SalidaInternaView.as_view(), name='salida_interna_detail'),
    path('salida-interna-procesar/', ProcesarSalidaInternaView.as_view(), name='salida_interna_procesar'),
    
    # API PARA LA BUSQUEDA DE REQUERIMIENTOS
    path('api/buscar_requerimiento/', BuscarRequerimientoInternoAPI.as_view(), name='api_buscar_requerimiento'),
    path('api/detalle-requerimiento/<str:idreqinterno>/', DetalleRequerimientoAPI.as_view(), name='api_detalle_requerimiento'),

    #Api para proceso de requerimientos
    path('api/procesar-requerimiento/', ProcesarRequerimientoInternoAPI.as_view(), name='api_procesar_requerimiento'),

    # API para responsables
    path('api/responsables/', ResponsablesAPI.as_view(), name='api_responsables'),

    # API para la consulta de stock de productos
    path('api/tcambio/', TipoCambioView.as_view(), name='api_tcambio'),

    # API para el documento de las salidas internas
    path('api/salida-interna/<str:id_salida>/', GetSalidaInternaDocument.as_view(), name='api_salida_interna_donluis'),

    #====================================================================================================================
    # SALIDAS INTERNAS - CAMPO VERDE
    #====================================================================================================================

    path('salida-interna-cv/', SalidaInternaViewCV.as_view(), name='salida_interna_cv'),
    path('salida-interna-cv/<str:id>/', SalidaInternaViewCV.as_view(), name='salida_interna_detail_cv'),
    path('salida-interna-procesar-cv/', ProcesarSalidaInternaViewCV.as_view(), name='salida_interna_procesar_cv'),
    
    # # API PARA LA BUSQUEDA DE REQUERIMIENTOS
    path('api/buscar_requerimiento-cv/', BuscarRequerimientoInternoAPICV.as_view(), name='api_buscar_requerimiento_cv'),
    path('api/detalle-requerimiento-cv/<str:idreqinterno>/', DetalleRequerimientoAPICV.as_view(), name='api_detalle_requerimiento_cv'),

    # #Api para proceso de requerimientos
    path('api/procesar-requerimiento-cv/', ProcesarRequerimientoInternoAPICV.as_view(), name='api_procesar_requerimiento_cv'),

    # # API para responsables
    path('api/responsables-cv/', ResponsablesAPICV.as_view(), name='api_responsables_cv'),

    # # API para la consulta de stock de productos
    path('api/tcambio-cv/', TipoCambioViewCV.as_view(), name='api_tcambio_cv'),

    # # API para el documento de las salidas internas
    path('api/salida-interna-cv/<str:id_salida>/', GetSalidaInternaDocumentCV.as_view(), name='api_salida_interna_campoverde_cv'),


    #====================================================================================================================
    # SALIDAS INTERNAS - INVERSIONES AJS
    #====================================================================================================================


    path('salida-interna-ajs/', SalidaInternaViewAJS.as_view(), name='salida_interna_ajs'),
    path('salida-interna-ajs/<str:id>/', SalidaInternaViewAJS.as_view(), name='salida_interna_detail_ajs'),
    path('salida-interna-procesar-ajs/', ProcesarSalidaInternaViewAJS.as_view(), name='salida_interna_procesar_ajs'),
    
    # API PARA LA BUSQUEDA DE REQUERIMIENTOS
    path('api/buscar_requerimiento-ajs/', BuscarRequerimientoInternoAPIAJS.as_view(), name='api_buscar_requerimiento-ajs'),
    path('api/detalle-requerimiento-ajs/<str:idreqinterno>/', DetalleRequerimientoAPIAJS.as_view(), name='api_detalle_requerimiento_ajs'),

    #Api para proceso de requerimientos
    path('api/procesar-requerimiento-ajs/', ProcesarRequerimientoInternoAPIAJS.as_view(), name='api_procesar_requerimiento_ajs'),

    # API para responsables
    path('api/responsables-ajs/', ResponsablesAPIAJS.as_view(), name='api_responsables_ajs'),

    # API para la consulta de stock de productos
    path('api/tcambio-ajs/', TipoCambioViewAJS.as_view(), name='api_tcambio_ajs'),

    # API para el documento de las salidas internas
    path('api/salida-interna-ajs/<str:id_salida>/', GetSalidaInternaDocumentAJS.as_view(), name='api_salida_interna_ajs'),

    
    #====================================================================================================================
    # ROTACION DE PRODUCTOS
    #====================================================================================================================

    path('almacen_rotacion_productos_dl/', rotacion_productos_dl.as_view(), name='almacen_rotacion_productos_dl'),

    # API PARA ROTACION DE PRODUCTOS
    path('api/rotacion_productos/', RotacionProductosView.as_view(), name='api_rotacion_productos'),


    path('consulta-salida-api/', ConsultaSalidaInternaAPI.as_view(), name='consulta_salida_api'),
   
   
    #====================================================================================================================
    # ROTACION DE PRODUCTOS - CAMPO VERDE
    #====================================================================================================================

    path('almacen_rotacion_productos_cv/', rotacion_productos_cv.as_view(), name='almacen_rotacion_productos_cv'),

    # # API PARA ROTACION DE PRODUCTOS
    path('api/rotacion_productos_cv/', RotacionProductosViewCV.as_view(), name='api_rotacion_productos_cv'),


    path('consulta-salida-api-cv/', ConsultaSalidaInternaAPICV.as_view(), name='consulta_salida_api_cv'),
   

    
    #====================================================================================================================
    # ROTACION DE PRODUCTOS - INVERSIONES AJS
    #====================================================================================================================

    path('almacen_rotacion_productos_ajs/', rotacion_productos_ajs.as_view(), name='almacen_rotacion_productos_ajs'),

    # # API PARA ROTACION DE PRODUCTOS
    path('api/rotacion_productos_ajs/', RotacionProductosViewAJS.as_view(), name='api_rotacion_productos_ajs'),


    path('consulta-salida-api-ajs/', ConsultaSalidaInternaAPIAJS.as_view(), name='consulta_salida_api_ajs'),
   
   
   #====================================================================================================================
    # REPORTE DE ALMACEN
    #====================================================================================================================
    path('almacen_reportes_dl/', ReportesView_dl.as_view(), name='almacen_reportes_dl'),
    
    
    #====================================================================================================================
    # REPORTE DE ALMACEN - CAMPO VERDE
    #====================================================================================================================
    path('almacen_reportes_cv/', ReportesView_cv.as_view(), name='almacen_reportes_cv'),


    #====================================================================================================================
    # REPORTE DE ALMACEN - INVERSIONES AJS
    #====================================================================================================================
    path('almacen_reportes_ajs/', ReportesView_ajs.as_view(), name='almacen_reportes_aj'),


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


    path('almacen_presupuesto_cv/', presupuesto_cv.as_view(), name='almacen_presupuesto_cv'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('almacen_servicios_totals_cv/', Costo_servicio_totals_cv, name='almacen_servicios_totals_cv'),
    path('almacen_servicios_cv/', Costo_Servicios_View_cv.as_view(), name='almacen_servicios_cv'),
    path('almacen_servicios_cv/<int:id>/', Costo_Servicios_View_cv.as_view(), name='almacen_servicios_cv_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('almacen_capex_totals_cv/', Costos_capex_totals_cv, name='almacen_capex_totals_cv'),

    path('almacen_capex_cv/', CapexView_cv.as_view(), name='almacen_capex_cv'),
    path('almacen_capex_cv/<int:id>/', CapexView_cv.as_view(), name='almacen_capex_cv_delete'),
    path('almacen_capex_cv/<int:id>/', CapexView_cv.as_view(), name='almacen_capex_cv_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('almacen_suministros_totals_cv/', Costos_suministros_totals_cv, name='almacen_suministros_totals_cv'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('almacen_combustibles-lubricantes_cv/', CombustiblesLubricantesView_cv.as_view(), name='almacen_combustibles_lubricantes_cv'),
    path('almacen_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='almacen_combustibles_lubricantes_cv_delete'),
    path('almacen_combustibles-lubricantes_cv/<int:id>/', CombustiblesLubricantesView_cv.as_view(), name='almacen_combustibles_lubricantes_cv_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('almacen_utiles-oficina_cv/', UtilesOficinaView_cv.as_view(), name='almacen_utiles_oficina_cv'),
    path('almacen_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='almacen_utiles_oficina_cv_delete'),
    path('almacen_utiles-oficina_cv/<int:id>/', UtilesOficinaView_cv.as_view(), name='almacen_utiles_oficina_cv_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('almacen_equipos-computo_cv/', EquiposComputoView_cv.as_view(), name='almacen_equipos_computo_cv'),
    path('almacen_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='almacen_equipos_computo_cv  _delete'),
    path('almacen_equipos-computo_cv/<int:id>/', EquiposComputoView_cv.as_view(), name='almacen_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('almacen_otros-suministros_cv/', OtrosSuministrosView_cv.as_view(), name='almacen_otros_suministros_cv'),
    path('almacen_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='almacen_otros_suministros_cv_delete'),   
    path('almacen_otros-suministros_cv/<int:id>/', OtrosSuministrosView_cv.as_view(), name='almacen_otros_suministros_cv_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('almacen_material-construccion_cv/', MaterialConstruccionView_cv.as_view(), name='almacen_material_construccion_cv'),
    path('almacen_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='almacen_material_construccion_cv_delete'),
    path('almacen_material-construccion_cv/<int:id>/', MaterialConstruccionView_cv.as_view(), name='almacen_material_construccion_cv_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('almacen_repuestos-accesorios_cv/', RepuestosAccesoriosView_cv.as_view(), name='almacen_repuestos_accesorios_cv'),
    path('almacen_repuestos-accesorios_cv/<int:id>/', RepuestosAccesoriosView_cv.as_view(), name='almacen_repuestos_accesorios_cv_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('almacen_equipos-uit_cv/', EquiposUITView_cv.as_view(), name='almacen_equipos_uit_cv'),
    path('almacen_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='almacen_equipos_uit_cv_delete'), 
    path('almacen_equipos-uit_cv/<int:id>/', EquiposUITView_cv.as_view(), name='almacen_equipos_uit_cv_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('almacen_materiales-agricultura_cv/', MaterialesAgriculturaView_cv.as_view(), name='almacen_materiales_agricultura_cv'),
    path('almacen_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='almacen_materiales_agricultura_cv_delete'),
    path('almacen_materiales-agricultura_cv/<int:id>/', MaterialesAgriculturaView_cv.as_view(), name='almacen_materiales_agricultura_cv_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('almacen_equipos-proteccion_cv/', EquiposProteccionView_cv.as_view(), name='almacen_equipos_proteccion_cv'),
    path('almacen_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='almacen_equipos_proteccion_cv_delete'),
    path('almacen_equipos-proteccion_cv/<int:id>/', EquiposProteccionView_cv.as_view(), name='almacen_equipos_proteccion_cv_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('almacen_salarios_cv/', CostoSalariosView_cv.as_view(), name='almacen_salarios_cv'),
    path('almacen_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='almacen_salarios_cv_delete'),
    path('almacen_salarios_cv/<int:id>/', CostoSalariosView_cv.as_view(), name='almacen_salarios_cv_detail'),
    path('almacen_salario_mensual_cv/', ApiMensualSalarios_cv.as_view(), name='almacen_salario_mensual_cv'),
    
    
    path('almacen_sueldos_cv/', CostoSueldosView_cv.as_view(), name='almacen_sueldos_cv'),
    path('almacen_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='almacen_sueldos_cv_delete'),
    path('almacen_sueldos_cv/<int:id>/', CostoSueldosView_cv.as_view(), name='almacen_sueldos_cv_detail'),
    path('almacen_sueldo_mensual_cv/', ApiMensualSueldos_cv.as_view(), name='almacen_sueldo_mensual_cv'),

    

    
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



    path('almacen_presupuesto_ajs/', presupuesto_ajs.as_view(), name='almacen_presupuesto_ajs'),

    #=============================================================================
    # SERVICIOS
    #=============================================================================
    path('almacen_servicios_totals_ajs/', Costo_servicio_totals_ajs, name='almacen_servicios_totals_ajs'),
    path('almacen_servicios_ajs/', Costo_Servicios_View_ajs.as_view(), name='almacen_servicios_ajs'),
    path('almacen_servicios_ajs/<int:id>/', Costo_Servicios_View_ajs.as_view(), name='almacen_servicios_ajs_detail'),

    #==============================================================================
    # CAPEX
    #==============================================================================

    path('almacen_capex_totals_ajs/', Costos_capex_totals_ajs, name='almacen_capex_totals_ajs'),

    path('almacen_capex_ajs/', CapexView_ajs.as_view(), name='almacen_capex_ajs'),
    path('almacen_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='almacen_capex_ajs_delete'),
    path('almacen_capex_ajs/<int:id>/', CapexView_ajs.as_view(), name='almacen_capex_ajs_detail'),

    #================================================
    # SUMINISTROS
    #================================================
    path('almacen_suministros_totals_ajs/', Costos_suministros_totals_ajs, name='almacen_suministros_totals_ajs'),

    #PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
    path('almacen_combustibles-lubricantes_ajs/', CombustiblesLubricantesView_ajs.as_view(), name='almacen_combustibles_lubricantes_ajs'),
    path('almacen_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='almacen_combustibles_lubricantes_ajs_delete'),
    path('almacen_combustibles-lubricantes_ajs/<int:id>/', CombustiblesLubricantesView_ajs.as_view(), name='almacen_combustibles_lubricantes_ajs_detail'),

    #PRESUPUESTO - UTILES DE OFICINA DE DON LUIS

    path('almacen_utiles-oficina_ajs/', UtilesOficinaView_ajs.as_view(), name='almacen_utiles_oficina_ajs'),
    path('almacen_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='almacen_utiles_oficina_ajs_delete'),
    path('almacen_utiles-oficina_ajs/<int:id>/', UtilesOficinaView_ajs.as_view(), name='almacen_utiles_oficina_ajs_detail'),

    #PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
    path('almacen_equipos-computo_ajs/', EquiposComputoView_ajs.as_view(), name='almacen_equipos_computo_ajs'),
    path('almacen_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='almacen_equipos_computo_ajs  _delete'),
    path('almacen_equipos-computo_ajs/<int:id>/', EquiposComputoView_ajs.as_view(), name='almacen_equipos_computo_detail'),
    
    #PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
    path('almacen_otros-suministros_ajs/', OtrosSuministrosView_ajs.as_view(), name='almacen_otros_suministros_ajs'),
    path('almacen_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='almacen_otros_suministros_ajs_delete'),   
    path('almacen_otros-suministros_ajs/<int:id>/', OtrosSuministrosView_ajs.as_view(), name='almacen_otros_suministros_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES DE CONSTRUCCION DE DON LUIS
    path('almacen_material-construccion_ajs/', MaterialConstruccionView_ajs.as_view(), name='almacen_material_construccion_ajs'),
    path('almacen_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='almacen_material_construccion_ajs_delete'),
    path('almacen_material-construccion_ajs/<int:id>/', MaterialConstruccionView_ajs.as_view(), name='almacen_material_construccion_ajs_detail'),
    
    #PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
    path('almacen_repuestos-accesorios_ajs/', RepuestosAccesoriosView_ajs.as_view(), name='almacen_repuestos_accesorios_ajs'),
    path('almacen_repuestos-accesorios_ajs/<int:id>/', RepuestosAccesoriosView_ajs.as_view(), name='almacen_repuestos_accesorios_ajs_delete'),

    #PRESUPUESTO - EQUIPOS DE UIT DE DON LUIS
    path('almacen_equipos-uit_ajs/', EquiposUITView_ajs.as_view(), name='almacen_equipos_uit_ajs'),
    path('almacen_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='almacen_equipos_uit_ajs_delete'), 
    path('almacen_equipos-uit_ajs/<int:id>/', EquiposUITView_ajs.as_view(), name='almacen_equipos_uit_ajs_detail'),
    
    #PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
    path('almacen_materiales-agricultura_ajs/', MaterialesAgriculturaView_ajs.as_view(), name='almacen_materiales_agricultura_ajs'),
    path('almacen_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='almacen_materiales_agricultura_ajs_delete'),
    path('almacen_materiales-agricultura_ajs/<int:id>/', MaterialesAgriculturaView_ajs.as_view(), name='almacen_materiales_agricultura_ajs_detail'),
    
    #PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
    path('almacen_equipos-proteccion_ajs/', EquiposProteccionView_ajs.as_view(), name='almacen_equipos_proteccion_ajs'),
    path('almacen_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='almacen_equipos_proteccion_ajs_delete'),
    path('almacen_equipos-proteccion_ajs/<int:id>/', EquiposProteccionView_ajs.as_view(), name='almacen_equipos_proteccion_ajs_detail'),

    #================================================
    # REMUNERACION
    #================================================
    path('almacen_salarios_ajs/', CostoSalariosView_ajs.as_view(), name='almacen_salarios_ajs'),
    path('almacen_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='almacen_salarios_ajs_delete'),
    path('almacen_salarios_ajs/<int:id>/', CostoSalariosView_ajs.as_view(), name='almacen_salarios_ajs_detail'),
    path('almacen_salario_mensual_ajs/', ApiMensualSalarios_ajs.as_view(), name='almacen_salario_mensual_ajs'),
    
    
    path('almacen_sueldos_ajs/', CostoSueldosView_ajs.as_view(), name='almacen_sueldos_ajs'),
    path('almacen_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='almacen_sueldos_ajs_delete'),
    path('almacen_sueldos_ajs/<int:id>/', CostoSueldosView_ajs.as_view(), name='almacen_sueldos_ajs_detail'),
    path('almacen_sueldo_mensual_ajs/', ApiMensualSueldos_ajs.as_view(), name='almacen_sueldo_mensual_ajs'),

    #====================================================================================================================
    # API para la fase FINAL de evaluaciones
    #====================================================================================================================
    
    path('api/fase-final/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluaciones'),
    path('api/fase-final/<int:id_evaluacion>/', FaseFinalEvaluacionesView.as_view(), name='fase_final_evaluacion_detalle'),
    
    #api para los detalles de la fase final
    path('api/detalles-evaluacion-final/', DetallesEvaluacionFinalModalView.as_view(), name='detalles_evaluacion_final_modal'),
    
    
    

]






