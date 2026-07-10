from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import View, TemplateView
from apps.connection.connect_donluis import connection_donluis
from apps.connection.connect_campoverde import connection_campoverde
from apps.connection.connect_inversioneajs import connection_inversioneajs
from apps.connection.connect_donluis_prueba import connection_donluis_prueba
from django.db import DatabaseError
import logging
import json
from apps.user.models import User




#PermissionRequiredMixin, Vistas HTML
class ApproveOrders(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_orders.html'
class Approvecompras(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_compras.html'

class Approveservicios(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_servicios.html'


class Approvealmacen(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_almacen.html'

class Approvepservicios(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/Pedido_servicios/approve_Pservicios.html'

class reqinternos(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/req_interno.html'
    
    
class fitosanidad(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_fitosanidad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Don Luis'
        context['tabs_aprobaciones'] = [
            {'nombre': 'Fitosanidad', 'url': 'fitosanidad', 'active': True},
            {'nombre': 'Requerimientos', 'url': 'req_internos', 'active': True},
            {'nombre': 'Pedidos de Compras', 'url': 'approve_almacen', 'active': True},
            {'nombre': 'Pedidos de Servicios', 'url': 'approve_pservicios', 'active': False},
            {'nombre': 'Ordenes de Compras', 'url': 'approve_compras', 'active': False},
            {'nombre': 'Ordenes de Servicios', 'url': 'approve_servicios', 'active': False},
        ]
        return context

class FitosanidadPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_fitosanidad_partial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Don Luis'
        return context

## AGREGO YERSON
class ReqInternoPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_req_interno_partial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Don Luis'
        return context

class PCompraPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_pcompras_partial.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Don Luis'
         return context

class PServicioPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_pservicios_partial.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Don Luis'
         return context

class OCompraPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_ocompras_partial.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Don Luis'
         return context

class OServicioPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_oservicios_partial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Don Luis'
        return context

## AGREGO YERSON - CAMPO VERDE

class fitosanidadCV(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_fitosanidad_cv.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Campo Verde'
        context['tabs_aprobaciones'] = [
            {'nombre': 'Fitosanidad CV', 'url': 'fitosanidad_cv', 'active': True},
            {'nombre': 'Requerimientos CV', 'url': 'req_internos_cv', 'active': False},
            {'nombre': 'Pedidos de Compras CV', 'url': 'approve_almacen_cv', 'active': False},
            {'nombre': 'Pedidos de Servicios CV', 'url': 'approve_pservicios_cv', 'active': False},
            {'nombre': 'Ordenes de Compras CV', 'url': 'approve_compras_cv', 'active': False},
            {'nombre': 'Ordenes de Servicios CV', 'url': 'approve_servicios_cv', 'active': False},
        ]
        return context

class FitosanidadCVPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_fitosanidad_partial_cv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Campo Verde'
        return context

class ReqInternoCVPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_req_interno_partial_cv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Campo Verde'
        return context

class PCompraCVPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_pcompras_partial_cv.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Campo Verde'
         return context

class PServicioCVPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_pservicios_partial_cv.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Campo Verde'
         return context

class OCompraCVPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_ocompras_partial_cv.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Campo Verde'
         return context

class OServicioCVPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_oservicios_partial_cv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Campo Verde'
        return context

## AGREGO YERSON - INVERSIONES AJS
class fitosanidadAJS(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_fitosanidad_ajs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Inversiones AJS'
        context['tabs_aprobaciones'] = [
            {'nombre': 'Fitosanidad AJS', 'url': 'fitosanidad_ajs', 'active': True},
            {'nombre': 'Requerimientos AJS', 'url': 'req_internos_ajs', 'active': False},
            {'nombre': 'Pedidos de Compras AJS', 'url': 'approve_almacen_ajs', 'active': False},
            {'nombre': 'Pedidos de Servicios AJS', 'url': 'approve_pservicios_ajs', 'active': False},
            {'nombre': 'Ordenes de Compras AJS', 'url': 'approve_compras_ajs', 'active': False},
            {'nombre': 'Ordenes de Servicios AJS', 'url': 'approve_servicios_ajs', 'active': False},
        ]
        return context

class FitosanidadAJSPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_fitosanidad_partial_ajs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Inversiones AJS'
        return context

class ReqInternoAJSPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_req_interno_partial_ajs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Don Luis'
        return context

class PCompraAJSPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_pcompras_partial_ajs.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Inversiones AJS'
         return context

class PServicioAJSPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_pservicios_partial_ajs.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Inversiones AJS'
         return context

class OCompraAJSPartialView(PermissionRequiredMixin, TemplateView):
     permission_required = 'user.aei_approve_orders'
     template_name = 'script/partials/approve_ocompras_partial_ajs.html'

     def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context['empresa_nombre'] = 'Inversiones AJS'
         return context

class OServicioAJSPartialView(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/partials/approve_oservicios_partial_ajs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa_nombre'] = 'Inversiones AJS'
        return context

############ Campo Verde ################
class reqinternosCV(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/req_interno_CV.html'

class ApprovealmacenCV(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_almacen_cv.html'


    
class ApprovepserviciosCV(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_Pservicios_cv.html'

# class fitosanidadCV(TemplateView):
#     permission_required = 'user.aei_approve_orders'
#     template_name = 'script/approve_fitosanidad_cv.html'

# class fitosanidadAJS(TemplateView):
#     permission_required = 'user.aei_approve_orders'
#     template_name = 'script/approve_fitosanidad_ajs.html'

class ApprovecomprasCV(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_compras_Cv.html'
class ApproveserviciosCV(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_servicios_cv.html'
##############INVERSIONES AJS 

class reqinternosAJS(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/req_interno_AJS.html'
class ApprovealmacenAJS(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_almacen_ajs.html'


class ApprovepserviciosAJS(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_Pservicios_ajs.html'


class ApprovecomprasAJS(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_compras_ajs.html'
class ApproveserviciosAJS(TemplateView):
    permission_required = 'user.aei_approve_orders'
    template_name = 'script/approve_servicios_ajs.html'



###################### PEDIDO ALMACEN #################################################
class ApprovealmacenLog(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("SELECT row_number() OVER (ORDER BY fdate) n,* FROM VIEW_RETURN_APPROVE_almacen ORDER BY fdate DESC")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'item':data[0],'idorden':data[1],'sucursal':data[2],'documento':data[3],'num_documento':data[4], 'fecha':data[5], 'moneda':data[6],'total':data[7],'estado':data[8],'area':data[9]})
        return JsonResponse(data_json, safe=False)


######################## ORDEN DE COMPRA Y SERVICIO ########################################
class ApproveOrdersLog(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("SELECT row_number() OVER (ORDER BY fdate) n,* FROM VIEW_RETURN_APPROVE_ORDERS ORDER BY fdate DESC")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'item':data[0],'idorden':data[1],'sucursal':data[2],'documento':data[3],'num_documento':data[4], 'fecha':data[5], 'moneda':data[6],'total':data[7],'proveedor':data[8],'estado':data[9],'area':data[10]})
        return JsonResponse(data_json, safe=False)
########################DON LUIS###################################################
class ApproveAlmacenAreas(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("select TRIM(IDAREA),  DESCRIPCION as AREA from AREAS ORDER BY DESCRIPCION")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idarea':data[0],'descripcion':data[1]})
        return JsonResponse(data_json, safe=False)


###################################################################################
##############CAMPO VERDE########################################
class ApproveAlmacenAreasCV(View):

    def get(self, request, *args, **kwargs):

        with connection_campoverde.cursor() as cursor:
            cursor.execute("select TRIM(IDAREA),  DESCRIPCION as AREA from AREAS ORDER BY DESCRIPCION")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idarea':data[0],'descripcion':data[1]})
        return JsonResponse(data_json, safe=False)
    #############################FILTRO DE LOS PENDIENTES ###############
class ReqInternoLogFilterCV(View):
    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_campoverde.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_REQUERIMIENTO_MEJORA '"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'item':data[0],'idorden':data[1],'sucursal':data[2],'documento':data[3],'num_documento':data[4], 'fecha':data[5], 'total':data[6],'estado':data[7],'areas':data[8],'fecha2':data[9],'almacen':data[10],'idarea':data[11],'observacion':data[12],'PRODUCTO':data[13],'IDCONSUMIDOR':data[14],'cantidad':data[15],'idmedida':data[16]})
        return JsonResponse(data_json, safe=False)
########################## DETALLE REQUERIMIENTO ###########
class ReqInternoLogDetailPurchaseCV(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_campoverde.cursor() as cursor:
            cursor.execute("select DR.IDREQINTERNO,DR.IDPRODUCTO,DR.DESCRIPCION,DR.IDMEDIDA,DR.ITEM,DR.CANTIDAD,DR.CANTAPROBADA,DR.IDCONSUMIDOR,RE.NOMBRE from   dREQINTERNO  AS DR INNER JOIN REQINTERNO AS R ON R.IDREQINTERNO=DR.IDREQINTERNO INNER JOIN RESPONSABLE AS RE ON R.IDRESPONSABLE=RE.IDRESPONSABLE WHERE DR.IDREQINTERNO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[4],'producto':data[2],'idmedida':data[3], 'cantidad':data[5],'consumidor':data[7],'responsable':data[8]})
        return JsonResponse(data_json, safe=False)
#################APROBACIÓN REQUERIMIENTO CV ##################



class UpdateReqInternosCV(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return HttpResponse("ID de servicio no válido", status=400)

            # Utilizar la conexión existente
            with connection_campoverde.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='AP' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='AP' WHERE IDREQINTERNO='{idservicio}'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='V1' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='V1' WHERE IDREQINTERNO='{idservicio}'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='AN' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='AN' WHERE IDREQINTERNO='{idservicio}'")
                
                # Confirmar la transacción
                connection_campoverde.commit()
                print(f"✅ Transacción confirmada para ID: {idservicio}")

            return JsonResponse({
                "success": True,
                "message": f"El requerimiento interno con ID {idservicio} ha sido actualizado correctamente.",
                "idservicio": idservicio,
                "accion": accion
            })
        except DatabaseError as e:
            # Registra el error
            print(f"❌ Error en la base de datos: {str(e)}")
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos: " + str(e)}, status=500)
        except Exception as e:
            # Registra el error
            print(f"❌ Error inesperado: {str(e)}")
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado: " + str(e)}, status=500)


      
################# PEDIDOS DE ALMACEN ####
class ApprovealmacenLogFilterCV(View):

    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_campoverde.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_almacen_mejora '"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({
                'item':data[0],
                'idorden':data[1],
                'sucursal':data[2],
                'documento':data[3],
                'num_documento':data[4], 
                'fecha':data[5], 
                'moneda':data[6],
                'total':data[7],
                'estado':data[8],
                'area':data[9],
                'nota':data[10],
                'almacen':data[11],
                'idarea':data[12],
                'descripcion':data[13],
                'idconsumidor':data[14],
                'consumidor_descripcion':data[15],
                'cantidad':data[16],
                'idmedida':data[17]
            })
        return JsonResponse(data_json, safe=False)
    
##################### DETALLE PEDIDO ALMACEN JHON GUTIERREZ
class ApprovealmacenLogDetailPurchaseCV(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_campoverde.cursor() as cursor:
            cursor.execute("select DP.idpedido, DP.idproducto, DP.descripcion, DP.idmedida, DP.cantidad,RE.NOMBRE, A.DESCRIPCION AS area,E.DESCRIPCION AS estado, P.nota as observacion from DPEDIDO DP INNER JOIN PEDIDO P ON P.IDPEDIDO=DP.IDPEDIDO INNER JOIN RESPONSABLE RE ON P.IDRESPONSABLE=RE.IDRESPONSABLE INNER JOIN AREAS A ON P.IDAREA = A.IDAREA INNER JOIN ESTADOS E ON P.IDESTADO = E.IDESTADO  where DP.IDPEDIDO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'responsable':data[5],'area':data[6],'estado':data[7],'observacion':data[8]})
        return JsonResponse(data_json, safe=False)
    
##########ACTUALIZAR ORDEN ALMACEN

class UpdateOrdenalmacenCV(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_campoverde.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update PEDIDO SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where IDPEDIDO='"+idservicio+"'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE PEDIDO SET IDESTADO='V1' where IDPEDIDO='"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE PEDIDO SET IDESTADO='AN'where IDPEDIDO='"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
        #################### PEDIDOS DE SERVICIOS



class ApprovepserviciosLogFilterCV(View):

    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovepserviciosLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_campoverde.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_PSERVICIOS_PRUEBA ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'estado': data[8],
                'area': data[9],
                'servicio_descripcion': data[13],
                'idconsumidor': data[14],
                'consumidor_descripcion': data[15],
                'observaciones': data[16]
            })
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            # Filtrar los datos por los estados especificados
            data_json = [item for item in data_json if item['estado'] in estados_list]
            print(f"🔍 Datos filtrados por estados {estados_list}: {len(data_json)} registros")
        
        print(f"🔍 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)




class ApprovePserviciosLogDetailServiceCV(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_campoverde.cursor() as cursor:
            cursor.execute("select DP.idpedido, DP.idproducto, DP.descripcion, DP.idmedida, DP.cantidad,RE.NOMBRE, p.OBSERVACIONES,  MON.DESCRIPCION as moneda, DP.precioservicio as precio, DP.TOTAL as total, P.TOTAL as sumaTotal,E.DESCRIPCION AS ESTADO ,A.DESCRIPCION AS AREA, DP.IDCONSUMIDOR from DPEDIDOSERVICIOS DP INNER JOIN PEDIDOSERVICIOS P ON P.IDPEDIDO=DP.IDPEDIDO INNER JOIN RESPONSABLE RE ON P.IDRESPONSABLE=RE.IDRESPONSABLE INNER JOIN MONEDAS MON ON P.IDMONEDA = MON.IDMONEDA INNER JOIN AREAS A ON P.IDAREA = A.IDAREA INNER JOIN ESTADOS E ON P.IDESTADO = E.IDESTADO where DP.IDPEDIDO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:    
            data_json.append({'idpedido':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'responsable':data[5],'observacion':data[6],'moneda':data[7],'precio':data[8],'total':data[9],'sumaTotal':data[10],'estado':data[11],'area':data[12],'consumidor':data[13]})
        return JsonResponse(data_json, safe=False)
##################### ACTUALIZAR PEDIDO SERVICIOS CV ##########

class UpdateOrdenpserviciosCV(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return JsonResponse({"error": "Acción no válida"}, status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return JsonResponse({"error": "ID de servicio no proporcionado"}, status=400)

            # Utilizar la conexión existente con parámetros seguros
            with connection_campoverde.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='AP', 
                            nrsidusuario_ap=?, 
                            nsrfecha_ap=GETDATE() 
                        WHERE IDPEDIDO=?
                    """, [portal_aei_user.username, idservicio])
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='V1' 
                        WHERE IDPEDIDO=?
                    """, [idservicio])
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='AN' 
                        WHERE IDPEDIDO=?
                    """, [idservicio])

                # Verificar si se actualizó algún registro
                if cursor.rowcount == 0:
                    return JsonResponse({"error": "No se encontró el pedido de servicio"}, status=404)

            return JsonResponse({
                "success": True, 
                "message": f"El servicio con ID {idservicio} ha sido actualizado correctamente.",
                "idservicio": idservicio,
                "accion": accion
            })
            
        except User.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=401)
        except DatabaseError as e:
            # Registra el error
            import logging
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos"}, status=500)
        except Exception as e:
            # Registra el error
            import logging
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado en el servidor"}, status=500)
   




############################### ORDEN DE COMPRAS 



class ApprovecomprasLogFilter(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovecomprasLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_campoverde.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_compras ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11] if len(data) > 11 else '',
                'idconsumidor': data[12] if len(data) > 12 else ''
            })
        
        print(f"📊 Total registros obtenidos de SP: {len(data_json)}")
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            print(f"📋 Estados solicitados: {estados_list}")
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            print(f"🔄 Estados convertidos para BD: {estados_bd}")
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            print(f"✂️ Filtrado: {data_json_original} -> {len(data_json)} registros")
            
        print(f"📤 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)




########################## DETALLE ORDEN COMPRA
class ApproveOrdersLogDetailPurchaseCV(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_campoverde.cursor() as cursor:
            
            cursor.execute("select doc.idcompra, doc.idproducto,	doc.descripcion, doc.idmedida, doc.cantidad, doc.item, doc.precio_unitario, doc.impuesto, doc.subtotalsindscto, doc.subtotalcondscto, doc.total, cl.RAZON_SOCIAL, cl.RUC, fp.DESCRIPCION, rp.nombre, oc.total, MON.descripcion as moneda, E.DESCRIPCION, CONCAT(OC.serie,' - ', OC.numero) AS SerieNumero, A.DESCRIPCION as area from DORDENCOMPRA doc inner join ORDENCOMPRA OC on oc.idcompra = doc.idcompra inner join CLIEPROV cl on cl.IDCLIEPROV = oc.idclieprov inner join FORMA_PAGO fp on fp.IDFPAGO = oc.idfpago inner join RESPONSABLE rp on rp.IDRESPONSABLE = oc.idresponsable inner join MONEDAS MON on MON.IDMONEDA = OC.idmoneda inner join ESTADOS E ON OC.idestado = E.IDESTADO inner join AREAS A ON OC.IDAREA = A.IDAREA where doc.idcompra ='"+idorder+"' order by doc.item asc")

            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({
                            'idcompra':data[0],
                            'idproducto':data[1],
                            'producto':data[2],
                            'idmedida':data[3],
                            'cantidad':data[4],
                            'item':data[5],
                            'precio_unitario':data[6],
                            'moneda':data[16],
                            'impuesto':data[7],
                            'subtotalsindscto':data[8],
                            'subtotalcondscto':data[9],
                            'total':data[10],
                            'proveedor':data[11],
                            'ruc':data[12],
                            'formapago':data[13],
                            'responsable':data[14],
                            'total_oc':data[15],
                            'estado':data[17],
                            'SerieNumero':data[18],
                            'area':data[19]
                        })
        return JsonResponse(data_json, safe=False)
####################### ACTUALIZAR ORDEN DE COMPRAS
class UpdateOrdenCompraCV(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_campoverde.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update ORDENCOMPRA SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where idcompra='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','Ordencompra','EDT_ORDENCOMPRAS','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
        
        ############################# ORDEN DE SERVICIO || JHON GUTIERREZ





class ApproveServiciosLogFilterCV(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        

        # Usar parámetros seguros para la consulta SQL
        with connection_campoverde.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_SERVICIOS_2025 ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11],
                'idconsumidor': data[12]
            })
        
       
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            
            
        
        return JsonResponse(data_json, safe=False)



################### DETALLE ORDEN SERVICIOS JHON GUTIERREZ
class ApproveOrdersLogDetailServiceCV(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_campoverde.cursor() as cursor:
            
            cursor.execute("select DO.idservicio, DO.idproducto, DO.descripcion, DO.idmedida, DO.cantidad, DO.item, DO.precio, DO.impuesto, DO.descuento, DO.total, MON.DESCRIPCION AS modena,OD.total as total_os, E.DESCRIPCION as estado, OD.solicitado AS responsable, C.RAZON_SOCIAL, FP.DESCRIPCION AS condicion, OD.RUC, CONCAT(OD.serie, ' - ', OD.numero) AS serie_numero, A.DESCRIPCION from DORDENSERVICIO DO INNER JOIN ORDENSERVICIO OD ON DO.idservicio = OD.idservicio INNER JOIN MONEDAS MON ON MON.idmoneda = OD.idmoneda INNER JOIN ESTADOS E ON OD.idestado = E.IDESTADO INNER JOIN CLIEPROV C ON OD.RUC =C.RUC INNER JOIN FORMA_PAGO FP ON OD.idfpago = FP.IDFPAGO INNER JOIN AREAS A ON A.IDAREA = OD.idarea  where DO.idservicio = '"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idservicio':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'item':data[5],'precio_unitario':data[6],'moneda':data[10],'impuesto':data[7],'descuento':data[8],'total':data[9],'total_os':data[11],'estado':data[12],'responsable':data[13],'proveedor':data[14],'condicion':data[15],'ruc':data[16],'serie_numero':data[17],'area':data[18]})
        return JsonResponse(data_json, safe=False)
    ################# ACTUALIZACIÓN ORDEN SERVICIO
class UpdateOrdenServicioCV(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_campoverde.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update ORDENSERVICIO SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where idservicio='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','ORDENSERVICIO','EDT_ORDENSERVICIOS','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
#################################################################################
################# INVERSIONES AJS################################################
class ApproveAlmacenAreasAJS(View):

    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("select TRIM(IDAREA),  DESCRIPCION as AREA from AREAS ORDER BY DESCRIPCION")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idarea':data[0],'descripcion':data[1]})
        return JsonResponse(data_json, safe=False)
    #############################FILTRO DE LOS PENDIENTES ###############
class ReqInternoLogFilter(View):
    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_donluis.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_REQUERIMIENTO_MEJORA '"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'item':data[0],'idorden':data[1],'sucursal':data[2],'documento':data[3],'num_documento':data[4], 'fecha':data[5], 'total':data[6],'estado':data[7],'areas':data[8],'fecha2':data[9],'almacen':data[10],'idarea':data[11],'observacion':data[12],'PRODUCTO':data[13],'IDCONSUMIDOR':data[14],'cantidad':data[15],'idmedida':data[16]})
        return JsonResponse(data_json, safe=False)
########################## DETALLE REQUERIMIENTO  AJS###########
class ReqInternoLogDetailPurchaseAJS(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("select DR.IDREQINTERNO,DR.IDPRODUCTO,DR.DESCRIPCION,DR.IDMEDIDA,DR.ITEM,DR.CANTIDAD,DR.CANTAPROBADA,DR.IDCONSUMIDOR,RE.NOMBRE from   dREQINTERNO  AS DR INNER JOIN REQINTERNO AS R ON R.IDREQINTERNO=DR.IDREQINTERNO INNER JOIN RESPONSABLE AS RE ON R.IDRESPONSABLE=RE.IDRESPONSABLE WHERE DR.IDREQINTERNO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[4],'producto':data[2],'idmedida':data[3], 'cantidad':data[5],'consumidor':data[7],'responsable':data[8]})
        return JsonResponse(data_json, safe=False)
#################APROBACIÓN REQUERIMIENTO AJS ##################





class UpdateReqInternosAJS(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update REQINTERNO set IDESTADO='AP' where IDREQINTERNO='"+idservicio+"'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE PEDIDOSERVICIOS SET IDESTADO='V1' where IDPEDIDO='"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE PEDIDOSERVICIOS SET IDESTADO='AN'where IDPEDIDO='"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)




class UpdateReqInternos(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return HttpResponse("ID de servicio no válido", status=400)

            # Utilizar la conexión existente
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='AP' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='AP' WHERE IDREQINTERNO='{idservicio}'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='V1' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='V1' WHERE IDREQINTERNO='{idservicio}'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='AN' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='AN' WHERE IDREQINTERNO='{idservicio}'")
                
                # Confirmar la transacción
                connection_inversioneajs.commit()
                print(f"✅ Transacción confirmada para ID: {idservicio}")

            return JsonResponse({
                "success": True,
                "message": f"El requerimiento interno con ID {idservicio} ha sido actualizado correctamente.",
                "idservicio": idservicio,
                "accion": accion
            })
        except DatabaseError as e:
            # Registra el error
            print(f"❌ Error en la base de datos: {str(e)}")
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos: " + str(e)}, status=500)
        except Exception as e:
            # Registra el error
            print(f"❌ Error inesperado: {str(e)}")
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado: " + str(e)}, status=500)







###########################PEDIDO DE ALAMCEN AJS#################################


################# PEDIDOS DE ALMACEN 
class ApprovealmacenLogFilterAJS(View):

    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_almacen_mejora '"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
           data_json.append({
                'item':data[0],
                'idorden':data[1],
                'sucursal':data[2],
                'documento':data[3],
                'num_documento':data[4], 
                'fecha':data[5], 
                'moneda':data[6],
                'total':data[7],
                'estado':data[8],
                'area':data[9],
                'nota':data[10],
                'almacen':data[11],
                'idarea':data[12],
                'descripcion':data[13],
                'idconsumidor':data[14],
                'consumidor_descripcion':data[15],
                'cantidad':data[16],
                'idmedida':data[17]
           })
        return JsonResponse(data_json, safe=False)
    
##################### DETALLE
class ApprovealmacenLogDetailPurchaseAJS(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("select DP.idpedido, DP.idproducto, DP.descripcion, DP.idmedida, DP.cantidad,RE.NOMBRE,MON.DESCRIPCION as moneda from DPEDIDO DP INNER JOIN PEDIDO P ON P.IDPEDIDO=DP.IDPEDIDO INNER JOIN RESPONSABLE RE ON P.IDRESPONSABLE=RE.IDRESPONSABLE INNER JOIN MONEDAS MON ON P.IDMONEDA = MON.IDMONEDA  where DP.IDPEDIDO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'moneda':data[6],'responsable':data[5]})
        return JsonResponse(data_json, safe=False)
    
##########ACTUALIZAR ORDEN ALMACEN 

class UpdateOrdenalmacenAJS(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update PEDIDO SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where IDPEDIDO='"+idservicio+"'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE PEDIDO SET IDESTADO='V1' where IDPEDIDO='"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE PEDIDO SET IDESTADO='AN'where IDPEDIDO='"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
###################################################################################
########################### ORDEN DE SERVICIOS AJS



class ApprovepserviciosLogFilterAJS(View):

    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovepserviciosLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_PSERVICIOS_PRUEBA ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'estado': data[8],
                'area': data[9],
                'servicio_descripcion': data[13],
                'idconsumidor': data[14],
                'consumidor_descripcion': data[15],
                'observaciones': data[16]
            })
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            # Filtrar los datos por los estados especificados
            data_json = [item for item in data_json if item['estado'] in estados_list]
            print(f"🔍 Datos filtrados por estados {estados_list}: {len(data_json)} registros")
        
        print(f"🔍 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)





class ApprovePserviciosLogDetailServiceAJS(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("select DP.idpedido, DP.idproducto, DP.descripcion, DP.idmedida, DP.cantidad,RE.NOMBRE, p.OBSERVACIONES,  MON.DESCRIPCION as moneda, DP.precioservicio as precio, DP.TOTAL as total, P.TOTAL as sumaTotal,E.DESCRIPCION AS ESTADO ,A.DESCRIPCION AS AREA, DP.IDCONSUMIDOR AS CONSUMIDOR from DPEDIDOSERVICIOS DP INNER JOIN PEDIDOSERVICIOS P ON P.IDPEDIDO=DP.IDPEDIDO INNER JOIN RESPONSABLE RE ON P.IDRESPONSABLE=RE.IDRESPONSABLE INNER JOIN MONEDAS MON ON P.IDMONEDA = MON.IDMONEDA INNER JOIN AREAS A ON P.IDAREA = A.IDAREA INNER JOIN ESTADOS E ON P.IDESTADO = E.IDESTADO where DP.IDPEDIDO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'moneda':data[7],'precio':data[8],'total':data[9],'responsable':data[5],'observacion':data[6],'sumaTotal':data[10],'estado':data[11],'area':data[12],'consumidor':data[13]})
        return JsonResponse(data_json, safe=False)
##################### ACTUALIZAR PEDIDO SERVICIOS CV ##########



class UpdateOrdenpserviciosAJS(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return JsonResponse({"error": "Acción no válida"}, status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return JsonResponse({"error": "ID de servicio no proporcionado"}, status=400)

            # Utilizar la conexión existente con parámetros seguros
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='AP', 
                            nrsidusuario_ap=?, 
                            nsrfecha_ap=GETDATE() 
                        WHERE IDPEDIDO=?
                    """, [portal_aei_user.username, idservicio])
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='V1' 
                        WHERE IDPEDIDO=?
                    """, [idservicio])
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='AN' 
                        WHERE IDPEDIDO=?
                    """, [idservicio])

                # Verificar si se actualizó algún registro
                if cursor.rowcount == 0:
                    return JsonResponse({"error": "No se encontró el pedido de servicio"}, status=404)

            return JsonResponse({
                "success": True, 
                "message": f"El servicio con ID {idservicio} ha sido actualizado correctamente.",
                "idservicio": idservicio,
                "accion": accion
            })
            
        except User.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=401)
        except DatabaseError as e:
            # Registra el error
            import logging
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos"}, status=500)
        except Exception as e:
            # Registra el error
            import logging
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado en el servidor"}, status=500)
   
#################################################################################





class ApprovecomprasLogFilterAJS(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovecomprasLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_compras ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11] if len(data) > 11 else '',
                
                'comentario': data[14], 
                'idconsumidor': data[15] 
            })
        
        print(f"📊 Total registros obtenidos de SP: {len(data_json)}")
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Manejo especial para el caso SINPERMISOS
            if estados == 'SINPERMISOS':
                print("🚫 Acceso sin permisos - devolviendo lista vacía")
                return JsonResponse([], safe=False)
                
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            print(f"📋 Estados solicitados: {estados_list}")
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            print(f"🔄 Estados convertidos para BD: {estados_bd}")
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            print(f"✂️ Filtrado: {data_json_original} -> {len(data_json)} registros")
            
        print(f"📤 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)




########################## DETALLE ORDEN COMPRA AJS - JHON GUTIERREZ
class ApproveOrdersLogDetailPurchaseAJS(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_inversioneajs.cursor() as cursor:
            
            cursor.execute("select doc.idcompra, doc.idproducto,	doc.descripcion, doc.idmedida, doc.cantidad, doc.item, doc.precio_unitario, doc.impuesto, doc.subtotalsindscto, doc.subtotalcondscto, doc.total, cl.RAZON_SOCIAL, cl.RUC, fp.DESCRIPCION, rp.nombre, oc.total, MON.descripcion as moneda, E.DESCRIPCION, CONCAT(OC.serie,' - ', OC.numero) AS SerieNumero, A.DESCRIPCION as area from DORDENCOMPRA doc inner join ORDENCOMPRA OC on oc.idcompra = doc.idcompra inner join CLIEPROV cl on cl.IDCLIEPROV = oc.idclieprov inner join FORMA_PAGO fp on fp.IDFPAGO = oc.idfpago inner join RESPONSABLE rp on rp.IDRESPONSABLE = oc.idresponsable inner join MONEDAS MON on MON.IDMONEDA = OC.idmoneda inner join ESTADOS E ON OC.idestado = E.IDESTADO inner join AREAS A ON OC.IDAREA = A.IDAREA where doc.idcompra ='"+idorder+"' order by doc.item asc")
            
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({
                            'idcompra':data[0],
                            'idproducto':data[1],
                            'producto':data[2],
                            'idmedida':data[3],
                            'cantidad':data[4],
                            'item':data[5],
                            'precio_unitario':data[6],
                            'moneda':data[16],
                            'impuesto':data[7],
                            'subtotalsindscto':data[8],
                            'subtotalcondscto':data[9],
                            'total':data[10],
                            'proveedor':data[11],
                            'ruc':data[12],
                            'formapago':data[13],
                            'responsable':data[14],
                            'total_oc':data[15],
                            'estado':data[17],
                            'SerieNumero':data[18],
                            'area':data[19]
                        })
        return JsonResponse(data_json, safe=False)
####################### ACTUALIZAR ORDEN DE COMPRAS
class UpdateOrdenCompraAJS(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update ORDENCOMPRA SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where idcompra='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','Ordencompra','EDT_ORDENCOMPRAS','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
#################################################################

# ############################# ORDEN DE SERVICIO AJS JHON GUTIERREZ




class ApproveServiciosLogFilterAJS(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        

        # Usar parámetros seguros para la consulta SQL
        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_SERVICIOS_2025 ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11],
                'idconsumidor': data[12]
            })
        
       
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            
            
        
        return JsonResponse(data_json, safe=False)







################### DETALLE ORDEN SERVICIOS JHON GUTIERREZ
class ApproveOrdersLogDetailServiceAJS(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("select DO.idservicio, DO.idproducto, DO.descripcion, DO.idmedida, DO.cantidad, DO.item, DO.precio, DO.impuesto, DO.descuento, DO.total, MON.DESCRIPCION AS modena,OD.total as total_os, E.DESCRIPCION as estado, OD.solicitado AS responsable, C.RAZON_SOCIAL, FP.DESCRIPCION AS condicion, OD.RUC, CONCAT(OD.serie, ' - ', OD.numero) AS serie_numero, A.DESCRIPCION from DORDENSERVICIO DO INNER JOIN ORDENSERVICIO OD ON DO.idservicio = OD.idservicio INNER JOIN MONEDAS MON ON MON.idmoneda = OD.idmoneda INNER JOIN ESTADOS E ON OD.idestado = E.IDESTADO INNER JOIN CLIEPROV C ON OD.RUC =C.RUC INNER JOIN FORMA_PAGO FP ON OD.idfpago = FP.IDFPAGO INNER JOIN AREAS A ON A.IDAREA = OD.idarea  where DO.idservicio = '"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idservicio':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'item':data[5],'precio_unitario':data[6],'moneda':data[10],'impuesto':data[7],'descuento':data[8],'total':data[9],'total_os':data[11],'estado':data[12],'responsable':data[13],'proveedor':data[14],'condicion':data[15],'ruc':data[16],'serie_numero':data[17],'area':data[18]})
        return JsonResponse(data_json, safe=False)
    ################# ACTUALIZACIÓN ORDEN SERVICIO
class UpdateOrdenServicioAJS(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update ORDENSERVICIO SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where idservicio='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','ORDENSERVICIO','EDT_ORDENSERVICIOS','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
###################################################################################
class ApproveOrdersAreas(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("select TRIM(IDAREA),  DESCRIPCION as AREA from AREAS ORDER BY DESCRIPCION")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idarea':data[0],'descripcion':data[1]})
        return JsonResponse(data_json, safe=False)


########################################### APROVE PEDIDO ALMACEN JHON GUTIERREZ
class ApprovealmacenLogDetailPurchase(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_donluis.cursor() as cursor:
            cursor.execute("select DP.idpedido, DP.idproducto, DP.descripcion, DP.idmedida, DP.cantidad,RE.NOMBRE, A.DESCRIPCION AS area,E.DESCRIPCION AS estado, P.nota as observacion from DPEDIDO DP INNER JOIN PEDIDO P ON P.IDPEDIDO=DP.IDPEDIDO INNER JOIN RESPONSABLE RE ON P.IDRESPONSABLE=RE.IDRESPONSABLE INNER JOIN AREAS A ON P.IDAREA = A.IDAREA INNER JOIN ESTADOS E ON P.IDESTADO = E.IDESTADO  where DP.IDPEDIDO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'responsable':data[5],'area':data[6],'estado':data[7],'observacion':data[8]})
        return JsonResponse(data_json, safe=False)

    
###################################################################################
class ReqInternoLogDetailPurchase(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_donluis.cursor() as cursor:
            cursor.execute("select DR.IDREQINTERNO,DR.IDPRODUCTO,DR.DESCRIPCION,DR.IDMEDIDA,DR.ITEM,DR.CANTIDAD,DR.CANTAPROBADA,DR.IDCONSUMIDOR,RE.NOMBRE from   dREQINTERNO  AS DR INNER JOIN REQINTERNO AS R ON R.IDREQINTERNO=DR.IDREQINTERNO INNER JOIN RESPONSABLE AS RE ON R.IDRESPONSABLE=RE.IDRESPONSABLE   WHERE DR.IDREQINTERNO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[4],'producto':data[2],'idmedida':data[3], 'cantidad':data[5],'consumidor':data[7],'responsable':data[8]})
        return JsonResponse(data_json, safe=False)


############################################# PSERVICIOS JHON GUTIERREZ
class ApprovePserviciosLogDetailService(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_donluis.cursor() as cursor:
            cursor.execute("select DP.idpedido, DP.idproducto, DP.descripcion, DP.idmedida, DP.cantidad,RE.NOMBRE, p.OBSERVACIONES,  MON.DESCRIPCION as moneda, DP.precioservicio as precio, DP.TOTAL as total, P.TOTAL as sumaTotal,E.DESCRIPCION AS ESTADO ,A.DESCRIPCION AS AREA, DP.IDCONSUMIDOR AS CONSUMIDOR from DPEDIDOSERVICIOS DP INNER JOIN PEDIDOSERVICIOS P ON P.IDPEDIDO=DP.IDPEDIDO INNER JOIN RESPONSABLE RE ON P.IDRESPONSABLE=RE.IDRESPONSABLE INNER JOIN MONEDAS MON ON P.IDMONEDA = MON.IDMONEDA INNER JOIN AREAS A ON P.IDAREA = A.IDAREA INNER JOIN ESTADOS E ON P.IDESTADO = E.IDESTADO where DP.IDPEDIDO='"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idpedido':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'moneda':data[7],'precio':data[8],'total':data[9],'responsable':data[5],'observacion':data[6],'sumaTotal':data[10],'estado':data[11],'area':data[12], 'consumidor':data[13]})
        return JsonResponse(data_json, safe=False)

#################################################################################
######################################## ORDEN DE COMPRA JHON GUTIERREZ

class ApproveOrdersLogDetailPurchase(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_donluis.cursor() as cursor:
            cursor.execute("select doc.idcompra, doc.idproducto,	doc.descripcion, doc.idmedida, doc.cantidad, doc.item, doc.precio_unitario, doc.impuesto, doc.subtotalsindscto, doc.subtotalcondscto, doc.total, cl.RAZON_SOCIAL, cl.RUC, fp.DESCRIPCION, rp.nombre, oc.total, MON.descripcion as moneda, E.DESCRIPCION, CONCAT(OC.serie,' - ', OC.numero) AS SerieNumero, A.DESCRIPCION as area from DORDENCOMPRA doc inner join ORDENCOMPRA OC on oc.idcompra = doc.idcompra inner join CLIEPROV cl on cl.IDCLIEPROV = oc.idclieprov inner join FORMA_PAGO fp on fp.IDFPAGO = oc.idfpago inner join RESPONSABLE rp on rp.IDRESPONSABLE = oc.idresponsable inner join MONEDAS MON on MON.IDMONEDA = OC.idmoneda inner join ESTADOS E ON OC.idestado = E.IDESTADO inner join AREAS A ON OC.IDAREA = A.IDAREA where doc.idcompra ='"+idorder+"' order by doc.item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({
                            'idcompra':data[0],
                            'idproducto':data[1],
                            'producto':data[2],
                            'idmedida':data[3],
                            'cantidad':data[4],
                            'item':data[5],
                            'precio_unitario':data[6],
                            'moneda':data[16],
                            'impuesto':data[7],
                            'subtotalsindscto':data[8],
                            'subtotalcondscto':data[9],
                            'total':data[10],
                            'proveedor':data[11],
                            'ruc':data[12],
                            'formapago':data[13],
                            'responsable':data[14],
                            'total_oc':data[15],
                            'estado':data[17],
                            'SerieNumero':data[18],
                            'area':data[19]
                        })
        return JsonResponse(data_json, safe=False)



###################################################################################
class ApproveOrdersLogDetailService(View):

    def get(self, request, *args, **kwargs):

        idorder = self.kwargs.get('idorder')

        with connection_donluis.cursor() as cursor:
            
            cursor.execute("select DO.idservicio, DO.idproducto, DO.descripcion, DO.idmedida, DO.cantidad, DO.item, DO.precio, DO.impuesto, DO.descuento, DO.total, MON.DESCRIPCION AS modena,OD.total as total_os, E.DESCRIPCION as estado, OD.solicitado AS responsable, C.RAZON_SOCIAL, FP.DESCRIPCION AS condicion, OD.RUC, CONCAT(OD.serie, ' - ', OD.numero) AS serie_numero, A.DESCRIPCION from DORDENSERVICIO DO INNER JOIN ORDENSERVICIO OD ON DO.idservicio = OD.idservicio INNER JOIN MONEDAS MON ON MON.idmoneda = OD.idmoneda INNER JOIN ESTADOS E ON OD.idestado = E.IDESTADO INNER JOIN CLIEPROV C ON OD.RUC =C.RUC INNER JOIN FORMA_PAGO FP ON OD.idfpago = FP.IDFPAGO INNER JOIN AREAS A ON A.IDAREA = OD.idarea  where DO.idservicio = '"+idorder+"' order by item asc")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'idservicio':data[0],'idproducto':data[1],'producto':data[2],'idmedida':data[3], 'cantidad':data[4],'item':data[5],'precio_unitario':data[6],'moneda':data[10],'impuesto':data[7],'descuento':data[8],'total':data[9], 'total_os':data[11],'estado':data[12],'responsable':data[13],'proveedor':data[14],'condicion':data[15],'ruc':data[16],'serie_numero':data[17],'area':data[18]})
        return JsonResponse(data_json, safe=False)




###################################################################################

###################################################################################

class ApprovealmacenLogFilter(View):

    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_donluis.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_almacen_mejora'"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({
                'item':data[0],
                'idorden':data[1],
                'sucursal':data[2],
                'documento':data[3],
                'num_documento':data[4], 
                'fecha':data[5], 
                'moneda':data[6],
                'total':data[7],
                'estado':data[8],
                'area':data[9],
                'nota':data[10],
                'almacen':data[11],
                'idarea':data[12],
                'descripcion':data[13],
                'idconsumidor':data[14],
                'consumidor_descripcion':data[15],
                'cantidad':data[16],
                'idmedida':data[17]
                })
        return JsonResponse(data_json, safe=False)
###################################################################################
###################################################################################

class ApprovepserviciosLogFilter(View):

    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovepserviciosLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_donluis.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_PSERVICIOS_PRUEBA ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'estado': data[8],
                'area': data[9],
                'servicio_descripcion': data[13],
                'idconsumidor': data[14],
                'consumidor_descripcion': data[15],
                'observaciones': data[16]
            })
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            # Filtrar los datos por los estados especificados
            data_json = [item for item in data_json if item['estado'] in estados_list]
            print(f"🔍 Datos filtrados por estados {estados_list}: {len(data_json)} registros")
        
        print(f"🔍 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)




###################################################################################

class ApproveOrdersLogFilter(View):
    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_donluis.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_ORDERS '"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'item':data[0],'idorden':data[1],'sucursal':data[2],'documento':data[3],'num_documento':data[4], 'fecha':data[5], 'moneda':data[6],'total':data[7],'proveedor':data[8],'estado':data[9],'area':data[10]})
        return JsonResponse(data_json, safe=False)
###################################################################################


class ApprovecomprasLogFilter(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovecomprasLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_donluis.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_compras ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11] if len(data) > 11 else '',
                
                'comentario': data[14], 
                'idconsumidor': data[15] 
            })
        
        print(f"📊 Total registros obtenidos de SP: {len(data_json)}")
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Manejo especial para el caso SINPERMISOS
            if estados == 'SINPERMISOS':
                print("🚫 Acceso sin permisos - devolviendo lista vacía")
                return JsonResponse([], safe=False)
                
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            print(f"📋 Estados solicitados: {estados_list}")
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            print(f"🔄 Estados convertidos para BD: {estados_bd}")
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            print(f"✂️ Filtrado: {data_json_original} -> {len(data_json)} registros")
            
        print(f"📤 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)









class ApprovecomprasLogFilterCV(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        print(f"🔍 ApprovecomprasLogFilter - Área: {area}, Estados: {estados}")

        # Usar parámetros seguros para la consulta SQL
        with connection_campoverde.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_compras ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11] if len(data) > 11 else '',
                
                'comentario': data[14], 
                'idconsumidor': data[15] 
            })
        
        print(f"📊 Total registros obtenidos de SP: {len(data_json)}")
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Manejo especial para el caso SINPERMISOS
            if estados == 'SINPERMISOS':
                print("🚫 Acceso sin permisos - devolviendo lista vacía")
                return JsonResponse([], safe=False)
                
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            print(f"📋 Estados solicitados: {estados_list}")
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            print(f"🔄 Estados convertidos para BD: {estados_bd}")
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            print(f"✂️ Filtrado: {data_json_original} -> {len(data_json)} registros")
            
        print(f"📤 Total registros devueltos: {len(data_json)}")
        return JsonResponse(data_json, safe=False)




##################################### JHON GUTIERREZ


class ApproveServiciosLogFilter(View):
    def get(self, request, *args, **kwargs):
        area = self.kwargs.get('area')
        # Obtener estados desde kwargs (URL) o desde query parameters (GET)
        estados = self.kwargs.get('estados') or request.GET.get('estados', 'ALL')
        
        

        # Usar parámetros seguros para la consulta SQL
        with connection_donluis.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_APPROVE_SERVICIOS_2025 ?", [area])
            data_object = cursor.fetchall()
            cursor.close
        
        # Convertir los datos a lista de diccionarios
        data_json = []
        for data in data_object:
            data_json.append({
                'item': data[0],
                'idorden': data[1],
                'sucursal': data[2],
                'documento': data[3],
                'num_documento': data[4], 
                'fecha': data[5], 
                'moneda': data[6],
                'total': data[7],
                'proveedor': data[8],
                'estado': data[9],
                'area': data[10],
                'comentario': data[11],
                'idconsumidor': data[12]
            })
        
       
        
        # Mapeo de estados legibles a códigos de base de datos
        estado_mapping = {
            'PENDIENTE': 'PE',
            'V1': 'V1',
            'APROBADO': 'AP',
            'ANULADO': 'AN',
            'RECHAZADO': 'RE'
        }
        
        # Filtrar por estados si no es 'ALL'
        if estados and estados != 'ALL' and estados != '0':
            # Dividir los estados por coma si vienen múltiples estados
            estados_list = [estado.strip() for estado in estados.split(',')]
            
            
            # Convertir estados legibles a códigos de BD
            estados_bd = []
            for estado in estados_list:
                if estado in estado_mapping:
                    estados_bd.append(estado_mapping[estado])
                else:
                    # Si el estado ya viene como código de BD, usarlo directamente
                    estados_bd.append(estado)
            
            
            
            # Filtrar los datos por los estados especificados
            data_json_original = len(data_json)
            data_json = [item for item in data_json if item['estado'] in estados_bd]
            
            
            
        
        return JsonResponse(data_json, safe=False)




###################################################################################
class ReqInternoLogFilterAJS(View):
    def get(self, request, *args, **kwargs):

        area = self.kwargs.get('area')

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("EXEC PROC_RETURN_REQUERIMIENTO_MEJORA '"+area+"'")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'item':data[0],'idorden':data[1],'sucursal':data[2],'documento':data[3],'num_documento':data[4], 'fecha':data[5], 'total':data[6],'estado':data[7],'areas':data[8],'fecha2':data[9],'almacen':data[10],'idarea':data[11],'observacion':data[12],'PRODUCTO':data[13],'IDCONSUMIDOR':data[14],'cantidad':data[15],'idmedida':data[16]})
        return JsonResponse(data_json, safe=False)
    
#######################################
class fitosanidadLogFilter(View):

    def get(self, request, *args, **kwargs):
        try:
            area = self.kwargs.get('area')
            print(f"🔍 Fitosanidad - Filtrando por área: {area}")

            with connection_donluis.cursor() as cursor:
                # Usar el procedimiento almacenado PROC_RETURN_FITOSANIDAD
                print(f"📊 Ejecutando PROC_RETURN_FITOSANIDAD con área: {area}")
                cursor.execute("EXEC PROC_RETURN_FITOSANIDAD_PRUEBA ?", [area])
                data_object = cursor.fetchall()
                print(f"✅ Procedimiento ejecutado exitosamente. Registros encontrados: {len(data_object)}")
                cursor.close
                
            data_json = []
            for data in data_object:
                # Retornar los datos tal como los entrega el procedimiento almacenado
                data_json.append({
                    'item': data[0],           # n (row_number)
                    'idorden': data[1],        # IDRECOMENDACIONAPL
                    'sucursal': data[2],       # idsucursal
                    'documento': data[3],      # doc (FITOSANIDAD)
                    'num_documento': data[4],  # documento (concatenado)
                    'fecha': data[5],
                    'fecha_apl': data[6],
                    'estado': data[7],         # IDESTADO
                    'area': data[8], 
                    'area_descripcion': data[9], # DESCRIPCION del área
                    'date': data[10],
                    'almacen': data[11],
                    'area_secundario': data[12],
                    'consumidor': data[13],
                    'consumidor_descripcion': data[14],
                    'id_producto': data[15],
                    'descripcion_producto': data[16],
                    'descripcion_iac': data[17]
                })
            
            print(f"📦 JSON generado con {len(data_json)} registros")
            return JsonResponse(data_json, safe=False)
            
        except Exception as e:
            print(f"❌ Error en fitosanidadLogFilter: {str(e)}")
            logging.error(f"Error en fitosanidadLogFilter: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
#####################################################################################
class ApproveOrdersLogDetailFitosanidad(View):
     def get(self, request, *args, **kwargs):

         idorder = self.kwargs.get('idorder')

         with connection_donluis.cursor() as cursor:
             cursor.execute("SELECT R.IDRECOMENDACIONAPL,CONVERT(varchar, R.fecha_apl, 105) AS fecha_apl,R.IDESTADO,AR.DESCRIPCION AS AREA,RS.NOMBRE AS RESPONSABLE,R.IDCONSUMIDOR,DR.IDPRODUCTO,DR.DESCRIPCION,DR.IDMEDIDA,DR.CANTIDAD FROM RECOMENDACIONAPL R INNER JOIN DRECOMENDACIONAPL DR ON DR.IDRECOMENDACIONAPL = R.IDRECOMENDACIONAPL INNER JOIN RESPONSABLE RS ON RS.IDRESPONSABLE = R.IDRESPONSABLE INNER JOIN AREAS AR ON AR.IDAREA = R.idarea WHERE R.IDRECOMENDACIONAPL='"+idorder+"' ORDER BY item ASC")
             data_object = cursor.fetchall()
             cursor.close
         data_json = []
         for data in data_object:
             data_json.append({'fecha_apl':data[1],'AREA':data[3],'RESPONSABLE':data[4],'IDCONSUMIDOR':data[5],'IDPRODUCTO':data[6], 'DESCRIPCION':data[7],'IDMEDIDA':data[8],'CANTIDAD':data[9]})
         return JsonResponse(data_json, safe=False)
#####################################################################################
#### ACTUALIZAR ESTADO
class UpdateOrdenCompra(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_donluis.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update ORDENCOMPRA SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where idcompra='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','Ordencompra','EDT_ORDENCOMPRAS','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
#######################
class UpdateOrdenServicio(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_donluis.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update ORDENSERVICIO SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where idservicio='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','ORDENSERVICIO','EDT_ORDENSERVICIOS','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
        
########################################actualizar pedidos almacen

class UpdateOrdenalmacen(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)
            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Utilizar la conexión existente
            with connection_donluis.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update PEDIDO SET IDESTADO='AP', nrsidusuario_ap='"+portal_aei_user.username+"' , nsrfecha_ap=GETDATE() where IDPEDIDO='"+idservicio+"'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE PEDIDO SET IDESTADO='V1' where IDPEDIDO='"+idservicio+"'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE PEDIDO SET IDESTADO='AN'where IDPEDIDO='"+idservicio+"'")

            return HttpResponse(f"El servicio con idservicio {idservicio} ha sido actualizado.")
        except DatabaseError as e:
            # Registra el error
            logging.error("Error en la base de datos: " + str(e))
            return HttpResponse("Error en la base de datos: " + str(e), status=500)
        except Exception as e:
            # Registra el error
            logging.error("Error inesperado: " + str(e))
            return HttpResponse("Error inesperado: " + str(e), status=500)
########################################actualizar pedidos Servicios

class UpdateOrdenpservicios(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')
            portal_aei_user = User.objects.get(username=request.user.username)

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return JsonResponse({"error": "Acción no válida"}, status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return JsonResponse({"error": "ID de servicio no proporcionado"}, status=400)

            # Utilizar la conexión existente con parámetros seguros
            with connection_donluis.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='AP', 
                            nrsidusuario_ap=?, 
                            nsrfecha_ap=GETDATE() 
                        WHERE IDPEDIDO=?
                    """, [portal_aei_user.username, idservicio])
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='V1' 
                        WHERE IDPEDIDO=?
                    """, [idservicio])
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("""
                        UPDATE PEDIDOSERVICIOS 
                        SET IDESTADO='AN' 
                        WHERE IDPEDIDO=?
                    """, [idservicio])

                # Verificar si se actualizó algún registro
                if cursor.rowcount == 0:
                    return JsonResponse({"error": "No se encontró el pedido de servicio"}, status=404)

            return JsonResponse({
                "success": True, 
                "message": f"El servicio con ID {idservicio} ha sido actualizado correctamente.",
                "idservicio": idservicio,
                "accion": accion
            })
            
        except User.DoesNotExist:
            return JsonResponse({"error": "Usuario no encontrado"}, status=401)
        except DatabaseError as e:
            # Registra el error
            import logging
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos"}, status=500)
        except Exception as e:
            # Registra el error
            import logging
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado en el servidor"}, status=500)
        
#################################################################

class UpdateReqInternos(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return HttpResponse("ID de servicio no válido", status=400)

            # Utilizar la conexión existente
            with connection_donluis.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='AP' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='AP' WHERE IDREQINTERNO='{idservicio}'")
                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='V1' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='V1' WHERE IDREQINTERNO='{idservicio}'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("UPDATE REQINTERNO SET IDESTADO='AN' WHERE IDREQINTERNO='"+idservicio+"'")
                    print(f"✅ Ejecutando UPDATE REQINTERNO SET IDESTADO='AN' WHERE IDREQINTERNO='{idservicio}'")
                
                # Confirmar la transacción
                connection_donluis.commit()
                print(f"✅ Transacción confirmada para ID: {idservicio}")

            return JsonResponse({
                "success": True,
                "message": f"El requerimiento interno con ID {idservicio} ha sido actualizado correctamente.",
                "idservicio": idservicio,
                "accion": accion
            })
        except DatabaseError as e:
            # Registra el error
            print(f"❌ Error en la base de datos: {str(e)}")
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos: " + str(e)}, status=500)
        except Exception as e:
            # Registra el error
            print(f"❌ Error inesperado: {str(e)}")
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado: " + str(e)}, status=500)



############################APROBAR FITOSANIDAD
class Updatefitosanidad(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return HttpResponse("ID de servicio no válido", status=400)

            portal_aei_user = User.objects.get(username=request.user.username)

            # Utilizar la conexión existente
            with connection_donluis.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update RECOMENDACIONAPL SET IDESTADO='AP' where IDRECOMENDACIONAPL='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','Recomendacionapl','EDT_APLFITOSANITARIAS_DIARIO','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")
                    print(f"✅ Ejecutando update RECOMENDACIONAPL SET IDESTADO='AP' WHERE IDRECOMENDACIONAPL='{idservicio}'")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                    print(f"✅ Ejecutando EXEC ActualizarTablaVB '{idservicio}'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")
                    print(f"✅ Ejecutando EXEC ActualizarTablaAN '{idservicio}'")
                
                # Confirmar la transacción
                connection_donluis.commit()
                print(f"✅ Transacción confirmada para ID: {idservicio}")
                    
            cursor.execute("SELECT IDRECOMENDACIONAPL,IDDOCUMENTO,IDSUCURSAL,IDALMACEN,SERIE,NUMERO,CONVERT(CHAR(8),FECHA,112) AS FECHA,IDESTADO,idarea,IDRESPONSABLE,IDCONSUMIDOR FROM RECOMENDACIONAPL WHERE IDRECOMENDACIONAPL='"+idservicio+"'")
            data_object = cursor.fetchall()

            cursor.execute("SELECT ITEM,IDPRODUCTO,DESCRIPCION,IDMEDIDA,CAST(TOTAL AS VARCHAR(17)) AS CANTIDAD,TC.IDCONSUMIDOR,TC.IDACTIVIDAD,TC.IDLABOR FROM DRECOMENDACIONAPL TD INNER JOIN RECOMENDACIONAPL TC ON TD.IDRECOMENDACIONAPL = TC.IDRECOMENDACIONAPL WHERE TC.IDRECOMENDACIONAPL='"+idservicio+"'")
            data_object_det = cursor.fetchall()
            
            # cursor.close
            data_json = []
            # connection_donluis.close()
            for data in data_object:
                data_json.append({'idreqinterno':data[0],'iddocumento':'REQ','idsucursal':data[2],
                                  'idalmacen':data[3],'serie':data[4],'numero':data[5],'fecha':data[6],'estado':data[7],'idarea':data[8],
                                  'idresponsable':data[9],
                                  'dreqinterno':[dict(zip([desc[0].swapcase() for desc in cursor.description], detalle)) for detalle in data_object_det]})
            
            print(data_json)
            return JsonResponse(data_json, safe=False)
            
        except DatabaseError as e:
            # Registra el error
            print(f"❌ Error en la base de datos: {str(e)}")
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos: " + str(e)}, status=500)
        except Exception as e:
            # Registra el error
            print(f"❌ Error inesperado: {str(e)}")
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado: " + str(e)}, status=500)




######### PEDIDO DE COMPRA DON LUIS ####################
class OrderOCPedidodonluis(TemplateView):
    permission_required = 'script.ver_logistica_dl'
    template_name = 'script/order_oc_pedido_donluis.html'

class OrderOCPedidodonluisScript(View):

    def get(self, request, *args, **kwargs):
        with connection_donluis.cursor() as cursor:
            cursor.execute("SELECT P.IDDOCUMENTO as IDDOCUMENTO,  P.SERIE AS SERIE  , P.NUMERO AS NUMERO,P.IDPEDIDO,FORMAT(MAX(P.FECHA), 'dd/MM/yyyy') AS 'FECHA CREACIÓN', FORMAT(MAX(P.nsrfecha_ap), 'dd/MM/yyyy') AS 'APROBACIÓN DE PEDIDO',R.NOMBRE AS RESPONSABLE, dp.IDPRODUCTO,  dp.DESCRIPCION as 'DESCRIPCIÓN DE PEDIDO',SUM(DP.CANTIDAD) AS 'CANTIDAD_TOTAL',dp.IDMEDIDA ,COALESCE(ES.DESCRIPCION,'Pendiente') as 'ESTADO ITEM',ess.DESCRIPCION as 'ESTADO PEDIDO',  MAX(OC.IDDOCUMENTO) AS IDDOCUMENTO,  MAX(OC.SERIE) AS SERIE, MAX(OC.NUMERO) AS NUMERO, MAX(OC.idcompra) AS 'CODIGO DE COMPRA',FORMAT(MAX(OC.FECHACREACION), 'dd/MM/yyyy') AS 'FECHA CREACION OC', FORMAT(MAX(oc.nsrfecha_ap), 'dd/MM/yyyy') AS 'APROBACIÓN DE COMPRA' FROM PEDIDO AS P FULL OUTER JOIN DCOMPRAPEDIDOS DCP ON P.IDPEDIDO = DCP.IDPEDIDO LEFT OUTER JOIN ORDENCOMPRA AS OC ON OC.idcompra = DCP.idcompra Full OUTER JOIN DPEDIDO DP ON DP.IDPEDIDO = P.idpedido left JOIN ESTADOS ES ON ES.IDESTADO=DP.IDESTADO left join estados ess on ess.IDESTADO=p.IDESTADO INNER JOIN RESPONSABLE R ON P.IDRESPONSABLE=R.IDRESPONSABLE where p.IDESTADO<>'RE' AND P.IDESTADO<>'AN' GROUP BY P.IDDOCUMENTO, P.SERIE, P.NUMERO,P.IDPEDIDO,  dp.IDPRODUCTO,  dp.DESCRIPCION, DP.ITEM,  dp.IDESTADO,  dp.DESCRIPCION,  dp.IDMEDIDA,  ES.DESCRIPCION,  R.NOMBRE, p.idestado,  ess.DESCRIPCION ORDER BY MAX(P.fecha) DESC");
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'iddocumento_pe':data[0],'serie_pe':data[1],'numero_pe':data[2],'codigopedido':data[3],'fechapedido':data[4],'pedidoaprobacion':data[5],'responsables':data[6],'idproducto':data[7],'descripcionproducto':data[8], 'cantidad':data[9],'unidadmedida':data[10],'itemestado':data[11],'pedidoestado':data[12],'iddocumento_oc':data[13],'serie_oc':data[14],'numero_oc':data[15],'codigocompra':data[16], 'fechacompra':data[17], 'compraaprobacion':data[18]})
        return JsonResponse(data_json, safe=False)
    
    
##############PEDIDO DE COMPRA CAMPO VERDE ##############
class OrderOCPedidocampoverde(TemplateView):
    permission_required = 'ver_logistica_cv'
    template_name = 'script/order_oc_pedido_campoverde.html'

class OrderOCPedidocampoverdeScript(View):

    def get(self, request, *args, **kwargs):

        with connection_campoverde.cursor() as cursor:
            cursor.execute("SELECT P.IDDOCUMENTO as IDDOCUMENTO,  P.SERIE AS SERIE  , P.NUMERO AS NUMERO,P.IDPEDIDO,FORMAT(MAX(P.FECHA), 'dd/MM/yyyy') AS 'FECHA CREACIÓN', FORMAT(MAX(P.nsrfecha_ap), 'dd/MM/yyyy') AS 'APROBACIÓN DE PEDIDO',R.NOMBRE AS RESPONSABLE, dp.IDPRODUCTO,  dp.DESCRIPCION as 'DESCRIPCIÓN DE PEDIDO',SUM(DP.CANTIDAD) AS 'CANTIDAD_TOTAL',dp.IDMEDIDA ,COALESCE(ES.DESCRIPCION,'Pendiente') as 'ESTADO ITEM',ess.DESCRIPCION as 'ESTADO PEDIDO',  MAX(OC.IDDOCUMENTO) AS IDDOCUMENTO,  MAX(OC.SERIE) AS SERIE, MAX(OC.NUMERO) AS NUMERO, MAX(OC.idcompra) AS 'CODIGO DE COMPRA',FORMAT(MAX(OC.FECHACREACION), 'dd/MM/yyyy') AS 'FECHA CREACION OC', FORMAT(MAX(oc.nsrfecha_ap), 'dd/MM/yyyy') AS 'APROBACIÓN DE COMPRA' FROM PEDIDO AS P FULL OUTER JOIN DCOMPRAPEDIDOS DCP ON P.IDPEDIDO = DCP.IDPEDIDO LEFT OUTER JOIN ORDENCOMPRA AS OC ON OC.idcompra = DCP.idcompra Full OUTER JOIN DPEDIDO DP ON DP.IDPEDIDO = P.idpedido left JOIN ESTADOS ES ON ES.IDESTADO=DP.IDESTADO left join estados ess on ess.IDESTADO=p.IDESTADO INNER JOIN RESPONSABLE R ON P.IDRESPONSABLE=R.IDRESPONSABLE where p.IDESTADO<>'RE' AND P.IDESTADO<>'AN' GROUP BY P.IDDOCUMENTO, P.SERIE, P.NUMERO,P.IDPEDIDO,  dp.IDPRODUCTO,  dp.DESCRIPCION, DP.ITEM,  dp.IDESTADO,  dp.DESCRIPCION,  dp.IDMEDIDA,  ES.DESCRIPCION,  R.NOMBRE, p.idestado,  ess.DESCRIPCION ORDER BY MAX(P.fecha) DESC");
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'iddocumento_pe':data[0],'serie_pe':data[1],'numero_pe':data[2],'codigopedido':data[3],'fechapedido':data[4],'pedidoaprobacion':data[5],'responsables':data[6],'idproducto':data[7],'descripcionproducto':data[8], 'cantidad':data[9],'unidadmedida':data[10],'itemestado':data[11],'pedidoestado':data[12],'iddocumento_oc':data[13],'serie_oc':data[14],'numero_oc':data[15],'codigocompra':data[16], 'fechacompra':data[17], 'compraaprobacion':data[18]})
        return JsonResponse(data_json, safe=False)

##############PEDIDO DE COMPRA IVERSIONES AJS ##############

class OrderOCPedidoinversionesajs( TemplateView):
    permission_required = 'ver_logistica_ajs'
    template_name = 'script/order_oc_pedido_inversionesajs.html'

class OrderOCPedidoinversionesajsScript(View):

    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("SELECT P.IDDOCUMENTO as IDDOCUMENTO,  P.SERIE AS SERIE  , P.NUMERO AS NUMERO,P.IDPEDIDO,FORMAT(MAX(P.FECHA), 'dd/MM/yyyy') AS 'FECHA CREACIÓN', FORMAT(MAX(P.nsrfecha_ap), 'dd/MM/yyyy') AS 'APROBACIÓN DE PEDIDO',R.NOMBRE AS RESPONSABLE, dp.IDPRODUCTO,  dp.DESCRIPCION as 'DESCRIPCIÓN DE PEDIDO',SUM(DP.CANTIDAD) AS 'CANTIDAD_TOTAL',dp.IDMEDIDA ,COALESCE(ES.DESCRIPCION,'Pendiente') as 'ESTADO ITEM',ess.DESCRIPCION as 'ESTADO PEDIDO',  MAX(OC.IDDOCUMENTO) AS IDDOCUMENTO,  MAX(OC.SERIE) AS SERIE, MAX(OC.NUMERO) AS NUMERO, MAX(OC.idcompra) AS 'CODIGO DE COMPRA',FORMAT(MAX(OC.FECHACREACION), 'dd/MM/yyyy') AS 'FECHA CREACION OC', FORMAT(MAX(oc.nsrfecha_ap), 'dd/MM/yyyy') AS 'APROBACIÓN DE COMPRA' FROM PEDIDO AS P FULL OUTER JOIN DCOMPRAPEDIDOS DCP ON P.IDPEDIDO = DCP.IDPEDIDO LEFT OUTER JOIN ORDENCOMPRA AS OC ON OC.idcompra = DCP.idcompra Full OUTER JOIN DPEDIDO DP ON DP.IDPEDIDO = P.idpedido left JOIN ESTADOS ES ON ES.IDESTADO=DP.IDESTADO left join estados ess on ess.IDESTADO=p.IDESTADO INNER JOIN RESPONSABLE R ON P.IDRESPONSABLE=R.IDRESPONSABLE where p.IDESTADO<>'RE' AND P.IDESTADO<>'AN' GROUP BY P.IDDOCUMENTO, P.SERIE, P.NUMERO,P.IDPEDIDO,  dp.IDPRODUCTO,  dp.DESCRIPCION, DP.ITEM,  dp.IDESTADO,  dp.DESCRIPCION,  dp.IDMEDIDA,  ES.DESCRIPCION,  R.NOMBRE, p.idestado,  ess.DESCRIPCION ORDER BY MAX(P.fecha) DESC");
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'iddocumento_pe':data[0],'serie_pe':data[1],'numero_pe':data[2],'codigopedido':data[3],'fechapedido':data[4],'pedidoaprobacion':data[5],'responsables':data[6],'idproducto':data[7],'descripcionproducto':data[8], 'cantidad':data[9],'unidadmedida':data[10],'itemestado':data[11],'pedidoestado':data[12],'iddocumento_oc':data[13],'serie_oc':data[14],'numero_oc':data[15],'codigocompra':data[16], 'fechacompra':data[17], 'compraaprobacion':data[18]})
        return JsonResponse(data_json, safe=False)

############################################################

class OrderOCLogcampoverde(TemplateView):
    permission_required = 'ver_logistica_cv'
    template_name = 'script/order_oc_log_campoverde.html'



class OrderOCLogcampoverdeScript(View):

    def get(self, request, *args, **kwargs):
        with connection_campoverde.cursor() as cursor:
            cursor.execute("SELECT e.DESCRIPCION as estado,oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero AS DOCUMENTO_COMPRA,CL.RAZON_SOCIAL as PROVEEDOR,doc.idproducto, doc.descripcion, doc.idmedida as UNIDAD,doc.cantidad,doc.precio_unitario,doc.subtotalsindscto,doc.impuesto,doc.total,mo.DESCRIPCION as moneda,co.IDCONSUMIDOR as idconsumidor,co.DESCRIPCION as CONSUMIDOR,suc.DESCRIPCION as SUCURSAL,alm.DESCRIPCION as ALMACEN,oc.fecha,oc.periodo,SUM(di.CANTIDAD) as cantidad_recepcionada FROM dbo.ORDENCOMPRA as oc INNER JOIN dbo.ESTADOS as e ON oc.idestado = e.IDESTADO INNER JOIN dbo.MONEDAS as MO ON oc.idmoneda = MO.IDMONEDA INNER JOIN dbo.DORDENCOMPRA as doc ON oc.idcompra = doc.idcompra AND oc.idempresa = doc.idempresa INNER JOIN dbo.CLIEPROV as CL ON oc.idempresa = CL.IDEMPRESA AND oc.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES as suc ON oc.IDSUCURSAL = suc.IDSUCURSAL AND oc.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES as alm ON oc.IDEMPRESA = alm.IDEMPRESA AND oc.IDSUCURSAL = alm.IDSUCURSAL AND oc.IDALMACEN = alm.IDALMACEN LEFT JOIN dbo.CONSUMIDOR as co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM as di ON doc.idcompra = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA group by e.DESCRIPCION, oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero,CL.RAZON_SOCIAL, doc.idproducto, doc.descripcion, doc.idmedida, doc.cantidad,doc.precio_unitario, doc.subtotalsindscto, doc.impuesto, doc.total, mo.DESCRIPCION , co.IDCONSUMIDOR, co.DESCRIPCION,suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo order by documento_compra")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'subtotalsindscto':data[8],'impuesto':data[9],'total':data[10],'moneda':data[11],'idconsumidor':data[12], 'consumidor':data[13],'sucursal':data[14],'almacen':data[15],'fecha':data[16],'periodo':data[17],'cantidad_recepcionada':data[18]})
        return JsonResponse(data_json, safe=False)
    

###########################################################
class OrderOCLogdonluis(TemplateView):
    permission_required = 'ver_logistica_dl'
    template_name = 'script/order_oc_log_donluis.html'

class OrderOCLogdonluisScript(View):
    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("SELECT e.DESCRIPCION as estado,oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero AS DOCUMENTO_COMPRA,CL.RAZON_SOCIAL as PROVEEDOR,doc.idproducto, doc.descripcion, doc.idmedida as UNIDAD,doc.cantidad,doc.precio_unitario,doc.subtotalsindscto,doc.impuesto,doc.total,mo.DESCRIPCION as moneda,co.IDCONSUMIDOR as idconsumidor,co.DESCRIPCION as CONSUMIDOR,suc.DESCRIPCION as SUCURSAL,alm.DESCRIPCION as ALMACEN,oc.fecha,oc.periodo,SUM(di.CANTIDAD) as cantidad_recepcionada FROM dbo.ORDENCOMPRA as oc INNER JOIN dbo.ESTADOS as e ON oc.idestado = e.IDESTADO INNER JOIN dbo.MONEDAS as MO ON oc.idmoneda = MO.IDMONEDA INNER JOIN dbo.DORDENCOMPRA as doc ON oc.idcompra = doc.idcompra AND oc.idempresa = doc.idempresa INNER JOIN dbo.CLIEPROV as CL ON oc.idempresa = CL.IDEMPRESA AND oc.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES as suc ON oc.IDSUCURSAL = suc.IDSUCURSAL AND oc.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES as alm ON oc.IDEMPRESA = alm.IDEMPRESA AND oc.IDSUCURSAL = alm.IDSUCURSAL AND oc.IDALMACEN = alm.IDALMACEN LEFT JOIN dbo.CONSUMIDOR as co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM as di ON doc.idcompra = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA group by e.DESCRIPCION, oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero,CL.RAZON_SOCIAL, doc.idproducto, doc.descripcion, doc.idmedida, doc.cantidad,doc.precio_unitario, doc.subtotalsindscto, doc.impuesto, doc.total, mo.DESCRIPCION , co.IDCONSUMIDOR, co.DESCRIPCION,suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo order by documento_compra")            #cursor.execute("SELECT e.DESCRIPCION,(oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero) as documento_compra, CL.RAZON_SOCIAL, TRIM(doc.idproducto), doc.descripcion, doc.idmedida as UNIDAD, doc.cantidad, cast(round(doc.precio_unitario,2) as numeric(10,2)),  cast(round(doc.subtotalsindscto,2) as numeric(10,2)), cast(round(doc.impuesto,2) as numeric(10,2)), cast(round(doc.total,2) as numeric(10,2)), mo.DESCRIPCION, co.IDCONSUMIDOR, co.DESCRIPCION, suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo, cast(round(ISNULL(SUM(di.CANTIDAD) , 0 ),2) as numeric(10,2)) FROM dbo.ORDENCOMPRA as oc INNER JOIN   dbo.ESTADOS AS e ON oc.idestado = e.IDESTADO INNER JOIN   dbo.MONEDAS AS MO ON oc.idmoneda = MO.IDMONEDA INNER JOIN  dbo.DORDENCOMPRA AS doc ON oc.idcompra = doc.idcompra AND oc.idempresa = doc.idempresa INNER JOIN  dbo.CLIEPROV AS CL ON oc.idempresa = CL.IDEMPRESA AND oc.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES AS suc ON oc.IDSUCURSAL = suc.IDSUCURSAL AND oc.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES AS alm ON oc.IDEMPRESA = alm.IDEMPRESA AND oc.IDSUCURSAL = alm.IDSUCURSAL AND oc.IDALMACEN = alm.IDALMACEN INNER JOIN  dbo.CONSUMIDOR AS co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM AS di ON doc.idcompra = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA group by e.DESCRIPCION, oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero,CL.RAZON_SOCIAL, doc.idproducto, doc.descripcion, doc.idmedida, doc.cantidad, doc.precio_unitario, doc.subtotalsindscto, doc.impuesto, doc.total, mo.DESCRIPCION , co.IDCONSUMIDOR, co.DESCRIPCION, suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo order by documento_compra")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'subtotalsindscto':data[8],'impuesto':data[9],'total':data[10],'moneda':data[11],'idconsumidor':data[12], 'consumidor':data[13],'sucursal':data[14],'almacen':data[15],'fecha':data[16],'periodo':data[17],'cantidad_recepcionada':data[18]})
        return JsonResponse(data_json, safe=False)
    
######CONTABILIDAD ####################
################PROVISISONES SR VICTOR JHON GUTIERREZ

class Provision_donluis(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.contabilidad'
    template_name = 'script/provision_donluis.html'

class Provision_Campo_verde(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.contabilidad'
    template_name = 'script/provision_campo_verde.html'

class Provision_inversionesajs(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.contabilidad'
    template_name = 'script/provision_inversionesajs.html'

class Libro_mayor_conta (TemplateView):
    permission_required = 'ver_conta'
    template_name = 'script/libro_mayor_conta.html'

class Libro_mayor_conta_cv (TemplateView):
    permission_required = 'ver_conta'
    template_name = 'script/libro_mayor_conta_cv.html'

class Libro_mayor_conta_ajs (TemplateView):
    permission_required = 'ver_conta'
    template_name = 'script/libro_mayor_conta_ajs.html'



################ESTADO DE GANANCIAS Y PERDIDAS JHON GUTIERREZ

class Egp_funcion(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.contabilidad'
    template_name = 'script/Egp_funcion.html'

class Egp_funcion_campoverde(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.contabilidad'
    template_name = 'script/Egp_funcion_campoverde.html'

class Egp_funcion_inversionesajs(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.contabilidad'
    template_name = 'script/Egp_funcion_inversionesajs.html'



################PROVISISONES LOGICA SR VICTOR JHON GUTIERREZ
class Provision_campoverdeScript(View):
    def get(self, request, *args, **kwargs):

        with connection_campoverde.cursor() as cursor:
            cursor.execute('''SELECT  CONVERT(date, CP.fechaRegistro) AS fechaRegistro, CONVERT(date, CP.vencimiento) AS vencimiento, FP.DIAS_CREDITO,
    CP.idclieprov,
    CL.RAZON_SOCIAL,
    CP.iddocumento,
    CP.serie,
    CP.numero,
    CP.glosa,
    CP.idmoneda,
    CASE 
        WHEN CP.idmoneda = '01' THEN 'Soles'
        WHEN CP.idmoneda = '02' THEN 'Dolares'
        ELSE 'Otra Moneda' 
    END AS moneda,
    CP.importe,
    cp.es_detraccion,
    cp.idregimen,
    CP.con_retencion,
    CASE 
        WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN 'Ret 3%'
        WHEN cp.idregimen = '03' AND cp.es_detraccion = '1' THEN 'Det  ' + CAST(DD.TASADET AS VARCHAR) -- Agrega DD.TASADET al porcentaje
        ELSE ''
    END AS porcentaje,
    CASE 
        WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN 0.97
        ELSE 1
    END AS nuevo_campo,
    ROUND(
        CASE 
            WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN CP.importe * 0.97
            WHEN cp.idregimen = '03' AND cp.es_detraccion = '1' AND DD.TASADET IS NOT NULL THEN CP.importe * ((100-DD.TASADET)/100)
            ELSE CP.importe
        END
    , 2) AS importe_nuevo_redondeado,
    ((100-DD.TASADET)/100) AS importe_det
FROM COBRARPAGARDOC CP
INNER JOIN FORMA_PAGO FP ON CP.IDFPAGO = FP.IDFPAGO
INNER JOIN CLIEPROV CL ON CP.idclieprov = CL.idclieprov
LEFT JOIN DET_DETRACCION DD ON CP.idcobrarpagardoc=DD.IDCOBRARPAGARDOC
WHERE cp.iddocumento<>'FEX'  AND
	   DATEDIFF(DAY, GETDATE(), CP.vencimiento) > 0;
''')
           
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'fecharegistro':data[0].strftime('%d-%m-%Y'),'vencimiento':data[1].strftime('%d-%m-%Y'),'diascreditos':data[2],'ruc':data[3],'razon_social':data[4],'iddocumento':data[5], 'serie':data[6], 'numero':data[7],'glosa':data[8],'idmoneda':data[9],'moneda':data[10],'importe':data[11],'porcentaje':data[15], 'importe_total':data[17]})
        return JsonResponse(data_json, safe=False)


class Provision_inversionesajsScript(View): 
    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute('''SELECT  CONVERT(date, CP.fechaRegistro) AS fechaRegistro, CONVERT(date, CP.vencimiento) AS vencimiento, FP.DIAS_CREDITO,
    CP.idclieprov,
    CL.RAZON_SOCIAL,
    CP.iddocumento,
    CP.serie,
    CP.numero,
    CP.glosa,
    CP.idmoneda,
    CASE 
        WHEN CP.idmoneda = '01' THEN 'Soles'
        WHEN CP.idmoneda = '02' THEN 'Dolares'
        ELSE 'Otra Moneda' 
    END AS moneda,
    CP.importe,
    cp.es_detraccion,
    cp.idregimen,
    CP.con_retencion,
    CASE 
        WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN 'Ret 3%'
        WHEN cp.idregimen = '03' AND cp.es_detraccion = '1' THEN 'Det  ' + CAST(DD.TASADET AS VARCHAR) -- Agrega DD.TASADET al porcentaje
        ELSE ''
    END AS porcentaje,
    CASE 
        WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN 0.97
        ELSE 1
    END AS nuevo_campo,
    ROUND(
        CASE 
            WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN CP.importe * 0.97
            WHEN cp.idregimen = '03' AND cp.es_detraccion = '1' AND DD.TASADET IS NOT NULL THEN CP.importe * ((100-DD.TASADET)/100)
            ELSE CP.importe
        END
    , 2) AS importe_nuevo_redondeado,
    ((100-DD.TASADET)/100) AS importe_det
FROM COBRARPAGARDOC CP
INNER JOIN FORMA_PAGO FP ON CP.IDFPAGO = FP.IDFPAGO
INNER JOIN CLIEPROV CL ON CP.idclieprov = CL.idclieprov
LEFT JOIN DET_DETRACCION DD ON CP.idcobrarpagardoc=DD.IDCOBRARPAGARDOC
WHERE cp.iddocumento<>'FEX'  AND
	   DATEDIFF(DAY, GETDATE(), CP.vencimiento) > 0;
''')
           
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'fecharegistro':data[0].strftime('%d-%m-%Y'),'vencimiento':data[1].strftime('%d-%m-%Y'),'diascreditos':data[2],'ruc':data[3],'razon_social':data[4],'iddocumento':data[5], 'serie':data[6], 'numero':data[7],'glosa':data[8],'idmoneda':data[9],'moneda':data[10],'importe':data[11],'porcentaje':data[15], 'importe_total':data[17]})
        return JsonResponse(data_json, safe=False)


class Provision_donluisScript(View):
    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute('''SELECT CONVERT(date, CP.fechaRegistro) AS fechaRegistro, CONVERT(date, CP.vencimiento) AS vencimiento, FP.DIAS_CREDITO,
    CP.idclieprov,
    CL.RAZON_SOCIAL,
    CP.iddocumento,
    CP.serie,
    CP.numero,
    CP.glosa,
    CP.idmoneda,
    CASE 
        WHEN CP.idmoneda = '01' THEN 'Soles'
        WHEN CP.idmoneda = '02' THEN 'Dolares'
        ELSE 'Otra Moneda' 
    END AS moneda,
    CP.importe,
    cp.es_detraccion,
    cp.idregimen,
    CP.con_retencion,
    CASE 
        WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN 'Ret 3%'
        WHEN cp.idregimen = '03' AND cp.es_detraccion = '1' THEN 'Det  ' + CAST(DD.TASADET AS VARCHAR) -- Agrega DD.TASADET al porcentaje
        ELSE ''
    END AS porcentaje,
    CASE 
        WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN 0.97
        ELSE 1
    END AS nuevo_campo,
    ROUND(
        CASE 
            WHEN cp.idregimen = '01' AND cp.es_detraccion = '0' THEN CP.importe * 0.97
            WHEN cp.idregimen = '03' AND cp.es_detraccion = '1' AND DD.TASADET IS NOT NULL THEN CP.importe * ((100-DD.TASADET)/100)
            ELSE CP.importe
        END
    , 2) AS importe_nuevo_redondeado,
    ((100-DD.TASADET)/100) AS importe_det
FROM COBRARPAGARDOC CP
INNER JOIN FORMA_PAGO FP ON CP.IDFPAGO = FP.IDFPAGO
INNER JOIN CLIEPROV CL ON CP.idclieprov = CL.idclieprov
LEFT JOIN DET_DETRACCION DD ON CP.idcobrarpagardoc=DD.IDCOBRARPAGARDOC
WHERE cp.iddocumento<>'FEX'  AND
	   DATEDIFF(DAY, GETDATE(), CP.vencimiento) > 0;
''')
           
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'fecharegistro':data[0].strftime('%d-%m-%Y'),'vencimiento':data[1].strftime('%d-%m-%Y'),'diascreditos':data[2],'ruc':data[3],'razon_social':data[4],'iddocumento':data[5], 'serie':data[6], 'numero':data[7],'glosa':data[8],'idmoneda':data[9],'moneda':data[10],'importe':data[11],'porcentaje':data[15], 'importe_total':data[17]})
        return JsonResponse(data_json, safe=False)


##################
class OrderOCLogCMPA(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_order_oc'
    template_name = 'script/order_oc_log_cmpa.html'


class OrderOCLogCMPAScript(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("SELECT e.DESCRIPCION as estado,oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero AS DOCUMENTO_COMPRA,CL.RAZON_SOCIAL as PROVEEDOR,doc.idproducto, doc.descripcion, doc.idmedida as UNIDAD,doc.cantidad,doc.precio_unitario,doc.subtotalsindscto,doc.impuesto,doc.total,mo.DESCRIPCION as moneda,co.IDCONSUMIDOR as idconsumidor,co.DESCRIPCION as CONSUMIDOR,suc.DESCRIPCION as SUCURSAL,alm.DESCRIPCION as ALMACEN,oc.fecha,oc.periodo,SUM(di.CANTIDAD) as cantidad_recepcionada FROM dbo.ORDENCOMPRA as oc INNER JOIN dbo.ESTADOS as e ON oc.idestado = e.IDESTADO INNER JOIN dbo.MONEDAS as MO ON oc.idmoneda = MO.IDMONEDA INNER JOIN dbo.DORDENCOMPRA as doc ON oc.idcompra = doc.idcompra AND oc.idempresa = doc.idempresa INNER JOIN dbo.CLIEPROV as CL ON oc.idempresa = CL.IDEMPRESA AND oc.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES as suc ON oc.IDSUCURSAL = suc.IDSUCURSAL AND oc.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES as alm ON oc.IDEMPRESA = alm.IDEMPRESA AND oc.IDSUCURSAL = alm.IDSUCURSAL AND oc.IDALMACEN = alm.IDALMACEN LEFT JOIN dbo.CONSUMIDOR as co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM as di ON doc.idcompra = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA group by e.DESCRIPCION, oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero,CL.RAZON_SOCIAL, doc.idproducto, doc.descripcion, doc.idmedida, doc.cantidad,doc.precio_unitario, doc.subtotalsindscto, doc.impuesto, doc.total, mo.DESCRIPCION , co.IDCONSUMIDOR, co.DESCRIPCION,suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo order by documento_compra")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'subtotalsindscto':data[8],'impuesto':data[9],'total':data[10],'moneda':data[11],'idconsumidor':data[12], 'consumidor':data[13],'sucursal':data[14],'almacen':data[15],'fecha':data[16],'periodo':data[17],'cantidad_recepcionada':data[18]})
        return JsonResponse(data_json, safe=False)


#################
class OrderOCLoginversioneajs(TemplateView):
    permission_required = 'ver_logistica_ajs'
    template_name = 'script/order_oc_log_inversioneajs.html'

class OrderOCLoginversioneajsScript(View):

    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("SELECT e.DESCRIPCION as estado,oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero AS DOCUMENTO_COMPRA,CL.RAZON_SOCIAL as PROVEEDOR,doc.idproducto, doc.descripcion, doc.idmedida as UNIDAD,doc.cantidad,doc.precio_unitario,doc.subtotalsindscto,doc.impuesto,doc.total,mo.DESCRIPCION as moneda,co.IDCONSUMIDOR as idconsumidor,co.DESCRIPCION as CONSUMIDOR,suc.DESCRIPCION as SUCURSAL,alm.DESCRIPCION as ALMACEN,oc.fecha,oc.periodo,SUM(di.CANTIDAD) as cantidad_recepcionada FROM dbo.ORDENCOMPRA as oc INNER JOIN dbo.ESTADOS as e ON oc.idestado = e.IDESTADO INNER JOIN dbo.MONEDAS as MO ON oc.idmoneda = MO.IDMONEDA INNER JOIN dbo.DORDENCOMPRA as doc ON oc.idcompra = doc.idcompra AND oc.idempresa = doc.idempresa INNER JOIN dbo.CLIEPROV as CL ON oc.idempresa = CL.IDEMPRESA AND oc.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES as suc ON oc.IDSUCURSAL = suc.IDSUCURSAL AND oc.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES as alm ON oc.IDEMPRESA = alm.IDEMPRESA AND oc.IDSUCURSAL = alm.IDSUCURSAL AND oc.IDALMACEN = alm.IDALMACEN LEFT JOIN dbo.CONSUMIDOR as co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM as di ON doc.idcompra = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA group by e.DESCRIPCION, oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero,CL.RAZON_SOCIAL, doc.idproducto, doc.descripcion, doc.idmedida, doc.cantidad,doc.precio_unitario, doc.subtotalsindscto, doc.impuesto, doc.total, mo.DESCRIPCION , co.IDCONSUMIDOR, co.DESCRIPCION,suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo order by documento_compra")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'subtotalsindscto':data[8],'impuesto':data[9],'total':data[10],'moneda':data[11],'idconsumidor':data[12], 'consumidor':data[13],'sucursal':data[14],'almacen':data[15],'fecha':data[16],'periodo':data[17],'cantidad_recepcionada':data[18]})
        return JsonResponse(data_json, safe=False)
#####################
class OrderOSLogcampoverde(TemplateView):
    permission_required = 'ver_logistica_cv'
    template_name = 'script/order_os_log_campoverde.html'

class OrderOSLogcampoverdeScript(View):

    def get(self, request, *args, **kwargs):

        with connection_campoverde.cursor() as cursor:
            cursor.execute("select e.DESCRIPCION as estado, os.iddocumento + ' ' + os.serie + ' ' + os.numero AS DOCUMENTO_SERVICIO, CL.RAZON_SOCIAL AS PROVEEDOR, TRIM(doc.idproducto), doc.descripcion, doc.idmedida as UNIDAD, doc.cantidad, doc.precio, doc.total, mo.DESCRIPCION as moneda, co.IDCONSUMIDOR AS idconsumidor, co.DESCRIPCION AS CONSUMIDOR, suc.DESCRIPCION as SUCURSAL, alm.DESCRIPCION as ALMACEN, os.fecha, os.periodo FROM    dbo.ORDENSERVICIO AS os INNER JOIN   dbo.ESTADOS AS e ON os.idestado = e.IDESTADO INNER JOIN   dbo.MONEDAS AS MO ON os.idmoneda = MO.IDMONEDA INNER JOIN  dbo.DORDENSERVICIO AS doc ON os.idservicio = doc.idservicio AND os.idservicio = doc.idservicio INNER JOIN  dbo.CLIEPROV AS CL ON os.idempresa = CL.IDEMPRESA AND os.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES AS suc ON os.IDSUCURSAL = suc.IDSUCURSAL AND os.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES AS alm ON os.IDEMPRESA = alm.IDEMPRESA AND os.IDSUCURSAL = alm.IDSUCURSAL AND os.IDALMACEN = alm.IDALMACEN INNER JOIN  dbo.CONSUMIDOR AS co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM AS di ON doc.idservicio = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA where os.iddocumento = 'OSR' order by DOCUMENTO_SERVICIO")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'total':data[8],'moneda':data[9],'idconsumidor':data[10], 'consumidor':data[11],'sucursal':data[12],'almacen':data[13],'fecha':data[14],'periodo':data[15]})
        return JsonResponse(data_json, safe=False)

class OrderOSLogdonluis(TemplateView):
    permission_required = 'script.ver_logistica_dl'
    template_name = 'script/order_os_log_donluis.html'

class OrderOSLogdonluisScript(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("select e.DESCRIPCION as estado, os.iddocumento + ' ' + os.serie + ' ' + os.numero AS DOCUMENTO_SERVICIO, CL.RAZON_SOCIAL AS PROVEEDOR, TRIM(doc.idproducto), doc.descripcion, doc.idmedida as UNIDAD, doc.cantidad, doc.precio, doc.total, mo.DESCRIPCION as moneda, co.IDCONSUMIDOR AS idconsumidor, co.DESCRIPCION AS CONSUMIDOR, suc.DESCRIPCION as SUCURSAL, alm.DESCRIPCION as ALMACEN, os.fecha, os.periodo FROM    dbo.ORDENSERVICIO AS os INNER JOIN   dbo.ESTADOS AS e ON os.idestado = e.IDESTADO INNER JOIN   dbo.MONEDAS AS MO ON os.idmoneda = MO.IDMONEDA INNER JOIN  dbo.DORDENSERVICIO AS doc ON os.idservicio = doc.idservicio AND os.idservicio = doc.idservicio INNER JOIN  dbo.CLIEPROV AS CL ON os.idempresa = CL.IDEMPRESA AND os.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES AS suc ON os.IDSUCURSAL = suc.IDSUCURSAL AND os.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES AS alm ON os.IDEMPRESA = alm.IDEMPRESA AND os.IDSUCURSAL = alm.IDSUCURSAL AND os.IDALMACEN = alm.IDALMACEN INNER JOIN  dbo.CONSUMIDOR AS co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM AS di ON doc.idservicio = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA where os.iddocumento = 'OSR' order by DOCUMENTO_SERVICIO")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'total':data[8],'moneda':data[9],'idconsumidor':data[10], 'consumidor':data[11],'sucursal':data[12],'almacen':data[13],'fecha':data[14],'periodo':data[15]})
        return JsonResponse(data_json, safe=False)
    


# ALMACEN INVERSIONES AJS FITO - JHON GUTIERREZ#

class Nisira_almacen_inversionesAJS_fito_Script(View):

    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("exec nsp_recomendacionapl;")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'periodo':data[0],'almacen':data[1],'documento':data[2],'año':data[3],'fecha':data[4],'estado':data[5], 'item':data[6], 'idproducto':data[7],'descripcion':data[8],'idmedida':data[9],'idingrediente':data[10], 'descripcion_iac':data[11],'uac':data[12],'total':data[13],'totalxcil':data[14],'fraccionxcil':data[15],'documento_req':data[16],'doc_salida':data[17]})
        return JsonResponse(data_json, safe=False)

# ALMACEN CAMPO VERDE FITO - JHON GUTIERREZ#

class Nisira_almacen_campo_verde_fito_Script(View):

    def get(self, request, *args, **kwargs):

        with connection_campoverde.cursor() as cursor:
            cursor.execute("exec nsp_recomendacionapl;")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
           data_json.append({'periodo':data[0],'almacen':data[1],'documento':data[2],'año':data[3],'fecha':data[4],'estado':data[5], 'item':data[6], 'idproducto':data[7],'descripcion':data[8],'idmedida':data[9],'idingrediente':data[10], 'descripcion_iac':data[11],'uac':data[12],'total':data[13],'totalxcil':data[14],'fraccionxcil':data[15],'documento_req':data[16],'doc_salida':data[17]})
        return JsonResponse(data_json, safe=False)

# ALMACEN CAMPO DON LUIS - JHON GUTIERREZ#

class Nisira_almacen_don_luis_fito_Script(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("exec nsp_recomendacionapl;")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'periodo':data[0],'almacen':data[1],'documento':data[2],'año':data[3],'fecha':data[4],'estado':data[5], 'item':data[6], 'idproducto':data[7],'descripcion':data[8],'idmedida':data[9],'idingrediente':data[10], 'descripcion_iac':data[11],'uac':data[12],'total':data[13],'totalxcil':data[14],'fraccionxcil':data[15],'documento_req':data[16],'doc_salida':data[17]})  
        return JsonResponse(data_json, safe=False)

##########
class OrderOSLogcmpa(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_order_os'
    template_name = 'script/order_os_log_cmpa.html'

class OrderOSLogcmpaScript(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("select e.DESCRIPCION as estado, os.iddocumento + ' ' + os.serie + ' ' + os.numero AS DOCUMENTO_SERVICIO, CL.RAZON_SOCIAL AS PROVEEDOR, TRIM(doc.idproducto), doc.descripcion, doc.idmedida as UNIDAD, doc.cantidad, doc.precio, doc.total, mo.DESCRIPCION as moneda, co.IDCONSUMIDOR AS idconsumidor, co.DESCRIPCION AS CONSUMIDOR, suc.DESCRIPCION as SUCURSAL, alm.DESCRIPCION as ALMACEN, os.fecha, os.periodo FROM    dbo.ORDENSERVICIO AS os INNER JOIN   dbo.ESTADOS AS e ON os.idestado = e.IDESTADO INNER JOIN   dbo.MONEDAS AS MO ON os.idmoneda = MO.IDMONEDA INNER JOIN  dbo.DORDENSERVICIO AS doc ON os.idservicio = doc.idservicio AND os.idservicio = doc.idservicio INNER JOIN  dbo.CLIEPROV AS CL ON os.idempresa = CL.IDEMPRESA AND os.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES AS suc ON os.IDSUCURSAL = suc.IDSUCURSAL AND os.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES AS alm ON os.IDEMPRESA = alm.IDEMPRESA AND os.IDSUCURSAL = alm.IDSUCURSAL AND os.IDALMACEN = alm.IDALMACEN INNER JOIN  dbo.CONSUMIDOR AS co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM AS di ON doc.idservicio = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA where os.iddocumento = 'OSR' order by DOCUMENTO_SERVICIO")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'total':data[8],'moneda':data[9],'idconsumidor':data[10], 'consumidor':data[11],'sucursal':data[12],'almacen':data[13],'fecha':data[14],'periodo':data[15]})
        return JsonResponse(data_json, safe=False)

############
class OrderOSLoginversioneajs( TemplateView):
    permission_required = 'order_os_log_inversioneajs'
    template_name = 'script/order_os_log_inversioneajs.html'

class OrderOSLoginversioneajsScript(View):

    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute("select e.DESCRIPCION as estado, os.iddocumento + ' ' + os.serie + ' ' + os.numero AS DOCUMENTO_SERVICIO, CL.RAZON_SOCIAL AS PROVEEDOR, TRIM(doc.idproducto), doc.descripcion, doc.idmedida as UNIDAD, doc.cantidad, doc.precio, doc.total, mo.DESCRIPCION as moneda, co.IDCONSUMIDOR AS idconsumidor, co.DESCRIPCION AS CONSUMIDOR, suc.DESCRIPCION as SUCURSAL, alm.DESCRIPCION as ALMACEN, os.fecha, os.periodo FROM    dbo.ORDENSERVICIO AS os INNER JOIN   dbo.ESTADOS AS e ON os.idestado = e.IDESTADO INNER JOIN   dbo.MONEDAS AS MO ON os.idmoneda = MO.IDMONEDA INNER JOIN  dbo.DORDENSERVICIO AS doc ON os.idservicio = doc.idservicio AND os.idservicio = doc.idservicio INNER JOIN  dbo.CLIEPROV AS CL ON os.idempresa = CL.IDEMPRESA AND os.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES AS suc ON os.IDSUCURSAL = suc.IDSUCURSAL AND os.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES AS alm ON os.IDEMPRESA = alm.IDEMPRESA AND os.IDSUCURSAL = alm.IDSUCURSAL AND os.IDALMACEN = alm.IDALMACEN INNER JOIN  dbo.CONSUMIDOR AS co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM AS di ON doc.idservicio = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA where os.iddocumento = 'OSR' order by DOCUMENTO_SERVICIO")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'total':data[8],'moneda':data[9],'idconsumidor':data[10], 'consumidor':data[11],'sucursal':data[12],'almacen':data[13],'fecha':data[14],'periodo':data[15]})
        return JsonResponse(data_json, safe=False)


class ReporteFacturaPrueba(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_order_oc'
    template_name = 'script/reporte_factura_prueba.html'


class ReporteFacturaPruebaScript(View):

    def get(self, request, *args, **kwargs):
        with connection_donluis.cursor() as cursor:
            cursor.execute("SELECT e.DESCRIPCION,(oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero) as documento_compra, CL.RAZON_SOCIAL, TRIM(doc.idproducto), doc.descripcion, doc.idmedida as UNIDAD, doc.cantidad, cast(round(doc.precio_unitario,2) as numeric(10,2)),  cast(round(doc.subtotalsindscto,2) as numeric(10,2)), cast(round(doc.impuesto,2) as numeric(10,2)), cast(round(doc.total,2) as numeric(10,2)), mo.DESCRIPCION, co.IDCONSUMIDOR, co.DESCRIPCION, suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo, cast(round(ISNULL(SUM(di.CANTIDAD) , 0 ),2) as numeric(10,2)) FROM dbo.ORDENCOMPRA as oc INNER JOIN   dbo.ESTADOS AS e ON oc.idestado = e.IDESTADO INNER JOIN   dbo.MONEDAS AS MO ON oc.idmoneda = MO.IDMONEDA INNER JOIN  dbo.DORDENCOMPRA AS doc ON oc.idcompra = doc.idcompra AND oc.idempresa = doc.idempresa INNER JOIN  dbo.CLIEPROV AS CL ON oc.idempresa = CL.IDEMPRESA AND oc.idclieprov = CL.IDCLIEPROV INNER JOIN dbo.SUCURSALES AS suc ON oc.IDSUCURSAL = suc.IDSUCURSAL AND oc.IDEMPRESA = suc.IDEMPRESA INNER JOIN dbo.ALMACENES AS alm ON oc.IDEMPRESA = alm.IDEMPRESA AND oc.IDSUCURSAL = alm.IDSUCURSAL AND oc.IDALMACEN = alm.IDALMACEN INNER JOIN  dbo.CONSUMIDOR AS co ON doc.idempresa = co.IDEMPRESA AND co.IDCONSUMIDOR = doc.idconsumidor LEFT JOIN dbo.DINGRESOSALIDAALM AS di ON doc.idcompra = di.IDREFERENCIA AND doc.item = di.ITEMREF AND doc.idempresa = di.IDEMPRESA group by e.DESCRIPCION, oc.iddocumento + ' ' + oc.serie + ' ' + oc.numero,CL.RAZON_SOCIAL, doc.idproducto, doc.descripcion, doc.idmedida, doc.cantidad, doc.precio_unitario, doc.subtotalsindscto, doc.impuesto, doc.total, mo.DESCRIPCION , co.IDCONSUMIDOR, co.DESCRIPCION, suc.DESCRIPCION, alm.DESCRIPCION, oc.fecha, oc.periodo order by documento_compra")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'estado':data[0],'documento':data[1],'razon_social':data[2],'idproducto':data[3],'producto':data[4],'unidad':data[5], 'cantidad':data[6], 'precio_unitario':data[7],'subtotalsindscto':data[8],'impuesto':data[9],'total':data[10],'moneda':data[11],'idconsumidor':data[12], 'consumidor':data[13],'sucursal':data[14],'almacen':data[15],'fecha':data[16],'periodo':data[17],'cantidad_recepcionada':data[18]})
        return JsonResponse(data_json, safe=False)

####################################
class CreditNoteInvoice(PermissionRequiredMixin, TemplateView):
    permission_required = 'user.aei_reports_note_invoice'
    template_name = 'script/credit_note_invoice.html'


class CreditNoteInvoiceScript(View):

    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute("select * from nv_notas_factura")
            data_object = cursor.fetchall()
            cursor.close
        data_json = []
        for data in data_object:
            data_json.append({'sucursal':data[0],'moneda':data[1],'razon_social':data[2],'producto':data[3],'fecha_factura':data[4],'factura':data[5],'importe_factura':data[6],'tcambio_factura':data[7],'fecha_nota':data[8],'nota':data[9],'importe_nota':data[10],'tcambio_nota':data[11],'tipo_venta':data[12],'descripcion':data[13]})
        return JsonResponse(data_json, safe=False)

    ## estructura para CAMPO VERDE 02082024

class fitosanidadLogFilterCV(View):

    def get(self, request, *args, **kwargs):
        try:
            area = self.kwargs.get('area')
            print(f"🔍 Fitosanidad - Filtrando por área: {area}")

            with connection_campoverde.cursor() as cursor:
                # Usar el procedimiento almacenado PROC_RETURN_FITOSANIDAD
                print(f"📊 Ejecutando PROC_RETURN_FITOSANIDAD con área: {area}")
                cursor.execute("EXEC PROC_RETURN_FITOSANIDAD_PRUEBA ?", [area])
                data_object = cursor.fetchall()
                print(f"✅ Procedimiento ejecutado exitosamente. Registros encontrados: {len(data_object)}")
                cursor.close
                
            data_json = []
            for data in data_object:
                # Retornar los datos tal como los entrega el procedimiento almacenado
                data_json.append({
                    'item': data[0],           # n (row_number)
                    'idorden': data[1],        # IDRECOMENDACIONAPL
                    'sucursal': data[2],       # idsucursal
                    'documento': data[3],      # doc (FITOSANIDAD)
                    'num_documento': data[4],  # documento (concatenado)
                    'fecha': data[5],
                    'fecha_apl': data[6],
                    'estado': data[7],         # IDESTADO
                    'area': data[8], 
                    'area_descripcion': data[9], # DESCRIPCION del área
                    'date': data[10],
                    'almacen': data[11],
                    'area_secundario': data[12],
                    'consumidor': data[13],
                    'consumidor_descripcion': data[14],
                    'id_producto': data[15],
                    'descripcion_producto': data[16],
                    'descripcion_iac': data[17]
                })
            
            print(f"📦 JSON generado con {len(data_json)} registros")
            return JsonResponse(data_json, safe=False)
            
        except Exception as e:
            print(f"❌ Error en fitosanidadLogFilter: {str(e)}")
            logging.error(f"Error en fitosanidadLogFilter: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)


class fitosanidadLogFilterAJS(View):

    def get(self, request, *args, **kwargs):
        
        try:
            area = self.kwargs.get('area')
            print(f"🔍 Fitosanidad - Filtrando por área: {area}")


            with connection_inversioneajs.cursor() as cursor:
                # Usar el procedimiento almacenado PROC_RETURN_FITOSANIDAD
                print(f"📊 Ejecutando PROC_RETURN_FITOSANIDAD con área: {area}")
                cursor.execute("EXEC PROC_RETURN_FITOSANIDAD_PRUEBA ? ", [area])
                data_object = cursor.fetchall()
                print(f"✅ Procedimiento ejecutado exitosamente. Registros encontrados: {len(data_object)}")
                cursor.close
                
            data_json = []
            for data in data_object:
                data_json.append({
                    'item': data[0],           # n (row_number)
                        'idorden': data[1],        # IDRECOMENDACIONAPL
                        'sucursal': data[2],       # idsucursal
                        'documento': data[3],      # doc (FITOSANIDAD)
                        'num_documento': data[4],  # documento (concatenado)
                        'fecha': data[5],
                        'fecha_apl': data[6],
                        'estado': data[7],         # IDESTADO
                        'area': data[8], 
                        'area_descripcion': data[9], # DESCRIPCION del área
                        'date': data[10],
                        'almacen': data[11],
                        'area_secundario': data[12],
                        'consumidor': data[13],
                        'consumidor_descripcion': data[14],
                        'id_producto': data[15],
                        'descripcion_producto': data[16],
                        'descripcion_iac': data[17]
                })
                
            print(f"📦 JSON generado con {len(data_json)} registros")
            return JsonResponse(data_json, safe=False)
            
        except Exception as e:
            print(f"❌ Error en fitosanidadLogFilter: {str(e)}")
            logging.error(f"Error en fitosanidadLogFilter: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)




class ApproveOrdersLogDetailFitosanidadCV(View):
     def get(self, request, *args, **kwargs):

         idorder = self.kwargs.get('idorder')

         with connection_campoverde.cursor() as cursor:
             cursor.execute("SELECT R.IDRECOMENDACIONAPL,CONVERT(varchar, R.fecha_apl, 105) AS fecha_apl,R.IDESTADO,AR.DESCRIPCION AS AREA,RS.NOMBRE AS RESPONSABLE,R.IDCONSUMIDOR,DR.IDPRODUCTO,DR.DESCRIPCION,DR.IDMEDIDA,DR.CANTIDAD FROM RECOMENDACIONAPL R INNER JOIN DRECOMENDACIONAPL DR ON DR.IDRECOMENDACIONAPL = R.IDRECOMENDACIONAPL INNER JOIN RESPONSABLE RS ON RS.IDRESPONSABLE = R.IDRESPONSABLE INNER JOIN AREAS AR ON AR.IDAREA = R.idarea WHERE R.IDRECOMENDACIONAPL='"+idorder+"' ORDER BY item ASC")
             data_object = cursor.fetchall()
             cursor.close
         data_json = []
         for data in data_object:
             data_json.append({'fecha_apl':data[1],'AREA':data[3],'RESPONSABLE':data[4],'IDCONSUMIDOR':data[5],'IDPRODUCTO':data[6], 'DESCRIPCION':data[7],'IDMEDIDA':data[8],'CANTIDAD':data[9]})
         return JsonResponse(data_json, safe=False)


class ApproveOrdersLogDetailFitosanidadAJS(View):
     def get(self, request, *args, **kwargs):

         idorder = self.kwargs.get('idorder')

         with connection_inversioneajs.cursor() as cursor:
             cursor.execute("SELECT R.IDRECOMENDACIONAPL,CONVERT(varchar, R.fecha_apl, 105) AS fecha_apl,R.IDESTADO,AR.DESCRIPCION AS AREA,RS.NOMBRE AS RESPONSABLE,R.IDCONSUMIDOR,DR.IDPRODUCTO,DR.DESCRIPCION,DR.IDMEDIDA,DR.CANTIDAD FROM RECOMENDACIONAPL R INNER JOIN DRECOMENDACIONAPL DR ON DR.IDRECOMENDACIONAPL = R.IDRECOMENDACIONAPL INNER JOIN RESPONSABLE RS ON RS.IDRESPONSABLE = R.IDRESPONSABLE INNER JOIN AREAS AR ON AR.IDAREA = R.idarea WHERE R.IDRECOMENDACIONAPL='"+idorder+"' ORDER BY item ASC")
             data_object = cursor.fetchall()
             cursor.close
         data_json = []
         for data in data_object:
             data_json.append({'fecha_apl':data[1],'AREA':data[3],'RESPONSABLE':data[4],'IDCONSUMIDOR':data[5],'IDPRODUCTO':data[6], 'DESCRIPCION':data[7],'IDMEDIDA':data[8],'CANTIDAD':data[9]})
         return JsonResponse(data_json, safe=False)






class UpdatefitosanidadCV(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return HttpResponse("ID de servicio no válido", status=400)

            portal_aei_user = User.objects.get(username=request.user.username)

            # Utilizar la conexión existente
            with connection_campoverde.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update RECOMENDACIONAPL SET IDESTADO='AP' where IDRECOMENDACIONAPL='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','Recomendacionapl','EDT_APLFITOSANITARIAS_DIARIO','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")
                    print(f"✅ Ejecutando update RECOMENDACIONAPL SET IDESTADO='AP' WHERE IDRECOMENDACIONAPL='{idservicio}'")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                    print(f"✅ Ejecutando EXEC ActualizarTablaVB '{idservicio}'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")
                    print(f"✅ Ejecutando EXEC ActualizarTablaAN '{idservicio}'")
                
                # Confirmar la transacción
                connection_campoverde.commit()
                print(f"✅ Transacción confirmada para ID: {idservicio}")
                    
            cursor.execute("SELECT IDRECOMENDACIONAPL,IDDOCUMENTO,IDSUCURSAL,IDALMACEN,SERIE,NUMERO,CONVERT(CHAR(8),FECHA,112) AS FECHA,IDESTADO,idarea,IDRESPONSABLE,IDCONSUMIDOR FROM RECOMENDACIONAPL WHERE IDRECOMENDACIONAPL='"+idservicio+"'")
            data_object = cursor.fetchall()

            cursor.execute("SELECT ITEM,IDPRODUCTO,DESCRIPCION,IDMEDIDA,CAST(TOTAL AS VARCHAR(17)) AS CANTIDAD,TC.IDCONSUMIDOR,TC.IDACTIVIDAD,TC.IDLABOR FROM DRECOMENDACIONAPL TD INNER JOIN RECOMENDACIONAPL TC ON TD.IDRECOMENDACIONAPL = TC.IDRECOMENDACIONAPL WHERE TC.IDRECOMENDACIONAPL='"+idservicio+"'")
            data_object_det = cursor.fetchall()
            
            # cursor.close
            data_json = []
            # connection_donluis.close()
            for data in data_object:
                data_json.append({'idreqinterno':data[0],'iddocumento':'REQ','idsucursal':data[2],
                                  'idalmacen':data[3],'serie':data[4],'numero':data[5],'fecha':data[6],'estado':data[7],'idarea':data[8],
                                  'idresponsable':data[9],
                                  'dreqinterno':[dict(zip([desc[0].swapcase() for desc in cursor.description], detalle)) for detalle in data_object_det]})
            
            print(data_json)
            return JsonResponse(data_json, safe=False)
            
        except DatabaseError as e:
            # Registra el error
            print(f"❌ Error en la base de datos: {str(e)}")
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos: " + str(e)}, status=500)
        except Exception as e:
            # Registra el error
            print(f"❌ Error inesperado: {str(e)}")
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado: " + str(e)}, status=500)


    
    
        
class UpdatefitosanidadAJS(View):
    def get(self, request, *args, **kwargs):
        try:
            # Recuperar el valor de idservicio que se utilizará como condición
            idservicio = self.kwargs.get('idservicio')

            # Obtener la acción de la solicitud
            accion = request.GET.get('accion', '')
            print("Acción recibida:", accion)
            print("Valor de idservicio:", idservicio)

            # Verificar si la acción es válida
            if accion not in ('aprobar', 'vb', 'anular'):
                return HttpResponse("Acción no válida", status=400)

            # Verificar que idservicio no esté vacío
            if not idservicio:
                return HttpResponse("ID de servicio no válido", status=400)

            portal_aei_user = User.objects.get(username=request.user.username)

            # Utilizar la conexión existente
            with connection_inversioneajs.cursor() as cursor:
                if accion == 'aprobar':
                    # Realiza la actualización en la base de datos para acción 'aprobar'
                    cursor.execute("update RECOMENDACIONAPL SET IDESTADO='AP' where IDRECOMENDACIONAPL='"+idservicio+"'")
                    cursor.execute("insert into LOGESTADOS values('001','"+idservicio+"','"+portal_aei_user.username+"','Recomendacionapl','EDT_APLFITOSANITARIAS_DIARIO','AP',GETDATE(),GETDATE(),'N','','"+portal_aei_user.username+"')")
                    print(f"✅ Ejecutando update RECOMENDACIONAPL SET IDESTADO='AP' WHERE IDRECOMENDACIONAPL='{idservicio}'")

                elif accion == 'vb':
                    # Realiza la actualización en la base de datos para acción 'vb'
                    cursor.execute("EXEC ActualizarTablaVB '"+idservicio+"'")
                    print(f"✅ Ejecutando EXEC ActualizarTablaVB '{idservicio}'")
                elif accion == 'anular':
                    # Realiza la actualización en la base de datos para acción 'anular'
                    cursor.execute("EXEC ActualizarTablaAN '"+idservicio+"'")
                    print(f"✅ Ejecutando EXEC ActualizarTablaAN '{idservicio}'")
                
                # Confirmar la transacción
                connection_inversioneajs.commit()
                print(f"✅ Transacción confirmada para ID: {idservicio}")
                    
            cursor.execute("SELECT IDRECOMENDACIONAPL,IDDOCUMENTO,IDSUCURSAL,IDALMACEN,SERIE,NUMERO,CONVERT(CHAR(8),FECHA,112) AS FECHA,IDESTADO,idarea,IDRESPONSABLE,IDCONSUMIDOR FROM RECOMENDACIONAPL WHERE IDRECOMENDACIONAPL='"+idservicio+"'")
            data_object = cursor.fetchall()

            cursor.execute("SELECT ITEM,IDPRODUCTO,DESCRIPCION,IDMEDIDA,CAST(TOTAL AS VARCHAR(17)) AS CANTIDAD,TC.IDCONSUMIDOR,TC.IDACTIVIDAD,TC.IDLABOR FROM DRECOMENDACIONAPL TD INNER JOIN RECOMENDACIONAPL TC ON TD.IDRECOMENDACIONAPL = TC.IDRECOMENDACIONAPL WHERE TC.IDRECOMENDACIONAPL='"+idservicio+"'")
            data_object_det = cursor.fetchall()
            
            # cursor.close
            data_json = []
            # connection_donluis.close()
            for data in data_object:
                data_json.append({'idreqinterno':data[0],'iddocumento':'REQ','idsucursal':data[2],
                                  'idalmacen':data[3],'serie':data[4],'numero':data[5],'fecha':data[6],'estado':data[7],'idarea':data[8],
                                  'idresponsable':data[9],
                                  'dreqinterno':[dict(zip([desc[0].swapcase() for desc in cursor.description], detalle)) for detalle in data_object_det]})
            
            print(data_json)
            return JsonResponse(data_json, safe=False)
            
        except DatabaseError as e:
            # Registra el error
            print(f"❌ Error en la base de datos: {str(e)}")
            logging.error("Error en la base de datos: " + str(e))
            return JsonResponse({"error": "Error en la base de datos: " + str(e)}, status=500)
        except Exception as e:
            # Registra el error
            print(f"❌ Error inesperado: {str(e)}")
            logging.error("Error inesperado: " + str(e))
            return JsonResponse({"error": "Error inesperado: " + str(e)}, status=500)

       
        


# Modulo - alamacén --fitosanidad || JHON GUTIERREZ
        
class Fitosanidad_almacen_nisira ( TemplateView):
    permission_required = 'gre'
    template_name = 'script/repo_nisira_almacen_donluis_fitosanidad.html'

class Repo_nisira_almacen_campoverde_fito ( TemplateView):
    permission_required = 'gre'
    template_name = 'script/repo_nisira_almacen_campoverde_fitosanidad.html'

class Repo_nisira_almacen_inversionesAJS_fito ( TemplateView):
    permission_required = 'gre'
    template_name = 'script/repo_nisira_almacen_inversionesAJS_fitosanidad.html'


# SPACE CALIDAD - JHON GUTIERREZ
class Space_calidad_poda ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/poda_calidad.html'


class Space_calidad_raleo ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/raleo_calidad.html'

# SPACE EVALUACIONES - JHON GUTIERREZ

class Space_evaluaciones_fitosanitarias ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_fitosanitarias.html'

class Space_evaluaciones_brotacion ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_brotacion.html'

class Space_evaluaciones_long_brote ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_long_brote.html'

class Space_evaluaciones_long_racimo ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_long_racimo.html'

class Space_evaluaciones_cont_racimo ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_cont_racimo.html'

class Space_evaluaciones_floracion_cuaja ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_floracion_cuaja.html'

class Space_evaluaciones_calibre_bayas ( TemplateView):
    permission_required = 'ver_reportes_space'
    template_name = 'space/evaluaciones_calibre_bayas.html'

class Recursos_humanos ( TemplateView):
    permission_required = ''
    template_name = 'rrhh/recursos_humanos.html'










class Libro_mayor_conta_script(View):
    def get(self, request, *args, **kwargs):

        with connection_donluis.cursor() as cursor:
            cursor.execute(" EXEC CONT_RPT_LIBROMAYOR_EXCEL_V1 '001','202401','202401','','',1,'A',1 ")
           
            data_object = cursor.fetchall()
            
        data_json = []
        for data in data_object:
            
            data_json.append({
                'IDCUENTA':data[0],
                'NOMBRE_CTA':data[1],
                'IDCCOSTO':data[2],
                'DESC_CCOSTO':data[3],
                'PERIODO':data[4],
                'ORIGEN':data[5],
                'VOUCHER':data[6],
                'FECHA':data[7],
                'DOCUMENTO':data[8],
                'GLOSA':data[9],
                'IDCABCONTA':data[10],
                'IDREF':data[11],
                'TABLAREF':data[12],
                'CARGO_MOF':data[13],
                'ABONO_MOF':data[14],
                'SALDO_MOF':data[15],
                'CARGO_MEX':data[16],
                'ABONO_MEX':data[17],
                'SALDO_MEX':data[18],
                'INI_CARGO_MOF':data[19],
                'INI_ABONO_MOF':data[20],
                'INI_CARGO_MEX':data[21],
                'INI_ABONO_MEX':data[22],
                'CARGO':data[23],
                'ABONO':data[24],
                'SALDO':data[25],
                'CARGO1':data[26],
                'ABONO1':data[27],
                'SALDO1':data[28],
                'IDOPERACION':data[29],
                'NOMBRE_OPERA':data[30],
                'NUMERO_OPERA':data[31],
                'IDCLIEPROV':data[32],
                'RAZONSOCIAL':data[33],
                'COD_MONEDA':data[34],
                'MONEDA':data[35],
                'REFERENCIA':data[36],
                'IDENTIFICADOR':data[37],
                'ORDEN':data[38],
                'FECHA_DOC':data[39],
                'IDACTIVO':data[40],
                'IDPRODUCTO':data[41],
                'RAZONSOCIAL2':data[42],
                'FECHA_REFERENCIA':data[43],
                'unidad_negocio':data[44],
                'observacion':data[45],
                'lote_ref':data[46],
                'cantidad':data[47],
                'item':data[48],
                'idconsumidor':data[49],
                'desc_consumidor':data[50],
                'idactividad':data[51],
                'desc_actividad':data[52],
                'idlabor':data[53],
                'desc_labor':data[54],
                'es_gasto_nodeducible':data[55],
                'PRODUCTO':data[56],
                'PRECIO_MOF':data[57],
                'PRECIO_MOEX':data[58],
                'IDCUENTA_EQUIVALENTE':data[59],
                'DESCRIPCION_EQUIVALENTE':data[60],
            })

         # Obtener parámetros de paginación
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 15))

        # Crear paginador
        paginator = Paginator(data_json, length)
        page_number = (start // length) + 1
        page = paginator.page(page_number)

        # Preparar datos para DataTables
        response = {
            "draw": int(request.GET.get('draw', 0)),
            "recordsTotal": paginator.count,
            "recordsFiltered": paginator.count,
            "data": list(page.object_list)
        }

        return JsonResponse(response)



class Libro_mayor_conta_cv_script(View):
    def get(self, request, *args, **kwargs):

        with connection_campoverde.cursor() as cursor:
            cursor.execute(" EXEC CONT_RPT_LIBROMAYOR_EXCEL_V1 '001','202401','202401','','',1,'A',1 ")
           
            data_object = cursor.fetchall()
            
        data_json = []
        for data in data_object:
            
            data_json.append({
                'IDCUENTA':data[0],
                'NOMBRE_CTA':data[1],
                'IDCCOSTO':data[2],
                'DESC_CCOSTO':data[3],
                'PERIODO':data[4],
                'ORIGEN':data[5],
                'VOUCHER':data[6],
                'FECHA':data[7],
                'DOCUMENTO':data[8],
                'GLOSA':data[9],
                'IDCABCONTA':data[10],
                'IDREF':data[11],
                'TABLAREF':data[12],
                'CARGO_MOF':data[13],
                'ABONO_MOF':data[14],
                'SALDO_MOF':data[15],
                'CARGO_MEX':data[16],
                'ABONO_MEX':data[17],
                'SALDO_MEX':data[18],
                'INI_CARGO_MOF':data[19],
                'INI_ABONO_MOF':data[20],
                'INI_CARGO_MEX':data[21],
                'INI_ABONO_MEX':data[22],
                'CARGO':data[23],
                'ABONO':data[24],
                'SALDO':data[25],
                'CARGO1':data[26],
                'ABONO1':data[27],
                'SALDO1':data[28],
                'IDOPERACION':data[29],
                'NOMBRE_OPERA':data[30],
                'NUMERO_OPERA':data[31],
                'IDCLIEPROV':data[32],
                'RAZONSOCIAL':data[33],
                'COD_MONEDA':data[34],
                'MONEDA':data[35],
                'REFERENCIA':data[36],
                'IDENTIFICADOR':data[37],
                'ORDEN':data[38],
                'FECHA_DOC':data[39],
                'IDACTIVO':data[40],
                'IDPRODUCTO':data[41],
                'RAZONSOCIAL2':data[42],
                'FECHA_REFERENCIA':data[43],
                'unidad_negocio':data[44],
                'observacion':data[45],
                'lote_ref':data[46],
                'cantidad':data[47],
                'item':data[48],
                'idconsumidor':data[49],
                'desc_consumidor':data[50],
                'idactividad':data[51],
                'desc_actividad':data[52],
                'idlabor':data[53],
                'desc_labor':data[54],
                'es_gasto_nodeducible':data[55],
                'PRODUCTO':data[56],
                'PRECIO_MOF':data[57],
                'PRECIO_MOEX':data[58],
                'IDCUENTA_EQUIVALENTE':data[59],
                'DESCRIPCION_EQUIVALENTE':data[60],
            })

         # Obtener parámetros de paginación
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 15))

        # Crear paginador
        paginator = Paginator(data_json, length)
        page_number = (start // length) + 1
        page = paginator.page(page_number)

        # Preparar datos para DataTables
        response = {
            "draw": int(request.GET.get('draw', 0)),
            "recordsTotal": paginator.count,
            "recordsFiltered": paginator.count,
            "data": list(page.object_list)
        }

        return JsonResponse(response)
    

class Libro_mayor_conta_ajs_script(View):
    def get(self, request, *args, **kwargs):

        with connection_inversioneajs.cursor() as cursor:
            cursor.execute(" EXEC CONT_RPT_LIBROMAYOR_EXCEL_V1 '001','202401','202401','','',1,'A',1 ")
           
            data_object = cursor.fetchall()
            
        data_json = []
        for data in data_object:
            
            data_json.append({
                'IDCUENTA':data[0],
                'NOMBRE_CTA':data[1],
                'IDCCOSTO':data[2],
                'DESC_CCOSTO':data[3],
                'PERIODO':data[4],
                'ORIGEN':data[5],
                'VOUCHER':data[6],
                'FECHA':data[7],
                'DOCUMENTO':data[8],
                'GLOSA':data[9],
                'IDCABCONTA':data[10],
                'IDREF':data[11],
                'TABLAREF':data[12],
                'CARGO_MOF':data[13],
                'ABONO_MOF':data[14],
                'SALDO_MOF':data[15],
                'CARGO_MEX':data[16],
                'ABONO_MEX':data[17],
                'SALDO_MEX':data[18],
                'INI_CARGO_MOF':data[19],
                'INI_ABONO_MOF':data[20],
                'INI_CARGO_MEX':data[21],
                'INI_ABONO_MEX':data[22],
                'CARGO':data[23],
                'ABONO':data[24],
                'SALDO':data[25],
                'CARGO1':data[26],
                'ABONO1':data[27],
                'SALDO1':data[28],
                'IDOPERACION':data[29],
                'NOMBRE_OPERA':data[30],
                'NUMERO_OPERA':data[31],
                'IDCLIEPROV':data[32],
                'RAZONSOCIAL':data[33],
                'COD_MONEDA':data[34],
                'MONEDA':data[35],
                'REFERENCIA':data[36],
                'IDENTIFICADOR':data[37],
                'ORDEN':data[38],
                'FECHA_DOC':data[39],
                'IDACTIVO':data[40],
                'IDPRODUCTO':data[41],
                'RAZONSOCIAL2':data[42],
                'FECHA_REFERENCIA':data[43],
                'unidad_negocio':data[44],
                'observacion':data[45],
                'lote_ref':data[46],
                'cantidad':data[47],
                'item':data[48],
                'idconsumidor':data[49],
                'desc_consumidor':data[50],
                'idactividad':data[51],
                'desc_actividad':data[52],
                'idlabor':data[53],
                'desc_labor':data[54],
                'es_gasto_nodeducible':data[55],
                'PRODUCTO':data[56],
                'PRECIO_MOF':data[57],
                'PRECIO_MOEX':data[58],
                'IDCUENTA_EQUIVALENTE':data[59],
                'DESCRIPCION_EQUIVALENTE':data[60],
            })

         # Obtener parámetros de paginación
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 15))

        # Crear paginador
        paginator = Paginator(data_json, length)
        page_number = (start // length) + 1
        page = paginator.page(page_number)

        # Preparar datos para DataTables
        response = {
            "draw": int(request.GET.get('draw', 0)),
            "recordsTotal": paginator.count,
            "recordsFiltered": paginator.count,
            "data": list(page.object_list)
        }

        return JsonResponse(response)
    




# ===============================
# NUEVOS DASHBOARDS DE APROBACIONES
# ===============================

class AprobacionesDashboardDonLuis(PermissionRequiredMixin, TemplateView):
    """Dashboard de aprobaciones para Don Luis"""
    permission_required = 'script.MODULO_APROBACIONES_DONLUIS'
    template_name = 'script/dashboard_aprobaciones_donluis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = 'Don Luis'
        context['empresa_codigo'] = 'donluis'
        
        # Obtener datos reales de la base de datos
        try:
            with connection_donluis.cursor() as cursor:
                # Fitosanidad - contar registros pendientes
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM FITOSANIDAD_ALMACEN
                """)
                fitosanidad_data = cursor.fetchone()
                
                # Requerimientos internos
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM REQUERIMIENTO_INTERNO
                """)
                requerimientos_data = cursor.fetchone()
                
                # Pedidos de compras
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM PEDIDO_COMPRA
                """)
                pedidos_compras_data = cursor.fetchone()
                
                # Pedidos de servicios
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM PEDIDO_SERVICIO
                """)
                pedidos_servicios_data = cursor.fetchone()
                
                # Ordenes de compras
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM ORDEN_COMPRA
                """)
                ordenes_compras_data = cursor.fetchone()
                
                # Ordenes de servicios
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM ORDEN_SERVICIO
                """)
                ordenes_servicios_data = cursor.fetchone()
                
        except Exception as e:
            # Si hay error, usar datos por defecto
            fitosanidad_data = (0, 0, 0)
            requerimientos_data = (0, 0, 0)
            pedidos_compras_data = (0, 0, 0)
            pedidos_servicios_data = (0, 0, 0)
            ordenes_compras_data = (0, 0, 0)
            ordenes_servicios_data = (0, 0, 0)
        
        # Definir los módulos disponibles para Don Luis con datos reales
        context['modulos'] = [
            {
                'nombre': 'Fitosanidad',
                'descripcion': 'Gestión de aprobaciones fitosanitarias',
                'icono': 'fa-leaf',
                'color': 'success',
                'url': 'fitosanidad',
                'permiso': 'script.MODULO_APROBACIONES_DONLUIS_FITOSANIDAD',
                'pendientes': fitosanidad_data[0] if fitosanidad_data else 0,
                'aprobados': fitosanidad_data[1] if fitosanidad_data else 0,
                'total': fitosanidad_data[2] if fitosanidad_data else 0
            },
            {
                'nombre': 'Requerimientos',
                'descripcion': 'Aprobación de requerimientos internos',
                'icono': 'fa-clipboard-list',
                'color': 'info',
                'url': 'req_internos',
                'permiso': 'script.MODULO_APROBACIONES_DONLUIS_REQUERIMIENTOS',
                'pendientes': requerimientos_data[0] if requerimientos_data else 0,
                'aprobados': requerimientos_data[1] if requerimientos_data else 0,
                'total': requerimientos_data[2] if requerimientos_data else 0
            },
            {
                'nombre': 'Pedidos de Compras',
                'descripcion': 'Aprobación de pedidos de compras',
                'icono': 'fa-shopping-cart',
                'color': 'warning',
                'url': 'approve_almacen',
                'permiso': 'script.MODULO_APROBACIONES_DONLUIS_PEDIDOS_COMPRAS',
                'pendientes': pedidos_compras_data[0] if pedidos_compras_data else 0,
                'aprobados': pedidos_compras_data[1] if pedidos_compras_data else 0,
                'total': pedidos_compras_data[2] if pedidos_compras_data else 0
            },
            {
                'nombre': 'Pedidos de Servicios',
                'descripcion': 'Aprobación de pedidos de servicios',
                'icono': 'fa-tools',
                'color': 'secondary',
                'url': 'approve_pservicios',
                'permiso': 'script.MODULO_APROBACIONES_DONLUIS_PEDIDOS_SERVICIOS',
                'pendientes': pedidos_servicios_data[0] if pedidos_servicios_data else 0,
                'aprobados': pedidos_servicios_data[1] if pedidos_servicios_data else 0,
                'total': pedidos_servicios_data[2] if pedidos_servicios_data else 0
            },
            {
                'nombre': 'Ordenes de Compras',
                'descripcion': 'Aprobación de órdenes de compras',
                'icono': 'fa-file-invoice-dollar',
                'color': 'primary',
                'url': 'approve_compras',
                'permiso': 'script.MODULO_APROBACIONES_DONLUIS_APROBACION_ORDENES',
                'pendientes': ordenes_compras_data[0] if ordenes_compras_data else 0,
                'aprobados': ordenes_compras_data[1] if ordenes_compras_data else 0,
                'total': ordenes_compras_data[2] if ordenes_compras_data else 0
            },
            {
                'nombre': 'Ordenes de Servicios',
                'descripcion': 'Aprobación de órdenes de servicios',
                'icono': 'fa-cogs',
                'color': 'dark',
                'url': 'approve_servicios',
                'permiso': 'script.MODULO_APROBACIONES_DONLUIS_APROBACION_ORDENES',
                'pendientes': ordenes_servicios_data[0] if ordenes_servicios_data else 0,
                'aprobados': ordenes_servicios_data[1] if ordenes_servicios_data else 0,
                'total': ordenes_servicios_data[2] if ordenes_servicios_data else 0
            }
        ]
        
        return context


class AprobacionesDashboardAJS(PermissionRequiredMixin, TemplateView):
    """Dashboard de aprobaciones para Inversiones AJS"""
    permission_required = 'script.MODULO_APROBACIONES_AJS'
    template_name = 'script/dashboard_aprobaciones_ajs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = 'Inversiones AJS'
        context['empresa_codigo'] = 'inversionesajs'
        
        # Obtener datos reales de la base de datos AJS
        try:
            with connection_inversioneajs.cursor() as cursor:
                # Fitosanidad
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM FITOSANIDAD_ALMACEN
                """)
                fitosanidad_data = cursor.fetchone()
                
                # Requerimientos internos
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM REQUERIMIENTO_INTERNO
                """)
                requerimientos_data = cursor.fetchone()
                
                # Pedidos de compras
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM PEDIDO_COMPRA
                """)
                pedidos_compras_data = cursor.fetchone()
                
                # Pedidos de servicios
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM PEDIDO_SERVICIO
                """)
                pedidos_servicios_data = cursor.fetchone()
                
                # Ordenes de compras
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM ORDEN_COMPRA
                """)
                ordenes_compras_data = cursor.fetchone()
                
                # Ordenes de servicios
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM ORDEN_SERVICIO
                """)
                ordenes_servicios_data = cursor.fetchone()
                
        except Exception as e:
            # Si hay error, usar datos por defecto
            fitosanidad_data = (0, 0, 0)
            requerimientos_data = (0, 0, 0)
            pedidos_compras_data = (0, 0, 0)
            pedidos_servicios_data = (0, 0, 0)
            ordenes_compras_data = (0, 0, 0)
            ordenes_servicios_data = (0, 0, 0)
        
        # Definir los módulos disponibles para AJS con datos reales
        context['modulos'] = [
            {
                'nombre': 'Fitosanidad AJS',
                'descripcion': 'Gestión de aprobaciones fitosanitarias',
                'icono': 'fa-leaf',
                'color': 'success',
                'url': 'fitosanidad_ajs',
                'permiso': 'script.MODULO_APROBACIONES_AJS_FITOSANIDAD',
                'pendientes': fitosanidad_data[0] if fitosanidad_data else 0,
                'aprobados': fitosanidad_data[1] if fitosanidad_data else 0,
                'total': fitosanidad_data[2] if fitosanidad_data else 0
            },
            {
                'nombre': 'Requerimientos AJS',
                'descripcion': 'Aprobación de requerimientos internos',
                'icono': 'fa-clipboard-list',
                'color': 'info',
                'url': 'req_internos_ajs',
                'permiso': 'script.MODULO_APROBACIONES_AJS_REQUERIMIENTOS',
                'pendientes': requerimientos_data[0] if requerimientos_data else 0,
                'aprobados': requerimientos_data[1] if requerimientos_data else 0,
                'total': requerimientos_data[2] if requerimientos_data else 0
            },
            {
                'nombre': 'Pedidos de Compras AJS',
                'descripcion': 'Aprobación de pedidos de compras',
                'icono': 'fa-shopping-cart',
                'color': 'warning',
                'url': 'approve_almacen_ajs',
                'permiso': 'script.MODULO_APROBACIONES_AJS_PEDIDOS_COMPRAS',
                'pendientes': pedidos_compras_data[0] if pedidos_compras_data else 0,
                'aprobados': pedidos_compras_data[1] if pedidos_compras_data else 0,
                'total': pedidos_compras_data[2] if pedidos_compras_data else 0
            },
            {
                'nombre': 'Pedidos de Servicios AJS',
                'descripcion': 'Aprobación de pedidos de servicios',
                'icono': 'fa-tools',
                'color': 'secondary',
                'url': 'approve_pservicios_ajs',
                'permiso': 'script.MODULO_APROBACIONES_AJS_PEDIDOS_SERVICIOS',
                'pendientes': pedidos_servicios_data[0] if pedidos_servicios_data else 0,
                'aprobados': pedidos_servicios_data[1] if pedidos_servicios_data else 0,
                'total': pedidos_servicios_data[2] if pedidos_servicios_data else 0
            },
            {
                'nombre': 'Ordenes de Compras AJS',
                'descripcion': 'Aprobación de órdenes de compras',
                'icono': 'fa-file-invoice-dollar',
                'color': 'primary',
                'url': 'approve_compras_ajs',
                'permiso': 'script.MODULO_APROBACIONES_AJS_APROBACION_ORDENES',
                'pendientes': ordenes_compras_data[0] if ordenes_compras_data else 0,
                'aprobados': ordenes_compras_data[1] if ordenes_compras_data else 0,
                'total': ordenes_compras_data[2] if ordenes_compras_data else 0
            },
            {
                'nombre': 'Ordenes de Servicios AJS',
                'descripcion': 'Aprobación de órdenes de servicios',
                'icono': 'fa-cogs',
                'color': 'dark',
                'url': 'approve_servicios_ajs',
                'permiso': 'script.MODULO_APROBACIONES_AJS_APROBACION_ORDENES',
                'pendientes': ordenes_servicios_data[0] if ordenes_servicios_data else 0,
                'aprobados': ordenes_servicios_data[1] if ordenes_servicios_data else 0,
                'total': ordenes_servicios_data[2] if ordenes_servicios_data else 0
            }
        ]
        
        return context


class AprobacionesDashboardCampoVerde(PermissionRequiredMixin, TemplateView):
    """Dashboard de aprobaciones para Campo Verde"""
    permission_required = 'script.MODULO_APROBACIONES_CV'
    template_name = 'script/dashboard_aprobaciones_campoverde.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = 'Campo Verde'
        context['empresa_codigo'] = 'campoverde'
        
        # Obtener datos reales de la base de datos Campo Verde
        try:
            with connection_campoverde.cursor() as cursor:
                # Fitosanidad
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM FITOSANIDAD_ALMACEN
                """)
                fitosanidad_data = cursor.fetchone()
                
                # Requerimientos internos
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM REQUERIMIENTO_INTERNO
                """)
                requerimientos_data = cursor.fetchone()
                
                # Pedidos de compras
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM PEDIDO_COMPRA
                """)
                pedidos_compras_data = cursor.fetchone()
                
                # Pedidos de servicios
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM PEDIDO_SERVICIO
                """)
                pedidos_servicios_data = cursor.fetchone()
                
                # Ordenes de compras
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM ORDEN_COMPRA
                """)
                ordenes_compras_data = cursor.fetchone()
                
                # Ordenes de servicios
                cursor.execute("""
                    SELECT 
                        COUNT(CASE WHEN ESTADO = 'PENDIENTE' THEN 1 END) as pendientes,
                        COUNT(CASE WHEN ESTADO = 'APROBADO' THEN 1 END) as aprobados,
                        COUNT(*) as total
                    FROM ORDEN_SERVICIO
                """)
                ordenes_servicios_data = cursor.fetchone()
                
        except Exception as e:
            # Si hay error, usar datos por defecto
            fitosanidad_data = (0, 0, 0)
            requerimientos_data = (0, 0, 0)
            pedidos_compras_data = (0, 0, 0)
            pedidos_servicios_data = (0, 0, 0)
            ordenes_compras_data = (0, 0, 0)
            ordenes_servicios_data = (0, 0, 0)
        
        # Definir los módulos disponibles para Campo Verde con datos reales
        context['modulos'] = [
            {
                'nombre': 'Fitosanidad CV',
                'descripcion': 'Gestión de aprobaciones fitosanitarias',
                'icono': 'fa-leaf',
                'color': 'success',
                'url': 'fitosanidad_cv',
                'permiso': 'script.MODULO_APROBACIONES_CV_FITOSANIDAD',
                'pendientes': fitosanidad_data[0] if fitosanidad_data else 0,
                'aprobados': fitosanidad_data[1] if fitosanidad_data else 0,
                'total': fitosanidad_data[2] if fitosanidad_data else 0
            },
            {
                'nombre': 'Requerimientos CV',
                'descripcion': 'Aprobación de requerimientos internos',
                'icono': 'fa-clipboard-list',
                'color': 'info',
                'url': 'req_internos_cv',
                'permiso': 'script.MODULO_APROBACIONES_CV_REQUERIMIENTOS',
                'pendientes': requerimientos_data[0] if requerimientos_data else 0,
                'aprobados': requerimientos_data[1] if requerimientos_data else 0,
                'total': requerimientos_data[2] if requerimientos_data else 0
            },
            {
                'nombre': 'Pedidos de Compras CV',
                'descripcion': 'Aprobación de pedidos de compras',
                'icono': 'fa-shopping-cart',
                'color': 'warning',
                'url': 'approve_almacen_cv',
                'permiso': 'script.MODULO_APROBACIONES_CV_PEDIDOS_COMPRAS',
                'pendientes': pedidos_compras_data[0] if pedidos_compras_data else 0,
                'aprobados': pedidos_compras_data[1] if pedidos_compras_data else 0,
                'total': pedidos_compras_data[2] if pedidos_compras_data else 0
            },
            {
                'nombre': 'Pedidos de Servicios CV',
                'descripcion': 'Aprobación de pedidos de servicios',
                'icono': 'fa-tools',
                'color': 'secondary',
                'url': 'approve_pservicios_cv',
                'permiso': 'script.MODULO_APROBACIONES_CV_PEDIDOS_SERVICIOS',
                'pendientes': pedidos_servicios_data[0] if pedidos_servicios_data else 0,
                'aprobados': pedidos_servicios_data[1] if pedidos_servicios_data else 0,
                'total': pedidos_servicios_data[2] if pedidos_servicios_data else 0
            },
            {
                'nombre': 'Ordenes de Compras CV',
                'descripcion': 'Aprobación de órdenes de compras',
                'icono': 'fa-file-invoice-dollar',
                'color': 'primary',
                'url': 'approve_compras_cv',
                'permiso': 'script.MODULO_APROBACIONES_CV_APROBACION_ORDENES',
                'pendientes': ordenes_compras_data[0] if ordenes_compras_data else 0,
                'aprobados': ordenes_compras_data[1] if ordenes_compras_data else 0,
                'total': ordenes_compras_data[2] if ordenes_compras_data else 0
            },
            {
                'nombre': 'Ordenes de Servicios CV',
                'descripcion': 'Aprobación de órdenes de servicios',
                'icono': 'fa-cogs',
                'color': 'dark',
                'url': 'approve_servicios_cv',
                'permiso': 'script.MODULO_APROBACIONES_CV_APROBACION_ORDENES',
                'pendientes': ordenes_servicios_data[0] if ordenes_servicios_data else 0,
                'aprobados': ordenes_servicios_data[1] if ordenes_servicios_data else 0,
                'total': ordenes_servicios_data[2] if ordenes_servicios_data else 0
            }
        ]
        
        return context