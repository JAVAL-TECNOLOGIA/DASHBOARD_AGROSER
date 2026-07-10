from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import OrderOCLogCMPA, OrderOCLogCMPAScript, \
    ApproveOrders, ApproveOrdersLog, ApproveOrdersLogFilter, ApproveOrdersLogDetailPurchase, \
    ApproveOrdersLogDetailService, ApproveOrdersAreas, \
    OrderOCLogcampoverde, OrderOCLogcampoverdeScript, OrderOCLogdonluis, OrderOCLogdonluisScript, \
    OrderOCLoginversioneajs, OrderOCLoginversioneajsScript, \
    OrderOSLogcampoverde, OrderOSLogcampoverdeScript, OrderOSLogdonluis, OrderOSLogcmpa, OrderOSLogcmpaScript, \
    OrderOSLogdonluisScript, OrderOSLoginversioneajs, OrderOSLoginversioneajsScript, \
    CreditNoteInvoice, CreditNoteInvoiceScript, ReporteFacturaPrueba, ReporteFacturaPruebaScript, OrderOCPedidodonluis, \
    OrderOCPedidodonluisScript, OrderOCPedidocampoverde, OrderOCPedidocampoverdeScript, \
    OrderOCPedidoinversionesajs, OrderOCPedidoinversionesajsScript, ReqInternoPartialView, UpdateOrdenServicio, Approvealmacen, \
    ApprovealmacenLog, ApproveAlmacenAreas, ApprovealmacenLogDetailPurchase, ApprovealmacenLogFilter, \
    UpdateOrdenalmacen, \
    Approvepservicios, ApprovePserviciosLogDetailService, ApprovepserviciosLogFilter, UpdateOrdenpservicios, \
    reqinternos, ReqInternoLogFilter, ReqInternoLogDetailPurchase, UpdateReqInternos, Approvecompras, \
    ApprovecomprasLogFilter, Approveservicios, ApproveServiciosLogFilter, UpdateOrdenCompra, fitosanidadLogFilter, \
    fitosanidad, reqinternosCV, ApproveAlmacenAreasCV, \
    ReqInternoLogFilterCV, ReqInternoLogDetailPurchaseCV, UpdateReqInternosCV, ApprovealmacenCV, \
    ApprovealmacenLogFilterCV, ApprovealmacenLogDetailPurchaseCV, UpdateOrdenalmacenCV, ApprovepserviciosCV, \
    ApprovepserviciosLogFilterCV, ApprovePserviciosLogDetailServiceCV, UpdateOrdenpserviciosCV, ApprovecomprasCV, \
    ApprovecomprasLogFilterCV, ApproveOrdersLogDetailPurchaseCV, \
    UpdateOrdenCompraCV, ApproveserviciosCV, ApproveServiciosLogFilterCV, ApproveOrdersLogDetailServiceCV, \
    UpdateOrdenServicioCV, reqinternosAJS, ApprovealmacenAJS, ApprovepserviciosAJS, ApprovecomprasAJS, \
    ApproveserviciosAJS, \
    ApproveAlmacenAreasAJS, ReqInternoLogFilterAJS, ReqInternoLogDetailPurchaseAJS, UpdateReqInternosAJS, \
    ApprovealmacenLogFilterAJS, ApprovealmacenLogDetailPurchaseAJS, ApprovepserviciosLogFilterAJS, \
    ApprovePserviciosLogDetailServiceAJS, \
    UpdateOrdenpserviciosAJS, ApprovecomprasLogFilterAJS, ApproveOrdersLogDetailPurchaseAJS, UpdateOrdenCompraAJS, \
    ApproveServiciosLogFilterAJS, ApproveOrdersLogDetailServiceAJS, UpdateOrdenServicioAJS, Updatefitosanidad, \
    Provision_donluis, Provision_donluisScript, ApproveOrdersLogDetailFitosanidad, \
    UpdatefitosanidadCV, fitosanidadLogFilterCV, ApproveOrdersLogDetailFitosanidadCV, fitosanidadCV, \
    Fitosanidad_almacen_nisira, Repo_nisira_almacen_campoverde_fito, Repo_nisira_almacen_inversionesAJS_fito, \
    Nisira_almacen_inversionesAJS_fito_Script, Nisira_almacen_campo_verde_fito_Script, \
    Nisira_almacen_don_luis_fito_Script, Provision_inversionesajs, Provision_Campo_verde, Provision_campoverdeScript, \
    Provision_inversionesajsScript, Space_calidad_poda, Space_calidad_raleo, Space_evaluaciones_fitosanitarias, \
    Space_evaluaciones_brotacion, \
    Space_evaluaciones_long_brote, Space_evaluaciones_long_racimo, Space_evaluaciones_cont_racimo, \
    Space_evaluaciones_floracion_cuaja, Space_evaluaciones_calibre_bayas, Recursos_humanos, Egp_funcion, \
    Egp_funcion_campoverde, Egp_funcion_inversionesajs, Libro_mayor_conta, Libro_mayor_conta_cv, Libro_mayor_conta_ajs, \
    Libro_mayor_conta_script, Libro_mayor_conta_cv_script, Libro_mayor_conta_ajs_script, UpdateOrdenalmacenAJS, \
    fitosanidadAJS, fitosanidadLogFilterAJS, ApproveOrdersLogDetailFitosanidadAJS, UpdatefitosanidadAJS, \
    AprobacionesDashboardDonLuis, AprobacionesDashboardAJS, AprobacionesDashboardCampoVerde, FitosanidadPartialView, \
    ReqInternoPartialView, PCompraPartialView,PServicioPartialView, OCompraPartialView, OServicioPartialView,\
    FitosanidadCVPartialView, ReqInternoCVPartialView, PCompraCVPartialView, PServicioCVPartialView, \
	OCompraCVPartialView, OServicioCVPartialView, FitosanidadAJSPartialView, ReqInternoAJSPartialView, \
	PCompraAJSPartialView, PServicioAJSPartialView, OCompraAJSPartialView, OServicioAJSPartialView

urlpatterns = [

    # ===============================
    # NUEVOS DASHBOARDS DE APROBACIONES
    # ===============================
    path('aprobaciones/donluis/', login_required(AprobacionesDashboardDonLuis.as_view()), name='aprobaciones_donluis'),
    path('aprobaciones/ajs/', login_required(AprobacionesDashboardAJS.as_view()), name='aprobaciones_ajs'),
    path('aprobaciones/campoverde/', login_required(AprobacionesDashboardCampoVerde.as_view()), name='aprobaciones_campoverde'),

    path('actualizar-orden-servicio/<str:idservicio>/', UpdateOrdenServicio.as_view(), name='actualizar-orden-servicio'),
    path('actualizar-orden-servicio_cv/<str:idservicio>/', UpdateOrdenServicioCV.as_view(), name='actualizar-orden-servicio_cv'),
    path('actualizar-orden-servicio_ajs/<str:idservicio>/', UpdateOrdenServicioAJS.as_view(), name='actualizar-orden-servicio_ajs'),
	
 	path('actualizar-orden-compra-cv/<str:idservicio>/', UpdateOrdenCompraCV.as_view(), name='actualizar-orden-compra-cv'),
	path('actualizar-orden-compra-ajs/<str:idservicio>/', UpdateOrdenCompraAJS.as_view(), name='actualizar-orden-compra-ajs'),

    path('actualizar-orden-almacen-cv/<str:idservicio>/', UpdateOrdenalmacenCV.as_view(), name='actualizar-orden-almacen-cv'),

    path('actualizar-orden-almacen-ajs/<str:idservicio>/', UpdateOrdenalmacenAJS.as_view(), name='actualizar-orden-almacen-ajs'),

	path('actualizar-orden-pservicios_cv/<str:idservicio>/', UpdateOrdenpserviciosCV.as_view(), name='actualizar-orden-pservicios_cv'),
    path('actualizar-req-interno-cv/<str:idservicio>/', UpdateReqInternosCV.as_view(), name='actualizar-req-interno-cv'),
    path('actualizar-req-interno-ajs/<str:idservicio>/', UpdateReqInternosAJS.as_view(), name='actualizar-req-interno-ajs'),
    path('actualizar-orden-pservicios_ajs/<str:idservicio>/', UpdateOrdenpserviciosAJS.as_view(), name='actualizar-orden-pservicios_ajs'),
   ##DONLUIS
    path('actualizar-orden-fitosanidad/<str:idservicio>/', Updatefitosanidad.as_view(), name='actualizar-orden-fitosanidad'),
   ## CAMPO VERDE
   	path('actualizar-orden-fitosanidad-CV/<str:idservicio>/', UpdatefitosanidadCV.as_view(), name='actualizar-orden-fitosanidad-CV'),
   ## INVERSIONES AJS
	path('actualizar-orden-fitosanidad-AJS/<str:idservicio>/', UpdatefitosanidadAJS.as_view(), name='actualizar-orden-fitosanidad-AJS'),
 
 
 	path('actualizar-orden-compra/<str:idservicio>/', UpdateOrdenCompra.as_view(), name='actualizar-orden-compra'),

    path('actualizar-orden-almacen/<str:idservicio>/', UpdateOrdenalmacen.as_view(), name='actualizar-orden-almacen'),
    path('actualizar-orden-pservicios/<str:idservicio>/', UpdateOrdenpservicios.as_view(), name='actualizar-orden-pservicios'),
	path('actualizar-req-interno/<str:idservicio>/', UpdateReqInternos.as_view(), name='actualizar-req-interno'),

 	path('approve_almacen/', Approvealmacen.as_view(), name='approve_almacen'),
   	path('approve_almacen_cv/', ApprovealmacenCV.as_view(), name='approve_almacen_cv'),
   	path('approve_almacen_ajs/', ApprovealmacenAJS.as_view(), name='approve_almacen_ajs'),

	path('approve_pservicios/', Approvepservicios.as_view(), name='approve_pservicios'),
	path('approve_pservicios_cv',ApprovepserviciosCV.as_view(),name='approve_pservicios_cv'),
 	path('approve_pservicios_ajs',ApprovepserviciosAJS.as_view(),name='approve_pservicios_ajs'),

	path('approve_orders/', ApproveOrders.as_view(), name='approve_orders'),
	path('approve_compras/', Approvecompras.as_view(), name='approve_compras'),
 	path('approve_compras_cv/', ApprovecomprasCV.as_view(), name='approve_compras_cv'),
 	path('approve_compras_ajs/', ApprovecomprasAJS.as_view(), name='approve_compras_ajs'),

 	path('approve_servicios/', Approveservicios.as_view(), name='approve_servicios'),
   	path('approve_servicios_cv/', ApproveserviciosCV.as_view(), name='approve_servicios_cv'),
   	path('approve_servicios_ajs/', ApproveserviciosAJS.as_view(), name='approve_servicios_ajs'),

	path('req_internos/', reqinternos.as_view(), name='req_internos'),
   	path('req_internos_cv/', reqinternosCV.as_view(), name='req_internos_cv'),
   	path('req_internos_ajs/', reqinternosAJS.as_view(), name='req_internos_ajs'),
	
	##DONLUIS
    path('fitosanidad/', fitosanidad.as_view(), name='fitosanidad'),
    # AGREGO YERSON
    path("fitosanidad/partial/", FitosanidadPartialView.as_view(), name="fitosanidad_partial"),
    path("req_internos/partial/", ReqInternoPartialView.as_view(), name="req_internos_partial"),
    path("ped_compras/partial/", login_required(PCompraPartialView.as_view()), name="ped_compras_partial"),
    path("ped_servicios/partial/", login_required(PServicioPartialView.as_view()), name="ped_servicios_partial"),
    path("ordenes_compras/partial/", login_required(OCompraPartialView.as_view()), name="ordenes_compras_partial"),
    path("ordenes_servicios/partial/", login_required(OServicioPartialView.as_view()), name="ordenes_servicios_partial"),
    
    # AGREGO YERSON - CAMPO VERDE
    path('fitosanidad_cv/', fitosanidadCV.as_view(), name='fitosanidad_cv'),
    path("fitosanidad_cv/partial/", FitosanidadCVPartialView.as_view(), name="fitosanidad_cv_partial"),
    path("req_internos_cv/partial/", ReqInternoCVPartialView.as_view(), name="req_internos_cv_partial"),
    path("ped_compras_cv/partial/", login_required(PCompraCVPartialView.as_view()), name="ped_compras_cv_partial"),
    path("ped_servicios_cv/partial/", login_required(PServicioCVPartialView.as_view()), name="ped_servicios_cv_partial"),
    path("ordenes_compras_cv/partial/", login_required(OCompraCVPartialView.as_view()), name="ordenes_compras_cv_partial"),
    path("ordenes_servicios_cv/partial/", login_required(OServicioCVPartialView.as_view()), name="ordenes_servicios_cv_partial"),
    
    # AGREGO YERSON - INVERSIONES AJS
    path('fitosanidad_ajs/', fitosanidadAJS.as_view(), name='fitosanidad_ajs'),
    path("fitosanidad_ajs/partial/", FitosanidadAJSPartialView.as_view(), name="fitosanidad_ajs_partial"),
    path("req_internos_ajs/partial/", ReqInternoAJSPartialView.as_view(), name="req_internos_ajs_partial"),
    path("ped_compras_ajs/partial/", login_required(PCompraAJSPartialView.as_view()), name="ped_compras_ajs_partial"),
    path("ped_servicios_ajs/partial/", login_required(PServicioAJSPartialView.as_view()), name="ped_servicios_ajs_partial"),
    path("ordenes_compras_ajs/partial/", login_required(OCompraAJSPartialView.as_view()), name="ordenes_compras_ajs_partial"),
    path("ordenes_servicios_ajs/partial/", login_required(OServicioAJSPartialView.as_view()), name="ordenes_servicios_ajs_partial"),
    
    # path("fitosanidad/partial/", fitosanidad.as_view(), name="fitosanidad_partial"),

    ##CAMPOVERDE
    path('fitosanidadCV/', fitosanidadCV.as_view(), name='fitosanidadCV'),
    ##INVERSIONESAJS
    
    #path('fitosanidadAJS/', fitosanidadAJS.as_view(), name='fitosanidadAJS'),

	##DONLUIS
 	path('fitosanidad_log_filter/<str:area>/', fitosanidadLogFilter.as_view(), name='fitosanidad_log_filter'),
	##CAMPOVERDE
    path('fitosanidad_log_filter_CV/<str:area>/', fitosanidadLogFilterCV.as_view(), name='fitosanidad_log_filter_CV'),
	##INVERSIONESAJS
 
    path('fitosanidad_log_filter_AJS/<str:area>/', fitosanidadLogFilterAJS.as_view(), name='fitosanidad_log_filter_AJS'),

 
	path('approve_orders_log/', ApproveOrdersLog.as_view(), name='approve_orders_log'),
 	path('approve_almacen_log/',  ApprovealmacenLog.as_view(), name='approve_almacen_log'),
	
	# ORDEN DE SERCICIO - CAMPOVERDE
	path('approve_servicios_log_filter_cv/<str:area>/', ApproveServiciosLogFilterCV.as_view(), name='approve_servicios_log_filter_cv'),
	path('approve_servicios_log_filter_cv/<str:area>/<str:estados>/', ApproveServiciosLogFilterCV.as_view(), name='approve_servicios_log_filter_cv'),
	
	#ORDEN DE SERVICIO - INVERSIONES AJS
	path('approve_servicios_log_filter_ajs/<str:area>/', ApproveServiciosLogFilterAJS.as_view(), name='approve_servicios_log_filter_ajs'),
	path('approve_servicios_log_filter_ajs/<str:area>/<str:estados>/', ApproveServiciosLogFilterAJS.as_view(), name='approve_servicios_log_filter_ajs'),

	#ORDEN DE SERVICIO - DONLUIS
	path('approve_servicios_log_filter/<str:area>/', ApproveServiciosLogFilter.as_view(), name='approve_servicios_log_filter'),
	path('approve_servicios_log_filter/<str:area>/<str:estados>/', ApproveServiciosLogFilter.as_view(), name='approve_servicios_log_filter'),
	
	# ORDEN DE COMPRA - DONLUIS
	path('approve_compras_log_filter/<str:area>/', ApprovecomprasLogFilter.as_view(), name='approve_compras_log_filter'),
	path('approve_compras_log_filter/<str:area>/<str:estados>/', ApprovecomprasLogFilter.as_view(), name='approve_compras_log_filter'),

	# ORDEN DE COMPRA - CAMPOVERDE#
	path('approve_compras_log_filter_cv/<str:area>/', ApprovecomprasLogFilterCV.as_view(), name='approve_compras_log_filter_cv'),
	path('approve_compras_log_filter_cv/<str:area>/<str:estados>/', ApprovecomprasLogFilterCV.as_view(), name='approve_compras_log_filter_cv'),
    
	# ORDEN DE COMPRA - INVERSIONES AJS
	path('approve_compras_log_filter_ajs/<str:area>/', ApprovecomprasLogFilterAJS.as_view(), name='approve_compras_log_filter_ajs'),
	path('approve_compras_log_filter_ajs/<str:area>/<str:estados>/', ApprovecomprasLogFilterAJS.as_view(), name='approve_compras_log_filter_ajs'),

	
	path('approve_orders_log_filter/<str:area>/', ApproveOrdersLogFilter.as_view(), name='approve_orders_log_filter'),
	path('approve_orders_log_detail_purchase/<str:idorder>/', ApproveOrdersLogDetailPurchase.as_view(), name='approve_orders_log_detail_purchase'),
	path('approve_orders_log_detail_purchase_cv/<str:idorder>/', ApproveOrdersLogDetailPurchaseCV.as_view(), name='approve_orders_log_detail_purchase_cv'),	
	path('approve_orders_log_detail_purchase_ajs/<str:idorder>/', ApproveOrdersLogDetailPurchaseAJS.as_view(), name='approve_orders_log_detail_purchase_ajs'),	

 	path('approve_orders_log_detail_service/<str:idorder>/', ApproveOrdersLogDetailService.as_view(), name='approve_orders_log_detail_service'),
 	path('approve_orders_log_detail_service_cv/<str:idorder>/', ApproveOrdersLogDetailServiceCV.as_view(), name='approve_orders_log_detail_service_cv'),
 	path('approve_orders_log_detail_service_ajs/<str:idorder>/', ApproveOrdersLogDetailServiceAJS.as_view(), name='approve_orders_log_detail_service_ajs'),
 	##DONLUIS
    path('approve_orders_log_detail_fitosanidad/<str:idorder>/', ApproveOrdersLogDetailFitosanidad.as_view(), name='approve_orders_log_detail_fitosanidad'),
	##CAMPVERDE
	path('approve_orders_log_detail_fitosanidad_CV/<str:idorder>/', ApproveOrdersLogDetailFitosanidadCV.as_view(), name='approve_orders_log_detail_fitosanidad_CV'),
	##INVERSIONESAJS
	path('approve_orders_log_detail_fitosanidad_AJS/<str:idorder>/', ApproveOrdersLogDetailFitosanidadAJS.as_view(), name='approve_orders_log_detail_fitosanidad_AJS'),

	path('approve_pservicios_log_detail_service/<str:idorder>/', ApprovePserviciosLogDetailService.as_view(), name='approve_pservicios_log_detail_service'),	
	path('approve_pservicios_log_detail_service_cv/<str:idorder>/', ApprovePserviciosLogDetailServiceCV.as_view(), name='approve_pservicios_log_detail_service_cv'),		
	path('approve_pservicios_log_detail_service_ajs/<str:idorder>/', ApprovePserviciosLogDetailServiceAJS.as_view(), name='approve_pservicios_log_detail_service_ajs'),		

  	path('approve_orders_areas', ApproveOrdersAreas.as_view(), name='approve_orders_areas'),
 	path('approve_almacen_areas', ApproveAlmacenAreas.as_view(), name='approve_almacen_areas'),
   	path('approve_almacen_areas_cv', ApproveAlmacenAreasCV.as_view(), name='approve_almacen_areas_cv'),
   	path('approve_almacen_areas_ajs', ApproveAlmacenAreasAJS.as_view(), name='approve_almacen_areas_ajs'),

	path('approve_almacen_log_detail_purchase/<str:idorder>/', ApprovealmacenLogDetailPurchase.as_view(), name='approve_almacen_log_detail_purchase'),
	path('approve_almacen_log_detail_purchase_cv/<str:idorder>/', ApprovealmacenLogDetailPurchaseCV.as_view(), name='approve_almacen_log_detail_purchase_cv'),
	path('approve_almacen_log_detail_purchase_ajs/<str:idorder>/', ApprovealmacenLogDetailPurchaseAJS.as_view(), name='approve_almacen_log_detail_purchase_ajs'),

	path('req_interno_log_detail_purchase/<str:idorder>/', ReqInternoLogDetailPurchase.as_view(), name='approve_almacen_log_detail_purchase'),
 	path('req_interno_log_detail_purchase_cv/<str:idorder>/', ReqInternoLogDetailPurchaseCV.as_view(), name='req_interno_log_detail_purchase_cv'),
 	path('req_interno_log_detail_purchase_ajs/<str:idorder>/', ReqInternoLogDetailPurchaseAJS.as_view(), name='req_interno_log_detail_purchase_ajs'),

  	path('approve_almacen_log_filter/<str:area>/', ApprovealmacenLogFilter.as_view(), name='approve_orders_log_filter'),
	path('approve_almacen_log_filter_cv/<str:area>/', ApprovealmacenLogFilterCV.as_view(), name='approve_orders_log_filter_cv'),
	path('approve_almacen_log_filter_ajs/<str:area>/', ApprovealmacenLogFilterAJS.as_view(), name='approve_orders_log_filter_ajs'),

 	path('approve_pservicios_log_filter/<str:area>/', ApprovepserviciosLogFilter.as_view(), name='approve_pservicios_log_filter'),
 	path('approve_pservicios_log_filter/<str:area>/<str:estados>/', ApprovepserviciosLogFilter.as_view(), name='approve_pservicios_log_filter_with_estados'),
 	

	path('approve_pservicios_log_filter_cv/<str:area>/', ApprovepserviciosLogFilterCV.as_view(), name='approve_pservicios_log_filter_cv'),	
 	path('approve_pservicios_log_filter_cv/<str:area>/<str:estados>/', ApprovepserviciosLogFilterCV.as_view(), name='approve_pservicios_log_filter_cv'),	
 	
	
	
	
	path('approve_pservicios_log_filter_ajs/<str:area>/', ApprovepserviciosLogFilterAJS.as_view(), name='approve_pservicios_log_filter_ajs'),	
 	path('approve_pservicios_log_filter_ajs/<str:area>/<str:estados>/', ApprovepserviciosLogFilterAJS.as_view(), name='approve_pservicios_log_filter_ajs'),

	path('req_interno_log_filter/<str:area>/', ReqInternoLogFilter.as_view(), name='req_interno_log_filter'),
	path('req_interno_log_filter_cv/<str:area>/', ReqInternoLogFilterCV.as_view(), name='req_interno_log_filter_cv'),
	path('req_interno_log_filter_ajs/<str:area>/', ReqInternoLogFilterAJS.as_view(), name='req_interno_log_filter_ajs'),

  	path('order_oc_log_campoverde/', OrderOCLogcampoverde.as_view(), name='order_oc_log_campoverde'),
	path('order_oc_log_campoverde_script/', OrderOCLogcampoverdeScript.as_view(), name='order_oc_log_campoverde_script'),
	path('order_oc_log_donluis/', OrderOCLogdonluis.as_view(), name='order_oc_log_donluis'),
    

    ############################################### CONTABILIDAD ###############################################
	#CONTABILILDAD PROVISION JHON GUTIERREZ
	path('provision_donluis/', Provision_donluis.as_view(), name='provision_donluis'),
    path('provision_campo_verde/', Provision_Campo_verde.as_view(), name='provision_campo_verde'),
    path('provision_inversionesajs/', Provision_inversionesajs.as_view(), name='provision_inversionesajs'),

	#CONTABILILDAD EGP POR FUNCION JHON GUTIERREZ
    
	path('egp_funcion/', Egp_funcion.as_view(), name='egp_funcion'),
    path('egp_funcion_campoverde/', Egp_funcion_campoverde.as_view(), name='egp_funcion_campoverde'),
    path('egp_funcion_inversionesajs/', Egp_funcion_inversionesajs.as_view(), name='egp_funcion_inversionesajs'),
	
 	path('reporte_factura_prueba/', ReporteFacturaPrueba.as_view(), name='reporte_factura_prueba'),
	path('reporte_factura_prueba_script/', ReporteFacturaPruebaScript.as_view(), name='reporte_factura_prueba_script'),
	path('order_oc_log_donluis_script/', OrderOCLogdonluisScript.as_view(), name='order_oc_log_donluis_script'),
	path('order_oc_log_inversioneajs/', OrderOCLoginversioneajs.as_view(), name='order_oc_log_inversioneajs'),
	
	#CONTABILIDAD PROVISION JHON GUTIERREZ
	path('provisison_donluis_script/', Provision_donluisScript.as_view(), name='provisison_donluis_script'),
	path('provisison_campoverde_script/', Provision_campoverdeScript.as_view(), name='provisison_campoverde_script'),
    path('provisison_inversionesajs_script/', Provision_inversionesajsScript.as_view(), name='provisison_inversionesajs_script'),

	#CONTABILIDAD --LIBRO MAYOR-- JHON GUTIERREZ

	path('libro_mayor_conta/', Libro_mayor_conta.as_view(), name='libro_mayor_conta'),
    path('libro_mayor_conta_script/', Libro_mayor_conta_script.as_view(), name='libro_mayor_conta_script'),

	path('libro_mayor_conta_cv/', Libro_mayor_conta_cv.as_view(), name='libro_mayor_conta_cv'),
    path('libro_mayor_conta_script_cv/', Libro_mayor_conta_cv_script.as_view(), name='libro_mayor_conta_script_cv'),
    

	path('libro_mayor_conta_ajs/', Libro_mayor_conta_ajs.as_view(), name='libro_mayor_conta_ajs'),
    path('libro_mayor_conta_script_ajs/', Libro_mayor_conta_ajs_script.as_view(), name='libro_mayor_conta_script_ajs'),
    

	







 	path('order_oc_log_inversioneajs_script/', OrderOCLoginversioneajsScript.as_view(), name='order_oc_log_inversioneajs_script'),
	path('order_oc_log_cmpa/', OrderOCLogCMPA.as_view(), name='order_oc_log_cmpa'),
	path('order_oc_log_cmpa_script/', OrderOCLogCMPAScript.as_view(), name='order_oc_log_cmpa_script'),

	path('order_os_log_campoverde/', OrderOSLogcampoverde.as_view(), name='order_os_log_campoverde'),
	path('order_os_log_campoverde_script/', OrderOSLogcampoverdeScript.as_view(), name='order_os_log_campoverde_script'),
	path('order_os_log_donluis/', OrderOSLogdonluis.as_view(), name='order_os_log_donluis'),
	path('order_os_log_donluis_script/', OrderOSLogdonluisScript.as_view(), name='order_os_log_donluis_script'),
	path('order_os_log_inversioneajs/', OrderOSLoginversioneajs.as_view(), name='order_os_log_inversioneajs'),
	path('order_os_log_inversioneajs_script/', OrderOSLoginversioneajsScript.as_view(), name='order_os_log_inversioneajs_script'),
	path('order_os_log_cmpa/', OrderOSLogcmpa.as_view(), name='order_os_log_cmpa'),
	path('order_os_log_cmpa_script/', OrderOSLogcmpaScript.as_view(), name='order_os_log_cmpa_script'),

	path('credit_note_invoice/', CreditNoteInvoice.as_view(), name='credit_note_invoice'),
	path('credit_note_invoice_script/', CreditNoteInvoiceScript.as_view(), name='credit_note_invoice_script'),

	path('order_oc_pedido_donluis/', OrderOCPedidodonluis.as_view(), name='order_oc_pedido_donluis'),
	path('order_oc_pedido_donluis_script/', OrderOCPedidodonluisScript.as_view(), name='order_oc_pedido_donluis_script'),

 	path('order_oc_pedido_campoverde/', OrderOCPedidocampoverde.as_view(), name='order_oc_pedido_campoverde'),
	path('order_oc_pedido_campoverde_script/', OrderOCPedidocampoverdeScript.as_view(), name='order_oc_pedido_campoverde_script'),

 	path('order_oc_pedido_inversionesajs/', OrderOCPedidoinversionesajs.as_view(), name='order_oc_pedido_inversionesajs'),
	path('order_oc_pedido_inversionesajs_script/', OrderOCPedidoinversionesajsScript.as_view(), name='order_oc_pedido_inversionesajs_script'),
    
	# ALMACEN_FITOSANIDAD JHON GUTIERREZ
	path('fitosanidad_almacen_nisira/', Fitosanidad_almacen_nisira.as_view() , name='fitosanidad_almacen_nisira'),
	path('campoverde_fitosanidad_almacen_nisira/', Repo_nisira_almacen_campoverde_fito.as_view() , name='campoverde_fitosanidad_almacen_nisira'),
    path('inversiones_fitosanidad_almacen_nisira/', Repo_nisira_almacen_inversionesAJS_fito.as_view() , name='inversiones_fitosanidad_almacen_nisira'),
    
	#ALMACEN_FITOSANIDAD JHON GUTIERREZ#
	path('nisira_almacen_inversionesAJS_fito_Script/', Nisira_almacen_inversionesAJS_fito_Script.as_view(), name='nisira_almacen_inversionesAJS_fito_Script'),
    path('nisira_almacen_campo_verde_fito_Script/', Nisira_almacen_campo_verde_fito_Script.as_view(), name='nisira_almacen_campo_verde_fito_Script'),
	path('nisira_almacen_don_luis_fito_Script/', Nisira_almacen_don_luis_fito_Script.as_view(), name='nisira_almacen_don_luis_fito_Script'),
    
	# SPACE JHON GUTIERREZ
    path('space_calidad_poda/', Space_calidad_poda.as_view(), name='space_calidad_poda'),
    path('space_calidad_raleo/', Space_calidad_raleo.as_view(), name='space_calidad_raleo'),
    path('space_evaluaciones_fitosanitarias/', Space_evaluaciones_fitosanitarias.as_view(), name='space_evaluaciones_fitosanitarias'),
    path('space_evaluaciones_brotacion/', Space_evaluaciones_brotacion.as_view(), name='space_evaluaciones_brotacion'),
    path('space_evaluaciones_long_brote/', Space_evaluaciones_long_brote.as_view(), name='space_evaluaciones_long_brote'),
    path('space_evaluaciones_long_racimo/', Space_evaluaciones_long_racimo.as_view(), name='space_evaluaciones_long_racimo'),
	path('space_evaluaciones_cont_racimo/', Space_evaluaciones_cont_racimo.as_view(), name='space_evaluaciones_cont_racimo'),
    path('space_evaluaciones_floracion_cuaja/', Space_evaluaciones_floracion_cuaja.as_view(), name='space_evaluaciones_floracion_cuaja'),
    path('space_evaluaciones_calibre_bayas/', Space_evaluaciones_calibre_bayas.as_view(), name='space_evaluaciones_calibre_bayas'),
    

	################ COSTOS JHON GUTIERREZ   ################
    
	#DISTRIBUCION COSTOS  DON LUIS
    
]	