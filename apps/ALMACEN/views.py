from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from apps.connection.connect_donluis import connection_donluis
from apps.connection.connect_campoverde import connection_campoverde
from apps.connection.connect_inversioneajs import connection_inversioneajs
from apps.connection.connect_donluis_prueba import connection_donluis_prueba
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.connection.connect_portalaei import connection_portalaei
from decimal import Decimal
import json
from django.db import connection
from django.db import IntegrityError
from django.db import transaction
from datetime import datetime, date
import traceback









# Create your views here.

#=================================================================================================================
#MODULO PRESUPUESTOS
#AUTOR: JHON GUTIERREZ
#FECHA: 06/01/2025
#MODIFICACIONES: 
# 06/01/2025: Se crea el modulo de presupuestos
#=================================================================================================================



class req_internos_dl(TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_req_interno_dl.html'


class req_internos_don_luis (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_req_internos_dl.html'


#****** REQUIRIMIENTO CAMPO VERDE *******
class req_internos_campo_verde (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_req_internos_cv.html'



#****** REQUIRIMIENTO INVERSIONES AJS *******
class req_internos_ajs (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_req_internos_ajs.html'
    
# PRESUPUESTO

class presupuesto_dl(TemplateView):
    permission_required = 'modulo_almacen'
    template_name = 'ALMACEN/pages/almacen_presupuesto_dl.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return context

#==============================================================================================
# ROTACION DE PRODUCTOS
# AUTOR: JHON GUTIERREZ
#==============================================================================================

class rotacion_productos_dl (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_rotacion_productos_dl.html'


#==============================================================================================
# ROTACION DE PRODUCTOS - CAMPO VERDE
# AUTOR: YERSON GARCIA
#==============================================================================================

class rotacion_productos_cv (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_rotacion_productos_cv.html'

#==============================================================================================
# REPORTE DE ROTACION DE PRODUCTOS
# AUTOR: JHON GUTIERREZ
#==============================================================================================



@method_decorator(csrf_exempt, name='dispatch')
class RotacionProductosView(View):
    """
    Vista para el reporte de rotación de productos
    Ejecuta el procedimiento SP_OBTENER_SALIDAS_POR_RANGO_FECHAS
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener parámetros de la solicitud
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            print(f"🔍 Rotación de productos - Parámetros recibidos:")
            print(f"   - Fecha inicio: {fecha_inicio}")
            print(f"   - Fecha fin: {fecha_fin}")
            
            # Validar parámetros obligatorios
            if not fecha_inicio or not fecha_fin:
                return JsonResponse({
                    'success': False,
                    'message': 'Las fechas de inicio y fin son obligatorias'
                }, status=400)
            
            # Ejecutar consulta
            resultados, estadisticas = self._ejecutar_procedimiento_rotacion(fecha_inicio, fecha_fin)
            
            # Retornar datos en JSON
            return JsonResponse({
                'success': True,
                'data': resultados,
                'estadisticas': estadisticas,
                'info': {
                    'total_registros': len(resultados),
                    'fecha_consulta': fecha_inicio + ' al ' + fecha_fin,
                    'procedimiento': 'SP_OBTENER_SALIDAS_POR_RANGO_FECHAS'
                }
            })
            
        except Exception as e:
            print(f"❌ Error en RotacionProductosView: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def _ejecutar_procedimiento_rotacion(self, fecha_inicio, fecha_fin):
        """
        Ejecuta el procedimiento almacenado SP_OBTENER_SALIDAS_POR_RANGO_FECHAS
        """
        try:
            cursor = connection_donluis.cursor()
            
            print(f"🔄 Ejecutando procedimiento SP_OBTENER_SALIDAS_POR_RANGO_FECHAS...")
            
            # Ejecutar el procedimiento almacenado
            cursor.execute("""
                EXEC SP_OBTENER_SALIDAS_POR_RANGO_FECHAS 
                    @FECHA_INICIO = ?, 
                    @FECHA_FIN = ?
            """, [fecha_inicio, fecha_fin])
            
            # Obtener los resultados principales
            columns = [desc[0] for desc in cursor.description]
            resultados_raw = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(resultados_raw)} productos")
            
            # Convertir resultados a lista de diccionarios
            resultados = []
            for row in resultados_raw:
                resultado = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fechas
                    if isinstance(value, datetime) and value:
                        resultado[column_name] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, date) and value:
                        resultado[column_name] = value.strftime('%Y-%m-%d')
                    else:
                        # Limpiar strings
                        if isinstance(value, str):
                            resultado[column_name] = value.strip()
                        else:
                            resultado[column_name] = value
                
                resultados.append(resultado)
            
            # Obtener estadísticas (segundo conjunto de resultados)
            cursor.nextset()
            estadisticas = {}
            if cursor.description:
                stats_columns = [desc[0] for desc in cursor.description]
                stats_row = cursor.fetchone()
                
                if stats_row:
                    for i, value in enumerate(stats_row):
                        estadisticas[stats_columns[i]] = value
            
            cursor.close()
            return resultados, estadisticas
            
        except Exception as e:
            print(f"❌ Error ejecutando procedimiento: {str(e)}")
            raise



#==============================================================================================
# REPORTE DE ROTACION DE PRODUCTOS - CAMPO VERDE
# AUTOR: YERSON GARCIA
#==============================================================================================


@method_decorator(csrf_exempt, name='dispatch')
class RotacionProductosViewCV(View):
    """
    Vista para el reporte de rotación de productos
    Ejecuta el procedimiento SP_OBTENER_SALIDAS_POR_RANGO_FECHAS
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener parámetros de la solicitud
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            print(f"🔍 Rotación de productos - Parámetros recibidos:")
            print(f"   - Fecha inicio: {fecha_inicio}")
            print(f"   - Fecha fin: {fecha_fin}")
            
            # Validar parámetros obligatorios
            if not fecha_inicio or not fecha_fin:
                return JsonResponse({
                    'success': False,
                    'message': 'Las fechas de inicio y fin son obligatorias'
                }, status=400)
            
            # Ejecutar consulta
            resultados, estadisticas = self._ejecutar_procedimiento_rotacion(fecha_inicio, fecha_fin)
            
            # Retornar datos en JSON
            return JsonResponse({
                'success': True,
                'data': resultados,
                'estadisticas': estadisticas,
                'info': {
                    'total_registros': len(resultados),
                    'fecha_consulta': fecha_inicio + ' al ' + fecha_fin,
                    'procedimiento': 'SP_OBTENER_SALIDAS_POR_RANGO_FECHAS'
                }
            })
            
        except Exception as e:
            print(f"❌ Error en RotacionProductosView: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def _ejecutar_procedimiento_rotacion(self, fecha_inicio, fecha_fin):
        """
        Ejecuta el procedimiento almacenado SP_OBTENER_SALIDAS_POR_RANGO_FECHAS
        """
        try:
            cursor = connection_campoverde.cursor()
            
            print(f"🔄 Ejecutando procedimiento SP_OBTENER_SALIDAS_POR_RANGO_FECHAS...")
            
            # Ejecutar el procedimiento almacenado
            cursor.execute("""
                EXEC SP_OBTENER_SALIDAS_POR_RANGO_FECHAS 
                    @FECHA_INICIO = ?, 
                    @FECHA_FIN = ?
            """, [fecha_inicio, fecha_fin])
            
            # Obtener los resultados principales
            columns = [desc[0] for desc in cursor.description]
            resultados_raw = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(resultados_raw)} productos")
            
            # Convertir resultados a lista de diccionarios
            resultados = []
            for row in resultados_raw:
                resultado = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fechas
                    if isinstance(value, datetime) and value:
                        resultado[column_name] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, date) and value:
                        resultado[column_name] = value.strftime('%Y-%m-%d')
                    else:
                        # Limpiar strings
                        if isinstance(value, str):
                            resultado[column_name] = value.strip()
                        else:
                            resultado[column_name] = value
                
                resultados.append(resultado)
            
            # Obtener estadísticas (segundo conjunto de resultados)
            cursor.nextset()
            estadisticas = {}
            if cursor.description:
                stats_columns = [desc[0] for desc in cursor.description]
                stats_row = cursor.fetchone()
                
                if stats_row:
                    for i, value in enumerate(stats_row):
                        estadisticas[stats_columns[i]] = value
            
            cursor.close()
            return resultados, estadisticas
            
        except Exception as e:
            print(f"❌ Error ejecutando procedimiento: {str(e)}")
            raise










#==============================================================================================
# SERVICIOS
# AUTOR: JHON GUTIERREZ
#==============================================================================================

#REPORTE DE TOTALES DE SERVICIOS

def Costo_servicio_totals(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:

        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '8', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '8'
            """)

        # Obtener los nombres de las columnas
        columns = [col[0] for col in cursor.description]

        # Obtener la primera fila
        row = cursor.fetchone()

        results = {}

        if row:
            for i, value in enumerate(row):
                if isinstance(value, Decimal):
                    value = float(value)
                results[columns[i]] = value if value is not None else 0

    return JsonResponse(results)




# CRUD DE SERVICIOS
@method_decorator(csrf_exempt, name='dispatch')
class Costo_Servicios_dlView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Verificar si ya existe la observación para esta área
            check_query = """
            SELECT COUNT(*) 
                FROM TIC_servicios 
                WHERE observacion = ? 
                AND id_area = ? 
                AND observacion IS NOT NULL
            """
            observacion = data.get('observacion', '').strip()  # Eliminar espacios en blanco
            area_id = data.get('id_area', 8)
            if observacion:  # Solo verificar si hay una observación
                cursor.execute(check_query, [observacion, area_id])
                result = cursor.fetchone()
                count = result[0] if result else 0
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)

                id_campania = data.get('ID_CAMPANIA')

            
            query = """
            INSERT INTO TIC_servicios (
                idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO,id_area, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Valores base
            values = [
                data['idproducto'],
                data['grupo_servicio'],
                data['subgrupo_servicio'],
                data['descripcion'],
                float(data.get('precio_unitario', 0)),
                data.get('observacion', ''),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = int(data.get(f'{mes}_cantidad', 0))
                precio = cantidad * float(data.get('precio_unitario', 0))
                values.extend([cantidad, precio])
            
            # Agregar usuario
            """ nombre_usuario = f"{request.user.first_name} {request.user.last_name}".strip()
            if not nombre_usuario:
                nombre_usuario = request.user.username
            values.append(nombre_usuario) """
            
            values.append(request.user.id) # ID DEL USUARIO
            values.append(8) # ID DEL AREA 
            values.append(id_campania) # ID DE LA CAMPANIA


            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio registrado correctamente'})
        
        
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Ya existe un servicio con esta observación en esta área'
            }, status=400)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            campania = request.GET.get('year', '')

            if id:
                query = """
                SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_servicios
                WHERE id = ?  AND id_area = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_servicios 
                    WHERE id_area = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_servicios 
                    WHERE id_area = 8
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM TIC_servicios WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM TIC_servicios WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

             # Verificar si ya existe la observación para esta área (excluyendo el registro actual)
            check_query = """
            SELECT COUNT(*) 
            FROM TIC_servicios 
            WHERE observacion = ? 
            AND id_area = ? 
            AND id != ?
            AND observacion IS NOT NULL
            """
            observacion = data.get('observacion', '').strip()
            area_id = data.get('id_area', 8)
            if observacion:
                cursor.execute(check_query, [observacion, area_id, id])
                result = cursor.fetchone()
                count = result[0] if result else 0
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)
            
            cursor.execute("SELECT id FROM TIC_servicios WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            
            query = """
            UPDATE TIC_servicios
            SET idproducto = ?, grupo_servicio = ?, subgrupo_servicio = ?, descripcion = ?, precio_unitario = ?, observacion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?
            WHERE id = ?
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['grupo_servicio'],
                data['subgrupo_servicio'],
                data['descripcion'],
                precio_unitario,
                data.get('observacion', ''),
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = int(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            
            values.extend([request.user.id,8, id])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio actualizado correctamente'})
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Ya existe un servicio con esta observación en esta área'
            }, status=400)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#==============================================================================================
# SUMINISTROS
# AUTOR: JHON GUTIERREZ
#==============================================================================================



#REPORTE DE TOTALES DE SUMINISTROS

def Costos_suministros_totals_dl(request):

    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:
        if campania:
            cursor.execute("EXEC RPT_PST_SUMINISTROS %s, %s", [8, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS %s", [8])

        rows = cursor.fetchall()

    results = {k: v for (k, v) in rows}
    return JsonResponse(results)

#TIPOS DE SUMINISTROS


@method_decorator(csrf_exempt, name='dispatch')
class CombustiblesLubricantesView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,1,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    
    # El método GET 

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parametro de campaña del request
            campania = request.GET.get('year', '')
            
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 1
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 1
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 1
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,1])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     

@method_decorator(csrf_exempt, name='dispatch')
class UtilesOficinaView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,5,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET 

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? 
                AND id_area = 8
                AND id_tipo_suministro = 5 
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Obtener el parametro de campaña del request
                campania = request.GET.get('year', '')
                
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 5
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})



    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ?
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,5])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EquiposComputoView(View): 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            


            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,7,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 7
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 7
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? 
            AND id_area = 8
            AND id_tipo_suministro = 7
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,7])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@method_decorator(csrf_exempt, name='dispatch')
class OtrosSuministrosView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8,id_campania])

            # Agregar el nombre completo del usuario al final de la lista de valores
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 8
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8])


            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MaterialConstruccionView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,4,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 4
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 4
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 4
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,4])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

@method_decorator(csrf_exempt, name='dispatch')
class RepuestosAccesoriosView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,2,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 2
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 2
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
            try:
                data = json.loads(request.body)
                cursor = connection_portalaei.cursor()
                
                # Primero, verificamos si el producto existe
                cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
                if cursor.fetchone() is None:
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
                
                # Si el producto existe, lo actualizamos
                query = """
                    UPDATE TIC_suministros
                SET idproducto = ?, descripcion = ?,
                    enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                    marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                    mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                    julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                    septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                    noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                    USUARIO = ?, id_area = ?, id_tipo_suministro = ?
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 2
                """
                
                precio_unitario = float(data.get('precio_unitario', 0))
                values = [
                    data['idproducto'],
                    data['descripcion'],
                ]
                
                for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                    cantidad = float(data.get(f'{mes}_cantidad', 0))
                    precio = precio_unitario * cantidad if cantidad > 0 else 0
                    values.extend([cantidad, precio])

                # Agregar el nombre completo del usuario al final de la lista de valores
                values.extend([request.user.id,8,2])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     

@method_decorator(csrf_exempt, name='dispatch')
class EquiposUITView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,9,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 9
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 9
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
            try:
                data = json.loads(request.body)
                cursor = connection_portalaei.cursor()
                
                # Primero, verificamos si el producto existe
                cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
                if cursor.fetchone() is None:
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
                
                # Si el producto existe, lo actualizamos
                query = """
                    UPDATE TIC_suministros
                SET idproducto = ?, descripcion = ?,
                    enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                    marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                    mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                    julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                    septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                    noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                    USUARIO = ?, id_area = ?, id_tipo_suministro = ?
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 9
                """
                
                precio_unitario = float(data.get('precio_unitario', 0))
                values = [
                    data['idproducto'],
                    data['descripcion'],
                ]
                
                for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                    cantidad = float(data.get(f'{mes}_cantidad', 0))
                    precio = precio_unitario * cantidad if cantidad > 0 else 0
                    values.extend([cantidad, precio])

                # Agregar el nombre completo del usuario al final de la lista de valores
                values.extend([request.user.id,8,9])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
       

@method_decorator(csrf_exempt, name='dispatch')
class MaterialesAgriculturaView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,3,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})



    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 3
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 3
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 3
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,3])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
  

@method_decorator(csrf_exempt, name='dispatch')
class EquiposProteccionView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO TIC_suministros (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,6,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})


    
    # El método GET permanece sin cambios

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 6
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 8 AND id_tipo_suministro = 6
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 8 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_suministros WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_suministros WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_suministros
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 6
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,6])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     




#==============================================================================================
# MODULO: CAPEX
# AUTOR: JHON GUTIERREZ
# FECHA: 27/11/2024
#==============================================================================================


def Costos_capex_totals(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            EXEC RPT_PST_CAPEX '8'

        """)
        
        # Obtener los nombres de las columnas
        columns = [col[0] for col in cursor.description]
        # Obtener la primera fila de resultados
        row = cursor.fetchone()
        
        # Crear el diccionario combinando columnas con valores
        results = {}
        if row:
            for i, value in enumerate(row):
                # Convertir Decimal a float si es necesario
                if isinstance(value, Decimal):
                    value = float(value)
                results[columns[i]] = value if value is not None else 0
                
    return JsonResponse(results)


@method_decorator(csrf_exempt, name='dispatch')
class CapexView(View):


    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            idproducto = data.get('idproducto')
            id_area = data.get('id_area', 8)
            id_campania = data.get('ID_CAMPANIA')

            if idproducto == '11111111111':
                # Para productos nuevos, validar que tenga observación
                observacion = data.get('observacion', '').strip()
                if not observacion:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'La observación es requerida para productos nuevos'
                    }, status=400)
            else:
                # Para productos normales, verificar que no exista el mismo producto en la misma área
                check_query = """
                SELECT COUNT(*) 
                FROM TIC_capex 
                WHERE idproducto = ? 
                AND id_area = ?
                AND idproducto <> '11111111111'
                """
                cursor.execute(check_query, [idproducto, id_area])
                result = cursor.fetchone()
                count = result[0] if result else 0
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Este producto ya existe en esta área. Por favor, seleccione un producto diferente.'
                    }, status=400)
            
            # Continuar con la inserción si pasa las validaciones
            query = """
            INSERT INTO TIC_capex (
                idproducto, descripcion, precio_unitario, observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO, id_area, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                idproducto,
                data['descripcion'],
                precio_unitario,
                data.get('observacion', ''),  # Puede ser vacío si no es producto nuevo
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            values.extend([request.user.id, id_area, id_campania])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'CAPEX registrado correctamente'})
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # El método GET permanece sin cambios
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parametro de campaña del request
            campania = request.GET.get('year', '')
            
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,observacion
                FROM TIC_capex
                WHERE id = ? AND id_area = 8 
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                           observacion
                    FROM TIC_capex
                    WHERE id_area = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                           observacion
                    FROM TIC_capex
                    WHERE id_area = 8
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_capex WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM TIC_capex WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM TIC_capex WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE TIC_capex
            SET idproducto = ?, descripcion = ?, precio_unitario = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, observacion = ?
            WHERE id = ? AND id_area = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            # Procesar los meses
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar usuario, área y observación
            values.extend([
                request.user.id,
                8,
                data.get('observacion', '')  # Movido aquí para coincidir con el orden del query
            ])
            
            # Agregar el id al final
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



#==============================================================================================
# MODULO: REMUNERACION
# AUTOR: JHON GUTIERREZ
# FECHA: 27/11/2024
#==============================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CostoSueldosView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            id_campania = data.get('ID_CAMPANIA')

            query = """
            INSERT INTO tb_remuneracion (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?, ?)
            """

            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                1,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id_campania # ID_CAMPANIA
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Sueldo registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM tb_remuneracion
                WHERE id = ? AND id_area = 8 AND id_remuneracion = 1
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            else:
                campania = request.GET.get('year', '')
                print(f"DEBUG SUELDOS: Recibido year={campania}, GET params={dict(request.GET)}")
                
                # Primero verificar qué valores de ID_CAMPANIA existen
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 8 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 8 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    print(f"DEBUG SUELDOS: Ejecutando query con campania={campania}")
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 8 AND id_remuneracion = 1
                    """
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                print(f"DEBUG SUELDOS: Encontrados {len(data)} registros")
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            print(f"DEBUG SUELDOS ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM tb_remuneracion WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM tb_remuneracion WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Sueldo eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM tb_remuneracion WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')

            query = """
            UPDATE tb_remuneracion
            SET dni = ?, nombre = ?, regimen_laboral = ?, cargo = ?, fecha_ingreso = ?,
                enero = ?, febrero = ?, marzo = ?, abril = ?, mayo = ?, junio = ?,
                julio = ?, agosto = ?, septiembre = ?, octubre = ?, noviembre = ?, diciembre = ?,
                asignacion = ?, USUARIO = ?, id_area = ?, id_remuneracion = ?, fecha = GETDATE(), vacacion = ?
            WHERE id = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario y id
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                1,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id # id
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSueldos(View):
     def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [8, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [8, 1])
                        # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            # Obtener los resultados
            results = cursor.fetchall()
            # Convertir los resultados a un diccionario y asegurar que 'id' esté presente
            data = []
            for row in results:
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                # Si no existe 'id', agregarlo como None
                if 'id' not in item:
                    item['id'] = None
                data.append(item)
            cursor.close()
            return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class CostoSalariosView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            id_campania = data.get('ID_CAMPANIA')

            query = """
            INSERT INTO tb_remuneracion (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?, ?)
            """
                
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                2,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id_campania # ID_CAMPANIA
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM tb_remuneracion
                WHERE id = ? AND id_area = 8 AND id_remuneracion = 2
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            else:
                campania = request.GET.get('year', '')
                print(f"DEBUG SALARIOS: Recibido year={campania}, GET params={dict(request.GET)}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 8 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 8 AND id_remuneracion = 2
                    """
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                print(f"DEBUG SALARIOS: Encontrados {len(data)} registros")
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            print(f"DEBUG SALARIOS ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM tb_remuneracion WHERE id = ? ", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM tb_remuneracion WHERE id = ? ", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM tb_remuneracion WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')

            query = """
            UPDATE tb_remuneracion
            SET dni = ?, nombre = ?, regimen_laboral = ?, cargo = ?, fecha_ingreso = ?,
                enero = ?, febrero = ?, marzo = ?, abril = ?, mayo = ?, junio = ?,
                julio = ?, agosto = ?, septiembre = ?, octubre = ?, noviembre = ?, diciembre = ?,
                asignacion = ?, USUARIO = ?, id_area = ?, id_remuneracion = ?, fecha = GETDATE(), vacacion = ?
            WHERE id = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario y id
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                2,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id # id
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSalarios(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [8, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [8, 2])
                        
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener los resultados
            results = cursor.fetchall()
            
            # Convertir los resultados a un diccionario
            data = []
            for row in results:
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                data.append(item)
            
            cursor.close()
            return JsonResponse({"data": data})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)





#====================================================================================================================
    #EVALUACION DE DESEMPEÑO
#====================================================================================================================

class evaluacion_desempeño(TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/components/DonLuis/eva_desempeno/rrhh_evaluacion_desempeño.html'


class ObjetivosEvaluacionView(View):
    @transaction.atomic
    
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro de periodo desde la URL (año)
            periodo = request.GET.get('campania', None)  # Mantener 'campania' como nombre del parámetro para compatibilidad
            
            # Si no se proporciona periodo, usar el año actual
            if not periodo:
                from datetime import date
                periodo = str(date.today().year)
            
            # Extraer solo el año si viene en formato CAMP2026
            if periodo.startswith('CAMP'):
                periodo = periodo.replace('CAMP', '')
            
            try:
            # Ejecutar el procedimiento almacenado con el área 4 hardcodeada
                cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @periodo=?", [8, periodo])
            
            except Exception as sp_error:
                # Si el procedimiento falla, usar una consulta directa
                print(f"Error en procedimiento almacenado: {sp_error}")
                cursor.execute("""
                    SELECT 
                        e.id,
                        e.id_evaluador,
                        e.id_evaluado,
                        e.id_area,
                        e.periodo,
                        u1.first_name + ' ' + u1.last_name as evaluador,
                        u2.first_name + ' ' + u2.last_name as evaluado,
                        a.nombre_area
                    FROM RRHH_EVALUACIONES e
                    LEFT JOIN user_user u1 ON e.id_evaluador = u1.id
                    LEFT JOIN user_user u2 ON e.id_evaluado = u2.id
                    LEFT JOIN RRHH_AREAS a ON e.id_area = a.id_area
                    WHERE e.id_area = ? AND e.periodo = ?
                """, [8, periodo])
            
            # Obtener los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            objetivos = []
            for row in cursor.fetchall():
                objetivo = dict(zip(columns, row))
                # Convertir fechas a formato string para JSON si existen
                if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                    objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                    objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                objetivos.append(objetivo)

            return JsonResponse({
                'status': 'success',
                'data': objetivos,
                'periodo': periodo
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

        finally:
            if cursor:
                cursor.close()


@method_decorator(csrf_exempt, name='dispatch')
class DetallesObjetivosView(View):
    @transaction.atomic
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Verificar si es un nuevo objetivo individual (tiene id_evaluacion)
            if 'id_evaluacion' in data:
                # Insertar solo el objetivo
                obj_query = """
                INSERT INTO RRHH_OBJETIVOS 
                (id_evaluacion, descripcion, fecha_inicio, fecha_fin, 
                indicador,meta, no_cumple, cumple, excede, sobresaliente) 
                VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(obj_query, [
                    data['id_evaluacion'],
                    data['descripcion'],
                    data['fecha_inicio'],
                    data['fecha_fin'],
                    data['indicador'],
                    data['meta'],
                    data.get('no_cumple', 0),
                    data.get('cumple', 0),
                    data.get('excede', 0),
                    data.get('sobresaliente', 0)
                ])
                
                connection_portalaei.commit()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Objetivo guardado correctamente',
                    'id_evaluacion': data['id_evaluacion']
                })
                
            else:
                # Verificar si ya existe una evaluación para este evaluado
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM RRHH_EVALUACIONES 
                    WHERE id_evaluado = ?
                """, [data['id_evaluado']])

                result = cursor.fetchone()
                count = result[0] if result else 0
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe una evaluación para este colaborador'
                    }, status=400)

                # Lógica existente para crear nueva evaluación con objetivos
                eval_query = """
                INSERT INTO RRHH_EVALUACIONES 
                (id_evaluador, id_evaluado, id_area, periodo) 
                VALUES (?, ?, ?, ?);
                """
                
                cursor.execute(eval_query, [
                    data['id_evaluador'],
                    data['id_evaluado'],
                    data['id_area'],
                    data['periodo']
                ])

                cursor.execute("SELECT IDENT_CURRENT('RRHH_EVALUACIONES')")
                result = cursor.fetchone()
                id_evaluacion = result[0] if result else 0
                
                obj_query = """
                INSERT INTO RRHH_OBJETIVOS 
                (id_evaluacion, descripcion, fecha_inicio, fecha_fin, 
                indicador,meta, no_cumple, cumple, excede, sobresaliente) 
                VALUES (?, ?,?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                for objetivo in data['objetivos']:
                    cursor.execute(obj_query, [
                        id_evaluacion,
                        objetivo['descripcion'],
                        objetivo['fecha_inicio'],
                        objetivo['fecha_fin'],
                        objetivo['indicador'],
                        objetivo['meta'],
                        objetivo.get('no_cumple', 0),
                        objetivo.get('cumple', 0),
                        objetivo.get('excede', 0),
                        objetivo.get('sobresaliente', 0)
                    ])
                
                connection_portalaei.commit()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluación y objetivos guardados correctamente',
                    'id_evaluacion': id_evaluacion
                })
            
        except KeyError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Falta el campo requerido: {str(e)}'
            }, status=400)
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
        
        finally:
            if cursor:
                cursor.close()




    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si se proporcionó un ID específico
            objetivo_id = kwargs.get('id')
            
            if objetivo_id:
                # Si hay ID, ejecutar consulta para un objetivo específico
                cursor.execute("""
                    SELECT * FROM RRHH_OBJETIVOS WHERE id = ?
                """, [objetivo_id])
            else:
                # Si no hay ID, ejecutar el procedimiento para todos
                cursor.execute("EXEC RRHH_EV_OBJETIVOS_MEJORA 8")
            
            # Obtener los resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
                
            return JsonResponse({
                'status': 'success',
                'message': 'Datos obtenidos correctamente',
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # 1. Obtener el id_evaluacion del objetivo
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_OBJETIVOS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Objetivo no encontrado'
                }, status=404)
                
            id_evaluacion = result[0]
            
            # 2. Contar cuántos objetivos tiene la evaluación
            cursor.execute("""
                SELECT COUNT(*) 
                FROM RRHH_OBJETIVOS 
                WHERE id_evaluacion = ?
            """, [id_evaluacion])
            
            result = cursor.fetchone()
            cantidad_objetivos = result[0] if result else 0
            
            # 3. Si es el último objetivo, verificar si hay competencias asociadas
            if cantidad_objetivos == 1:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM RRHH_COMPETENCIAS 
                    WHERE id_evaluacion = ? AND estado = 1
                """, [id_evaluacion])
                
                result = cursor.fetchone()
                cantidad_competencias = result[0] if result else 0
                
                if cantidad_competencias > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No se puede eliminar el objetivo. Existen competencias asociadas a esta evaluación. Por favor, elimine primero las competencias.',
                        'data': {
                            'competencias_existentes': cantidad_competencias
                        }
                    }, status=400)
            
            # 4. Eliminar el objetivo
            cursor.execute("""
                DELETE FROM RRHH_OBJETIVOS 
                WHERE id = ?
            """, [id])
            
            # 5. Si era el último objetivo y no hay competencias, eliminar la evaluación
            if cantidad_objetivos == 1:
                cursor.execute("""
                    DELETE FROM RRHH_EVALUACIONES 
                    WHERE id = ?
                """, [id_evaluacion])
                mensaje = 'Objetivo y evaluación eliminados correctamente'
            else:
                mensaje = 'Objetivo eliminado correctamente'
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': mensaje,
                'data': {
                    'objetivo_id': id,
                    'evaluacion_id': id_evaluacion,
                    'evaluacion_eliminada': cantidad_objetivos == 1
                }
            })
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def put(self, request, id, *args, **kwargs):
        try:
            # Decodificar los datos JSON del body
            data = json.loads(request.body)
            
            # Validar que el objetivo existe
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_OBJETIVOS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Objetivo no encontrado'
                }, status=404)

            # Actualizar el objetivo
            update_query = """
                UPDATE RRHH_OBJETIVOS 
                SET descripcion = ?,
                    fecha_inicio = ?,
                    fecha_fin = ?,
                    indicador = ?,
                    meta = ?,
                    no_cumple = ?,
                    cumple = ?,
                    excede = ?,
                    sobresaliente = ?
                WHERE id = ?
            """
            
            cursor.execute(update_query, [
                data['descripcion'],
                data['fecha_inicio'],
                data['fecha_fin'],
                data['indicador'],
                data['meta'],
                data.get('no_cumple', 0),
                data.get('cumple', 0),
                data.get('excede', 0),
                data.get('sobresaliente', 0),
                id
            ])
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Objetivo actualizado correctamente',
                'data': {
                    'id': id,
                    'descripcion': data['descripcion'],
                    'fecha_inicio': data['fecha_inicio'],
                    'fecha_fin': data['fecha_fin'],
                    'indicador': data['indicador'],
                    'meta': data['meta'],
                    'no_cumple': data.get('no_cumple', 0),
                    'cumple': data.get('cumple', 0),
                    'excede': data.get('excede', 0),
                    'sobresaliente': data.get('sobresaliente', 0)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            }, status=400)
            
        except KeyError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Falta el campo requerido: {str(e)}'
            }, status=400)
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()
    
@method_decorator(csrf_exempt, name='dispatch')
class CompetenciasEvaluacionDetailView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            id_evaluacion = data.get('id_evaluacion')
            competencias = data.get('competencias', [])
            
            # Validar que exista id_evaluacion
            if not id_evaluacion:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El ID de evaluación es requerido'
                }, status=400)
            
            # Validar que haya al menos una competencia
            if not competencias:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Debe enviar al menos una competencia'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            try:
                # Insertar cada competencia
                for competencia in competencias:
                    cursor.execute("""
                        INSERT INTO RRHH_COMPETENCIAS (
                            id_evaluacion,
                            id_tipo_competencia,
                            meta,
                            comentarios,
                            no_cumple,
                            cumple,
                            excede,
                            sobresaliente,
                            estado,
                            fecha_inicio,
                            fecha_fin
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?
                        )
                    """, [
                        id_evaluacion,
                        competencia['id_tipo_competencia'],
                        competencia['meta'],
                        competencia['comentarios'],
                        competencia['no_cumple'],
                        competencia['cumple'],
                        competencia['excede'],
                        competencia['sobresaliente'],
                        competencia['fecha_inicio'],
                        competencia['fecha_fin']
                    ])
                
                cursor.commit()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Competencias guardadas correctamente'
                })
                
            except Exception as e:
                # Si hay error, hacer rollback
                cursor.rollback()
                print(f"Error al guardar competencias: {str(e)}")
                raise e
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si se proporcionó un ID específico
            competencia_id = kwargs.get('id')
            
            if competencia_id:
                # Si hay ID, ejecutar consulta para una competencia específica
                cursor.execute("""
                    SELECT 
                        comp.id,
                        comp.id_evaluacion,
                        u.first_name as nombre_evaluado,
                        u.last_name as apellido_evaluado,
                        tc.id as id_tipo_competencia,
                        tc.nombre as nombre_competencia,
                        comp.meta,
                        comp.comentarios,
                        e.periodo,
                        a.nombre_area,
                        comp.fecha_inicio,
						comp.fecha_fin,
                        comp.no_cumple,
                        comp.cumple,
                        comp.excede,
                        comp.sobresaliente,
                        comp.estado
                    FROM RRHH_COMPETENCIAS comp
                    INNER JOIN RRHH_EVALUACIONES e ON comp.id_evaluacion = e.id
                    INNER JOIN user_user u ON e.id_evaluado = u.id
                    INNER JOIN AREA a ON e.id_area = a.id_area
                    INNER JOIN RRHH_TIPOS_COMPETENCIAS tc ON comp.id_tipo_competencia = tc.id
                    WHERE comp.id = ?
                """, [competencia_id])
            else:
                # Si no hay ID, ejecutar el procedimiento para todos
                cursor.execute("EXEC RRHH_EV_COMPETENCIAS_MEJORA 8")
            
            # Obtener los resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                
                # Convertir el campo periodo a formato de fecha si existe y no es None
                if 'periodo' in result and result['periodo']:
                    try:
                        result['periodo'] = result['periodo'].strftime('%Y-%m-%d')
                    except AttributeError:
                        result['periodo'] = result['periodo']
                
                # Asegurar que los campos numéricos sean números
                for field in ['no_cumple', 'cumple', 'excede', 'sobresaliente']:
                    if field in result:
                        result[field] = int(result[field]) if result[field] is not None else 0
                
                # Asegurar que estado sea booleano
                if 'estado' in result:
                    result['estado'] = bool(result['estado'])
                
                results.append(result)
                
            return JsonResponse({
                'status': 'success',
                'message': 'Datos obtenidos correctamente',
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()
    

    def put(self, request, id, *args, **kwargs):
        try:
            # Decodificar los datos JSON del body
            data = json.loads(request.body)
            
            # Validar que la competencia existe
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_COMPETENCIAS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Competencia no encontrada'
                }, status=404)

            # Actualizar la competencia
            update_query = """
                UPDATE RRHH_COMPETENCIAS 
                SET id_tipo_competencia = ?,
                    meta = ?,
                    comentarios = ?,
                    no_cumple = ?,
                    cumple = ?,
                    excede = ?,
                    sobresaliente = ?
                WHERE id = ?
            """
            
            cursor.execute(update_query, [
                data['id_tipo_competencia'],
                data['meta'],
                data['comentarios'],
                data.get('no_cumple', 0),
                data.get('cumple', 0),
                data.get('excede', 0),
                data.get('sobresaliente', 0),
                id
            ])
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Competencia actualizada correctamente',
                'data': {
                    'id': id,
                    'id_tipo_competencia': data['id_tipo_competencia'],
                    'meta': data['meta'],
                    'comentarios': data['comentarios'],
                    'no_cumple': data.get('no_cumple', 0),
                    'cumple': data.get('cumple', 0),
                    'excede': data.get('excede', 0),
                    'sobresaliente': data.get('sobresaliente', 0)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            }, status=400)
            
        except KeyError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Falta el campo requerido: {str(e)}'
            }, status=400)
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def delete(self, request, id, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # 1. Verificar si la competencia existe
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_COMPETENCIAS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Competencia no encontrada'
                }, status=404)
                
            id_evaluacion = result[0]
            
            # 2. Eliminar solo la competencia
            cursor.execute("""
                DELETE FROM RRHH_COMPETENCIAS 
                WHERE id = ?
            """, [id])
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Competencia eliminada correctamente',
                'data': {
                    'competencia_id': id,
                    'evaluacion_id': id_evaluacion,
                    'evaluacion_eliminada': False  # Siempre será False ya que no eliminamos la evaluación
                }
            })
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()






#================================================================================================================   
# REQ. INTERNOS - DON LUIS
#================================================================================================================





@method_decorator(csrf_exempt, name='dispatch')
class RequerimientosInternosView(View):
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            # Obtener parámetros de filtro desde la URL
            estado = request.GET.get('estado', None)
            area = request.GET.get('area', None)
            motivo = request.GET.get('motivo', None)
            cliente = request.GET.get('cliente', None)
            fecha_desde = request.GET.get('desde', None)
            fecha_hasta = request.GET.get('hasta', None)
            
            cursor = connection_donluis.cursor()
            
            # Consulta optimizada proporcionada
            query = """
            SELECT TOP 500
                R.IDREQINTERNO,
                CONVERT(VARCHAR(10), R.FECHA, 103) AS fecha,
                E.RAZON_SOCIAL AS sucursal,
                A.DESCRIPCION AS almacen,
                CONCAT(R.IDDOCUMENTO,' ' ,R.SERIE ,' ',R.NUMERO) AS documento,
                RE.NOMBRE AS responsable,
                AR.DESCRIPCION AS area,
                M.DESCRIPCION AS motivo,
                ES.DESCRIPCION AS estado,
                R.OBSERVACION AS nota_uso,
                R.IDESTADO,
                EM.IDEMISOR,
                EM.DESCRIPCION AS PUNTO_EMISION,
                -- Periodo en formato "MES - AÑO"
                (CASE RIGHT(R.PERIODO, 2)
                    WHEN '01' THEN 'ENERO'
                    WHEN '02' THEN 'FEBRERO'
                    WHEN '03' THEN 'MARZO'
                    WHEN '04' THEN 'ABRIL'
                    WHEN '05' THEN 'MAYO'
                    WHEN '06' THEN 'JUNIO'
                    WHEN '07' THEN 'JULIO'
                    WHEN '08' THEN 'AGOSTO'
                    WHEN '09' THEN 'SEPTIEMBRE'
                    WHEN '10' THEN 'OCTUBRE'
                    WHEN '11' THEN 'NOVIEMBRE'
                    WHEN '12' THEN 'DICIEMBRE'
                    ELSE 'DESCONOCIDO'
                END + ' - ' + LEFT(R.PERIODO, 4)) AS PERIODO
            FROM REQINTERNO R WITH (NOLOCK)
            INNER JOIN EMPRESAS E WITH (NOLOCK) ON E.IDEMPRESA = R.IDEMPRESA
            INNER JOIN ALMACENES A WITH (NOLOCK) ON A.IDALMACEN = R.IDALMACEN AND A.IDSUCURSAL ='001'
            INNER JOIN RESPONSABLE RE WITH (NOLOCK) ON RE.IDRESPONSABLE = R.IDRESPONSABLE
            INNER JOIN AREAS AR WITH (NOLOCK) ON AR.IDAREA = R.IDAREA
            INNER JOIN MOTIVOSREQINTERNO M WITH (NOLOCK) ON M.IDMOTIVO = R.IDMOTIVO
            INNER JOIN ESTADOS ES WITH (NOLOCK) ON ES.IDESTADO = R.IDESTADO
            INNER JOIN EMISOR EM ON EM.IDEMISOR = R.IDEMISOR
            WHERE R.IDESTADO IN ('PE', 'AP','TP')
            """
            
            # Modificar la condición de estado si se especifica en la URL
            if estado and estado != '(Todos)':
                if estado == 'atendido_total':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AT'")
                elif estado == 'atendido_parcial':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AP'")
                elif estado == 'aprobado':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AP'")
                elif estado == 'pendiente':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'PE'")
                elif estado == 'todos':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "1=1")
            
            # Añadir filtros adicionales
            params = []
            
            if area and area != '(Todos)':
                query += " AND AR.DESCRIPCION LIKE ?"
                params.append(f'%{area}%')
            
            if motivo and motivo != '(Todos)':
                query += " AND M.DESCRIPCION LIKE ?"
                params.append(f'%{motivo}%')
            
            if cliente:
                query += " AND E.RAZON_SOCIAL LIKE ?"
                params.append(f'%{cliente}%')
            
            # if fecha_desde:
            #     query += " AND R.FECHA >= CONVERT(DATETIME, ?, 103)"
            #     params.append(fecha_desde)
            
            # if fecha_hasta:
            #     query += " AND R.FECHA <= CONVERT(DATETIME, ?, 103)"
            #     params.append(fecha_hasta)
            
            if fecha_desde:
                query += " AND R.FECHA >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query += " AND R.FECHA <= ?"
                params.append(fecha_hasta)
                
            # Ordenar por fecha más reciente primero
            query += " ORDER BY R.FECHA DESC"
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Obtener resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            # Procesar los resultados
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                
                # Agregar clase CSS según el estado para formateo en frontend
                if item['IDESTADO'] == 'AT':
                    item['estado_clase'] = 'bg-info text-white'
                elif item['IDESTADO'] == 'AP':
                    item['estado_clase'] = 'bg-success text-white'
                elif item['IDESTADO'] == 'PE':
                    item['estado_clase'] = 'bg-warning text-dark'
                else:
                    item['estado_clase'] = 'bg-secondary text-white'
                
                # Eliminar el IDESTADO ya que no es necesario en el frontend
                item.pop('IDESTADO', None)
                
                results.append(item)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Requerimientos internos obtenidos correctamente',
                'total_registros': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()



@method_decorator(csrf_exempt, name='dispatch')
class DetalleRequerimientoInternoAPI(View):
    def get(self, request, idreqinterno):
        cursor = None
        try:
            cursor = connection_donluis.cursor()
            # 1. Limpiamos el parámetro para evitar inyección SQL
            idreqinterno_limpio = idreqinterno.strip()
            
            # 2. Consulta SQL con parámetro correcto y TRIM para evitar problemas con espacios
            query = """
                SELECT 
                    TRIM(R.IDREQINTERNO) AS IDREQINTERNO,
                    TRIM(R.ITEM) AS ITEM,
                    TRIM(R.IDPRODUCTO) AS IDPRODUCTO,
                    TRIM(R.DESCRIPCION) AS PRODUCTO,
                    TRIM(R.IDMEDIDA) AS IDMEDIDA,
                    CONVERT(VARCHAR(20), R.CANTIDAD) AS CANTIDAD,
                    TRIM(R.IDCLIEPROV) AS IDDESTINO,
                    TRIM(C.RAZON_SOCIAL) AS DESTINO,
                    TRIM(R.IDCONSUMIDOR) AS IDCONSUMIDOR,
                    TRIM(CO.DESCRIPCION) AS CONSUMIDOR,
                    ISNULL(TRIM(R.OBSERVACIONES), '') AS OBSERVACIONES,
                    CONVERT(VARCHAR(1), R.ATENDIDO) AS ATENDIDO,
                    TRIM(R.IDACTIVIDAD) AS IDACTIVIDAD,
                    TRIM(AC.DESCRIPCION) AS ACTIVIDAD,
                    TRIM(R.ESTADOS) AS ESTADOS,
					ISNULL(F.CANTIDAD_POR_ATENDER, R.CANTAPROBADA) AS CANTIDAD_PENDIENTE,
                    ISNULL(F.TOTAL_CANTIDAD_SALIDA, 0) AS TOTAL_SALIDAS_REALIZADAS
                FROM DREQINTERNO R
				LEFT JOIN fn_CANTIDAD_POR_ATENDER_REQINTERNO('001','?') F 
				ON R.IDREQINTERNO = F.IDREQINTERNO 
                    AND R.ITEM = F.ITEM 
                    AND LTRIM(RTRIM(R.IDPRODUCTO)) = F.IDPRODUCTO
                LEFT JOIN CLIEPROV C ON C.IDCLIEPROV = R.IDCLIEPROV
                LEFT JOIN RESPONSABLE RE ON RE.IDRESPONSABLE = R.IDRESPONSABLE
                LEFT JOIN ACTIVIDAD AC ON AC.IDACTIVIDAD = R.IDACTIVIDAD
                LEFT JOIN CONSUMIDOR CO ON CO.IDCONSUMIDOR = R.IDCONSUMIDOR
                WHERE TRIM(R.IDREQINTERNO) = ?
                ORDER BY R.ITEM
            """
            
            # 3. Ejecutamos la consulta con el parámetro
            cursor.execute(query, [idreqinterno_limpio])
            
            # 4. Procesamos los resultados
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                results.append(item)
            
            # 5. Respuesta JSON con información útil
            return JsonResponse({
                'status': 'success',
                'message': 'Detalles del requerimiento obtenidos correctamente',
                'id_consultado': idreqinterno_limpio,
                'total_items': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'id_consultado': idreqinterno if 'idreqinterno' in locals() else 'no disponible',
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()


@method_decorator(csrf_exempt, name='dispatch')
class ConsultaStockProductoAPI(View):
    def get(self, request, idproducto):
        cursor = None
        try:
            # 1. Limpiamos el parámetro para evitar inyección SQL
            idproducto_limpio = idproducto.strip()
            
            # 2. Usamos connection_donluis que parece ser la conexión específica para este caso
            cursor = connection_donluis.cursor()
            
            # 3. Consulta exactamente como has pedido
            query = """
                SELECT * FROM VIEW_STOCKALMACEN WHERE IDPRODUCTO = ?
            """
            
            # 4. Ejecutamos la consulta con el parámetro limpio
            cursor.execute(query, [idproducto_limpio])
            
            # 5. Procesamos los resultados
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                results.append(item)
            
            # 6. Respuesta JSON con metadatos útiles
            return JsonResponse({
                'status': 'success',
                'message': f'Stock del producto {idproducto_limpio} obtenido correctamente',
                'producto_consultado': idproducto_limpio,
                'almacenes_encontrados': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'producto_consultado': idproducto if 'idproducto' in locals() else 'no disponible',
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()


#================================================================================================================   
# REQ. INTERNOS - CAMPO VERDE
#================================================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class RequerimientosInternosViewCV(View):
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            # Obtener parámetros de filtro desde la URL
            estado = request.GET.get('estado', None)
            area = request.GET.get('area', None)
            motivo = request.GET.get('motivo', None)
            cliente = request.GET.get('cliente', None)
            fecha_desde = request.GET.get('desde', None)
            fecha_hasta = request.GET.get('hasta', None)
            
            cursor = connection_campoverde.cursor()
            
            # Consulta optimizada proporcionada
            query = """
            SELECT TOP 500
                R.IDREQINTERNO,
                CONVERT(VARCHAR(10), R.FECHA, 103) AS fecha,
                E.RAZON_SOCIAL AS sucursal,
                A.DESCRIPCION AS almacen,
                CONCAT(R.IDDOCUMENTO,' ' ,R.SERIE ,' ',R.NUMERO) AS documento,
                RE.NOMBRE AS responsable,
                AR.DESCRIPCION AS area,
                M.DESCRIPCION AS motivo,
                ES.DESCRIPCION AS estado,
                R.OBSERVACION AS nota_uso,
                R.IDESTADO,
                EM.IDEMISOR,
                EM.DESCRIPCION AS PUNTO_EMISION,
                -- Periodo en formato "MES - AÑO"
                (CASE RIGHT(R.PERIODO, 2)
                    WHEN '01' THEN 'ENERO'
                    WHEN '02' THEN 'FEBRERO'
                    WHEN '03' THEN 'MARZO'
                    WHEN '04' THEN 'ABRIL'
                    WHEN '05' THEN 'MAYO'
                    WHEN '06' THEN 'JUNIO'
                    WHEN '07' THEN 'JULIO'
                    WHEN '08' THEN 'AGOSTO'
                    WHEN '09' THEN 'SEPTIEMBRE'
                    WHEN '10' THEN 'OCTUBRE'
                    WHEN '11' THEN 'NOVIEMBRE'
                    WHEN '12' THEN 'DICIEMBRE'
                    ELSE 'DESCONOCIDO'
                END + ' - ' + LEFT(R.PERIODO, 4)) AS PERIODO
            FROM REQINTERNO R WITH (NOLOCK)
            INNER JOIN EMPRESAS E WITH (NOLOCK) ON E.IDEMPRESA = R.IDEMPRESA
            INNER JOIN ALMACENES A WITH (NOLOCK) ON A.IDALMACEN = R.IDALMACEN AND A.IDSUCURSAL ='002'
            INNER JOIN RESPONSABLE RE WITH (NOLOCK) ON RE.IDRESPONSABLE = R.IDRESPONSABLE
            INNER JOIN AREAS AR WITH (NOLOCK) ON AR.IDAREA = R.IDAREA
            INNER JOIN MOTIVOSREQINTERNO M WITH (NOLOCK) ON M.IDMOTIVO = R.IDMOTIVO
            INNER JOIN ESTADOS ES WITH (NOLOCK) ON ES.IDESTADO = R.IDESTADO
            INNER JOIN EMISOR EM ON EM.IDEMISOR = R.IDEMISOR
            WHERE R.IDESTADO IN ('PE', 'AP','TP')
            """
            
            # Modificar la condición de estado si se especifica en la URL
            if estado and estado != '(Todos)':
                if estado == 'atendido_total':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AT'")
                elif estado == 'atendido_parcial':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AP'")
                elif estado == 'aprobado':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AP'")
                elif estado == 'pendiente':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'PE'")
                elif estado == 'todos':
                    query = query.replace("R.IDESTADO IN ('PE', 'AP')", "1=1")
            
            # Añadir filtros adicionales
            params = []
            
            if area and area != '(Todos)':
                query += " AND AR.DESCRIPCION LIKE ?"
                params.append(f'%{area}%')
            
            if motivo and motivo != '(Todos)':
                query += " AND M.DESCRIPCION LIKE ?"
                params.append(f'%{motivo}%')
            
            if cliente:
                query += " AND E.RAZON_SOCIAL LIKE ?"
                params.append(f'%{cliente}%')
            
            # if fecha_desde:
            #     query += " AND R.FECHA >= CONVERT(DATETIME, ?, 103)"
            #     params.append(fecha_desde)
            
            # if fecha_hasta:
            #     query += " AND R.FECHA <= CONVERT(DATETIME, ?, 103)"
            #     params.append(fecha_hasta)
            
            if fecha_desde:
                query += " AND R.FECHA >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query += " AND R.FECHA <= ?"
                params.append(fecha_hasta)
            
            # Ordenar por fecha más reciente primero
            query += " ORDER BY R.FECHA DESC"
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Obtener resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            # Procesar los resultados
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                
                # Agregar clase CSS según el estado para formateo en frontend
                if item['IDESTADO'] == 'AT':
                    item['estado_clase'] = 'bg-info text-white'
                elif item['IDESTADO'] == 'AP':
                    item['estado_clase'] = 'bg-success text-white'
                elif item['IDESTADO'] == 'PE':
                    item['estado_clase'] = 'bg-warning text-dark'
                else:
                    item['estado_clase'] = 'bg-secondary text-white'
                
                # Eliminar el IDESTADO ya que no es necesario en el frontend
                item.pop('IDESTADO', None)
                
                results.append(item)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Requerimientos internos obtenidos correctamente',
                'total_registros': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()


@method_decorator(csrf_exempt, name='dispatch')
class DetalleRequerimientoInternoAPICV(View):
    def get(self, request, idreqinterno):
        cursor = None
        try:
            cursor = connection_campoverde.cursor()
            # 1. Limpiamos el parámetro para evitar inyección SQL
            idreqinterno_limpio = idreqinterno.strip()
            
            # 2. Consulta SQL con parámetro correcto y TRIM para evitar problemas con espacios
            query = """
                SELECT 
                    TRIM(R.IDREQINTERNO) AS IDREQINTERNO,
                    TRIM(R.ITEM) AS ITEM,
                    TRIM(R.IDPRODUCTO) AS IDPRODUCTO,
                    TRIM(R.DESCRIPCION) AS PRODUCTO,
                    TRIM(R.IDMEDIDA) AS IDMEDIDA,
                    CONVERT(VARCHAR(20), R.CANTIDAD) AS CANTIDAD,
                    TRIM(R.IDCLIEPROV) AS IDDESTINO,
                    TRIM(C.RAZON_SOCIAL) AS DESTINO,
                    TRIM(R.IDCONSUMIDOR) AS IDCONSUMIDOR,
                    TRIM(CO.DESCRIPCION) AS CONSUMIDOR,
                    ISNULL(TRIM(R.OBSERVACIONES), '') AS OBSERVACIONES,
                    CONVERT(VARCHAR(1), R.ATENDIDO) AS ATENDIDO,
                    TRIM(R.IDACTIVIDAD) AS IDACTIVIDAD,
                    TRIM(AC.DESCRIPCION) AS ACTIVIDAD,
                    TRIM(R.ESTADOS) AS ESTADOS,
					ISNULL(F.CANTIDAD_POR_ATENDER, R.CANTAPROBADA) AS CANTIDAD_PENDIENTE,
                    ISNULL(F.TOTAL_CANTIDAD_SALIDA, 0) AS TOTAL_SALIDAS_REALIZADAS
                FROM DREQINTERNO R
				LEFT JOIN fn_CANTIDAD_POR_ATENDER_REQINTERNO('001','?') F 
				ON R.IDREQINTERNO = F.IDREQINTERNO 
                    AND R.ITEM = F.ITEM 
                    AND LTRIM(RTRIM(R.IDPRODUCTO)) = F.IDPRODUCTO
                LEFT JOIN CLIEPROV C ON C.IDCLIEPROV = R.IDCLIEPROV
                LEFT JOIN RESPONSABLE RE ON RE.IDRESPONSABLE = R.IDRESPONSABLE
                LEFT JOIN ACTIVIDAD AC ON AC.IDACTIVIDAD = R.IDACTIVIDAD
                LEFT JOIN CONSUMIDOR CO ON CO.IDCONSUMIDOR = R.IDCONSUMIDOR
                WHERE TRIM(R.IDREQINTERNO) = ?
                ORDER BY R.ITEM
            """
            
            # 3. Ejecutamos la consulta con el parámetro
            cursor.execute(query, [idreqinterno_limpio])
            
            # 4. Procesamos los resultados
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                results.append(item)
            
            # 5. Respuesta JSON con información útil
            return JsonResponse({
                'status': 'success',
                'message': 'Detalles del requerimiento obtenidos correctamente',
                'id_consultado': idreqinterno_limpio,
                'total_items': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'id_consultado': idreqinterno if 'idreqinterno' in locals() else 'no disponible',
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()


@method_decorator(csrf_exempt, name='dispatch')
class ConsultaStockProductoAPICV(View):
    def get(self, request, idproducto):
        cursor = None
        try:
            # 1. Limpiamos el parámetro para evitar inyección SQL
            idproducto_limpio = idproducto.strip()
            
            # 2. Usamos connection_campoverde que parece ser la conexión específica para este caso
            cursor = connection_campoverde.cursor()
            
            # 3. Consulta exactamente como has pedido
            query = """
                SELECT * FROM VIEW_STOCKALMACEN WHERE IDPRODUCTO = ?
            """
            
            # 4. Ejecutamos la consulta con el parámetro limpio
            cursor.execute(query, [idproducto_limpio])
            
            # 5. Procesamos los resultados
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                results.append(item)
            
            # 6. Respuesta JSON con metadatos útiles
            return JsonResponse({
                'status': 'success',
                'message': f'Stock del producto {idproducto_limpio} obtenido correctamente',
                'producto_consultado': idproducto_limpio,
                'almacenes_encontrados': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'producto_consultado': idproducto if 'idproducto' in locals() else 'no disponible',
                'traceback': traceback.format_exc()
            }, status=500)

        finally:
            if cursor:
                cursor.close()



#================================================================================================================
# REQUERIMIENTOS INTERNOS - DON LUIS
#================================================================================================================


@method_decorator(csrf_exempt, name='dispatch')
class SalidaInternaView(View):
    """
    Vista para manejar las salidas internas de almacén en el sistema Nisira
    Maneja el registro completo: encabezado, detalles y referencias
    """
    
    def post(self, request, *args, **kwargs):
        """
        Crea una nueva salida interna completa siguiendo el flujo del ERP Nisira
        """
        try:
            data = json.loads(request.body)
            cursor = connection_donluis.cursor()
            
            # VERIFICAR ESTADO DE AUTOCOMMIT
            print(f"🔧 Autocommit inicial: {connection_donluis.autocommit}")
            
            # FORZAR AUTOCOMMIT=True para evitar problemas de transacción
            connection_donluis.autocommit = True
            print("🔧 Autocommit forzado a True")
            
            # Validar datos del encabezado
            encabezado = data.get('encabezado', {})
            productos = data.get('productos', [])
            doc_referencia = data.get('documento_referencia', {})
            
            self._validar_datos_encabezado(encabezado)
            
            if not productos:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe incluir al menos un producto'
                })
            
            # PASO 1: OBTENER DATOS DE CABECERA POR DEFECTO (como hace el ERP)
            print("🔄 Paso 1: Obteniendo datos de cabecera por defecto...")
            self._obtener_datos_cabecera_defecto(cursor, encabezado)
            
            # PASO 2: OBTENER SERIES DISPONIBLES (como hace el ERP)
            print("🔄 Paso 2: Obteniendo series disponibles...")
            series_disponibles = self._obtener_series_disponibles(cursor, encabezado)
            
            if not series_disponibles:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay series disponibles para este usuario/documento'
                })
            
            # PASO 3: USAR LA PRIMERA SERIE DISPONIBLE
            serie_usar = series_disponibles[0]
            encabezado['SERIE'] = serie_usar['SERIE']
            print(f"🔄 Paso 3: Usando serie {serie_usar['SERIE']}")
            
            # CON AUTOCOMMIT=True NO NECESITAMOS TRANSACCIONES EXPLÍCITAS
            print("🔄 Procesando con autocommit...")
            
            try:
                # PASO 4: Insertar encabezado
                print("🔄 Paso 4: Insertando encabezado...")
                id_generado = self._insertar_encabezado(cursor, encabezado)
                
                # PASO 5: Insertar detalles de productos
                print("🔄 Paso 5: Insertando detalles...")
                self._insertar_detalles(cursor, id_generado, productos)
                
                # PASO 6: Insertar documento de referencia si existe
                if doc_referencia:
                    print("🔄 Paso 6: Insertando documento referencia...")
                    self._insertar_documento_referencia(cursor, id_generado, doc_referencia)
                
                
                
                # PASO 9: Obtener documento creado ANTES del commit
                print("🔄 Paso 9: Obteniendo documento creado...")
                try:
                    documento_creado = self._obtener_documento_creado(cursor, id_generado)
                    print(f"📋 Documento obtenido: {documento_creado}")
                except Exception as doc_error:
                    print(f"❌ Error al obtener documento: {str(doc_error)}")
                    documento_creado = None
                
                # CON AUTOCOMMIT=True CADA COMANDO YA SE CONFIRMA AUTOMÁTICAMENTE
                print("🔄 Verificando registros en base de datos...")
                
                # VERIFICAR SI EL REGISTRO PERSISTE
                cursor.execute("""
                    SELECT COUNT(*) FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [id_generado, encabezado['IDEMPRESA']])
                result = cursor.fetchone()
                count_final = result[0] if result else 0
                print(f"📈 Registros en BD: {count_final}")
                
                if count_final == 0:
                    print("❌ ADVERTENCIA: El registro no se encontró en la BD")
                else:
                    print("✅ Registro confirmado en base de datos")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Salida interna registrada exitosamente',
                    'data': documento_creado
                })
                
            except Exception as e:
                # CON AUTOCOMMIT=True NO NECESITAMOS ROLLBACK MANUAL
                print(f"❌ Error en procesamiento: {str(e)}")
                raise e
                
        except ValueError as ve:
            return JsonResponse({
                'success': False,
                'message': f'Error de validación: {str(ve)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar salida interna: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    def get(self, request, id=None, *args, **kwargs):
        """
        Obtiene salidas internas - lista o detalle específico
        """
        try:
            cursor = connection_donluis.cursor()
            
            if id:
                # Obtener salida específica con sus detalles
                return self._obtener_salida_detalle(cursor, id)
            else:
                # Obtener lista de salidas con filtros usando procedimiento almacenado
                return self._obtener_lista_salidas(cursor, request)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al consultar salidas: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    # MÉTODOS PRIVADOS AUXILIARES
    
    def _obtener_series_disponibles(self, cursor, encabezado):
        """Obtiene las series disponibles para el usuario usando el procedimiento del ERP"""
        try:
            print(f"🔍 Ejecutando objtablas_returnSeries con parámetros:")
            print(f"   - IDEMPRESA: {encabezado['IDEMPRESA']}")
            print(f"   - IDEMISOR: {encabezado['IDEMISOR']}")
            print(f"   - IDDOCUMENTO: {encabezado['IDDOCUMENTO']}")
            print(f"   - IDUSUARIO: {encabezado['IDUSUARIO']}")
            
            # MÉTODO 1: Intentar con el procedimiento
            try:
                cursor.execute("""
                    EXEC objtablas_returnSeries ?, ?, ?, ?, ?
                """, [
                    encabezado['IDEMPRESA'],    # @C_EMP
                    encabezado['IDEMISOR'],     # @C_EMI  
                    encabezado['IDDOCUMENTO'],  # @C_DOC (SAL)
                    '',                         # @C_TIPOVENTA (vacío para almacén)
                    encabezado['IDUSUARIO']     # @C_USU
                ])
                
                resultados = cursor.fetchall()
                series_disponibles = []
                
                for row in resultados:
                    numero_raw = str(row[1]).strip()  # Eliminar espacios en blanco
                    # Formatear el número con padding si es necesario
                    if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                        numero_formateado = numero_raw
                    else:
                        numero_int = int(numero_raw) if numero_raw else 1
                        numero_formateado = f"{numero_int:07d}"  # 7 dígitos con padding
                    
                    series_disponibles.append({
                        'SERIE': row[0],
                        'NUMERO': numero_formateado
                    })
                
                if series_disponibles:
                    print(f"✅ Series encontradas vía procedimiento: {len(series_disponibles)}")
                    for serie in series_disponibles:
                        print(f"   - Serie: {serie['SERIE']}, Próximo número: {serie['NUMERO']}")
                    return series_disponibles
                    
            except Exception as proc_error:
                print(f"⚠️ Error en procedimiento: {str(proc_error)}")
            
            # MÉTODO 2: Consulta directa a NUMEMISOR como fallback
            print("🔄 Intentando consulta directa a NUMEMISOR...")
            cursor.execute("""
                SELECT SERIE, NUMERO 
                FROM NUMEMISOR 
                WHERE IDEMPRESA = ? 
                AND IDEMISOR = ? 
                AND IDDOCUMENTO = ? 
                AND ESTADO = 1
                ORDER BY SERIE
            """, [
                encabezado['IDEMPRESA'],
                encabezado['IDEMISOR'], 
                encabezado['IDDOCUMENTO']
            ])
            
            resultados = cursor.fetchall()
            series_disponibles = []
            
            for row in resultados:
                numero_raw = str(row[1]).strip()  # Eliminar espacios en blanco
                # Formatear el número con padding si es necesario
                if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                    numero_formateado = numero_raw
                else:
                    numero_int = int(numero_raw) if numero_raw else 1
                    numero_formateado = f"{numero_int:07d}"  # 7 dígitos con padding
                
                series_disponibles.append({
                    'SERIE': row[0],
                    'NUMERO': numero_formateado
                })
            
            print(f"📋 Series disponibles encontradas (consulta directa): {len(series_disponibles)}")
            for serie in series_disponibles:
                print(f"   - Serie: {serie['SERIE']}, Próximo número: {serie['NUMERO']}")
            
            return series_disponibles
            
        except Exception as e:
            print(f"❌ Error al obtener series: {str(e)}")
            return []
    
    def _obtener_datos_cabecera_defecto(self, cursor, encabezado):
        """Obtiene datos por defecto de cabecera como hace el ERP"""
        try:
            # Construir XML similar al del ERP (simplificado)
            xml_data = f"""<?xml version = "1.0" encoding="Windows-1252" standalone="yes"?>
            <VFPData>
                <torigen>
                    <ctabla>emisor</ctabla>
                    <cid>{encabezado['IDEMISOR']}</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdemisor</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>operaciones</ctabla>
                    <cid>SALM</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdoperacion</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>estados</ctabla>
                    <cid>PE</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdestado</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>monedas</ctabla>
                    <cid>{encabezado['IDMONEDA']}</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>cntmoneda.txtdescripcion</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>responsable</ctabla>
                    <cid>{encabezado['IDRESPONSABLE']}</cid>
                    <cpropiedad>nombre</cpropiedad>
                    <ccontenedor>cntresponsable.txtdescripcion</ccontenedor>
                </torigen>
            </VFPData>"""
            
            cursor.execute("""
                EXEC GETRECORD_DATOSCABECERA_SALIDASINTERNAS ?, ?
            """, [encabezado['IDEMPRESA'], xml_data])
            
            # El procedimiento puede devolver datos, pero por ahora solo lo ejecutamos
            print("✅ Datos de cabecera por defecto obtenidos")
            return True
            
        except Exception as e:
            print(f"⚠️ Advertencia al obtener datos cabecera defecto: {str(e)}")
            return False
    
    def _generar_idingresosalidaalm(self, cursor, encabezado):
        """Genera el IDINGRESOSALIDAALM usando DPARAMS como hace el ERP"""
        try:
            # Obtener el siguiente ID desde DPARAMS
            cursor.execute("""
                SELECT id FROM DPARAMS 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = '_'
            """, [encabezado['IDEMPRESA']])
            
            resultado = cursor.fetchone()
            if resultado:
                siguiente_id = resultado[0]
            else:
                siguiente_id = 39860  # Valor base observado en los ejemplos
                
            # Generar ID con formato observado: _76F0TDC7939860
            # Formato: _[3chars][1digit][4chars][6digits]
            import random, string
            parte1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))  # 76F
            parte2 = random.choice(string.digits)  # 0
            parte3 = ''.join(random.choices(string.ascii_uppercase, k=4))  # TDCR
            parte4 = f"{siguiente_id}"  # 39860
            
            id_generado = f"_{parte1}{parte2}{parte3}{parte4}"
            
            print(f"🔢 ID generado: {id_generado}")
            return id_generado
            
        except Exception as e:
            # Fallback: generar ID aleatorio con formato correcto
            import random, string
            parte1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            parte2 = random.choice(string.digits)
            parte3 = ''.join(random.choices(string.ascii_uppercase, k=4))
            parte4 = f"{random.randint(39860, 99999)}"
            
            id_generado = f"_{parte1}{parte2}{parte3}{parte4}"
            print(f"⚠️ Error en DPARAMS, usando ID aleatorio: {id_generado}")
            return id_generado
    


    def _generar_numoperacion(self, cursor, encabezado):
        """
        Genera el NUMOPERACION con lógica mensual simplificada:
        - Nuevo mes = 0000000001
        - Mismo mes = siguiente número
        """
        try:
            # Obtener datos básicos
            periodo_actual = encabezado.get('PERIODO')
            idempresa = encabezado.get('IDEMPRESA', '001')
            
            if not periodo_actual:
                from datetime import datetime
                fecha_actual = datetime.now()
                periodo_actual = f"{fecha_actual.year}{fecha_actual.month:02d}"
            
            # Buscar el último NUMOPERACION del mes actual
            cursor.execute("""
                SELECT MAX(CAST(NUMOPERACION AS INTEGER)) 
                FROM INGRESOSALIDAALM 
                WHERE IDEMPRESA = ? AND PERIODO = ?
                AND NUMOPERACION IS NOT NULL AND NUMOPERACION != ''
            """, [idempresa, periodo_actual])
            
            resultado = cursor.fetchone()
            ultimo_numero = resultado[0] if resultado and resultado[0] else 0
            
            # Generar siguiente número
            siguiente_numero = ultimo_numero + 1
            numoperacion_generado = f"{siguiente_numero:010d}"
            
            # Log simple
            if ultimo_numero == 0:
                print(f"🆕 Nuevo mes {periodo_actual}: {numoperacion_generado}")
            else:
                print(f"📈 Mes {periodo_actual}: {ultimo_numero} → {numoperacion_generado}")
            
            return numoperacion_generado
            
        except Exception as e:
            # Fallback simple: número aleatorio con formato correcto
            import random
            numero_emergencia = random.randint(1, 999999)
            fallback = f"{numero_emergencia:010d}"
            print(f"❌ Error: {str(e)} | Usando: {fallback}")
            return fallback    


    
    def _obtener_siguiente_numero(self, cursor, encabezado, serie):
        """Obtiene el siguiente número para la serie"""
        try:
            # Ya tenemos el número desde _obtener_series_disponibles
            cursor.execute("""
                SELECT NUMERO FROM NUMEMISOR 
                WHERE IDEMPRESA = ? AND IDEMISOR = ? AND IDDOCUMENTO = ? AND SERIE = ?
            """, [encabezado['IDEMPRESA'], encabezado['IDEMISOR'], encabezado['IDDOCUMENTO'], serie])
            
            resultado = cursor.fetchone()
            if resultado:
                numero_raw = str(resultado[0]).strip()  # Eliminar espacios en blanco
                # Si el número es una cadena y ya tiene formato, usarlo tal cual
                if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                    numero_formateado = numero_raw
                    print(f"📝 Número ya formateado: {numero_formateado}")
                else:
                    # Si es número entero o cadena corta, formatear con padding de ceros
                    numero_int = int(numero_raw) if numero_raw else 1
                    numero_formateado = f"{numero_int:07d}"  # Formato: 0061752 (7 dígitos)
                    print(f"📝 Número formateado: {numero_formateado}")
                
                print(f"🔢 Número obtenido: {numero_formateado}")
                return numero_formateado
            else:
                print("⚠️ No se encontró número en NUMEMISOR, usando 0000001")
                return "0000001"
                
        except Exception as e:
            print(f"⚠️ Error obteniendo número: {str(e)}")
            return "0000001"
    
    def _actualizar_dparams(self, cursor, encabezado, id_usado, numoperacion_usado):
        """Actualiza DPARAMS con los valores usados"""
        try:
            # Actualizar contador de IDINGRESOSALIDAALM
            cursor.execute("""
                UPDATE DPARAMS SET id = id + 1 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = '_'
            """, [encabezado['IDEMPRESA']])
            
            # Actualizar contador de NUMOPERACION
            cursor.execute("""
                UPDATE DPARAMS SET id = id + 1 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = 'SALM'
            """, [encabezado['IDEMPRESA']])
            
            # Actualizar NUMEMISOR con formato de 7 dígitos
            cursor.execute("""
                UPDATE NUMEMISOR 
                SET NUMERO = RIGHT('0000000' + CAST((CAST(NUMERO AS INT) + 1) AS VARCHAR), 7)
                WHERE IDEMPRESA = ? AND IDEMISOR = ? AND IDDOCUMENTO = ? AND SERIE = ?
            """, [encabezado['IDEMPRESA'], encabezado['IDEMISOR'], encabezado['IDDOCUMENTO'], encabezado['SERIE']])
            
            print("✅ DPARAMS y NUMEMISOR actualizados")
            
        except Exception as e:
            print(f"⚠️ Error actualizando contadores: {str(e)}")

    def _validar_datos_encabezado(self, encabezado):
        """Valida que los datos del encabezado sean correctos"""
        campos_requeridos = [
            'IDEMPRESA', 'IDEMISOR', 'PERIODO', 'IDALMACEN', 
            'IDDOCUMENTO', 'FECHA', 'IDRESPONSABLE', 
            'GLOSA', 'IDMONEDA', 'TCAMBIO', 'IDSUCURSAL', 'IDUSUARIO'
        ]
        
        for campo in campos_requeridos:
            if campo not in encabezado or not encabezado[campo]:
                raise ValueError(f'El campo {campo} es requerido')
    



    
    def _insertar_encabezado(self, cursor, encabezado):
        """Inserta el encabezado en INGRESOSALIDAALM generando previamente los valores como hace el ERP"""
        
        # PASO 1: GENERAR IDINGRESOSALIDAALM usando DPARAMS
        idingresosalidaalm_generado = self._generar_idingresosalidaalm(cursor, encabezado)
        
        # PASO 2: GENERAR NUMOPERACION usando DPARAMS  
        numoperacion_generado = self._generar_numoperacion(cursor, encabezado)
        
        # PASO 3: OBTENER SERIE Y NÚMERO (ya tenemos desde _obtener_series_disponibles)
        serie_usar = encabezado['SERIE']
        numero_usar = self._obtener_siguiente_numero(cursor, encabezado, serie_usar)
        
        # PASO 4: INSERTAR CON TODOS LOS CAMPOS OBLIGATORIOS Y VALORES POR DEFECTO
        sql = """
        INSERT INTO INGRESOSALIDAALM (
            IDEMPRESA, IDINGRESOSALIDAALM, IDEMISOR, PERIODO, IDOPERACION, 
            NUMOPERACION, IDSUBDIARIO, VOUCHER, IDALMACEN, IDDOCUMENTO, SERIE, NUMERO, FECHA,
            IDRESPONSABLE, GLOSA, IDMONEDA, TCAMBIO, TCMONEDA, IDMOTIVO,
            IDALMACEND, FECHADOCORIGEN, SINCRONIZA, IDESTADO, FECHACREACION, 
            CONTABILIZADO, IDSUCURSALD, IDSUCURSAL, VENTANA, IDPARTEPRODUCCION, 
            TOTAL, IDUSUARIO, IDCONSUMIDOR, IMPRESO, IMPORTADO, ES_COSTOS,
            pesodocorigen3, IDREGISTROVAR, AREA_HA, IMPORTADO_EXTERNO, automatico_asociaop,
            numversion, PTOPARTIDA, MOTIVO_TRASLADO, transferir_comprometido, idviaje,
            dni, precio_generado, IDCHOFER, CMA30EQPID_CAMION, CMA30EQPID_CARRETA,
            IDRUTA, IDLUGAR_O, IDLUGAR_D, ITEM_RUTA, fecha_syncro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        
        parametros = [
            encabezado['IDEMPRESA'],                    # 1. IDEMPRESA
            idingresosalidaalm_generado,                # 2. IDINGRESOSALIDAALM (GENERADO)
            encabezado['IDEMISOR'],                     # 3. IDEMISOR  
            encabezado['PERIODO'],                      # 4. PERIODO
            'SALM',                                     # 5. IDOPERACION (Salidas Almacén)
            numoperacion_generado,                      # 6. NUMOPERACION (GENERADO)
            '004',                                      # 7. IDSUBDIARIO (OBLIGATORIO para salidas)
            numoperacion_generado,                      # 8. VOUCHER (mismo que NUMOPERACION)
            encabezado['IDALMACEN'],                    # 9. IDALMACEN
            encabezado['IDDOCUMENTO'],                  # 10. IDDOCUMENTO (SAL)
            serie_usar,                                 # 11. SERIE (GENERADA)
            numero_usar,                                # 12. NUMERO (GENERADO)
            encabezado['FECHA'],                        # 13. FECHA
            encabezado['IDRESPONSABLE'],                # 14. IDRESPONSABLE
            encabezado['GLOSA'],                        # 15. GLOSA
            encabezado['IDMONEDA'],                     # 16. IDMONEDA
            encabezado['TCAMBIO'],                      # 17. TCAMBIO
            encabezado.get('TCMONEDA', 1.000000),       # 18. TCMONEDA
            encabezado['IDMOTIVO'],                     # 19. IDMOTIVO
            encabezado.get('IDALMACEND'),               # 20. IDALMACEND (puede ser NULL)
            encabezado.get('FECHADOCORIGEN', encabezado['FECHA']),  # 21. FECHADOCORIGEN
            encabezado.get('SINCRONIZA', 'N'),          # 22. SINCRONIZA
            encabezado.get('IDESTADO', 'PE'),           # 23. IDESTADO (Pendiente)
            # 24. FECHACREACION = GETDATE() - no parámetro
            encabezado.get('CONTABILIZADO', 0),         # 24. CONTABILIZADO
            encabezado.get('IDSUCURSALD'),              # 25. IDSUCURSALD (puede ser NULL)
            encabezado['IDSUCURSAL'],                   # 26. IDSUCURSAL
            encabezado.get('VENTANA', 'EDT_SALIDAS'),   # 27. VENTANA
            encabezado.get('IDPARTEPRODUCCION'),        # 28. IDPARTEPRODUCCION (puede ser NULL)
            0.0000,                                     # 29. TOTAL (OBLIGATORIO, inicia en 0)
            encabezado['IDUSUARIO'],                    # 30. IDUSUARIO
            '',                                         # 31. IDCONSUMIDOR (DEFAULT '')
            0,                                          # 32. IMPRESO (DEFAULT 0)
            0,                                          # 33. IMPORTADO (DEFAULT 0)
            0,                                          # 34. ES_COSTOS (DEFAULT 0)
            0,                                          # 35. pesodocorigen3 (DEFAULT 0)
            0,                                          # 36. IDREGISTROVAR (DEFAULT 0)
            0,                                          # 37. AREA_HA (DEFAULT 0)
            0,                                          # 38. IMPORTADO_EXTERNO (DEFAULT 0)
            0,                                          # 39. automatico_asociaop (DEFAULT 0)
            0,                                          # 40. numversion (DEFAULT 0)
            '',                                         # 41. PTOPARTIDA (DEFAULT '')
            '',                                         # 42. MOTIVO_TRASLADO (DEFAULT '')
            0,                                          # 43. transferir_comprometido (DEFAULT 0)
            '',                                         # 44. idviaje (DEFAULT '')
            '',                                         # 45. dni (DEFAULT '')
            0,                                          # 46. precio_generado (DEFAULT 0)
            '',                                         # 47. IDCHOFER (DEFAULT '')
            '',                                         # 48. CMA30EQPID_CAMION (DEFAULT '')
            '',                                         # 49. CMA30EQPID_CARRETA (DEFAULT '')
            '',                                         # 50. IDRUTA (DEFAULT '')
            '',                                         # 51. IDLUGAR_O (DEFAULT '')
            '',                                         # 52. IDLUGAR_D (DEFAULT '')
            ''                                          # 53. ITEM_RUTA (DEFAULT '')
            # fecha_syncro = GETDATE() - no parámetro
        ]
        
        print(f"📝 Insertando registro con valores generados:")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm_generado}")
        print(f"   - NUMOPERACION: {numoperacion_generado}")  
        print(f"   - SERIE: {serie_usar}")
        print(f"   - NUMERO: {numero_usar}")
        
        try:
            print(f"🔄 Ejecutando INSERT en INGRESOSALIDAALM...")
            print(f"📊 Total de parámetros: {len(parametros)}")
            cursor.execute(sql, parametros)
            print(f"✅ INSERT ejecutado exitosamente")
            
            # Verificar que se insertó
            cursor.execute("SELECT @@ROWCOUNT")
            rows_affected = cursor.fetchone()[0]
            print(f"📈 Filas afectadas: {rows_affected}")
            
            if rows_affected == 0:
                print("❌ ADVERTENCIA: No se insertaron filas")
            
        except Exception as insert_error:
            print(f"❌ ERROR en INSERT: {str(insert_error)}")
            raise insert_error
        
        # ACTUALIZAR DPARAMS con los nuevos valores usados
        try:
            print(f"🔄 Actualizando DPARAMS...")
            self._actualizar_dparams(cursor, encabezado, idingresosalidaalm_generado, numoperacion_generado)
            print(f"✅ DPARAMS actualizado")
        except Exception as dparams_error:
            print(f"❌ ERROR en DPARAMS: {str(dparams_error)}")
            raise dparams_error
        
        print(f"✅ Encabezado creado: ID={idingresosalidaalm_generado}, Serie={serie_usar}, Número={numero_usar}")
        
        return idingresosalidaalm_generado



    def _insertar_detalles(self, cursor, idingresosalidaalm, productos):
        """Inserta los detalles de productos en DINGRESOSALIDAALM"""
        
        # VERIFICAR QUE NO EXISTAN DETALLES PREVIAMENTE
        cursor.execute("""
            SELECT COUNT(*) FROM DINGRESOSALIDAALM 
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Advertencia: Ya existen {count} detalles para {idingresosalidaalm}")
            # Eliminar detalles existentes
            cursor.execute("""
                DELETE FROM DINGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ?
            """, [idingresosalidaalm])
        
        sql = """
        INSERT INTO DINGRESOSALIDAALM (
            IDEMPRESA, IDINGRESOSALIDAALM, ITEM, IDPRODUCTO, DESCRIPCION,
            IDSERIE, IDLOTEP, IDMEDIDA, IDESTADOPRODUCTO, IDPROYECTO,
            IDACTIVIDAD, IDLABOR, IDCONSUMIDOR, TCAMBIO, COMPROMETIDO,
            IDEMPAQUE, CANTEMPAQUE, CANTIDAD, AREA, NUMPALETA, PRECIO,
            IMPORTE, IDREFERENCIA, ITEMREF, TABLAREF, PRECIOMOF,
            PRECIOMEX, IMPORTEMOF, IMPORTEMEX, IDPARTIDAPSTAL,
            CODINTERNO, CODIGOBARRA, IDUBICACION, LOTEORIGEN,
            PRODUCTOORIGEN, OBSERVACIONES, IDFALLA, IDPRODUCTOPROCESO,
            IDMOVCOMPROMETIDO, MERMA, FACTORINSUMO, CANTINSUMO,
            CANTIPRODUCIDA, IDSIEMBRA, IDCAMPANA, IDORDENPRODUCCION,
            IDLOTEPRODUCCION, DOCORDENPRODUCCION, VOLUMEN, IDACTIVO,
            IDCULTIVO, IDPRODUCTODESTINO, DSC_PRODUCTODESTINO, IDMEDIDA2,
            CANTIDAD2, idvehiculo, docreqinterno, idreqinterno,
            ITEMREF_ORDENPRODUCCION, placa, kilometraje, chofer,
            NRO_VALE, SEMANA, DOSISLOTE, estructura, itemreqinterno,
            DSC_DOCVENTA, IDDOC_VENTA, idchofer, cMA30EqpID,
            NROENVASES, idinvernadero, idnave, idcampanainvernadero, horometro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for i, producto in enumerate(productos, 1):
            # GENERAR ITEM ÚNICO
            item_numero = f"{i:03d}"
            
            try:
                parametros = [
                    producto.get('IDEMPRESA'),
                    idingresosalidaalm,
                    item_numero,  # ITEM con formato 001, 002, etc.
                    producto.get('IDPRODUCTO'),
                    producto.get('DESCRIPCION'),
                    producto.get('IDSERIE'),
                    producto.get('IDLOTEP'),
                    producto.get('IDMEDIDA'),
                    producto.get('IDESTADOPRODUCTO', '0'),
                    producto.get('IDPROYECTO'),
                    producto.get('IDACTIVIDAD'),
                    producto.get('IDLABOR'),
                    producto.get('IDCONSUMIDOR'),
                    producto.get('TCAMBIO'),
                    producto.get('COMPROMETIDO', 1),
                    producto.get('IDEMPAQUE'),
                    producto.get('CANTEMPAQUE', 0),
                    producto.get('CANTIDAD'),
                    producto.get('AREA'),
                    producto.get('NUMPALETA'),
                    producto.get('PRECIO', 0),
                    producto.get('IMPORTE', 0),
                    producto.get('IDREFERENCIA'),
                    producto.get('ITEMREF'),
                    producto.get('TABLAREF'),
                    producto.get('PRECIOMOF', 0),
                    producto.get('PRECIOMEX', 0),
                    producto.get('IMPORTEMOF', 0),
                    producto.get('IMPORTEMEX', 0),
                    producto.get('IDPARTIDAPSTAL'),
                    producto.get('CODINTERNO'),
                    producto.get('CODIGOBARRA'),
                    producto.get('IDUBICACION'),
                    producto.get('LOTEORIGEN'),
                    producto.get('PRODUCTOORIGEN'),
                    producto.get('OBSERVACIONES'),
                    producto.get('IDFALLA'),
                    producto.get('IDPRODUCTOPROCESO'),
                    producto.get('IDMOVCOMPROMETIDO'),
                    producto.get('MERMA', 0),
                    producto.get('FACTORINSUMO', 0),
                    producto.get('CANTINSUMO', 0),
                    producto.get('CANTIPRODUCIDA', 0),
                    producto.get('IDSIEMBRA'),
                    producto.get('IDCAMPANA'),
                    producto.get('IDORDENPRODUCCION'),
                    producto.get('IDLOTEPRODUCCION'),
                    producto.get('DOCORDENPRODUCCION'),
                    producto.get('VOLUMEN'),
                    producto.get('IDACTIVO'),
                    producto.get('IDCULTIVO'),
                    producto.get('IDPRODUCTODESTINO'),
                    producto.get('DSC_PRODUCTODESTINO'),
                    producto.get('IDMEDIDA2'),
                    producto.get('CANTIDAD2', 0),
                    producto.get('idvehiculo'),
                    producto.get('docreqinterno'),
                    producto.get('idreqinterno'),
                    producto.get('ITEMREF_ORDENPRODUCCION'),
                    producto.get('placa'),
                    producto.get('kilometraje'),
                    producto.get('chofer'),
                    producto.get('NRO_VALE'),
                    producto.get('SEMANA'),
                    producto.get('DOSISLOTE'),
                    producto.get('estructura'),
                    producto.get('itemreqinterno'),
                    producto.get('DSC_DOCVENTA'),
                    producto.get('IDDOC_VENTA'),
                    producto.get('idchofer'),
                    producto.get('cMA30EqpID'),
                    producto.get('NROENVASES', 0),
                    producto.get('idinvernadero'),
                    producto.get('idnave'),
                    producto.get('idcampanainvernadero'),
                    producto.get('horometro', 0)
                ]
                
                cursor.execute(sql, parametros)
                print(f"Detalle insertado: ITEM {item_numero} - Producto {producto.get('IDPRODUCTO')}")
                
            except Exception as e:
                print(f"Error insertando item {item_numero}: {str(e)}")
                raise e


    


    def _insertar_documento_referencia(self, cursor, idingresosalidaalm, doc_referencia):
        """Inserta la referencia al documento origen en DOCREFERENCIA"""
        sql = """
        INSERT INTO DOCREFERENCIA (
            IDEMPRESA, IDORIGEN, TABLA, IDREFERENCIA,
            IDDOCUMENTO, SERIE, NUMERO, FECHA
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        parametros = [
            doc_referencia['IDEMPRESA'],
            idingresosalidaalm,
            doc_referencia.get('TABLA', 'REQINTERNO'),
            doc_referencia['IDREFERENCIA'],
            doc_referencia['IDDOCUMENTO'],
            doc_referencia['SERIE'],
            doc_referencia['NUMERO'],
            doc_referencia['FECHA']
        ]
        
        cursor.execute(sql, parametros)
    
    
    
    
    
    
    def _obtener_documento_creado(self, cursor, idingresosalidaalm):
        """Obtiene los datos del documento recién creado"""
        print(f"🔍 Buscando documento con ID: {idingresosalidaalm}")
        
        try:
            # Usar consulta con NOLOCK para leer datos no confirmados en la misma transacción
            cursor.execute("""
                SELECT IDINGRESOSALIDAALM, SERIE, NUMERO, FECHA, GLOSA, IDESTADO
                FROM INGRESOSALIDAALM WITH (NOLOCK)
                WHERE IDINGRESOSALIDAALM = ?
            """, [idingresosalidaalm])
            
            row = cursor.fetchone()
            print(f"🔍 Resultado de consulta: {row}")
            
            if row:
                documento = {
                    'idingresosalidaalm': row[0],
                    'serie': row[1],
                    'numero': row[2],
                    'fecha': row[3].strftime('%Y-%m-%d') if row[3] else None,
                    'glosa': row[4],
                    'estado': row[5]
                }
                print(f"✅ Documento encontrado: {documento}")
                return documento
            else:
                print("❌ No se encontró el documento con NOLOCK")
                
                # Intentar sin NOLOCK como fallback
                cursor.execute("""
                    SELECT IDINGRESOSALIDAALM, SERIE, NUMERO, FECHA, GLOSA, IDESTADO
                    FROM INGRESOSALIDAALM
                    WHERE IDINGRESOSALIDAALM = ?
                """, [idingresosalidaalm])
                
                row = cursor.fetchone()
                print(f"🔍 Resultado sin NOLOCK: {row}")
                
                if row:
                    documento = {
                        'idingresosalidaalm': row[0],
                        'serie': row[1],
                        'numero': row[2],
                        'fecha': row[3].strftime('%Y-%m-%d') if row[3] else None,
                        'glosa': row[4],
                        'estado': row[5]
                    }
                    print(f"✅ Documento encontrado sin NOLOCK: {documento}")
                    return documento
                else:
                    print("❌ No se encontró el documento en ninguna consulta")
                    return None
                    
        except Exception as e:
            print(f"❌ Error en consulta: {str(e)}")
            return None
    
    
    def _obtener_salida_detalle(self, cursor, idingresosalidaalm):
        """
        Obtiene el detalle completo de una salida específica usando consultas directas
        """
        try:
            # Consulta principal para obtener el encabezado de la salida interna
            cursor.execute("""
                SELECT * FROM INGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = '001'
            """, [idingresosalidaalm])
            
            encabezado_rows = cursor.fetchall()
            if not encabezado_rows:
                return JsonResponse({
                    'success': False,
                    'message': 'Salida interna no encontrada'
                }, status=404)
        
            # Convertir encabezado a diccionario
            encabezado_columns = [col[0] for col in cursor.description]
            encabezado_dict = dict(zip(encabezado_columns, encabezado_rows[0]))
            
            # Procesar fechas en el encabezado
            fecha_fields = ['FECHA', 'FECHACREACION', 'FECHADOCORIGEN', 'FECHATRASLADO', 'FECHADOCORIGEN2', 'FECHADOCORIGEN3', 'FECHACOSECHA', 'FECHAEXPIRACION', 'FECHA1', 'FECHA2']
            for field in fecha_fields:
                if field in encabezado_dict and encabezado_dict[field] is not None:
                    if hasattr(encabezado_dict[field], 'strftime'):
                        encabezado_dict[field] = encabezado_dict[field].strftime('%Y-%m-%d %H:%M:%S')
            
            # Obtener los detalles de la salida interna
            cursor.execute("""
                SELECT d.*, p.DESCRIPCION as DESCRIPCION_PRODUCTO
                FROM DINGRESOSALIDAALM d
                LEFT JOIN PRODUCTOS p ON d.IDPRODUCTO = p.IDPRODUCTO AND d.IDEMPRESA = p.IDEMPRESA
                WHERE d.IDINGRESOSALIDAALM = ? AND d.IDEMPRESA = '001'
                ORDER BY d.ITEM
            """, [idingresosalidaalm])
            
            detalles_rows = cursor.fetchall()
            detalles_columns = [col[0] for col in cursor.description]
            
            # Convertir detalles a lista de diccionarios
            detalles_list = []
            for detalle_row in detalles_rows:
                detalle_dict = dict(zip(detalles_columns, detalle_row))
                
                # Procesar fechas en los detalles
                fecha_fields_detalle = ['FECHA', 'VENCEPRODU', 'FECHA_SALIDA', 'FECHAETIQUETA', 'fecha_produccion', 'fecha_d']
                for field in fecha_fields_detalle:
                    if field in detalle_dict and detalle_dict[field] is not None:
                        if hasattr(detalle_dict[field], 'strftime'):
                            detalle_dict[field] = detalle_dict[field].strftime('%Y-%m-%d %H:%M:%S')
                
                # Procesar campos numéricos para evitar problemas de serialización
                numeric_fields = [
                    'TCAMBIO', 'COMPROMETIDO', 'CANTEMPAQUE', 'TARA', 'CANTBRUTA', 'CANTREMITIDA', 
                    'CANTREFERENCIAL', 'LIQUIDADO', 'DEVUELTO', 'DESCUENTO_I', 'DESCUENTO', 'ARANCEL',
                    'PESO', 'CANTIDAD', 'AREA', 'COSTODESCUENTO', 'DISTRIBUCION', 'REVISADO', 
                    'DESPACHADO', 'PRECIO', 'IMPORTE', 'VVENTA', 'IMPUESTO', 'IMPUESTO_I', 
                    'PRECIOMOF', 'PRECIOMEX', 'IMPORTEMOF', 'IMPORTEMEX', 'KGSELECCION', 'KGDEVOLUCION',
                    'KGPELADOS', 'KGTROZO', 'KGPELADILLA', 'TOTALCORTADO', 'RENDPELADO', 'KGENVASADO',
                    'KGDRENADOS', 'RENDENVASADO', 'MERMA', 'FACTORINSUMO', 'CANTINSUMO', 'CANTIPRODUCIDA',
                    'FACTURABLE', 'VOLUMEN', 'PRECIOVENTA', 'TARA2', 'CANTIDAD2', 'con_insumos',
                    'muestrabotonveh', 'liberado', 'BRUTO', 'NETO', 'JABAS', 'REB_A', 'CST_RECURSIVO',
                    'ALM_CAB', 'kilometraje', 'automatico_asociaop', 'GRATUITO', 'DOSISLOTE',
                    'por_oc_importado', 'con_certificacion', 'CANTEMPAQUE2', 'PESOPROMEDIO', 
                    'taraxempaque', 'Cant_Recibida', 'CANTIDAD_HISTORICO', 'preciofactura', 
                    'vventafactura', 'importefactura', 'impuestofac', 'NROENVASES', 'PESO_HISTORICO',
                    'ES_DRAWBACK', 'AUTOMATICO', 'dosis_tanque', 'nrotanque', 'horometro', 
                    'SOPLETEADO', 'cantidad_d', 'TCMONEDA'
                ]
                
                for field in numeric_fields:
                    if field in detalle_dict:
                        try:
                            if detalle_dict[field] is not None:
                                detalle_dict[field] = float(detalle_dict[field])
                            else:
                                detalle_dict[field] = 0.0
                        except (ValueError, TypeError):
                            detalle_dict[field] = 0.0
                
                # Procesar campos de texto para limpiar espacios
                text_fields = [
                    'IDPRODUCTO', 'DESCRIPCION', 'DESCRIPCION_PRODUCTO', 'IDKIT', 'IDSERIE', 
                    'IDLOTEP', 'IDMEDIDA', 'IDESTADOPRODUCTO', 'IDPROYECTO', 'IDACTIVIDAD', 
                    'IDLABOR', 'IDCONSUMIDOR', 'IDCAMPANA_P', 'IDCONSUMIDORO', 'IDDOCUMENTO',
                    'SERIE', 'NUMERO', 'IDEMPAQUE', 'NUMPALETA', 'IDREFERENCIA', 'ITEMREF',
                    'TABLAREF', 'IDPARTIDAPSTAL', 'JULRECEPCION', 'JULCOSECHA', 'DESCCALIBRE',
                    'FORMATO', 'CODFABRICA', 'CODINTERNO', 'CODIGOBARRA', 'IDUBICACION',
                    'IDPROCESO', 'IDSUBPROCESO', 'LOTEORIGEN', 'PRODUCTOORIGEN', 'OBSERVACIONES',
                    'HORA', 'NROVIAJE', 'OBSERVACION', 'IDFALLA', 'IDPRODUCTOPROCESO', 
                    'IDMOVCOMPROMETIDO', 'DUA', 'SERIEDUA', 'IDDEVOLUCION', 'ITEMDEVO',
                    'IDSIEMBRA', 'IDCAMPANA', 'IDORDENPRODUCCION', 'IDLOTEPRODUCCION', 
                    'DOCORDENPRODUCCION', 'DOCLOTEPRODUCCION', 'IDMEDIDAEQ', 'IDUNIDADCOSTO',
                    'IDUNIDADNEGOCIO', 'IDACTIVO', 'IDCULTIVO', 'IDVARIEDAD', 'IDTIPOCOSECHA',
                    'IDCABEZAL', 'IDPRODUCTODESTINO', 'DSC_PRODUCTODESTINO', 'IDMEDIDA2', 'DM',
                    'IDCAMARA', 'idvehiculo', 'anio', 'idcolor', 'IDORDENMANTENIMIENTO',
                    'DOCORDENMANTENIMIENTO', 'docreqinterno', 'idreqinterno', 'ITEMREF_ORDENPRODUCCION',
                    'IDTALLA', 'IDENVASE', 'IDCONDICION', 'IDPRESENTACION', 'DSC_CULTIVO',
                    'DSC_VARIEDAD', 'DSC_COLOR', 'DSC_TALLA', 'DSC_ENVASE', 'DSC_CONDICION',
                    'DSC_PRESENTACION', 'IDREFERENCIA2', 'ITEMREF2', 'TABLAREF2', 'IDACTIVO_AVICOLA',
                    'placa', 'chofer', 'NRO_VALE', 'ITEM1', 'IDUBICACIONA', 'SEMANA',
                    'IDTIPOAFECTACION', 'estructura', 'itemreqinterno', 'dato1', 'idestadoc',
                    'DSC_DOCVENTA', 'IDDOC_VENTA', 'idlotep_o', 'idempaque2', 'IDCUENTA',
                    'idchofer', 'cMA30EqpID', 'IDRECOLECCION', 'IDTURNORIE', 'zonificacion',
                    'idproductod', 'descripciond', 'idconsumidord', 'idlotepd', 'IDUBICACIOND',
                    'ccalidad', 'idccalidad', 'idproductor', 'idarea', 'idresponsable',
                    'idinvernadero', 'idnave', 'idcampanainvernadero', 'IDESTADO', 'idembarcacion',
                    'LDP', 'item_d'
                ]
                
                for field in text_fields:
                    if field in detalle_dict and detalle_dict[field] is not None:
                        detalle_dict[field] = str(detalle_dict[field]).strip()
                    elif field in detalle_dict:
                        detalle_dict[field] = ''
                
                detalles_list.append(detalle_dict)
            
            # Calcular totales
            totales_dict = {
                'TOTAL_CANTIDAD': sum(float(d.get('CANTIDAD', 0) or 0) for d in detalles_list),
                'TOTAL_PESO': sum(float(d.get('PESO', 0) or 0) for d in detalles_list),
                'TOTAL_IMPORTE': sum(float(d.get('IMPORTE', 0) or 0) for d in detalles_list),
                'TotalDetalles': len(detalles_list)
            }
            
            # Procesar campos de texto en encabezado para limpiar espacios
            text_fields_encabezado = [
                'IDEMPRESA', 'IDINGRESOSALIDAALM', 'IDEMISOR', 'PERIODO', 'IDOPERACION', 
                'NUMOPERACION', 'IDSUBDIARIO', 'VOUCHER', 'IDALMACEN', 'IDDOCUMENTO', 
                'SERIE', 'NUMERO', 'IDCLIEPROV', 'IDPROYECTO', 'IDRESPONSABLE', 'GLOSA',
                'IDMONEDA', 'IDMOTIVO', 'IDALMACEND', 'IDDOCORIGEN', 'SERIEDOCORIGEN',
                'NUMDOCORIGEN', 'IDFLETE', 'IDTRANSPORTISTA', 'CERTIFTRANSPORTE', 
                'CERTIFTRANSPORTE1', 'PLACA', 'PLACA1', 'MARCA', 'MARCA1', 'CHOFER',
                'BREVETE', 'LLEVADOPOR', 'DIRECLLEGADA', 'SINCRONIZA', 'IDESTADO',
                'IDCONTABILIZADO', 'IDCONSUMIDOR', 'IDLINEAPRODUC', 'IDLOTE', 'IDSUCURSALD',
                'IDDOCORIGEN2', 'SERIEDOCORIGEN2', 'NUMDOCORIGEN2', 'IDSUCURSAL', 'VENTANA',
                'OCCLIENTE', 'OTRADIRECCION', 'HORA', 'IDMONEDA_FLETE', 'IDCONTROLADOR',
                'IDCLIEPROVDEST', 'IDCOMPRA', 'IDUBIGEOLLEGADA', 'IDDOCORIGEN3', 'SERIEDOCORIGEN3',
                'NUMDOCORIGEN3', 'IDUNIDADNEGOCIO', 'IDCNFDISTRIBUCION', 'IDTURNOTRABAJO',
                'IDPRODUCTO', 'IDREFERENCIAPROCESO', 'IDPROCESO', 'IDSUBPROCESO', 'NRO_PRECINTO',
                'IDPARTEPRODUCCION', 'IDSUBUNIDADNEGOCIO', 'itemptollegada', 'IDCLIEPROV2',
                'Idtipoenvioremision', 'IDREFERENCIA_EXTERNO', 'IDTIPOPRECINTO', 'IDAGRICULTOR',
                'IDSOLICITANTE', 'DESTINO', 'IDPTGENERADO', 'IDSALIDAMP', 'LINEA_EMBARQUE',
                'NRO_CONTENEDOR', 'NRO_DER', 'NRO_INSTRUCCION', 'NRO_PEDIDO', 'idcamara',
                'NROEMBARQUE', 'IDPACKINGLIST', 'IDUSUARIO1', 'IDUSUARIO2', 'IDREFERENCIA1',
                'IDREFERENCIA2', 'DOCREF2', 'VENTANAREF2', 'Codigo_Spring', 'IDBALANZA',
                'NROMATRICULA', 'idtipocamion', 'idalmacenmp', 'IDSALIDA_RECLASIF', 
                'IDINGRESO_RECLASIF', 'MODULO', 'idordenpro', 'idingresosalidaactivo',
                'IDMOTIVO_TRASLADO_SUNAT', 'PTOPARTIDA', 'MOTIVO_TRASLADO', 'IDUBIGEO1',
                'IDUBIGEO2', 'idviaje', 'dni', 'IDMOTIVO_AN', 'MOTIVO_AN', 'IDRESPONSABLE_AN',
                'OBSERVACION_AN', 'idusuario', 'IDVEHICULO', 'IDCHOFER', 'CMA30EQPID_CAMION',
                'CMA30EQPID_CARRETA', 'IDRUTA', 'IDLUGAR_O', 'IDLUGAR_D', 'ITEM_RUTA',
                'Ini_Desc_Usr', 'Fin_Desc_Usr', 'Lugar_Descarga', 'env_tipo_proceso',
                'env_idsuc_proceso', 'env_idalm_proceso', 'env_idsalida_proceso', 
                'env_idingreso_proceso', 'config_veh', 'GUIATRANSPORTISTA', 'NRO_BOOKING',
                'archivo_signed_ce', 'archivo_ce', 'idmodalidad_transporte', 'IDUBIGEOPARTIDA',
                'IDAREA', 'idcontrato', 'sello_ggn', 'sello_codProductor', 'sello_ProductoTransf',
                'IDESTADO2', 'IDTIPO_OPERACION_VOLCADO', 'IDINGRESOSALIDAALM_GENERAL', 'dua',
                'llevadopor_dni', 'IDUSUARIO_ULTIMO', 'origen_formulario', 'idingresosalidaalm_ajuste_inv',
                'NUM_EXPORTACION', 'CONSIGNATARIO', 'idingreso', 'idsalida', 'ticket_acopio',
                'NROPRESINTOCAMPO', 'idtipodesc', 'IDFPAGO', 'idmedida_peso', 'qr_sunat',
                'NUMPALLETMATPRIMA', 'chofer_apellido', 'IDORIGEN3', 'productor_ggn',
                'certificado_por', 'codigolp', 'idcomprador', 'idembarcacion', 'chofer_iddocidentidad',
                'DEPOSITORETIRO', 'CANAL', 'duadam'
            ]
            
            for field in text_fields_encabezado:
                if field in encabezado_dict and encabezado_dict[field] is not None:
                    encabezado_dict[field] = str(encabezado_dict[field]).strip()
                elif field in encabezado_dict:
                    encabezado_dict[field] = ''
            
            # Procesar campos numéricos en encabezado
            numeric_fields_encabezado = [
                'TCAMBIO', 'TCMONEDA', 'PRECIOIGV', 'REDONDEO', 'TOTAL', 'ES_GASTOS', 
                'ES_PROVISION', 'ES_RIEGO', 'CONTABILIZADO', 'VVENTA', 'IMPUESTO', 
                'DESCUENTO', 'VOLUMEN', 'NUMBATCH', 'NUMAUTOCLAVE', 'IMPRESO', 'IMPORTE_FLETE',
                'PESO_TOTAL', 'IMPORTADO', 'ES_COSTOS', 'pesodocorigen3', 'IDREGISTROVAR',
                'AREA_HA', 'IMPORTADO_EXTERNO', 'contador', 'PESO1', 'PESO2', 'automatico_asociaop',
                'numversion', 'transferir_comprometido', 'precio_generado', 'estado_ce',
                'ticket_pesada', 'ticket_pesada1', 'solicita_analisis', 'generado_x_distri',
                'nro_bultos', 'total_distribucion', 'mostrar_sellos', 'sello_estadoCertific',
                'importado_nsprov', 'cerrado', 'peso_descuento_comercial', 'precioun_desc_ajustado',
                'ind_retorno_vehiculo_envase_vacio', 'ind_retorno_vehiculo_vacio', 
                'ind_traslado_programado', 'ind_traslado_total_damods', 'ind_traslado_vehiculo_m1l',
                'ind_trasporte_subcontrado', 'ind_vehiculo_conductores_trasporte'
            ]
            
            for field in numeric_fields_encabezado:
                if field in encabezado_dict:
                    try:
                        if encabezado_dict[field] is not None:
                            encabezado_dict[field] = float(encabezado_dict[field])
                        else:
                            encabezado_dict[field] = 0.0
                    except (ValueError, TypeError):
                        encabezado_dict[field] = 0.0
            
            # Procesar campos booleanos/numéricos (0/1)
            boolean_fields_encabezado = ['CONTABILIZADO', 'CERRADO', 'IMPRESO']
            for field in boolean_fields_encabezado:
                if field in encabezado_dict:
                    try:
                        if encabezado_dict[field] is not None:
                            encabezado_dict[field] = bool(int(float(encabezado_dict[field])))
                        else:
                            encabezado_dict[field] = False
                    except (ValueError, TypeError):
                        encabezado_dict[field] = False

            return JsonResponse({
                'success': True,
                'message': 'Detalle de salida interna obtenido correctamente',
                'encabezado': encabezado_dict,
                'detalles': detalles_list,
                'totales': totales_dict,
                'total_items': len(detalles_list)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener el detalle de la salida interna: {str(e)}'
            }, status=500)
    
    def _obtener_lista_salidas(self, cursor, request):
        """Obtiene lista de salidas internas con filtros usando el procedimiento almacenado"""
        try:
            # Obtener parámetros de la request
            idempresa = request.GET.get('idempresa', '001')  # Default empresa
            fecha_desde = request.GET.get('fecha_desde')
            fecha_hasta = request.GET.get('fecha_hasta')
            idestado = request.GET.get('idestado')
            idmotivo = request.GET.get('idmotivo')
            
            # Convertir fechas si se proporcionan
            fecha_desde_param = None
            fecha_hasta_param = None
        
            if fecha_desde:
                try:
                    fecha_desde_param = datetime.strptime(fecha_desde, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                    }, status=400)
        
            if fecha_hasta:
                try:
                    fecha_hasta_param = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                    }, status=400)
            
            print(f"🔍 Ejecutando consulta de salidas internas con parámetros:")
            print(f"   - IDEMPRESA: {idempresa}")
            print(f"   - FECHA_DESDE: {fecha_desde_param}")
            print(f"   - FECHA_HASTA: {fecha_hasta_param}")
            print(f"   - IDESTADO: {idestado}")
            print(f"   - IDMOTIVO: {idmotivo}")
            
            # Ejecutar procedimiento almacenado
            cursor.execute("""
                EXEC SP_GET_SALIDAS_INTERNAS_ALMACEN ?, ?, ?, ?, ?
            """, [
                idempresa,
                fecha_desde_param,
                fecha_hasta_param,
                idestado if idestado and idestado != 'todos' else None,
                idmotivo if idmotivo and idmotivo != 'todos' else None
            ])
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(results)} registros")
        
            # Convertir a lista de diccionarios
            salidas = []
            for row in results:
                salida = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fechas
                    if isinstance(value, datetime) and value:
                        salida[column_name.lower()] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, date) and value:
                        salida[column_name.lower()] = value.strftime('%Y-%m-%d')
                    else:
                        # Limpiar strings (quitar espacios)
                        if isinstance(value, str):
                            salida[column_name.lower()] = value.strip()
                        else:
                            salida[column_name.lower()] = value
                
                salidas.append(salida)
        
            return JsonResponse({
                'success': True,
                'data': salidas,
                'total': len(salidas),
                'filtros_aplicados': {
                    'idempresa': idempresa,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'idestado': idestado,
                    'idmotivo': idmotivo
                },
                'info': {
                    'procedimiento_usado': 'SP_GET_SALIDAS_INTERNAS_ALMACEN',
                    'descripcion': 'Salidas internas obtenidas mediante procedimiento almacenado optimizado'
                }
            })
            
        except Exception as e:
            print(f"❌ Error en consulta de salidas: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al consultar salidas: {str(e)}'
            }, status=500)
    
    def _verificar_salida_modificable(self, cursor, idingresosalidaalm):
        """Verifica si una salida puede ser modificada"""
        cursor.execute("""
            SELECT IDESTADO FROM INGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        resultado = cursor.fetchone()
        if not resultado:
            return False
        
        # Solo permitir modificar si está en estado Pendiente
        return resultado[0] == 'PE'
    
    def _verificar_salida_anulable(self, cursor, idingresosalidaalm):
        """Verifica si una salida puede ser anulada"""
        cursor.execute("""
            SELECT IDESTADO, CONTABILIZADO FROM INGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        resultado = cursor.fetchone()
        if not resultado:
            return False
        
        estado, contabilizado = resultado
        # No permitir anular si ya está anulado o contabilizado
        return estado != 'AN' and contabilizado != 1
    
    def _actualizar_encabezado(self, cursor, idingresosalidaalm, datos_encabezado):
        """Actualiza el encabezado de una salida existente"""
        sql = """
        UPDATE INGRESOSALIDAALM 
        SET GLOSA = ?, IDRESPONSABLE = ?, IDMOTIVO = ?,
            FECHACREACION = GETDATE(), IDUSUARIO = ?
        WHERE IDINGRESOSALIDAALM = ?
        """
        
        cursor.execute(sql, [
            datos_encabezado.get('GLOSA'),
            datos_encabezado.get('IDRESPONSABLE'),
            datos_encabezado.get('IDMOTIVO'),
            datos_encabezado.get('IDUSUARIO'),
            idingresosalidaalm
        ])
    
    def _actualizar_detalles(self, cursor, idingresosalidaalm, productos):
        """Actualiza los detalles de una salida existente"""
        # Eliminar detalles existentes
        cursor.execute("""
            DELETE FROM DINGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        # Insertar nuevos detalles
        self._insertar_detalles(cursor, idingresosalidaalm, productos)


@method_decorator(csrf_exempt, name='dispatch')
class ProcesarSalidaInternaView(View):
    """
    Clase para procesar la contabilización y centralización de salidas internas
    Ejecuta los procedimientos CONTAB_INGRESOSALIDAALM y CENTRALIZA_ALMACENES
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa la contabilización y centralización de una salida interna
        """
        data = json.loads(request.body)
        
        idingresosalidaalm = data.get('IDINGRESOSALIDAALM', '')
        idempresa = data.get('IDEMPRESA', '001')
        ventana = data.get('VENTANA', 'EDT_SALIDAS')
        idemisor = data.get('IDEMISOR', '001')
        
        print(f"🔄 Iniciando contabilización...")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm}")
        print(f"   - IDEMPRESA: {idempresa}")
        print(f"   - VENTANA: {ventana}")
        print(f"   - IDEMISOR: {idemisor}")
        
        # Crear conexión principal
        cursor = connection_donluis.cursor()
        
        try:
            # 1. Verificar existencia y validaciones previas
            print("🔍 Validando documento...")
            
            # Verificar existencia del documento
            cursor.execute("""
                SELECT CONTABILIZADO, IDESTADO, IDMOTIVO, VENTANA 
                FROM INGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
            """, [idingresosalidaalm, idempresa])
            
            resultado = cursor.fetchone()
            if not resultado:
                return JsonResponse({
                    'success': False,
                    'error': f'No se encontró el documento {idingresosalidaalm}'
                })
            
            contabilizado_actual, estado_actual, idmotivo, ventana_doc = resultado
            print(f"📋 Estado actual - CONTABILIZADO: {contabilizado_actual}, ESTADO: {estado_actual}, MOTIVO: {idmotivo}")
            
            # Si ya está contabilizado, solo intentar centralizar
            if contabilizado_actual == 1:
                print("📋 Documento ya contabilizado, procediendo solo con centralización...")
                return self._centralizar_documento(idingresosalidaalm, idempresa, idemisor)
            
            if estado_actual == 'AN':
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede contabilizar un documento anulado'
                })
            
            # 2. Validar parámetros que pueden impedir la contabilización
            print("🔍 Validando parámetros internos...")
            
            # Verificar parámetro AL_EVITAR_CONTAB_ALM_CE
            cursor.execute("""
                SELECT ISNULL(VALOR,'NO') 
                FROM PARAMETRO 
                WHERE IDPARAMETRO = 'AL_EVITAR_CONTAB_ALM_EST_CE' AND IDEMPRESA = ?
            """, [idempresa])
            
            evitar_contab_ce = cursor.fetchone()
            evitar_contab_ce = evitar_contab_ce[0] if evitar_contab_ce else 'NO'
            
            if estado_actual == 'CE' and evitar_contab_ce == 'SI':
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede contabilizar documentos con estado CE según parámetro AL_EVITAR_CONTAB_ALM_EST_CE'
                })
            
            # Verificar si el motivo permite contabilización
            cursor.execute("""
                SELECT ISNULL(CONTAB_MOVALM,0) as KARDEX, TIPO_MOTIVO, ISNULL(ES_TRANSFERENCIA,0) as ES_TRANSFERENCIA
                FROM MOTIVOS 
                WHERE IDMOTIVO = ?
            """, [idmotivo])
            
            motivo_info = cursor.fetchone()
            if motivo_info:
                kardex, tipo_motivo, es_transferencia = motivo_info
                print(f"📋 Motivo info - KARDEX: {kardex}, TIPO: {tipo_motivo}, ES_TRANSFERENCIA: {es_transferencia}")
                
                if kardex == 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'El motivo {idmotivo} no permite generar movimientos de almacén (KARDEX=1)'
                    })
            
            # 3. Validar transferencias pendientes de aprobación
            if motivo_info and es_transferencia == 1:
                cursor.execute("""
                    SELECT ISNULL(VALOR,'NO') 
                    FROM PARAMETRO 
                    WHERE IDPARAMETRO = 'AL_TRANSF_CONTAB_APROB' AND IDEMPRESA = ?
                """, [idempresa])
                
                transf_aprob = cursor.fetchone()
                transf_aprob = transf_aprob[0] if transf_aprob else 'NO'
                
                if transf_aprob == 'SI':
                    print("⚠️ Documento de transferencia con validación de aprobación habilitada")
            
            # 4. Ejecutar el procedimiento de contabilización
            print(f"🔄 Ejecutando procedimiento CONTAB_INGRESOSALIDAALM...")
            
            import pyodbc
            
            # Crear nueva conexión independiente
            host = '192.168.0.5'
            database = 'DONLUIS'  # Para prueba
            user = 'sa'
            password = '@SADL.2023'
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};MARS_Connection=yes'
            
            conn = pyodbc.connect(conn_str)
            cursor_proc = conn.cursor()
            
            try:
                # Habilitar PRINT messages de SQL Server
                cursor_proc.execute("SET NOCOUNT OFF")
                
                # Ejecutar el procedimiento
                print(f"📤 Ejecutando: EXEC CONTAB_INGRESOSALIDAALM '{idingresosalidaalm}', '{idempresa}', '{ventana}', 'A', '{idemisor}'")
                
                cursor_proc.execute("""
                    EXEC CONTAB_INGRESOSALIDAALM ?, ?, ?, ?, ?
                """, [idingresosalidaalm, idempresa, ventana, 'A', idemisor])
                
                # Capturar mensajes del procedimiento
                messages = []
                while cursor_proc.nextset():
                    try:
                        results = cursor_proc.fetchall()
                        if results:
                            messages.extend([str(row) for row in results])
                    except:
                        pass
                
                # Confirmar transacción
                conn.commit()
                print("✅ Procedimiento de contabilización ejecutado y confirmado")
                
                if messages:
                    print(f"📝 Mensajes del procedimiento: {messages}")
                
                # 5. Verificar resultado de contabilización
                cursor_proc.execute("""
                    SELECT CONTABILIZADO 
                    FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [idingresosalidaalm, idempresa])
                
                resultado_final = cursor_proc.fetchone()
                contabilizado_final = resultado_final[0] if resultado_final else 0
                
                print(f"🔍 Verificación contabilización - CONTABILIZADO: {contabilizado_final}")
                
                cursor_proc.close()
                conn.close()
                
                if contabilizado_final == 1:
                    print("✅ Contabilización exitosa, procediendo con centralización...")
                    
                    # 6. Ejecutar centralización
                    resultado_centralizacion = self._centralizar_documento(idingresosalidaalm, idempresa, idemisor)
                    
                    # Combinar resultados
                    if resultado_centralizacion.status_code == 200:
                        data_centralizacion = json.loads(resultado_centralizacion.content)
                        if data_centralizacion.get('success'):
                            return JsonResponse({
                                'success': True,
                                'message': 'Procesos ejecutados exitosamente',
                                'data': {
                                    'IDINGRESOSALIDAALM': idingresosalidaalm,
                                    'CONTABILIZADO': contabilizado_final,
                                    'ESTADO': 'PE',
                                    'procesos_ejecutados': [
                                        'CONTAB_INGRESOSALIDAALM',
                                        'CENTRALIZA_ALMACENES'
                                    ]
                                }
                            })
                        else:
                            return JsonResponse({
                                'success': True,
                                'message': 'Contabilización exitosa, pero centralización falló',
                                'warning': data_centralizacion.get('error', 'Error desconocido en centralización'),
                                'data': {
                                    'IDINGRESOSALIDAALM': idingresosalidaalm,
                                    'CONTABILIZADO': contabilizado_final,
                                    'procesos_ejecutados': ['CONTAB_INGRESOSALIDAALM']
                                }
                            })
                    else:
                        return JsonResponse({
                            'success': True,
                            'message': 'Contabilización exitosa, pero error en centralización',
                            'warning': 'No se pudo ejecutar la centralización',
                            'data': {
                                'IDINGRESOSALIDAALM': idingresosalidaalm,
                                'CONTABILIZADO': contabilizado_final,
                                'procesos_ejecutados': ['CONTAB_INGRESOSALIDAALM']
                            }
                        })
                else:
                    # Intentar obtener más información sobre por qué falló
                    cursor.execute("""
                        SELECT TOP 1 
                            I.IDESTADO, I.IDESTADO2, M.CONTAB_MOVALM, M.TIPO_MOTIVO,
                            I.VENTANA, M.GRUPO_MOTIVO
                        FROM INGRESOSALIDAALM I
                        LEFT JOIN MOTIVOS M ON I.IDMOTIVO = M.IDMOTIVO
                        WHERE I.IDINGRESOSALIDAALM = ? AND I.IDEMPRESA = ?
                    """, [idingresosalidaalm, idempresa])
                    
                    debug_info = cursor.fetchone()
                    debug_msg = f"Debug info: {debug_info}" if debug_info else "No debug info available"
                    
                    return JsonResponse({
                        'success': False,
                        'error': 'El procedimiento se ejecutó pero no contabilizó el documento. Posibles causas: validaciones internas del procedimiento, estado del documento, configuración de parámetros.',
                        'debug': debug_msg,
                        'messages': messages,
                        'data': {
                            'IDINGRESOSALIDAALM': idingresosalidaalm,
                            'CONTABILIZADO': contabilizado_final
                        }
                    })
                    
            except Exception as proc_error:
                conn.rollback()
                cursor_proc.close()
                conn.close()
                print(f"❌ Error en procedimiento de contabilización: {str(proc_error)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al ejecutar procedimiento de contabilización: {str(proc_error)}'
                })
                
        except Exception as e:
            print(f"❌ Error general: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el proceso: {str(e)}'
            })
        finally:
            if cursor:
                cursor.close()

    def _centralizar_documento(self, idingresosalidaalm, idempresa, idemisor):
        """
        Ejecuta el procedimiento de centralización de almacenes
        EXEC CENTRALIZA_ALMACENES idempresa, idingresosalidaalm, '', idemisor
        """
        print(f"🔄 Iniciando centralización de almacenes...")
        print(f"   - IDEMPRESA: {idempresa}")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm}")
        print(f"   - IDEMISOR: {idemisor}")
        
        import pyodbc
        
        try:
            # Crear nueva conexión independiente para centralización
            host = '192.168.0.5'
            database = 'DONLUIS'  # Para prueba
            user = 'sa'
            password = '@SADL.2023'
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};MARS_Connection=yes'
            
            conn = pyodbc.connect(conn_str)
            cursor_proc = conn.cursor()
            
            try:
                # Habilitar PRINT messages de SQL Server
                cursor_proc.execute("SET NOCOUNT OFF")
                
                # Ejecutar el procedimiento de centralización
                print(f"📤 Ejecutando: EXEC CENTRALIZA_ALMACENES '{idempresa}', '{idingresosalidaalm}', '', '{idemisor}'")
                
                cursor_proc.execute("""
                    EXEC CENTRALIZA_ALMACENES ?, ?, ?, ?
                """, [idempresa, idingresosalidaalm, '', idemisor])
                
                # Capturar mensajes del procedimiento
                messages = []
                while cursor_proc.nextset():
                    try:
                        results = cursor_proc.fetchall()
                        if results:
                            messages.extend([str(row) for row in results])
                    except:
                        pass
                
                # Confirmar transacción
                conn.commit()
                print("✅ Procedimiento de centralización ejecutado y confirmado")
                
                if messages:
                    print(f"📝 Mensajes del procedimiento de centralización: {messages}")
                
                # Verificar estado final del documento
                cursor_proc.execute("""
                    SELECT IDESTADO 
                    FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [idingresosalidaalm, idempresa])
                
                resultado_estado = cursor_proc.fetchone()
                estado_final = resultado_estado[0] if resultado_estado else 'Desconocido'
                
                print(f"🔍 Verificación centralización - ESTADO: {estado_final}")
                
                cursor_proc.close()
                conn.close()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Centralización ejecutada exitosamente',
                    'data': {
                        'IDINGRESOSALIDAALM': idingresosalidaalm,
                        'ESTADO': estado_final,
                        'messages': messages
                    }
                })
                
            except Exception as proc_error:
                conn.rollback()
                cursor_proc.close()
                conn.close()
                print(f"❌ Error en procedimiento de centralización: {str(proc_error)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al ejecutar procedimiento de centralización: {str(proc_error)}'
                })
                
        except Exception as e:
            print(f"❌ Error general en centralización: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el proceso de centralización: {str(e)}'
            })


# Actualiza los estados del requerimiento procesado: 
#ProcesarRequerimientoInternoAPI
@method_decorator(csrf_exempt, name='dispatch')
class ProcesarRequerimientoInternoAPI(View):
    """
    Vista simplificada para procesar productos REQINTERNO
    Ejecuta stored procedures: CAMBIA_ESTADOREQINTERNO_DET y ACTUALIZA_ESTADO_REQINTERNO
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa requerimientos internos con la estructura enviada desde JavaScript
        """
        cursor = None
        
        try:
            print("🚀 ===== INICIANDO PROCESAMIENTO REQINTERNO API =====")
            
            # Parsear JSON del request
            data = json.loads(request.body)
            print(f"📋 Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Extraer secciones principales
            encabezado = data.get('encabezado', {})
            productos = data.get('productos', [])
            documento_referencia = data.get('documento_referencia', {})
            idingresosalidaalm = data.get('idingresosalidaalm', '')
            
            # Validaciones básicas
            if not encabezado.get('IDEMPRESA'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDEMPRESA faltante en encabezado',
                    'code': 'MISSING_IDEMPRESA'
                }, status=400)
            
            if not productos:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Lista de productos está vacía',
                    'code': 'MISSING_PRODUCTOS'
                }, status=400)
            
            if not documento_referencia.get('IDREFERENCIA'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDREFERENCIA faltante en documento_referencia',
                    'code': 'MISSING_IDREFERENCIA'
                }, status=400)
            
            if not idingresosalidaalm:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDINGRESOSALIDAALM está vacío',
                    'code': 'MISSING_IDINGRESOSALIDAALM'
                }, status=400)
            
            print("✅ Validaciones básicas exitosas")
            
            # Procesar con conexión fresca
            resultado = self._procesar_requerimiento_simplificado(
                encabezado, productos, documento_referencia, idingresosalidaalm
            )
            
            if resultado['success']:
                return JsonResponse({
                    'status': 'success',
                    'message': resultado['message'],
                    'data': {
                        'productos_procesados': resultado['productos_procesados'],
                        'idempresa': encabezado.get('IDEMPRESA'),
                        'idreferencia': documento_referencia.get('IDREFERENCIA'),
                        'idingresosalidaalm': idingresosalidaalm
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': resultado['message'],
                    'code': 'PROCESSING_ERROR'
                }, status=500)
                
        except json.JSONDecodeError as e:
            print(f"❌ Error JSON: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'JSON inválido: {str(e)}',
                'code': 'INVALID_JSON'
            }, status=400)
            
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            print(f"📊 Stack trace: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=500)
    
    def _procesar_requerimiento_simplificado(self, encabezado, productos, documento_referencia, idingresosalidaalm):
        """
        Procesa el requerimiento con conexión fresca usando el patrón de SalidaInternaView
        """
        try:
            # Obtener parámetros principales
            idempresa = encabezado.get('IDEMPRESA')
            idreferencia = documento_referencia.get('IDREFERENCIA')
            
            print(f"📋 ===== PROCESANDO REQUERIMIENTO =====")
            print(f"🏢 IDEMPRESA: {idempresa}")
            print(f"📄 IDREFERENCIA: {idreferencia}")
            print(f"🆔 IDINGRESOSALIDAALM: {idingresosalidaalm}")
            print(f"📦 Total productos: {len(productos)}")
            
            # Usar el mismo patrón que SalidaInternaView
            cursor = connection_donluis.cursor()
            
            # Forzar autocommit=True (igual que SalidaInternaView)
            connection_donluis.autocommit = True
            print("🔧 Autocommit configurado a True")
            
            productos_procesados = 0
            
            # PASO 1: Ejecutar CAMBIA_ESTADOREQINTERNO_DET para cada producto
            print("📋 ===== PASO 1: CAMBIA_ESTADOREQINTERNO_DET =====")
            
            for i, producto in enumerate(productos, 1):
                idproducto = producto.get('IDPRODUCTO', '')
                itemref = producto.get('ITEMREF', '')
                tablaref = producto.get('TABLAREF', 'REQINTERNO')
                
                print(f"📦 Producto {i}/{len(productos)}: {idproducto} - Item: {itemref}")
                
                if not idproducto or not itemref:
                    print(f"⚠️ Saltando producto {i} - datos incompletos")
                    continue
                
                # Generar XML
                xml_antes, xml_ahora = self._generar_xml_simple(
                    idproducto, idreferencia, itemref, tablaref
                )
                
                # Ejecutar procedimiento
                try:
                    cursor.execute(
                        "EXEC CAMBIA_ESTADOREQINTERNO_DET ?, ?, ?",
                        [idempresa, xml_antes, xml_ahora]
                    )
                    
                    # Consumir resultados
                    while cursor.nextset():
                        pass
                    
                    productos_procesados += 1
                    print(f"✅ Producto {i} procesado exitosamente")
                    
                except Exception as prod_error:
                    print(f"❌ Error procesando producto {i}: {str(prod_error)}")
                    raise prod_error
            
            print(f"✅ PASO 1 completado: {productos_procesados} productos")
            
            # PASO 2: Ejecutar ACTUALIZA_ESTADO_REQINTERNO
            print("📋 ===== PASO 2: ACTUALIZA_ESTADO_REQINTERNO =====")
            
            cursor.execute(
                "EXEC ACTUALIZA_ESTADO_REQINTERNO ?, ?, ?",
                [idempresa, idingresosalidaalm, idreferencia]
            )
            
            # Consumir resultados
            while cursor.nextset():
                pass
            
            print("✅ PASO 2 completado exitosamente")
            
            # Verificar resultados
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM REQINTERNO 
                    WHERE IDREFERENCIA = ? AND IDEMPRESA = ?
                """, [idreferencia, idempresa])
                result = cursor.fetchone()
                count_reqs = result[0] if result else 0
                print(f"📈 Requerimientos en BD: {count_reqs}")
            except Exception as verification_error:
                print(f"⚠️ Error en verificación: {str(verification_error)}")
            
            # Cerrar cursor
            cursor.close()
            print("🔄 Cursor cerrado")
            
            return {
                'success': True,
                'message': f'Procesamiento exitoso: {productos_procesados} productos',
                'productos_procesados': productos_procesados
            }
            
        except Exception as e:
            print(f"❌ Error en procesamiento: {str(e)}")
            
            # Limpiar cursor
            try:
                if 'cursor' in locals():
                    cursor.close()
            except:
                pass
            
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'productos_procesados': 0
            }
    
    def _generar_xml_simple(self, idproducto, idreferencia, itemref, tablaref="REQINTERNO"):
        """
        Genera XML para los procedimientos almacenados
        """
        def escape_xml(texto):
            if texto is None:
                return ""
            return str(texto).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Limpiar valores
        idproducto_clean = escape_xml(idproducto)
        idreferencia_clean = escape_xml(idreferencia)
        itemref_clean = escape_xml(itemref)
        tablaref_clean = escape_xml(tablaref)
        
        # XML Antes
        xml_antes = (
            f'<VFPData><disa_antes><record>'
            f'<idproducto>{idproducto_clean}</idproducto>'
            f'<idreferencia>{idreferencia_clean}</idreferencia>'
            f'<itemref>{itemref_clean}</itemref>'
            f'<tablaref>{tablaref_clean}</tablaref>'
            f'</record></disa_antes></VFPData>'
        )
        
        # XML Ahora
        xml_ahora = (
            f'<VFPData><disa_ahora><record>'
            f'<idproducto>{idproducto_clean}</idproducto>'
            f'<idreferencia>{idreferencia_clean}</idreferencia>'
            f'<itemref>{itemref_clean}</itemref>'
            f'<tablaref>{tablaref_clean}</tablaref>'
            f'</record></disa_ahora></VFPData>'
        )
        
        return xml_antes, xml_ahora


@method_decorator(csrf_exempt, name='dispatch')
class TipoCambioView(View):
    """
    Clase para obtener el tipo de cambio según la fecha
    Ejecuta la consulta: SELECT FECHA,T_COMPRA FROM TCAMBIO WHERE FECHA = ?
    """
    
    def get(self, request, *args, **kwargs):
        """
        Método GET para obtener el tipo de cambio
        Parámetros esperados:
        - fecha: fecha en formato YYYY-MM-DD
        """
        try:
            # Obtener la fecha del request
            fecha = request.GET.get('fecha')
            
            print(f"🔍 Consultando tipo de cambio para fecha: {fecha}")
            
            # Validar que se proporcione la fecha
            if not fecha:
                return JsonResponse({
                    'success': False,
                    'message': 'El parámetro fecha es obligatorio'
                }, status=400)
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Ejecutar consulta
            resultado = self._obtener_tipo_cambio(fecha)
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'data': resultado,
                    'message': 'Tipo de cambio obtenido correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró tipo de cambio para la fecha {fecha}',
                    'data': []
                })
                
        except Exception as e:
            print(f"❌ Error en TipoCambioView: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def post(self, request, *args, **kwargs):
        """
        Método POST para obtener el tipo de cambio
        Permite enviar la fecha en el body del request
        """
        try:
            # Obtener datos del body
            data = json.loads(request.body)
            fecha = data.get('fecha')
            
            print(f"🔍 Consultando tipo de cambio (POST) para fecha: {fecha}")
            
            # Validar que se proporcione la fecha
            if not fecha:
                return JsonResponse({
                    'success': False,
                    'message': 'El parámetro fecha es obligatorio'
                }, status=400)
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Ejecutar consulta
            resultado = self._obtener_tipo_cambio(fecha)
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'data': resultado,
                    'message': 'Tipo de cambio obtenido correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró tipo de cambio para la fecha {fecha}',
                    'data': []
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            print(f"❌ Error en TipoCambioView (POST): {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def _obtener_tipo_cambio(self, fecha):
        """
        Ejecuta la consulta SQL para obtener el tipo de cambio
        """
        try:
            cursor = connection_donluis.cursor()
            
            print(f"🔄 Ejecutando consulta SQL para fecha: {fecha}")
            
            # Ejecutar la consulta exacta que proporcionaste
            query = "SELECT FECHA, T_VENTA FROM TCAMBIO WHERE FECHA = ?"
            cursor.execute(query, [fecha])
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            resultados_raw = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(resultados_raw)} registros")
            
            # Convertir resultados a lista de diccionarios (formato JSON)
            resultados = []
            for row in resultados_raw:
                resultado = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fecha para que coincida con el formato esperado
                    if column_name == 'FECHA' and isinstance(value, datetime):
                        resultado[column_name] = value.strftime('%Y-%m-%dT%H:%M:%S')
                    else:
                        resultado[column_name] = value
                
                resultados.append(resultado)
            
            cursor.close()
            return resultados
            
        except Exception as e:
            print(f"❌ Error ejecutando consulta de tipo de cambio: {str(e)}")
            raise


@method_decorator(csrf_exempt, name='dispatch')
class ResponsablesAPI(View):
    """
    API para obtener responsables de la base de datos
    """
    
    def get(self, request, *args, **kwargs):
        """
        Obtiene lista de responsables con filtros opcionales
        """
        try:
            # Obtener parámetros de búsqueda
            idresponsable = request.GET.get('idresponsable', '').strip()
            nombre = request.GET.get('nombre', '').strip()
            
            cursor = connection_donluis.cursor()
            
            # Si se proporciona un ID específico, buscar solo ese responsable
            if idresponsable:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE idresponsable = ?
                """, [idresponsable])
            
            # Si se proporciona un nombre, buscar por coincidencia parcial
            elif nombre:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE nombre LIKE ?
                    ORDER BY nombre
                """, [f'%{nombre}%'])
            
            # Si no se proporcionan filtros, obtener todos los responsables
            else:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE idresponsable IS NOT NULL AND nombre IS NOT NULL
                    ORDER BY nombre
                """)
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            responsables = []
            for row in results:
                responsable = {}
                for i, value in enumerate(row):
                    column_name = columns[i].lower()
                    
                    # Limpiar strings (quitar espacios)
                    if isinstance(value, str):
                        responsable[column_name] = value.strip()
                    else:
                        responsable[column_name] = value
                
                responsables.append(responsable)
            
            cursor.close()
            
            return JsonResponse({
                'success': True,
                'data': responsables,
                'total': len(responsables),
                'message': f'Se encontraron {len(responsables)} responsables'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener responsables: {str(e)}',
                'data': []
            }, status=500)



#================================================================================================================
# REQUERIMIENTOS INTERNOS - CAMPO VERDE
#================================================================================================================


@method_decorator(csrf_exempt, name='dispatch')
class SalidaInternaViewCV(View):
    """
    Vista para manejar las salidas internas de almacén en el sistema Nisira
    Maneja el registro completo: encabezado, detalles y referencias
    """
    
    def post(self, request, *args, **kwargs):
        """
        Crea una nueva salida interna completa siguiendo el flujo del ERP Nisira
        """
        try:
            data = json.loads(request.body)
            cursor = connection_campoverde.cursor()
            
            # VERIFICAR ESTADO DE AUTOCOMMIT
            print(f"🔧 Autocommit inicial: {connection_campoverde.autocommit}")
            
            # FORZAR AUTOCOMMIT=True para evitar problemas de transacción
            connection_campoverde.autocommit = True
            print("🔧 Autocommit forzado a True")
            
            # Validar datos del encabezado
            encabezado = data.get('encabezado', {})
            productos = data.get('productos', [])
            doc_referencia = data.get('documento_referencia', {})
            
            self._validar_datos_encabezado(encabezado)
            
            if not productos:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe incluir al menos un producto'
                })
            
            # PASO 1: OBTENER DATOS DE CABECERA POR DEFECTO (como hace el ERP)
            print("🔄 Paso 1: Obteniendo datos de cabecera por defecto...")
            self._obtener_datos_cabecera_defecto(cursor, encabezado)
            
            # PASO 2: OBTENER SERIES DISPONIBLES (como hace el ERP)
            print("🔄 Paso 2: Obteniendo series disponibles...")
            series_disponibles = self._obtener_series_disponibles(cursor, encabezado)
            
            if not series_disponibles:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay series disponibles para este usuario/documento'
                })
            
            # PASO 3: USAR LA PRIMERA SERIE DISPONIBLE
            serie_usar = series_disponibles[0]
            encabezado['SERIE'] = serie_usar['SERIE']
            print(f"🔄 Paso 3: Usando serie {serie_usar['SERIE']}")
            
            # CON AUTOCOMMIT=True NO NECESITAMOS TRANSACCIONES EXPLÍCITAS
            print("🔄 Procesando con autocommit...")
            
            try:
                # PASO 4: Insertar encabezado
                print("🔄 Paso 4: Insertando encabezado...")
                id_generado = self._insertar_encabezado(cursor, encabezado)
                
                # PASO 5: Insertar detalles de productos
                print("🔄 Paso 5: Insertando detalles...")
                self._insertar_detalles(cursor, id_generado, productos)
                
                # PASO 6: Insertar documento de referencia si existe
                if doc_referencia:
                    print("🔄 Paso 6: Insertando documento referencia...")
                    self._insertar_documento_referencia(cursor, id_generado, doc_referencia)
                
                
                
                # PASO 9: Obtener documento creado ANTES del commit
                print("🔄 Paso 9: Obteniendo documento creado...")
                try:
                    documento_creado = self._obtener_documento_creado(cursor, id_generado)
                    print(f"📋 Documento obtenido: {documento_creado}")
                except Exception as doc_error:
                    print(f"❌ Error al obtener documento: {str(doc_error)}")
                    documento_creado = None
                
                # CON AUTOCOMMIT=True CADA COMANDO YA SE CONFIRMA AUTOMÁTICAMENTE
                print("🔄 Verificando registros en base de datos...")
                
                # VERIFICAR SI EL REGISTRO PERSISTE
                cursor.execute("""
                    SELECT COUNT(*) FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [id_generado, encabezado['IDEMPRESA']])
                result = cursor.fetchone()
                count_final = result[0] if result else 0
                print(f"📈 Registros en BD: {count_final}")
                
                if count_final == 0:
                    print("❌ ADVERTENCIA: El registro no se encontró en la BD")
                else:
                    print("✅ Registro confirmado en base de datos")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Salida interna registrada exitosamente',
                    'data': documento_creado
                })
                
            except Exception as e:
                # CON AUTOCOMMIT=True NO NECESITAMOS ROLLBACK MANUAL
                print(f"❌ Error en procesamiento: {str(e)}")
                raise e
                
        except ValueError as ve:
            return JsonResponse({
                'success': False,
                'message': f'Error de validación: {str(ve)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar salida interna: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    def get(self, request, id=None, *args, **kwargs):
        """
        Obtiene salidas internas - lista o detalle específico
        """
        try:
            cursor = connection_campoverde.cursor()
            
            if id:
                # Obtener salida específica con sus detalles
                return self._obtener_salida_detalle(cursor, id)
            else:
                # Obtener lista de salidas con filtros usando procedimiento almacenado
                return self._obtener_lista_salidas(cursor, request)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al consultar salidas: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    # MÉTODOS PRIVADOS AUXILIARES
    
    def _obtener_series_disponibles(self, cursor, encabezado):
        """Obtiene las series disponibles para el usuario usando el procedimiento del ERP"""
        try:
            print(f"🔍 Ejecutando objtablas_returnSeries con parámetros:")
            print(f"   - IDEMPRESA: {encabezado['IDEMPRESA']}")
            print(f"   - IDEMISOR: {encabezado['IDEMISOR']}")
            print(f"   - IDDOCUMENTO: {encabezado['IDDOCUMENTO']}")
            print(f"   - IDUSUARIO: {encabezado['IDUSUARIO']}")
            
            # MÉTODO 1: Intentar con el procedimiento
            try:
                cursor.execute("""
                    EXEC objtablas_returnSeries ?, ?, ?, ?, ?
                """, [
                    encabezado['IDEMPRESA'],    # @C_EMP
                    encabezado['IDEMISOR'],     # @C_EMI  
                    encabezado['IDDOCUMENTO'],  # @C_DOC (SAL)
                    '',                         # @C_TIPOVENTA (vacío para almacén)
                    encabezado['IDUSUARIO']     # @C_USU
                ])
                
                resultados = cursor.fetchall()
                series_disponibles = []
                
                for row in resultados:
                    numero_raw = str(row[1]).strip()  # Eliminar espacios en blanco
                    # Formatear el número con padding si es necesario
                    if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                        numero_formateado = numero_raw
                    else:
                        numero_int = int(numero_raw) if numero_raw else 1
                        numero_formateado = f"{numero_int:07d}"  # 7 dígitos con padding
                    
                    series_disponibles.append({
                        'SERIE': row[0],
                        'NUMERO': numero_formateado
                    })
                
                if series_disponibles:
                    print(f"✅ Series encontradas vía procedimiento: {len(series_disponibles)}")
                    for serie in series_disponibles:
                        print(f"   - Serie: {serie['SERIE']}, Próximo número: {serie['NUMERO']}")
                    return series_disponibles
                    
            except Exception as proc_error:
                print(f"⚠️ Error en procedimiento: {str(proc_error)}")
            
            # MÉTODO 2: Consulta directa a NUMEMISOR como fallback
            print("🔄 Intentando consulta directa a NUMEMISOR...")
            cursor.execute("""
                SELECT SERIE, NUMERO 
                FROM NUMEMISOR 
                WHERE IDEMPRESA = ? 
                AND IDEMISOR = ? 
                AND IDDOCUMENTO = ? 
                AND ESTADO = 1
                ORDER BY SERIE
            """, [
                encabezado['IDEMPRESA'],
                encabezado['IDEMISOR'], 
                encabezado['IDDOCUMENTO']
            ])
            
            resultados = cursor.fetchall()
            series_disponibles = []
            
            for row in resultados:
                numero_raw = str(row[1]).strip()  # Eliminar espacios en blanco
                # Formatear el número con padding si es necesario
                if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                    numero_formateado = numero_raw
                else:
                    numero_int = int(numero_raw) if numero_raw else 1
                    numero_formateado = f"{numero_int:07d}"  # 7 dígitos con padding
                
                series_disponibles.append({
                    'SERIE': row[0],
                    'NUMERO': numero_formateado
                })
            
            print(f"📋 Series disponibles encontradas (consulta directa): {len(series_disponibles)}")
            for serie in series_disponibles:
                print(f"   - Serie: {serie['SERIE']}, Próximo número: {serie['NUMERO']}")
            
            return series_disponibles
            
        except Exception as e:
            print(f"❌ Error al obtener series: {str(e)}")
            return []
    
    def _obtener_datos_cabecera_defecto(self, cursor, encabezado):
        """Obtiene datos por defecto de cabecera como hace el ERP"""
        try:
            # Construir XML similar al del ERP (simplificado)
            xml_data = f"""<?xml version = "1.0" encoding="Windows-1252" standalone="yes"?>
            <VFPData>
                <torigen>
                    <ctabla>emisor</ctabla>
                    <cid>{encabezado['IDEMISOR']}</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdemisor</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>operaciones</ctabla>
                    <cid>SALM</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdoperacion</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>estados</ctabla>
                    <cid>PE</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdestado</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>monedas</ctabla>
                    <cid>{encabezado['IDMONEDA']}</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>cntmoneda.txtdescripcion</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>responsable</ctabla>
                    <cid>{encabezado['IDRESPONSABLE']}</cid>
                    <cpropiedad>nombre</cpropiedad>
                    <ccontenedor>cntresponsable.txtdescripcion</ccontenedor>
                </torigen>
            </VFPData>"""
            
            cursor.execute("""
                EXEC GETRECORD_DATOSCABECERA_SALIDASINTERNAS ?, ?
            """, [encabezado['IDEMPRESA'], xml_data])
            
            # El procedimiento puede devolver datos, pero por ahora solo lo ejecutamos
            print("✅ Datos de cabecera por defecto obtenidos")
            return True
            
        except Exception as e:
            print(f"⚠️ Advertencia al obtener datos cabecera defecto: {str(e)}")
            return False
    
    def _generar_idingresosalidaalm(self, cursor, encabezado):
        """Genera el IDINGRESOSALIDAALM usando DPARAMS como hace el ERP"""
        try:
            # Obtener el siguiente ID desde DPARAMS
            cursor.execute("""
                SELECT id FROM DPARAMS 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = '_'
            """, [encabezado['IDEMPRESA']])
            
            resultado = cursor.fetchone()
            if resultado:
                siguiente_id = resultado[0]
            else:
                siguiente_id = 39860  # Valor base observado en los ejemplos
                
            # Generar ID con formato observado: _76F0TDC7939860
            # Formato: _[3chars][1digit][4chars][6digits]
            import random, string
            parte1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))  # 76F
            parte2 = random.choice(string.digits)  # 0
            parte3 = ''.join(random.choices(string.ascii_uppercase, k=4))  # TDCR
            parte4 = f"{siguiente_id}"  # 39860
            
            id_generado = f"_{parte1}{parte2}{parte3}{parte4}"
            
            print(f"🔢 ID generado: {id_generado}")
            return id_generado
            
        except Exception as e:
            # Fallback: generar ID aleatorio con formato correcto
            import random, string
            parte1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            parte2 = random.choice(string.digits)
            parte3 = ''.join(random.choices(string.ascii_uppercase, k=4))
            parte4 = f"{random.randint(39860, 99999)}"
            
            id_generado = f"_{parte1}{parte2}{parte3}{parte4}"
            print(f"⚠️ Error en DPARAMS, usando ID aleatorio: {id_generado}")
            return id_generado
    


    def _generar_numoperacion(self, cursor, encabezado):
        """
        Genera el NUMOPERACION con lógica mensual simplificada:
        - Nuevo mes = 0000000001
        - Mismo mes = siguiente número
        """
        try:
            # Obtener datos básicos
            periodo_actual = encabezado.get('PERIODO')
            idempresa = encabezado.get('IDEMPRESA', '001')
            
            if not periodo_actual:
                from datetime import datetime
                fecha_actual = datetime.now()
                periodo_actual = f"{fecha_actual.year}{fecha_actual.month:02d}"
            
            # Buscar el último NUMOPERACION del mes actual
            cursor.execute("""
                SELECT MAX(CAST(NUMOPERACION AS INTEGER)) 
                FROM INGRESOSALIDAALM 
                WHERE IDEMPRESA = ? AND PERIODO = ?
                AND NUMOPERACION IS NOT NULL AND NUMOPERACION != ''
            """, [idempresa, periodo_actual])
            
            resultado = cursor.fetchone()
            ultimo_numero = resultado[0] if resultado and resultado[0] else 0
            
            # Generar siguiente número
            siguiente_numero = ultimo_numero + 1
            numoperacion_generado = f"{siguiente_numero:010d}"
            
            # Log simple
            if ultimo_numero == 0:
                print(f"🆕 Nuevo mes {periodo_actual}: {numoperacion_generado}")
            else:
                print(f"📈 Mes {periodo_actual}: {ultimo_numero} → {numoperacion_generado}")
            
            return numoperacion_generado
            
        except Exception as e:
            # Fallback simple: número aleatorio con formato correcto
            import random
            numero_emergencia = random.randint(1, 999999)
            fallback = f"{numero_emergencia:010d}"
            print(f"❌ Error: {str(e)} | Usando: {fallback}")
            return fallback    


    
    def _obtener_siguiente_numero(self, cursor, encabezado, serie):
        """Obtiene el siguiente número para la serie"""
        try:
            # Ya tenemos el número desde _obtener_series_disponibles
            cursor.execute("""
                SELECT NUMERO FROM NUMEMISOR 
                WHERE IDEMPRESA = ? AND IDEMISOR = ? AND IDDOCUMENTO = ? AND SERIE = ?
            """, [encabezado['IDEMPRESA'], encabezado['IDEMISOR'], encabezado['IDDOCUMENTO'], serie])
            
            resultado = cursor.fetchone()
            if resultado:
                numero_raw = str(resultado[0]).strip()  # Eliminar espacios en blanco
                # Si el número es una cadena y ya tiene formato, usarlo tal cual
                if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                    numero_formateado = numero_raw
                    print(f"📝 Número ya formateado: {numero_formateado}")
                else:
                    # Si es número entero o cadena corta, formatear con padding de ceros
                    numero_int = int(numero_raw) if numero_raw else 1
                    numero_formateado = f"{numero_int:07d}"  # Formato: 0061752 (7 dígitos)
                    print(f"📝 Número formateado: {numero_formateado}")
                
                print(f"🔢 Número obtenido: {numero_formateado}")
                return numero_formateado
            else:
                print("⚠️ No se encontró número en NUMEMISOR, usando 0000001")
                return "0000001"
                
        except Exception as e:
            print(f"⚠️ Error obteniendo número: {str(e)}")
            return "0000001"
    
    def _actualizar_dparams(self, cursor, encabezado, id_usado, numoperacion_usado):
        """Actualiza DPARAMS con los valores usados"""
        try:
            # Actualizar contador de IDINGRESOSALIDAALM
            cursor.execute("""
                UPDATE DPARAMS SET id = id + 1 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = '_'
            """, [encabezado['IDEMPRESA']])
            
            # Actualizar contador de NUMOPERACION
            cursor.execute("""
                UPDATE DPARAMS SET id = id + 1 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = 'SALM'
            """, [encabezado['IDEMPRESA']])
            
            # Actualizar NUMEMISOR con formato de 7 dígitos
            cursor.execute("""
                UPDATE NUMEMISOR 
                SET NUMERO = RIGHT('0000000' + CAST((CAST(NUMERO AS INT) + 1) AS VARCHAR), 7)
                WHERE IDEMPRESA = ? AND IDEMISOR = ? AND IDDOCUMENTO = ? AND SERIE = ?
            """, [encabezado['IDEMPRESA'], encabezado['IDEMISOR'], encabezado['IDDOCUMENTO'], encabezado['SERIE']])
            
            print("✅ DPARAMS y NUMEMISOR actualizados")
            
        except Exception as e:
            print(f"⚠️ Error actualizando contadores: {str(e)}")

    def _validar_datos_encabezado(self, encabezado):
        """Valida que los datos del encabezado sean correctos"""
        campos_requeridos = [
            'IDEMPRESA', 'IDEMISOR', 'PERIODO', 'IDALMACEN', 
            'IDDOCUMENTO', 'FECHA', 'IDRESPONSABLE', 
            'GLOSA', 'IDMONEDA', 'TCAMBIO', 'IDSUCURSAL', 'IDUSUARIO'
        ]
        
        for campo in campos_requeridos:
            if campo not in encabezado or not encabezado[campo]:
                raise ValueError(f'El campo {campo} es requerido')
    



    
    def _insertar_encabezado(self, cursor, encabezado):
        """Inserta el encabezado en INGRESOSALIDAALM generando previamente los valores como hace el ERP"""
        
        # PASO 1: GENERAR IDINGRESOSALIDAALM usando DPARAMS
        idingresosalidaalm_generado = self._generar_idingresosalidaalm(cursor, encabezado)
        
        # PASO 2: GENERAR NUMOPERACION usando DPARAMS  
        numoperacion_generado = self._generar_numoperacion(cursor, encabezado)
        
        # PASO 3: OBTENER SERIE Y NÚMERO (ya tenemos desde _obtener_series_disponibles)
        serie_usar = encabezado['SERIE']
        numero_usar = self._obtener_siguiente_numero(cursor, encabezado, serie_usar)
        
        # PASO 4: INSERTAR CON TODOS LOS CAMPOS OBLIGATORIOS Y VALORES POR DEFECTO
        sql = """
        INSERT INTO INGRESOSALIDAALM (
            IDEMPRESA, IDINGRESOSALIDAALM, IDEMISOR, PERIODO, IDOPERACION, 
            NUMOPERACION, IDSUBDIARIO, VOUCHER, IDALMACEN, IDDOCUMENTO, SERIE, NUMERO, FECHA,
            IDRESPONSABLE, GLOSA, IDMONEDA, TCAMBIO, TCMONEDA, IDMOTIVO,
            IDALMACEND, FECHADOCORIGEN, SINCRONIZA, IDESTADO, FECHACREACION, 
            CONTABILIZADO, IDSUCURSALD, IDSUCURSAL, VENTANA, IDPARTEPRODUCCION, 
            TOTAL, IDUSUARIO, IDCONSUMIDOR, IMPRESO, IMPORTADO, ES_COSTOS,
            pesodocorigen3, IDREGISTROVAR, AREA_HA, IMPORTADO_EXTERNO, automatico_asociaop,
            numversion, PTOPARTIDA, MOTIVO_TRASLADO, transferir_comprometido, idviaje,
            dni, precio_generado, IDCHOFER, CMA30EQPID_CAMION, CMA30EQPID_CARRETA,
            IDRUTA, IDLUGAR_O, IDLUGAR_D, ITEM_RUTA, fecha_syncro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        
        parametros = [
            encabezado['IDEMPRESA'],                    # 1. IDEMPRESA
            idingresosalidaalm_generado,                # 2. IDINGRESOSALIDAALM (GENERADO)
            encabezado['IDEMISOR'],                     # 3. IDEMISOR  
            encabezado['PERIODO'],                      # 4. PERIODO
            'SALM',                                     # 5. IDOPERACION (Salidas Almacén)
            numoperacion_generado,                      # 6. NUMOPERACION (GENERADO)
            '004',                                      # 7. IDSUBDIARIO (OBLIGATORIO para salidas)
            numoperacion_generado,                      # 8. VOUCHER (mismo que NUMOPERACION)
            encabezado['IDALMACEN'],                    # 9. IDALMACEN
            encabezado['IDDOCUMENTO'],                  # 10. IDDOCUMENTO (SAL)
            serie_usar,                                 # 11. SERIE (GENERADA)
            numero_usar,                                # 12. NUMERO (GENERADO)
            encabezado['FECHA'],                        # 13. FECHA
            encabezado['IDRESPONSABLE'],                # 14. IDRESPONSABLE
            encabezado['GLOSA'],                        # 15. GLOSA
            encabezado['IDMONEDA'],                     # 16. IDMONEDA
            encabezado['TCAMBIO'],                      # 17. TCAMBIO
            encabezado.get('TCMONEDA', 1.000000),       # 18. TCMONEDA
            encabezado['IDMOTIVO'],                     # 19. IDMOTIVO
            encabezado.get('IDALMACEND'),               # 20. IDALMACEND (puede ser NULL)
            encabezado.get('FECHADOCORIGEN', encabezado['FECHA']),  # 21. FECHADOCORIGEN
            encabezado.get('SINCRONIZA', 'N'),          # 22. SINCRONIZA
            encabezado.get('IDESTADO', 'PE'),           # 23. IDESTADO (Pendiente)
            # 24. FECHACREACION = GETDATE() - no parámetro
            encabezado.get('CONTABILIZADO', 0),         # 24. CONTABILIZADO
            encabezado.get('IDSUCURSALD'),              # 25. IDSUCURSALD (puede ser NULL)
            encabezado['IDSUCURSAL'],                   # 26. IDSUCURSAL
            encabezado.get('VENTANA', 'EDT_SALIDAS'),   # 27. VENTANA
            encabezado.get('IDPARTEPRODUCCION'),        # 28. IDPARTEPRODUCCION (puede ser NULL)
            0.0000,                                     # 29. TOTAL (OBLIGATORIO, inicia en 0)
            encabezado['IDUSUARIO'],                    # 30. IDUSUARIO
            '',                                         # 31. IDCONSUMIDOR (DEFAULT '')
            0,                                          # 32. IMPRESO (DEFAULT 0)
            0,                                          # 33. IMPORTADO (DEFAULT 0)
            0,                                          # 34. ES_COSTOS (DEFAULT 0)
            0,                                          # 35. pesodocorigen3 (DEFAULT 0)
            0,                                          # 36. IDREGISTROVAR (DEFAULT 0)
            0,                                          # 37. AREA_HA (DEFAULT 0)
            0,                                          # 38. IMPORTADO_EXTERNO (DEFAULT 0)
            0,                                          # 39. automatico_asociaop (DEFAULT 0)
            0,                                          # 40. numversion (DEFAULT 0)
            '',                                         # 41. PTOPARTIDA (DEFAULT '')
            '',                                         # 42. MOTIVO_TRASLADO (DEFAULT '')
            0,                                          # 43. transferir_comprometido (DEFAULT 0)
            '',                                         # 44. idviaje (DEFAULT '')
            '',                                         # 45. dni (DEFAULT '')
            0,                                          # 46. precio_generado (DEFAULT 0)
            '',                                         # 47. IDCHOFER (DEFAULT '')
            '',                                         # 48. CMA30EQPID_CAMION (DEFAULT '')
            '',                                         # 49. CMA30EQPID_CARRETA (DEFAULT '')
            '',                                         # 50. IDRUTA (DEFAULT '')
            '',                                         # 51. IDLUGAR_O (DEFAULT '')
            '',                                         # 52. IDLUGAR_D (DEFAULT '')
            ''                                          # 53. ITEM_RUTA (DEFAULT '')
            # fecha_syncro = GETDATE() - no parámetro
        ]
        
        print(f"📝 Insertando registro con valores generados:")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm_generado}")
        print(f"   - NUMOPERACION: {numoperacion_generado}")  
        print(f"   - SERIE: {serie_usar}")
        print(f"   - NUMERO: {numero_usar}")
        
        try:
            print(f"🔄 Ejecutando INSERT en INGRESOSALIDAALM...")
            print(f"📊 Total de parámetros: {len(parametros)}")
            cursor.execute(sql, parametros)
            print(f"✅ INSERT ejecutado exitosamente")
            
            # Verificar que se insertó
            cursor.execute("SELECT @@ROWCOUNT")
            rows_affected = cursor.fetchone()[0]
            print(f"📈 Filas afectadas: {rows_affected}")
            
            if rows_affected == 0:
                print("❌ ADVERTENCIA: No se insertaron filas")
            
        except Exception as insert_error:
            print(f"❌ ERROR en INSERT: {str(insert_error)}")
            raise insert_error
        
        # ACTUALIZAR DPARAMS con los nuevos valores usados
        try:
            print(f"🔄 Actualizando DPARAMS...")
            self._actualizar_dparams(cursor, encabezado, idingresosalidaalm_generado, numoperacion_generado)
            print(f"✅ DPARAMS actualizado")
        except Exception as dparams_error:
            print(f"❌ ERROR en DPARAMS: {str(dparams_error)}")
            raise dparams_error
        
        print(f"✅ Encabezado creado: ID={idingresosalidaalm_generado}, Serie={serie_usar}, Número={numero_usar}")
        
        return idingresosalidaalm_generado



    def _insertar_detalles(self, cursor, idingresosalidaalm, productos):
        """Inserta los detalles de productos en DINGRESOSALIDAALM"""
        
        # VERIFICAR QUE NO EXISTAN DETALLES PREVIAMENTE
        cursor.execute("""
            SELECT COUNT(*) FROM DINGRESOSALIDAALM 
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Advertencia: Ya existen {count} detalles para {idingresosalidaalm}")
            # Eliminar detalles existentes
            cursor.execute("""
                DELETE FROM DINGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ?
            """, [idingresosalidaalm])
        
        sql = """
        INSERT INTO DINGRESOSALIDAALM (
            IDEMPRESA, IDINGRESOSALIDAALM, ITEM, IDPRODUCTO, DESCRIPCION,
            IDSERIE, IDLOTEP, IDMEDIDA, IDESTADOPRODUCTO, IDPROYECTO,
            IDACTIVIDAD, IDLABOR, IDCONSUMIDOR, TCAMBIO, COMPROMETIDO,
            IDEMPAQUE, CANTEMPAQUE, CANTIDAD, AREA, NUMPALETA, PRECIO,
            IMPORTE, IDREFERENCIA, ITEMREF, TABLAREF, PRECIOMOF,
            PRECIOMEX, IMPORTEMOF, IMPORTEMEX, IDPARTIDAPSTAL,
            CODINTERNO, CODIGOBARRA, IDUBICACION, LOTEORIGEN,
            PRODUCTOORIGEN, OBSERVACIONES, IDFALLA, IDPRODUCTOPROCESO,
            IDMOVCOMPROMETIDO, MERMA, FACTORINSUMO, CANTINSUMO,
            CANTIPRODUCIDA, IDSIEMBRA, IDCAMPANA, IDORDENPRODUCCION,
            IDLOTEPRODUCCION, DOCORDENPRODUCCION, VOLUMEN, IDACTIVO,
            IDCULTIVO, IDPRODUCTODESTINO, DSC_PRODUCTODESTINO, IDMEDIDA2,
            CANTIDAD2, idvehiculo, docreqinterno, idreqinterno,
            ITEMREF_ORDENPRODUCCION, placa, kilometraje, chofer,
            NRO_VALE, SEMANA, DOSISLOTE, estructura, itemreqinterno,
            DSC_DOCVENTA, IDDOC_VENTA, idchofer, cMA30EqpID,
            NROENVASES, idinvernadero, idnave, idcampanainvernadero, horometro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for i, producto in enumerate(productos, 1):
            # GENERAR ITEM ÚNICO
            item_numero = f"{i:03d}"
            
            try:
                parametros = [
                    producto.get('IDEMPRESA'),
                    idingresosalidaalm,
                    item_numero,  # ITEM con formato 001, 002, etc.
                    producto.get('IDPRODUCTO'),
                    producto.get('DESCRIPCION'),
                    producto.get('IDSERIE'),
                    producto.get('IDLOTEP'),
                    producto.get('IDMEDIDA'),
                    producto.get('IDESTADOPRODUCTO', '0'),
                    producto.get('IDPROYECTO'),
                    producto.get('IDACTIVIDAD'),
                    producto.get('IDLABOR'),
                    producto.get('IDCONSUMIDOR'),
                    producto.get('TCAMBIO'),
                    producto.get('COMPROMETIDO', 1),
                    producto.get('IDEMPAQUE'),
                    producto.get('CANTEMPAQUE', 0),
                    producto.get('CANTIDAD'),
                    producto.get('AREA'),
                    producto.get('NUMPALETA'),
                    producto.get('PRECIO', 0),
                    producto.get('IMPORTE', 0),
                    producto.get('IDREFERENCIA'),
                    producto.get('ITEMREF'),
                    producto.get('TABLAREF'),
                    producto.get('PRECIOMOF', 0),
                    producto.get('PRECIOMEX', 0),
                    producto.get('IMPORTEMOF', 0),
                    producto.get('IMPORTEMEX', 0),
                    producto.get('IDPARTIDAPSTAL'),
                    producto.get('CODINTERNO'),
                    producto.get('CODIGOBARRA'),
                    producto.get('IDUBICACION'),
                    producto.get('LOTEORIGEN'),
                    producto.get('PRODUCTOORIGEN'),
                    producto.get('OBSERVACIONES'),
                    producto.get('IDFALLA'),
                    producto.get('IDPRODUCTOPROCESO'),
                    producto.get('IDMOVCOMPROMETIDO'),
                    producto.get('MERMA', 0),
                    producto.get('FACTORINSUMO', 0),
                    producto.get('CANTINSUMO', 0),
                    producto.get('CANTIPRODUCIDA', 0),
                    producto.get('IDSIEMBRA'),
                    producto.get('IDCAMPANA'),
                    producto.get('IDORDENPRODUCCION'),
                    producto.get('IDLOTEPRODUCCION'),
                    producto.get('DOCORDENPRODUCCION'),
                    producto.get('VOLUMEN'),
                    producto.get('IDACTIVO'),
                    producto.get('IDCULTIVO'),
                    producto.get('IDPRODUCTODESTINO'),
                    producto.get('DSC_PRODUCTODESTINO'),
                    producto.get('IDMEDIDA2'),
                    producto.get('CANTIDAD2', 0),
                    producto.get('idvehiculo'),
                    producto.get('docreqinterno'),
                    producto.get('idreqinterno'),
                    producto.get('ITEMREF_ORDENPRODUCCION'),
                    producto.get('placa'),
                    producto.get('kilometraje'),
                    producto.get('chofer'),
                    producto.get('NRO_VALE'),
                    producto.get('SEMANA'),
                    producto.get('DOSISLOTE'),
                    producto.get('estructura'),
                    producto.get('itemreqinterno'),
                    producto.get('DSC_DOCVENTA'),
                    producto.get('IDDOC_VENTA'),
                    producto.get('idchofer'),
                    producto.get('cMA30EqpID'),
                    producto.get('NROENVASES', 0),
                    producto.get('idinvernadero'),
                    producto.get('idnave'),
                    producto.get('idcampanainvernadero'),
                    producto.get('horometro', 0)
                ]
                
                cursor.execute(sql, parametros)
                print(f"Detalle insertado: ITEM {item_numero} - Producto {producto.get('IDPRODUCTO')}")
                
            except Exception as e:
                print(f"Error insertando item {item_numero}: {str(e)}")
                raise e


    


    def _insertar_documento_referencia(self, cursor, idingresosalidaalm, doc_referencia):
        """Inserta la referencia al documento origen en DOCREFERENCIA"""
        sql = """
        INSERT INTO DOCREFERENCIA (
            IDEMPRESA, IDORIGEN, TABLA, IDREFERENCIA,
            IDDOCUMENTO, SERIE, NUMERO, FECHA
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        parametros = [
            doc_referencia['IDEMPRESA'],
            idingresosalidaalm,
            doc_referencia.get('TABLA', 'REQINTERNO'),
            doc_referencia['IDREFERENCIA'],
            doc_referencia['IDDOCUMENTO'],
            doc_referencia['SERIE'],
            doc_referencia['NUMERO'],
            doc_referencia['FECHA']
        ]
        
        cursor.execute(sql, parametros)
    
    
    
    
    
    
    def _obtener_documento_creado(self, cursor, idingresosalidaalm):
        """Obtiene los datos del documento recién creado"""
        print(f"🔍 Buscando documento con ID: {idingresosalidaalm}")
        
        try:
            # Usar consulta con NOLOCK para leer datos no confirmados en la misma transacción
            cursor.execute("""
                SELECT IDINGRESOSALIDAALM, SERIE, NUMERO, FECHA, GLOSA, IDESTADO
                FROM INGRESOSALIDAALM WITH (NOLOCK)
                WHERE IDINGRESOSALIDAALM = ?
            """, [idingresosalidaalm])
            
            row = cursor.fetchone()
            print(f"🔍 Resultado de consulta: {row}")
            
            if row:
                documento = {
                    'idingresosalidaalm': row[0],
                    'serie': row[1],
                    'numero': row[2],
                    'fecha': row[3].strftime('%Y-%m-%d') if row[3] else None,
                    'glosa': row[4],
                    'estado': row[5]
                }
                print(f"✅ Documento encontrado: {documento}")
                return documento
            else:
                print("❌ No se encontró el documento con NOLOCK")
                
                # Intentar sin NOLOCK como fallback
                cursor.execute("""
                    SELECT IDINGRESOSALIDAALM, SERIE, NUMERO, FECHA, GLOSA, IDESTADO
                    FROM INGRESOSALIDAALM
                    WHERE IDINGRESOSALIDAALM = ?
                """, [idingresosalidaalm])
                
                row = cursor.fetchone()
                print(f"🔍 Resultado sin NOLOCK: {row}")
                
                if row:
                    documento = {
                        'idingresosalidaalm': row[0],
                        'serie': row[1],
                        'numero': row[2],
                        'fecha': row[3].strftime('%Y-%m-%d') if row[3] else None,
                        'glosa': row[4],
                        'estado': row[5]
                    }
                    print(f"✅ Documento encontrado sin NOLOCK: {documento}")
                    return documento
                else:
                    print("❌ No se encontró el documento en ninguna consulta")
                    return None
                    
        except Exception as e:
            print(f"❌ Error en consulta: {str(e)}")
            return None
    
    
    def _obtener_salida_detalle(self, cursor, idingresosalidaalm):
        """
        Obtiene el detalle completo de una salida específica usando consultas directas
        """
        try:
            # Consulta principal para obtener el encabezado de la salida interna
            cursor.execute("""
                SELECT * FROM INGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = '001'
            """, [idingresosalidaalm])
            
            encabezado_rows = cursor.fetchall()
            if not encabezado_rows:
                return JsonResponse({
                    'success': False,
                    'message': 'Salida interna no encontrada'
                }, status=404)
        
            # Convertir encabezado a diccionario
            encabezado_columns = [col[0] for col in cursor.description]
            encabezado_dict = dict(zip(encabezado_columns, encabezado_rows[0]))
            
            # Procesar fechas en el encabezado
            fecha_fields = ['FECHA', 'FECHACREACION', 'FECHADOCORIGEN', 'FECHATRASLADO', 'FECHADOCORIGEN2', 'FECHADOCORIGEN3', 'FECHACOSECHA', 'FECHAEXPIRACION', 'FECHA1', 'FECHA2']
            for field in fecha_fields:
                if field in encabezado_dict and encabezado_dict[field] is not None:
                    if hasattr(encabezado_dict[field], 'strftime'):
                        encabezado_dict[field] = encabezado_dict[field].strftime('%Y-%m-%d %H:%M:%S')
            
            # Obtener los detalles de la salida interna
            cursor.execute("""
                SELECT d.*, p.DESCRIPCION as DESCRIPCION_PRODUCTO
                FROM DINGRESOSALIDAALM d
                LEFT JOIN PRODUCTOS p ON d.IDPRODUCTO = p.IDPRODUCTO AND d.IDEMPRESA = p.IDEMPRESA
                WHERE d.IDINGRESOSALIDAALM = ? AND d.IDEMPRESA = '001'
                ORDER BY d.ITEM
            """, [idingresosalidaalm])
            
            detalles_rows = cursor.fetchall()
            detalles_columns = [col[0] for col in cursor.description]
            
            # Convertir detalles a lista de diccionarios
            detalles_list = []
            for detalle_row in detalles_rows:
                detalle_dict = dict(zip(detalles_columns, detalle_row))
                
                # Procesar fechas en los detalles
                fecha_fields_detalle = ['FECHA', 'VENCEPRODU', 'FECHA_SALIDA', 'FECHAETIQUETA', 'fecha_produccion', 'fecha_d']
                for field in fecha_fields_detalle:
                    if field in detalle_dict and detalle_dict[field] is not None:
                        if hasattr(detalle_dict[field], 'strftime'):
                            detalle_dict[field] = detalle_dict[field].strftime('%Y-%m-%d %H:%M:%S')
                
                # Procesar campos numéricos para evitar problemas de serialización
                numeric_fields = [
                    'TCAMBIO', 'COMPROMETIDO', 'CANTEMPAQUE', 'TARA', 'CANTBRUTA', 'CANTREMITIDA', 
                    'CANTREFERENCIAL', 'LIQUIDADO', 'DEVUELTO', 'DESCUENTO_I', 'DESCUENTO', 'ARANCEL',
                    'PESO', 'CANTIDAD', 'AREA', 'COSTODESCUENTO', 'DISTRIBUCION', 'REVISADO', 
                    'DESPACHADO', 'PRECIO', 'IMPORTE', 'VVENTA', 'IMPUESTO', 'IMPUESTO_I', 
                    'PRECIOMOF', 'PRECIOMEX', 'IMPORTEMOF', 'IMPORTEMEX', 'KGSELECCION', 'KGDEVOLUCION',
                    'KGPELADOS', 'KGTROZO', 'KGPELADILLA', 'TOTALCORTADO', 'RENDPELADO', 'KGENVASADO',
                    'KGDRENADOS', 'RENDENVASADO', 'MERMA', 'FACTORINSUMO', 'CANTINSUMO', 'CANTIPRODUCIDA',
                    'FACTURABLE', 'VOLUMEN', 'PRECIOVENTA', 'TARA2', 'CANTIDAD2', 'con_insumos',
                    'muestrabotonveh', 'liberado', 'BRUTO', 'NETO', 'JABAS', 'REB_A', 'CST_RECURSIVO',
                    'ALM_CAB', 'kilometraje', 'automatico_asociaop', 'GRATUITO', 'DOSISLOTE',
                    'por_oc_importado', 'con_certificacion', 'CANTEMPAQUE2', 'PESOPROMEDIO', 
                    'taraxempaque', 'Cant_Recibida', 'CANTIDAD_HISTORICO', 'preciofactura', 
                    'vventafactura', 'importefactura', 'impuestofac', 'NROENVASES', 'PESO_HISTORICO',
                    'ES_DRAWBACK', 'AUTOMATICO', 'dosis_tanque', 'nrotanque', 'horometro', 
                    'SOPLETEADO', 'cantidad_d', 'TCMONEDA'
                ]
                
                for field in numeric_fields:
                    if field in detalle_dict:
                        try:
                            if detalle_dict[field] is not None:
                                detalle_dict[field] = float(detalle_dict[field])
                            else:
                                detalle_dict[field] = 0.0
                        except (ValueError, TypeError):
                            detalle_dict[field] = 0.0
                
                # Procesar campos de texto para limpiar espacios
                text_fields = [
                    'IDPRODUCTO', 'DESCRIPCION', 'DESCRIPCION_PRODUCTO', 'IDKIT', 'IDSERIE', 
                    'IDLOTEP', 'IDMEDIDA', 'IDESTADOPRODUCTO', 'IDPROYECTO', 'IDACTIVIDAD', 
                    'IDLABOR', 'IDCONSUMIDOR', 'IDCAMPANA_P', 'IDCONSUMIDORO', 'IDDOCUMENTO',
                    'SERIE', 'NUMERO', 'IDEMPAQUE', 'NUMPALETA', 'IDREFERENCIA', 'ITEMREF',
                    'TABLAREF', 'IDPARTIDAPSTAL', 'JULRECEPCION', 'JULCOSECHA', 'DESCCALIBRE',
                    'FORMATO', 'CODFABRICA', 'CODINTERNO', 'CODIGOBARRA', 'IDUBICACION',
                    'IDPROCESO', 'IDSUBPROCESO', 'LOTEORIGEN', 'PRODUCTOORIGEN', 'OBSERVACIONES',
                    'HORA', 'NROVIAJE', 'OBSERVACION', 'IDFALLA', 'IDPRODUCTOPROCESO', 
                    'IDMOVCOMPROMETIDO', 'DUA', 'SERIEDUA', 'IDDEVOLUCION', 'ITEMDEVO',
                    'IDSIEMBRA', 'IDCAMPANA', 'IDORDENPRODUCCION', 'IDLOTEPRODUCCION', 
                    'DOCORDENPRODUCCION', 'DOCLOTEPRODUCCION', 'IDMEDIDAEQ', 'IDUNIDADCOSTO',
                    'IDUNIDADNEGOCIO', 'IDACTIVO', 'IDCULTIVO', 'IDVARIEDAD', 'IDTIPOCOSECHA',
                    'IDCABEZAL', 'IDPRODUCTODESTINO', 'DSC_PRODUCTODESTINO', 'IDMEDIDA2', 'DM',
                    'IDCAMARA', 'idvehiculo', 'anio', 'idcolor', 'IDORDENMANTENIMIENTO',
                    'DOCORDENMANTENIMIENTO', 'docreqinterno', 'idreqinterno', 'ITEMREF_ORDENPRODUCCION',
                    'IDTALLA', 'IDENVASE', 'IDCONDICION', 'IDPRESENTACION', 'DSC_CULTIVO',
                    'DSC_VARIEDAD', 'DSC_COLOR', 'DSC_TALLA', 'DSC_ENVASE', 'DSC_CONDICION',
                    'DSC_PRESENTACION', 'IDREFERENCIA2', 'ITEMREF2', 'TABLAREF2', 'IDACTIVO_AVICOLA',
                    'placa', 'chofer', 'NRO_VALE', 'ITEM1', 'IDUBICACIONA', 'SEMANA',
                    'IDTIPOAFECTACION', 'estructura', 'itemreqinterno', 'dato1', 'idestadoc',
                    'DSC_DOCVENTA', 'IDDOC_VENTA', 'idlotep_o', 'idempaque2', 'IDCUENTA',
                    'idchofer', 'cMA30EqpID', 'IDRECOLECCION', 'IDTURNORIE', 'zonificacion',
                    'idproductod', 'descripciond', 'idconsumidord', 'idlotepd', 'IDUBICACIOND',
                    'ccalidad', 'idccalidad', 'idproductor', 'idarea', 'idresponsable',
                    'idinvernadero', 'idnave', 'idcampanainvernadero', 'IDESTADO', 'idembarcacion',
                    'LDP', 'item_d'
                ]
                
                for field in text_fields:
                    if field in detalle_dict and detalle_dict[field] is not None:
                        detalle_dict[field] = str(detalle_dict[field]).strip()
                    elif field in detalle_dict:
                        detalle_dict[field] = ''
                
                detalles_list.append(detalle_dict)
            
            # Calcular totales
            totales_dict = {
                'TOTAL_CANTIDAD': sum(float(d.get('CANTIDAD', 0) or 0) for d in detalles_list),
                'TOTAL_PESO': sum(float(d.get('PESO', 0) or 0) for d in detalles_list),
                'TOTAL_IMPORTE': sum(float(d.get('IMPORTE', 0) or 0) for d in detalles_list),
                'TotalDetalles': len(detalles_list)
            }
            
            # Procesar campos de texto en encabezado para limpiar espacios
            text_fields_encabezado = [
                'IDEMPRESA', 'IDINGRESOSALIDAALM', 'IDEMISOR', 'PERIODO', 'IDOPERACION', 
                'NUMOPERACION', 'IDSUBDIARIO', 'VOUCHER', 'IDALMACEN', 'IDDOCUMENTO', 
                'SERIE', 'NUMERO', 'IDCLIEPROV', 'IDPROYECTO', 'IDRESPONSABLE', 'GLOSA',
                'IDMONEDA', 'IDMOTIVO', 'IDALMACEND', 'IDDOCORIGEN', 'SERIEDOCORIGEN',
                'NUMDOCORIGEN', 'IDFLETE', 'IDTRANSPORTISTA', 'CERTIFTRANSPORTE', 
                'CERTIFTRANSPORTE1', 'PLACA', 'PLACA1', 'MARCA', 'MARCA1', 'CHOFER',
                'BREVETE', 'LLEVADOPOR', 'DIRECLLEGADA', 'SINCRONIZA', 'IDESTADO',
                'IDCONTABILIZADO', 'IDCONSUMIDOR', 'IDLINEAPRODUC', 'IDLOTE', 'IDSUCURSALD',
                'IDDOCORIGEN2', 'SERIEDOCORIGEN2', 'NUMDOCORIGEN2', 'IDSUCURSAL', 'VENTANA',
                'OCCLIENTE', 'OTRADIRECCION', 'HORA', 'IDMONEDA_FLETE', 'IDCONTROLADOR',
                'IDCLIEPROVDEST', 'IDCOMPRA', 'IDUBIGEOLLEGADA', 'IDDOCORIGEN3', 'SERIEDOCORIGEN3',
                'NUMDOCORIGEN3', 'IDUNIDADNEGOCIO', 'IDCNFDISTRIBUCION', 'IDTURNOTRABAJO',
                'IDPRODUCTO', 'IDREFERENCIAPROCESO', 'IDPROCESO', 'IDSUBPROCESO', 'NRO_PRECINTO',
                'IDPARTEPRODUCCION', 'IDSUBUNIDADNEGOCIO', 'itemptollegada', 'IDCLIEPROV2',
                'Idtipoenvioremision', 'IDREFERENCIA_EXTERNO', 'IDTIPOPRECINTO', 'IDAGRICULTOR',
                'IDSOLICITANTE', 'DESTINO', 'IDPTGENERADO', 'IDSALIDAMP', 'LINEA_EMBARQUE',
                'NRO_CONTENEDOR', 'NRO_DER', 'NRO_INSTRUCCION', 'NRO_PEDIDO', 'idcamara',
                'NROEMBARQUE', 'IDPACKINGLIST', 'IDUSUARIO1', 'IDUSUARIO2', 'IDREFERENCIA1',
                'IDREFERENCIA2', 'DOCREF2', 'VENTANAREF2', 'Codigo_Spring', 'IDBALANZA',
                'NROMATRICULA', 'idtipocamion', 'idalmacenmp', 'IDSALIDA_RECLASIF', 
                'IDINGRESO_RECLASIF', 'MODULO', 'idordenpro', 'idingresosalidaactivo',
                'IDMOTIVO_TRASLADO_SUNAT', 'PTOPARTIDA', 'MOTIVO_TRASLADO', 'IDUBIGEO1',
                'IDUBIGEO2', 'idviaje', 'dni', 'IDMOTIVO_AN', 'MOTIVO_AN', 'IDRESPONSABLE_AN',
                'OBSERVACION_AN', 'idusuario', 'IDVEHICULO', 'IDCHOFER', 'CMA30EQPID_CAMION',
                'CMA30EQPID_CARRETA', 'IDRUTA', 'IDLUGAR_O', 'IDLUGAR_D', 'ITEM_RUTA',
                'Ini_Desc_Usr', 'Fin_Desc_Usr', 'Lugar_Descarga', 'env_tipo_proceso',
                'env_idsuc_proceso', 'env_idalm_proceso', 'env_idsalida_proceso', 
                'env_idingreso_proceso', 'config_veh', 'GUIATRANSPORTISTA', 'NRO_BOOKING',
                'archivo_signed_ce', 'archivo_ce', 'idmodalidad_transporte', 'IDUBIGEOPARTIDA',
                'IDAREA', 'idcontrato', 'sello_ggn', 'sello_codProductor', 'sello_ProductoTransf',
                'IDESTADO2', 'IDTIPO_OPERACION_VOLCADO', 'IDINGRESOSALIDAALM_GENERAL', 'dua',
                'llevadopor_dni', 'IDUSUARIO_ULTIMO', 'origen_formulario', 'idingresosalidaalm_ajuste_inv',
                'NUM_EXPORTACION', 'CONSIGNATARIO', 'idingreso', 'idsalida', 'ticket_acopio',
                'NROPRESINTOCAMPO', 'idtipodesc', 'IDFPAGO', 'idmedida_peso', 'qr_sunat',
                'NUMPALLETMATPRIMA', 'chofer_apellido', 'IDORIGEN3', 'productor_ggn',
                'certificado_por', 'codigolp', 'idcomprador', 'idembarcacion', 'chofer_iddocidentidad',
                'DEPOSITORETIRO', 'CANAL', 'duadam'
            ]
            
            for field in text_fields_encabezado:
                if field in encabezado_dict and encabezado_dict[field] is not None:
                    encabezado_dict[field] = str(encabezado_dict[field]).strip()
                elif field in encabezado_dict:
                    encabezado_dict[field] = ''
            
            # Procesar campos numéricos en encabezado
            numeric_fields_encabezado = [
                'TCAMBIO', 'TCMONEDA', 'PRECIOIGV', 'REDONDEO', 'TOTAL', 'ES_GASTOS', 
                'ES_PROVISION', 'ES_RIEGO', 'CONTABILIZADO', 'VVENTA', 'IMPUESTO', 
                'DESCUENTO', 'VOLUMEN', 'NUMBATCH', 'NUMAUTOCLAVE', 'IMPRESO', 'IMPORTE_FLETE',
                'PESO_TOTAL', 'IMPORTADO', 'ES_COSTOS', 'pesodocorigen3', 'IDREGISTROVAR',
                'AREA_HA', 'IMPORTADO_EXTERNO', 'contador', 'PESO1', 'PESO2', 'automatico_asociaop',
                'numversion', 'transferir_comprometido', 'precio_generado', 'estado_ce',
                'ticket_pesada', 'ticket_pesada1', 'solicita_analisis', 'generado_x_distri',
                'nro_bultos', 'total_distribucion', 'mostrar_sellos', 'sello_estadoCertific',
                'importado_nsprov', 'cerrado', 'peso_descuento_comercial', 'precioun_desc_ajustado',
                'ind_retorno_vehiculo_envase_vacio', 'ind_retorno_vehiculo_vacio', 
                'ind_traslado_programado', 'ind_traslado_total_damods', 'ind_traslado_vehiculo_m1l',
                'ind_trasporte_subcontrado', 'ind_vehiculo_conductores_trasporte'
            ]
            
            for field in numeric_fields_encabezado:
                if field in encabezado_dict:
                    try:
                        if encabezado_dict[field] is not None:
                            encabezado_dict[field] = float(encabezado_dict[field])
                        else:
                            encabezado_dict[field] = 0.0
                    except (ValueError, TypeError):
                        encabezado_dict[field] = 0.0
            
            # Procesar campos booleanos/numéricos (0/1)
            boolean_fields_encabezado = ['CONTABILIZADO', 'CERRADO', 'IMPRESO']
            for field in boolean_fields_encabezado:
                if field in encabezado_dict:
                    try:
                        if encabezado_dict[field] is not None:
                            encabezado_dict[field] = bool(int(float(encabezado_dict[field])))
                        else:
                            encabezado_dict[field] = False
                    except (ValueError, TypeError):
                        encabezado_dict[field] = False

            return JsonResponse({
                'success': True,
                'message': 'Detalle de salida interna obtenido correctamente',
                'encabezado': encabezado_dict,
                'detalles': detalles_list,
                'totales': totales_dict,
                'total_items': len(detalles_list)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener el detalle de la salida interna: {str(e)}'
            }, status=500)
    
    def _obtener_lista_salidas(self, cursor, request):
        """Obtiene lista de salidas internas con filtros usando el procedimiento almacenado"""
        try:
            # Obtener parámetros de la request
            idempresa = request.GET.get('idempresa', '001')  # Default empresa
            fecha_desde = request.GET.get('fecha_desde')
            fecha_hasta = request.GET.get('fecha_hasta')
            idestado = request.GET.get('idestado')
            idmotivo = request.GET.get('idmotivo')
            
            # Convertir fechas si se proporcionan
            fecha_desde_param = None
            fecha_hasta_param = None
        
            if fecha_desde:
                try:
                    fecha_desde_param = datetime.strptime(fecha_desde, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                    }, status=400)
        
            if fecha_hasta:
                try:
                    fecha_hasta_param = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                    }, status=400)
            
            print(f"🔍 Ejecutando consulta de salidas internas con parámetros:")
            print(f"   - IDEMPRESA: {idempresa}")
            print(f"   - FECHA_DESDE: {fecha_desde_param}")
            print(f"   - FECHA_HASTA: {fecha_hasta_param}")
            print(f"   - IDESTADO: {idestado}")
            print(f"   - IDMOTIVO: {idmotivo}")
            
            # Ejecutar procedimiento almacenado
            cursor.execute("""
                EXEC SP_GET_SALIDAS_INTERNAS_ALMACEN ?, ?, ?, ?, ?
            """, [
                idempresa,
                fecha_desde_param,
                fecha_hasta_param,
                idestado if idestado and idestado != 'todos' else None,
                idmotivo if idmotivo and idmotivo != 'todos' else None
            ])
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(results)} registros")
        
            # Convertir a lista de diccionarios
            salidas = []
            for row in results:
                salida = {}
                for i, value in enumerate(row):
                    
                    column_name = columns[i]
                    
                    # Formatear fechas
                    if isinstance(value, datetime) and value:
                        salida[column_name.lower()] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, date) and value:
                        salida[column_name.lower()] = value.strftime('%Y-%m-%d')
                    else:
                        # Limpiar strings (quitar espacios)
                        if isinstance(value, str):
                            salida[column_name.lower()] = value.strip()
                        else:
                            salida[column_name.lower()] = value
                
                salidas.append(salida)
        
            return JsonResponse({
                'success': True,
                'data': salidas,
                'total': len(salidas),
                'filtros_aplicados': {
                    'idempresa': idempresa,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'idestado': idestado,
                    'idmotivo': idmotivo
                },
                'info': {
                    'procedimiento_usado': 'SP_GET_SALIDAS_INTERNAS_ALMACEN',
                    'descripcion': 'Salidas internas obtenidas mediante procedimiento almacenado optimizado'
                }
            })
            
        except Exception as e:
            print(f"❌ Error en consulta de salidas: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al consultar salidas: {str(e)}'
            }, status=500)
    
    def _verificar_salida_modificable(self, cursor, idingresosalidaalm):
        """Verifica si una salida puede ser modificada"""
        cursor.execute("""
            SELECT IDESTADO FROM INGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        resultado = cursor.fetchone()
        if not resultado:
            return False
        
        # Solo permitir modificar si está en estado Pendiente
        return resultado[0] == 'PE'
    
    def _verificar_salida_anulable(self, cursor, idingresosalidaalm):
        """Verifica si una salida puede ser anulada"""
        cursor.execute("""
            SELECT IDESTADO, CONTABILIZADO FROM INGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        resultado = cursor.fetchone()
        if not resultado:
            return False
        
        estado, contabilizado = resultado
        # No permitir anular si ya está anulado o contabilizado
        return estado != 'AN' and contabilizado != 1
    
    def _actualizar_encabezado(self, cursor, idingresosalidaalm, datos_encabezado):
        """Actualiza el encabezado de una salida existente"""
        sql = """
        UPDATE INGRESOSALIDAALM 
        SET GLOSA = ?, IDRESPONSABLE = ?, IDMOTIVO = ?,
            FECHACREACION = GETDATE(), IDUSUARIO = ?
        WHERE IDINGRESOSALIDAALM = ?
        """
        
        cursor.execute(sql, [
            datos_encabezado.get('GLOSA'),
            datos_encabezado.get('IDRESPONSABLE'),
            datos_encabezado.get('IDMOTIVO'),
            datos_encabezado.get('IDUSUARIO'),
            idingresosalidaalm
        ])
    
    def _actualizar_detalles(self, cursor, idingresosalidaalm, productos):
        """Actualiza los detalles de una salida existente"""
        # Eliminar detalles existentes
        cursor.execute("""
            DELETE FROM DINGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        # Insertar nuevos detalles
        self._insertar_detalles(cursor, idingresosalidaalm, productos)

@method_decorator(csrf_exempt, name='dispatch')
class ProcesarSalidaInternaViewCV(View):
    """
    Clase para procesar la contabilización y centralización de salidas internas
    Ejecuta los procedimientos CONTAB_INGRESOSALIDAALM y CENTRALIZA_ALMACENES
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa la contabilización y centralización de una salida interna
        """
        data = json.loads(request.body)
        
        idingresosalidaalm = data.get('IDINGRESOSALIDAALM', '')
        idempresa = data.get('IDEMPRESA', '001')
        ventana = data.get('VENTANA', 'EDT_SALIDAS')
        idemisor = data.get('IDEMISOR', '001')
        
        print(f"🔄 Iniciando contabilización...")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm}")
        print(f"   - IDEMPRESA: {idempresa}")
        print(f"   - VENTANA: {ventana}")
        print(f"   - IDEMISOR: {idemisor}")
        
        # Crear conexión principal
        cursor = connection_campoverde.cursor()
        
        try:
            # 1. Verificar existencia y validaciones previas
            print("🔍 Validando documento...")
            
            # Verificar existencia del documento
            cursor.execute("""
                SELECT CONTABILIZADO, IDESTADO, IDMOTIVO, VENTANA 
                FROM INGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
            """, [idingresosalidaalm, idempresa])
            
            resultado = cursor.fetchone()
            if not resultado:
                return JsonResponse({
                    'success': False,
                    'error': f'No se encontró el documento {idingresosalidaalm}'
                })
            
            contabilizado_actual, estado_actual, idmotivo, ventana_doc = resultado
            print(f"📋 Estado actual - CONTABILIZADO: {contabilizado_actual}, ESTADO: {estado_actual}, MOTIVO: {idmotivo}")
            
            # Si ya está contabilizado, solo intentar centralizar
            if contabilizado_actual == 1:
                print("📋 Documento ya contabilizado, procediendo solo con centralización...")
                return self._centralizar_documento(idingresosalidaalm, idempresa, idemisor)
            
            if estado_actual == 'AN':
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede contabilizar un documento anulado'
                })
            
            # 2. Validar parámetros que pueden impedir la contabilización
            print("🔍 Validando parámetros internos...")
            
            # Verificar parámetro AL_EVITAR_CONTAB_ALM_CE
            cursor.execute("""
                SELECT ISNULL(VALOR,'NO') 
                FROM PARAMETRO 
                WHERE IDPARAMETRO = 'AL_EVITAR_CONTAB_ALM_EST_CE' AND IDEMPRESA = ?
            """, [idempresa])
            
            evitar_contab_ce = cursor.fetchone()
            evitar_contab_ce = evitar_contab_ce[0] if evitar_contab_ce else 'NO'
            
            if estado_actual == 'CE' and evitar_contab_ce == 'SI':
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede contabilizar documentos con estado CE según parámetro AL_EVITAR_CONTAB_ALM_EST_CE'
                })
            
            # Verificar si el motivo permite contabilización
            cursor.execute("""
                SELECT ISNULL(CONTAB_MOVALM,0) as KARDEX, TIPO_MOTIVO, ISNULL(ES_TRANSFERENCIA,0) as ES_TRANSFERENCIA
                FROM MOTIVOS 
                WHERE IDMOTIVO = ?
            """, [idmotivo])
            
            motivo_info = cursor.fetchone()
            if motivo_info:
                kardex, tipo_motivo, es_transferencia = motivo_info
                print(f"📋 Motivo info - KARDEX: {kardex}, TIPO: {tipo_motivo}, ES_TRANSFERENCIA: {es_transferencia}")
                
                if kardex == 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'El motivo {idmotivo} no permite generar movimientos de almacén (KARDEX=1)'
                    })
            
            # 3. Validar transferencias pendientes de aprobación
            if motivo_info and es_transferencia == 1:
                cursor.execute("""
                    SELECT ISNULL(VALOR,'NO') 
                    FROM PARAMETRO 
                    WHERE IDPARAMETRO = 'AL_TRANSF_CONTAB_APROB' AND IDEMPRESA = ?
                """, [idempresa])
                
                transf_aprob = cursor.fetchone()
                transf_aprob = transf_aprob[0] if transf_aprob else 'NO'
                
                if transf_aprob == 'SI':
                    print("⚠️ Documento de transferencia con validación de aprobación habilitada")
            
            # 4. Ejecutar el procedimiento de contabilización
            print(f"🔄 Ejecutando procedimiento CONTAB_INGRESOSALIDAALM...")
            
            import pyodbc
            
            # Crear nueva conexión independiente
            host = '192.168.0.5'
            database = 'CAMPOVERDE'  # Para prueba
            user = 'sa'
            password = '@SADL.2023'
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};MARS_Connection=yes'
            
            conn = pyodbc.connect(conn_str)
            cursor_proc = conn.cursor()
            
            try:
                # Habilitar PRINT messages de SQL Server
                cursor_proc.execute("SET NOCOUNT OFF")
                
                # Ejecutar el procedimiento
                print(f"📤 Ejecutando: EXEC CONTAB_INGRESOSALIDAALM '{idingresosalidaalm}', '{idempresa}', '{ventana}', 'A', '{idemisor}'")
                
                cursor_proc.execute("""
                    EXEC CONTAB_INGRESOSALIDAALM ?, ?, ?, ?, ?
                """, [idingresosalidaalm, idempresa, ventana, 'A', idemisor])
                
                # Capturar mensajes del procedimiento
                messages = []
                while cursor_proc.nextset():
                    try:
                        results = cursor_proc.fetchall()
                        if results:
                            messages.extend([str(row) for row in results])
                    except:
                        pass
                
                # Confirmar transacción
                conn.commit()
                print("✅ Procedimiento de contabilización ejecutado y confirmado")
                
                if messages:
                    print(f"📝 Mensajes del procedimiento: {messages}")
                
                # 5. Verificar resultado de contabilización
                cursor_proc.execute("""
                    SELECT CONTABILIZADO 
                    FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [idingresosalidaalm, idempresa])
                
                resultado_final = cursor_proc.fetchone()
                contabilizado_final = resultado_final[0] if resultado_final else 0
                
                print(f"🔍 Verificación contabilización - CONTABILIZADO: {contabilizado_final}")
                
                cursor_proc.close()
                conn.close()
                
                if contabilizado_final == 1:
                    print("✅ Contabilización exitosa, procediendo con centralización...")
                    
                    # 6. Ejecutar centralización
                    resultado_centralizacion = self._centralizar_documento(idingresosalidaalm, idempresa, idemisor)
                    
                    # Combinar resultados
                    if resultado_centralizacion.status_code == 200:
                        data_centralizacion = json.loads(resultado_centralizacion.content)
                        if data_centralizacion.get('success'):
                            return JsonResponse({
                                'success': True,
                                'message': 'Procesos ejecutados exitosamente',
                                'data': {
                                    'IDINGRESOSALIDAALM': idingresosalidaalm,
                                    'CONTABILIZADO': contabilizado_final,
                                    'ESTADO': 'PE',
                                    'procesos_ejecutados': [
                                        'CONTAB_INGRESOSALIDAALM',
                                        'CENTRALIZA_ALMACENES'
                                    ]
                                }
                            })
                        else:
                            return JsonResponse({
                                'success': True,
                                'message': 'Contabilización exitosa, pero centralización falló',
                                'warning': data_centralizacion.get('error', 'Error desconocido en centralización'),
                                'data': {
                                    'IDINGRESOSALIDAALM': idingresosalidaalm,
                                    'CONTABILIZADO': contabilizado_final,
                                    'procesos_ejecutados': ['CONTAB_INGRESOSALIDAALM']
                                }
                            })
                    else:
                        return JsonResponse({
                            'success': True,
                            'message': 'Contabilización exitosa, pero error en centralización',
                            'warning': 'No se pudo ejecutar la centralización',
                            'data': {
                                'IDINGRESOSALIDAALM': idingresosalidaalm,
                                'CONTABILIZADO': contabilizado_final,
                                'procesos_ejecutados': ['CONTAB_INGRESOSALIDAALM']
                            }
                        })
                else:
                    # Intentar obtener más información sobre por qué falló
                    cursor.execute("""
                        SELECT TOP 1 
                            I.IDESTADO, I.IDESTADO2, M.CONTAB_MOVALM, M.TIPO_MOTIVO,
                            I.VENTANA, M.GRUPO_MOTIVO
                        FROM INGRESOSALIDAALM I
                        LEFT JOIN MOTIVOS M ON I.IDMOTIVO = M.IDMOTIVO
                        WHERE I.IDINGRESOSALIDAALM = ? AND I.IDEMPRESA = ?
                    """, [idingresosalidaalm, idempresa])
                    
                    debug_info = cursor.fetchone()
                    debug_msg = f"Debug info: {debug_info}" if debug_info else "No debug info available"
                    
                    return JsonResponse({
                        'success': False,
                        'error': 'El procedimiento se ejecutó pero no contabilizó el documento. Posibles causas: validaciones internas del procedimiento, estado del documento, configuración de parámetros.',
                        'debug': debug_msg,
                        'messages': messages,
                        'data': {
                            'IDINGRESOSALIDAALM': idingresosalidaalm,
                            'CONTABILIZADO': contabilizado_final
                        }
                    })
                    
            except Exception as proc_error:
                conn.rollback()
                cursor_proc.close()
                conn.close()
                print(f"❌ Error en procedimiento de contabilización: {str(proc_error)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al ejecutar procedimiento de contabilización: {str(proc_error)}'
                })
                
        except Exception as e:
            print(f"❌ Error general: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el proceso: {str(e)}'
            })
        finally:
            if cursor:
                cursor.close()

    def _centralizar_documento(self, idingresosalidaalm, idempresa, idemisor):
        """
        Ejecuta el procedimiento de centralización de almacenes
        EXEC CENTRALIZA_ALMACENES idempresa, idingresosalidaalm, '', idemisor
        """
        print(f"🔄 Iniciando centralización de almacenes...")
        print(f"   - IDEMPRESA: {idempresa}")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm}")
        print(f"   - IDEMISOR: {idemisor}")
        
        import pyodbc
        
        try:
            # Crear nueva conexión independiente para centralización
            host = '192.168.0.5'
            database = 'CAMPOVERDE'  # Para prueba
            user = 'sa'
            password = '@SADL.2023'
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};MARS_Connection=yes'
            
            conn = pyodbc.connect(conn_str)
            cursor_proc = conn.cursor()
            
            try:
                # Habilitar PRINT messages de SQL Server
                cursor_proc.execute("SET NOCOUNT OFF")
                
                # Ejecutar el procedimiento de centralización
                print(f"📤 Ejecutando: EXEC CENTRALIZA_ALMACENES '{idempresa}', '{idingresosalidaalm}', '', '{idemisor}'")
                
                cursor_proc.execute("""
                    EXEC CENTRALIZA_ALMACENES ?, ?, ?, ?
                """, [idempresa, idingresosalidaalm, '', idemisor])
                
                # Capturar mensajes del procedimiento
                messages = []
                while cursor_proc.nextset():
                    try:
                        results = cursor_proc.fetchall()
                        if results:
                            messages.extend([str(row) for row in results])
                    except:
                        pass
                
                # Confirmar transacción
                conn.commit()
                print("✅ Procedimiento de centralización ejecutado y confirmado")
                
                if messages:
                    print(f"📝 Mensajes del procedimiento de centralización: {messages}")
                
                # Verificar estado final del documento
                cursor_proc.execute("""
                    SELECT IDESTADO 
                    FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [idingresosalidaalm, idempresa])
                
                resultado_estado = cursor_proc.fetchone()
                estado_final = resultado_estado[0] if resultado_estado else 'Desconocido'
                
                print(f"🔍 Verificación centralización - ESTADO: {estado_final}")
                
                cursor_proc.close()
                conn.close()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Centralización ejecutada exitosamente',
                    'data': {
                        'IDINGRESOSALIDAALM': idingresosalidaalm,
                        'ESTADO': estado_final,
                        'messages': messages
                    }
                })
                
            except Exception as proc_error:
                conn.rollback()
                cursor_proc.close()
                conn.close()
                print(f"❌ Error en procedimiento de centralización: {str(proc_error)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al ejecutar procedimiento de centralización: {str(proc_error)}'
                })
                
        except Exception as e:
            print(f"❌ Error general en centralización: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el proceso de centralización: {str(e)}'
            })

@method_decorator(csrf_exempt, name='dispatch')
class ProcesarRequerimientoInternoAPICV(View):
    """
    Vista simplificada para procesar productos REQINTERNO
    Ejecuta stored procedures: CAMBIA_ESTADOREQINTERNO_DET y ACTUALIZA_ESTADO_REQINTERNO
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa requerimientos internos con la estructura enviada desde JavaScript
        """
        cursor = None
        
        try:
            print("🚀 ===== INICIANDO PROCESAMIENTO REQINTERNO API =====")
            
            # Parsear JSON del request
            data = json.loads(request.body)
            print(f"📋 Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Extraer secciones principales
            encabezado = data.get('encabezado', {})
            productos = data.get('productos', [])
            documento_referencia = data.get('documento_referencia', {})
            idingresosalidaalm = data.get('idingresosalidaalm', '')
            
            # Validaciones básicas
            if not encabezado.get('IDEMPRESA'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDEMPRESA faltante en encabezado',
                    'code': 'MISSING_IDEMPRESA'
                }, status=400)
            
            if not productos:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Lista de productos está vacía',
                    'code': 'MISSING_PRODUCTOS'
                }, status=400)
            
            if not documento_referencia.get('IDREFERENCIA'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDREFERENCIA faltante en documento_referencia',
                    'code': 'MISSING_IDREFERENCIA'
                }, status=400)
            
            if not idingresosalidaalm:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDINGRESOSALIDAALM está vacío',
                    'code': 'MISSING_IDINGRESOSALIDAALM'
                }, status=400)
            
            print("✅ Validaciones básicas exitosas")
            
            # Procesar con conexión fresca
            resultado = self._procesar_requerimiento_simplificado(
                encabezado, productos, documento_referencia, idingresosalidaalm
            )
            
            if resultado['success']:
                return JsonResponse({
                    'status': 'success',
                    'message': resultado['message'],
                    'data': {
                        'productos_procesados': resultado['productos_procesados'],
                        'idempresa': encabezado.get('IDEMPRESA'),
                        'idreferencia': documento_referencia.get('IDREFERENCIA'),
                        'idingresosalidaalm': idingresosalidaalm
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': resultado['message'],
                    'code': 'PROCESSING_ERROR'
                }, status=500)
                
        except json.JSONDecodeError as e:
            print(f"❌ Error JSON: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'JSON inválido: {str(e)}',
                'code': 'INVALID_JSON'
            }, status=400)
            
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            print(f"📊 Stack trace: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=500)
    
    def _procesar_requerimiento_simplificado(self, encabezado, productos, documento_referencia, idingresosalidaalm):
        """
        Procesa el requerimiento con conexión fresca usando el patrón de SalidaInternaView
        """
        try:
            # Obtener parámetros principales
            idempresa = encabezado.get('IDEMPRESA')
            idreferencia = documento_referencia.get('IDREFERENCIA')
            
            print(f"📋 ===== PROCESANDO REQUERIMIENTO =====")
            print(f"🏢 IDEMPRESA: {idempresa}")
            print(f"📄 IDREFERENCIA: {idreferencia}")
            print(f"🆔 IDINGRESOSALIDAALM: {idingresosalidaalm}")
            print(f"📦 Total productos: {len(productos)}")
            
            # Usar el mismo patrón que SalidaInternaView
            cursor = connection_campoverde.cursor()
            
            # Forzar autocommit=True (igual que SalidaInternaView)
            connection_campoverde.autocommit = True
            print("🔧 Autocommit configurado a True")
            
            productos_procesados = 0
            
            # PASO 1: Ejecutar CAMBIA_ESTADOREQINTERNO_DET para cada producto
            print("📋 ===== PASO 1: CAMBIA_ESTADOREQINTERNO_DET =====")
            
            for i, producto in enumerate(productos, 1):
                idproducto = producto.get('IDPRODUCTO', '')
                itemref = producto.get('ITEMREF', '')
                tablaref = producto.get('TABLAREF', 'REQINTERNO')
                
                print(f"📦 Producto {i}/{len(productos)}: {idproducto} - Item: {itemref}")
                
                if not idproducto or not itemref:
                    print(f"⚠️ Saltando producto {i} - datos incompletos")
                    continue
                
                # Generar XML
                xml_antes, xml_ahora = self._generar_xml_simple(
                    idproducto, idreferencia, itemref, tablaref
                )
                
                # Ejecutar procedimiento
                try:
                    cursor.execute(
                        "EXEC CAMBIA_ESTADOREQINTERNO_DET ?, ?, ?",
                        [idempresa, xml_antes, xml_ahora]
                    )
                    
                    # Consumir resultados
                    while cursor.nextset():
                        pass
                    
                    productos_procesados += 1
                    print(f"✅ Producto {i} procesado exitosamente")
                    
                except Exception as prod_error:
                    print(f"❌ Error procesando producto {i}: {str(prod_error)}")
                    raise prod_error
            
            print(f"✅ PASO 1 completado: {productos_procesados} productos")
            
            # PASO 2: Ejecutar ACTUALIZA_ESTADO_REQINTERNO
            print("📋 ===== PASO 2: ACTUALIZA_ESTADO_REQINTERNO =====")
            
            cursor.execute(
                "EXEC ACTUALIZA_ESTADO_REQINTERNO ?, ?, ?",
                [idempresa, idingresosalidaalm, idreferencia]
            )
            
            # Consumir resultados
            while cursor.nextset():
                pass
            
            print("✅ PASO 2 completado exitosamente")
            
            # Verificar resultados
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM REQINTERNO 
                    WHERE IDREFERENCIA = ? AND IDEMPRESA = ?
                """, [idreferencia, idempresa])
                result = cursor.fetchone()
                count_reqs = result[0] if result else 0
                print(f"📈 Requerimientos en BD: {count_reqs}")
            except Exception as verification_error:
                print(f"⚠️ Error en verificación: {str(verification_error)}")
            
            # Cerrar cursor
            cursor.close()
            print("🔄 Cursor cerrado")
            
            return {
                'success': True,
                'message': f'Procesamiento exitoso: {productos_procesados} productos',
                'productos_procesados': productos_procesados
            }
            
        except Exception as e:
            print(f"❌ Error en procesamiento: {str(e)}")
            
            # Limpiar cursor
            try:
                if 'cursor' in locals():
                    cursor.close()
            except:
                pass
            
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'productos_procesados': 0
            }
    
    def _generar_xml_simple(self, idproducto, idreferencia, itemref, tablaref="REQINTERNO"):
        """
        Genera XML para los procedimientos almacenados
        """
        def escape_xml(texto):
            if texto is None:
                return ""
            return str(texto).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Limpiar valores
        idproducto_clean = escape_xml(idproducto)
        idreferencia_clean = escape_xml(idreferencia)
        itemref_clean = escape_xml(itemref)
        tablaref_clean = escape_xml(tablaref)
        
        # XML Antes
        xml_antes = (
            f'<VFPData><disa_antes><record>'
            f'<idproducto>{idproducto_clean}</idproducto>'
            f'<idreferencia>{idreferencia_clean}</idreferencia>'
            f'<itemref>{itemref_clean}</itemref>'
            f'<tablaref>{tablaref_clean}</tablaref>'
            f'</record></disa_antes></VFPData>'
        )
        
        # XML Ahora
        xml_ahora = (
            f'<VFPData><disa_ahora><record>'
            f'<idproducto>{idproducto_clean}</idproducto>'
            f'<idreferencia>{idreferencia_clean}</idreferencia>'
            f'<itemref>{itemref_clean}</itemref>'
            f'<tablaref>{tablaref_clean}</tablaref>'
            f'</record></disa_ahora></VFPData>'
        )
        
        return xml_antes, xml_ahora

@method_decorator(csrf_exempt, name='dispatch')
class TipoCambioViewCV(View):
    """
    Clase para obtener el tipo de cambio según la fecha
    Ejecuta la consulta: SELECT FECHA,T_COMPRA FROM TCAMBIO WHERE FECHA = ?
    """
    
    def get(self, request, *args, **kwargs):
        """
        Método GET para obtener el tipo de cambio
        Parámetros esperados:
        - fecha: fecha en formato YYYY-MM-DD
        """
        try:
            # Obtener la fecha del request
            fecha = request.GET.get('fecha')
            
            print(f"🔍 Consultando tipo de cambio para fecha: {fecha}")
            
            # Validar que se proporcione la fecha
            if not fecha:
                return JsonResponse({
                    'success': False,
                    'message': 'El parámetro fecha es obligatorio'
                }, status=400)
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Ejecutar consulta
            resultado = self._obtener_tipo_cambio(fecha)
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'data': resultado,
                    'message': 'Tipo de cambio obtenido correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró tipo de cambio para la fecha {fecha}',
                    'data': []
                })
                
        except Exception as e:
            print(f"❌ Error en TipoCambioView: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def post(self, request, *args, **kwargs):
        """
        Método POST para obtener el tipo de cambio
        Permite enviar la fecha en el body del request
        """
        try:
            # Obtener datos del body
            data = json.loads(request.body)
            fecha = data.get('fecha')
            
            print(f"🔍 Consultando tipo de cambio (POST) para fecha: {fecha}")
            
            # Validar que se proporcione la fecha
            if not fecha:
                return JsonResponse({
                    'success': False,
                    'message': 'El parámetro fecha es obligatorio'
                }, status=400)
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Ejecutar consulta
            resultado = self._obtener_tipo_cambio(fecha)
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'data': resultado,
                    'message': 'Tipo de cambio obtenido correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró tipo de cambio para la fecha {fecha}',
                    'data': []
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            print(f"❌ Error en TipoCambioView (POST): {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def _obtener_tipo_cambio(self, fecha):
        """
        Ejecuta la consulta SQL para obtener el tipo de cambio
        """
        try:
            cursor = connection_campoverde.cursor()
            
            print(f"🔄 Ejecutando consulta SQL para fecha: {fecha}")
            
            # Ejecutar la consulta exacta que proporcionaste
            query = "SELECT FECHA, T_VENTA FROM TCAMBIO WHERE FECHA = ?"
            cursor.execute(query, [fecha])
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            resultados_raw = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(resultados_raw)} registros")
            
            # Convertir resultados a lista de diccionarios (formato JSON)
            resultados = []
            for row in resultados_raw:
                resultado = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fecha para que coincida con el formato esperado
                    if column_name == 'FECHA' and isinstance(value, datetime):
                        resultado[column_name] = value.strftime('%Y-%m-%dT%H:%M:%S')
                    else:
                        resultado[column_name] = value
                
                resultados.append(resultado)
            
            cursor.close()
            return resultados
            
        except Exception as e:
            print(f"❌ Error ejecutando consulta de tipo de cambio: {str(e)}")
            raise

@method_decorator(csrf_exempt, name='dispatch')
class ResponsablesAPICV(View):
    """
    API para obtener responsables de la base de datos
    """
    
    def get(self, request, *args, **kwargs):
        """
        Obtiene lista de responsables con filtros opcionales
        """
        try:
            # Obtener parámetros de búsqueda
            idresponsable = request.GET.get('idresponsable', '').strip()
            nombre = request.GET.get('nombre', '').strip()
            
            cursor = connection_campoverde.cursor()
            
            # Si se proporciona un ID específico, buscar solo ese responsable
            if idresponsable:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE idresponsable = ?
                """, [idresponsable])
            
            # Si se proporciona un nombre, buscar por coincidencia parcial
            elif nombre:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE nombre LIKE ?
                    ORDER BY nombre
                """, [f'%{nombre}%'])
            
            # Si no se proporcionan filtros, obtener todos los responsables
            else:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE idresponsable IS NOT NULL AND nombre IS NOT NULL
                    ORDER BY nombre
                """)
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            responsables = []
            for row in results:
                responsable = {}
                for i, value in enumerate(row):
                    column_name = columns[i].lower()
                    
                    # Limpiar strings (quitar espacios)
                    if isinstance(value, str):
                        responsable[column_name] = value.strip()
                    else:
                        responsable[column_name] = value
                
                responsables.append(responsable)
            
            cursor.close()
            
            return JsonResponse({
                'success': True,
                'data': responsables,
                'total': len(responsables),
                'message': f'Se encontraron {len(responsables)} responsables'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener responsables: {str(e)}',
                'data': []
            }, status=500)




#================================================================================================================
# API PARA LA BUSQUEDA DE REQUERIMIENTOS
#================================================================================================================




@method_decorator(csrf_exempt, name='dispatch')
class BuscarRequerimientoInternoAPI(View):
    """
    API para buscar requerimientos internos por número de documento
    Por defecto muestra todos los requerimientos pendientes para seleccionar
    """
    def get(self, request, *args, **kwargs):
        """
        Obtiene requerimientos internos con filtros avanzados
        
        Parámetros GET:
        - numero: número del requerimiento a buscar (opcional)
        - idreqinterno: ID del requerimiento interno exacto (opcional)
        - estado: estado del requerimiento (opcional - 'AP', 'TP', 'todos')
        - fecha_desde: fecha desde (formato YYYY-MM-DD, opcional)
        - fecha_hasta: fecha hasta (formato YYYY-MM-DD, opcional)
        - limit: límite de resultados (opcional, por defecto 50, máximo 100)
        """
        cursor = None
        try:
            # Obtener parámetros de búsqueda
            numero = request.GET.get('numero', '').strip()
            idreqinterno = request.GET.get('idreqinterno', '').strip()  # ✅ NUEVO PARÁMETRO
            estado = request.GET.get('estado', '').strip().upper()
            fecha_desde = request.GET.get('fecha_desde', '').strip()
            fecha_hasta = request.GET.get('fecha_hasta', '').strip()
            
            # Convertir limit a entero con validación
            try:
                limit = min(int(request.GET.get('limit', 50)), 100)
            except (ValueError, TypeError):
                limit = 50
            
            cursor = connection_donluis.cursor()
            
            # Query base sin parametrizar TOP
            base_query = f"""
                SELECT TOP {limit}
                    R.IDREQINTERNO,
                    R.IDDOCUMENTO AS TD,
                    R.SERIE,
                    R.NUMERO,
                    FORMAT(R.FECHA, 'dd/MM/yy') AS FECHA,
                    B.NOMBRE AS RAZON_SOCIAL,
                    R.IDESTADO,
                    R.IDMOTIVO,
                    R.IDDOCUMENTO AS DOC_ORIGEN,
                    R.IDEMPRESA,
                    R.OBSERVACION,
                    R.TOTAL,
                    R.IDRESPONSABLE
                FROM REQINTERNO R
                INNER JOIN RESPONSABLE B ON B.IDRESPONSABLE = R.IDRESPONSABLE
                WHERE 1=1
            """
            
            # Lista para parámetros (sin incluir limit)
            params = []
            conditions = []
            
            # ✅ FILTRO POR IDREQINTERNO EXACTO (NUEVA FUNCIONALIDAD)
            if idreqinterno:
                conditions.append("R.IDREQINTERNO = ?")
                params.append(idreqinterno)
                # Si buscamos por IDREQINTERNO exacto, ignoramos otros filtros para mejor performance
                # y devolvemos directamente el resultado
            else:
                # Filtro por estado
                if estado and estado != 'TODOS':
                    if estado == 'APROBADO':
                        conditions.append("R.IDESTADO = 'AP'")
                    elif estado == 'PENDIENTE':
                        conditions.append("R.IDESTADO = 'TP'")
                    else:
                        conditions.append("R.IDESTADO = ?")
                        params.append(estado)
                else:
                    conditions.append("(R.IDESTADO = 'AP' OR R.IDESTADO = 'TP')")
                
                # Filtro por número
                if numero:
                    conditions.append("R.NUMERO LIKE ?")
                    params.append(f'%{numero}%')
                
                # Filtro por fecha desde
                if fecha_desde:
                    try:
                        from datetime import datetime
                        datetime.strptime(fecha_desde, '%Y-%m-%d')
                        conditions.append("R.FECHA >= ?")
                        params.append(fecha_desde)
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                        }, status=400)
                
                # Filtro por fecha hasta
                if fecha_hasta:
                    try:
                        from datetime import datetime
                        datetime.strptime(fecha_hasta, '%Y-%m-%d')
                        conditions.append("R.FECHA <= ?")
                        params.append(fecha_hasta)
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                        }, status=400)
            
            # Construir query final
            if conditions:
                query = base_query + " AND " + " AND ".join(conditions)
            else:
                query = base_query
            
            query += " ORDER BY R.FECHA DESC, R.NUMERO DESC"
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Procesar resultados
            results = []
            for row in cursor.fetchall():
                results.append({
                    'IDREQINTERNO': row[0],
                    'TD': row[1],
                    'SERIE': row[2],
                    'NUMERO': row[3],
                    'FECHA': row[4],
                    'RAZON_SOCIAL': row[5],
                    'IDESTADO': row[6],
                    'IDMOTIVO': row[7],
                    'DOC_ORIGEN': row[8],
                    'DOC': f"{row[1]} {row[2]} {row[3]} - {row[4]}",
                    'IDEMPRESA': row[9],
                    'OBSERVACION': row[10],
                    'TOTAL': row[11],
                    'IDRESPONSABLE': row[12]
                })
            
            # Generar mensaje
            filtros_aplicados = []
            if idreqinterno:
                filtros_aplicados.append(f'IDREQINTERNO "{idreqinterno}"')
            if numero:
                filtros_aplicados.append(f'número "{numero}"')
            if estado and estado != 'TODOS':
                filtros_aplicados.append(f'estado "{estado}"')
            if fecha_desde:
                filtros_aplicados.append(f'desde {fecha_desde}')
            if fecha_hasta:
                filtros_aplicados.append(f'hasta {fecha_hasta}')
            
            if filtros_aplicados:
                mensaje = f'Se encontraron {len(results)} requerimientos con filtros: {", ".join(filtros_aplicados)}'
            else:
                mensaje = f'Se encontraron {len(results)} requerimientos (AP/TP)'
            
            return JsonResponse({
                'status': 'success',
                'message': mensaje,
                'total_encontrados': len(results),
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al buscar requerimientos: {str(e)}'
            }, status=500)
        finally:
            if cursor:
                cursor.close()



# Funciones auxiliares para procesar detalles de requerimientos

def procesar_detalle_requerimiento(detalle):
    """
    Procesa y limpia los datos de un detalle de requerimiento
    
    Args:
        detalle (dict): Diccionario con los datos del detalle
        
    Returns:
        dict: Detalle procesado y limpio
    """
    from decimal import Decimal
    import datetime
    
    detalle_procesado = {}
    
    for key, value in detalle.items():
        # Mantener precisión decimal completa
        if isinstance(value, Decimal):
            # Formatear a 6 decimales para preservar precisión
            detalle_procesado[key] = float(f"{value:.6f}")
        # Procesar fechas
        elif isinstance(value, datetime.datetime):
            detalle_procesado[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            detalle_procesado[f'{key}_FORMATTED'] = value.strftime('%d/%m/%Y')
        elif isinstance(value, datetime.date):
            detalle_procesado[key] = value.strftime('%Y-%m-%d')
            detalle_procesado[f'{key}_FORMATTED'] = value.strftime('%d/%m/%Y')
        # Limpiar strings (ya se hace en SQL pero por seguridad)
        elif isinstance(value, str):
            detalle_procesado[key] = value.strip()
        # Manejar valores None
        elif value is None:
            detalle_procesado[key] = ""
        else:
            detalle_procesado[key] = value
    
    # Campos calculados adicionales
    cantidad = detalle_procesado.get('CANTIDAD', 0)
    cant_aprobada = detalle_procesado.get('CANTAPROBADA', 0)
    
    # Estado de atención
    if detalle_procesado.get('ATENDIDO', 0) == 1:
        detalle_procesado['ESTADO_ATENCION'] = 'ATENDIDO'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'success'
    elif detalle_procesado.get('genero_salida', 0) == 1:
        detalle_procesado['ESTADO_ATENCION'] = 'EN_PROCESO'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'warning'
    else:
        detalle_procesado['ESTADO_ATENCION'] = 'PENDIENTE'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'danger'
    
    # Porcentaje de atención
    if cant_aprobada > 0:
        porcentaje = (cantidad / cant_aprobada) * 100
        detalle_procesado['PORCENTAJE_ATENCION'] = round(porcentaje, 6)
    else:
        detalle_procesado['PORCENTAJE_ATENCION'] = 0
    
    # Formato de cantidades para mostrar con 6 decimales
    detalle_procesado['CANTIDAD_DISPLAY'] = f"{cantidad:.6f}"
    detalle_procesado['CANTAPROBADA_DISPLAY'] = f"{cant_aprobada:.6f}"
    
    if 'CANTIDAD_PENDIENTE' in detalle_procesado:
        pendiente = detalle_procesado['CANTIDAD_PENDIENTE']
        detalle_procesado['CANTIDAD_PENDIENTE_DISPLAY'] = f"{pendiente:.6f}"
    
    return detalle_procesado





def calcular_estadisticas_requerimiento(detalles):
    """
    Calcula estadísticas generales del requerimiento
    
    Args:
        detalles (list): Lista de detalles del requerimiento
        
    Returns:
        dict: Estadísticas calculadas
    """
    if not detalles:
        return {}
    
    total_items = len(detalles)
    items_atendidos = sum(1 for d in detalles if d.get('ATENDIDO', 0) == 1)
    items_en_proceso = sum(1 for d in detalles if d.get('genero_salida', 0) == 1 and d.get('ATENDIDO', 0) == 0)
    items_pendientes = total_items - items_atendidos - items_en_proceso
    
    # Calcular totales de cantidades
    total_cantidad_solicitada = sum(d.get('CANTAPROBADA', 0) for d in detalles)
    total_cantidad_atendida = sum(d.get('CANTIDAD', 0) for d in detalles if d.get('ATENDIDO', 0) == 1)
    
    # Porcentaje general de atención
    porcentaje_atencion = 0
    if total_cantidad_solicitada > 0:
        porcentaje_atencion = round((total_cantidad_atendida / total_cantidad_solicitada) * 100, 2)
    
    # Productos únicos
    productos_unicos = len(set(d.get('IDPRODUCTO', '') for d in detalles))
    
    return {
        'total_items': total_items,
        'items_atendidos': items_atendidos,
        'items_en_proceso': items_en_proceso,
        'items_pendientes': items_pendientes,
        'porcentaje_items_atendidos': round((items_atendidos / total_items) * 100, 2) if total_items > 0 else 0,
        'total_cantidad_solicitada': total_cantidad_solicitada,
        'total_cantidad_atendida': total_cantidad_atendida,
        'porcentaje_atencion_cantidad': porcentaje_atencion,
        'productos_unicos': productos_unicos,
        'estado_general': 'COMPLETADO' if items_atendidos == total_items else 'PARCIAL' if items_atendidos > 0 else 'PENDIENTE'
    }




class DetalleRequerimientoAPI(View):
    def get(self, request, idreqinterno, *args, **kwargs):
        """
        Obtiene los detalles completos de un requerimiento interno por su IDREQINTERNO
        
        Args:
            idreqinterno (str): ID del requerimiento interno
            
        Returns:
            JsonResponse: Detalles del requerimiento o error
        """
        cursor = None
        try:
            # Validar que se proporcione el IDREQINTERNO
            if not idreqinterno or idreqinterno.strip() == '':
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDREQINTERNO es requerido'
                }, status=400)
            
            # Limpiar el parámetro de entrada
            idreqinterno_limpio = idreqinterno.strip()
            
            # Conectar a la base de datos
            cursor = connection_donluis.cursor()
            
            # Query optimizada con función de cantidad por atender
            query = """
                SELECT 
                    D.IDEMPRESA,
                    D.IDREQINTERNO,
                    D.ITEM,
                    LTRIM(RTRIM(D.IDPRODUCTO)) AS IDPRODUCTO,
                    LTRIM(RTRIM(D.DESCRIPCION)) AS DESCRIPCION,
                    LTRIM(RTRIM(D.IDMEDIDA)) AS IDMEDIDA,
                    D.CANTIDAD,
                    D.CANTIDAD AS CANTAPROBADA,
                    LTRIM(RTRIM(D.IDCONSUMIDOR)) AS IDCONSUMIDOR,
                    LTRIM(RTRIM(D.IDRESPONSABLE)) AS IDRESPONSABLE,
                    D.ATENDIDO,
                    D.ESTADOS,
                    -- Campos adicionales útiles
                    D.IDCLIEPROV,
                    D.PARAFECHA,
                    D.genero_salida,
                    -- Cantidad pendiente usando la función
                    ISNULL(F.CANTIDAD_POR_ATENDER, D.CANTAPROBADA) AS CANTIDAD_PENDIENTE,
                    ISNULL(F.TOTAL_CANTIDAD_SALIDA, 0) AS TOTAL_SALIDAS_REALIZADAS
                FROM DREQINTERNO D WITH (NOLOCK)
                LEFT JOIN fn_CANTIDAD_POR_ATENDER_REQINTERNO('001', ?) F 
                    ON D.IDREQINTERNO = F.IDREQINTERNO 
                    AND D.ITEM = F.ITEM 
                    AND LTRIM(RTRIM(D.IDPRODUCTO)) = F.IDPRODUCTO
                WHERE D.ATENDIDO = '0' AND D.IDREQINTERNO = ?
                ORDER BY CAST(D.ITEM AS INT)
            """
            
            # Ejecutar consulta pasando el mismo parámetro dos veces
            cursor.execute(query, [idreqinterno_limpio, idreqinterno_limpio])
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener todos los resultados
            rows = cursor.fetchall()
            
            if rows:
                # Convertir resultados a lista de diccionarios
                detalles = []
                for row in rows:
                    detalle = dict(zip(columns, row))
                    
                    # Procesar y limpiar datos
                    detalle_procesado = procesar_detalle_requerimiento(detalle)
                    detalles.append(detalle_procesado)
                
                cursor.close()
                
                # Calcular estadísticas del requerimiento
                estadisticas = calcular_estadisticas_requerimiento(detalles)
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Se encontraron {len(detalles)} detalles para el requerimiento {idreqinterno_limpio}',
                    'data': detalles,
                    'estadisticas': estadisticas,
                    'idreqinterno': idreqinterno_limpio,
                    'total_items': len(detalles)
                })
            
            else:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No se encontraron detalles para el requerimiento con IDREQINTERNO: {idreqinterno_limpio}',
                    'idreqinterno': idreqinterno_limpio
                }, status=404)
                
        except Exception as e:
            # Cerrar cursor en caso de error
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
                
            return JsonResponse({
                'status': 'error',
                'message': f'Error al consultar los detalles del requerimiento: {str(e)}',
                'idreqinterno': idreqinterno
            }, status=500)





# Clase adicional para consultas específicas de salidas internas
@method_decorator(csrf_exempt, name='dispatch')
class ConsultaSalidaInternaAPI(View):
    """
    API para consultas específicas de salidas internas
    """
    
    def get(self, request, *args, **kwargs):
        """
        Consultas especializadas para salidas internas
        """
        try:
            cursor = connection_donluis.cursor()
            tipo_consulta = request.GET.get('tipo', '')
            
            if tipo_consulta == 'resumen_periodo':
                return self._resumen_por_periodo(cursor, request)
            elif tipo_consulta == 'productos_salida':
                return self._productos_por_salida(cursor, request)
            elif tipo_consulta == 'validar_stock':
                return self._validar_stock_productos(cursor, request)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de consulta no válido'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error en consulta: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    def _resumen_por_periodo(self, cursor, request):
        """Obtiene resumen de salidas por período"""
        periodo = request.GET.get('periodo', '')
        
        cursor.execute("""
            SELECT IDESTADO, COUNT(*) as CANTIDAD, 
                   SUM(ISNULL(TOTAL, 0)) as IMPORTE_TOTAL
            FROM INGRESOSALIDAALM
            WHERE PERIODO = ? AND IDOPERACION = 'SALM'
            GROUP BY IDESTADO
        """, [periodo])
        
        resultados = cursor.fetchall()
        resumen = [{'estado': row[0], 'cantidad': row[1], 'importe': float(row[2])} for row in resultados]
        
        return JsonResponse({
            'success': True,
            'resumen': resumen
        })
    
    def _productos_por_salida(self, cursor, request):
        """Obtiene productos de una salida específica"""
        idingresosalidaalm = request.GET.get('id', '')
        
        cursor.execute("""
            SELECT ITEM, IDPRODUCTO, DESCRIPCION, CANTIDAD, 
                   IDMEDIDA, PRECIO, IMPORTE, IDCONSUMIDOR
            FROM DINGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
            ORDER BY ITEM
        """, [idingresosalidaalm])
        
        resultados = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in resultados]
        
        return JsonResponse({
            'success': True,
            'productos': productos
        })
    
    def _validar_stock_productos(self, cursor, request):
        """Valida stock disponible de productos"""
        productos = request.GET.get('productos', '').split(',')
        almacen = request.GET.get('almacen', '')
        
        validaciones = []
        for producto in productos:
            cursor.execute("""
                SELECT IDPRODUCTO, SUM(ISNULL(STOCK, 0)) as STOCK_DISPONIBLE
                FROM STOCK_PRODUCTOS 
                WHERE IDPRODUCTO = ? AND IDALMACEN = ?
                GROUP BY IDPRODUCTO
            """, [producto.strip(), almacen])
            
            resultado = cursor.fetchone()
            if resultado:
                validaciones.append({
                    'producto': resultado[0],
                    'stock_disponible': float(resultado[1]),
                    'disponible': float(resultado[1]) > 0
                })
            else:
                validaciones.append({
                    'producto': producto.strip(),
                    'stock_disponible': 0,
                    'disponible': False
                })
        
        return JsonResponse({
            'success': True,
            'validaciones': validaciones
        })




#================================================================================================================
# API PARA LA BUSQUEDA DE REQUERIMIENTOS - CAMPO VERDE
#================================================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class BuscarRequerimientoInternoAPICV(View):
    """
    API para buscar requerimientos internos por número de documento
    Por defecto muestra todos los requerimientos pendientes para seleccionar
    """
    def get(self, request, *args, **kwargs):
        """
        Obtiene requerimientos internos con filtros avanzados
        
        Parámetros GET:
        - numero: número del requerimiento a buscar (opcional)
        - idreqinterno: ID del requerimiento interno exacto (opcional)
        - estado: estado del requerimiento (opcional - 'AP', 'TP', 'todos')
        - fecha_desde: fecha desde (formato YYYY-MM-DD, opcional)
        - fecha_hasta: fecha hasta (formato YYYY-MM-DD, opcional)
        - limit: límite de resultados (opcional, por defecto 50, máximo 100)
        """
        cursor = None
        try:
            # Obtener parámetros de búsqueda
            numero = request.GET.get('numero', '').strip()
            idreqinterno = request.GET.get('idreqinterno', '').strip()  # ✅ NUEVO PARÁMETRO
            estado = request.GET.get('estado', '').strip().upper()
            fecha_desde = request.GET.get('fecha_desde', '').strip()
            fecha_hasta = request.GET.get('fecha_hasta', '').strip()
            
            # Convertir limit a entero con validación
            try:
                limit = min(int(request.GET.get('limit', 50)), 100)
            except (ValueError, TypeError):
                limit = 50
            
            cursor = connection_campoverde.cursor()
            
            # Query base sin parametrizar TOP
            base_query = f"""
                SELECT TOP {limit}
                    R.IDREQINTERNO,
                    R.IDDOCUMENTO AS TD,
                    R.SERIE,
                    R.NUMERO,
                    FORMAT(R.FECHA, 'dd/MM/yy') AS FECHA,
                    B.NOMBRE AS RAZON_SOCIAL,
                    R.IDESTADO,
                    R.IDMOTIVO,
                    R.IDDOCUMENTO AS DOC_ORIGEN,
                    R.IDEMPRESA,
                    R.OBSERVACION,
                    R.TOTAL,
                    R.IDRESPONSABLE
                FROM REQINTERNO R
                INNER JOIN RESPONSABLE B ON B.IDRESPONSABLE = R.IDRESPONSABLE
                WHERE 1=1
            """
            
            # Lista para parámetros (sin incluir limit)
            params = []
            conditions = []
            
            # ✅ FILTRO POR IDREQINTERNO EXACTO (NUEVA FUNCIONALIDAD)
            if idreqinterno:
                conditions.append("R.IDREQINTERNO = ?")
                params.append(idreqinterno)
                # Si buscamos por IDREQINTERNO exacto, ignoramos otros filtros para mejor performance
                # y devolvemos directamente el resultado
            else:
                # Filtro por estado
                if estado and estado != 'TODOS':
                    if estado == 'APROBADO':
                        conditions.append("R.IDESTADO = 'AP'")
                    elif estado == 'PENDIENTE':
                        conditions.append("R.IDESTADO = 'TP'")
                    else:
                        conditions.append("R.IDESTADO = ?")
                        params.append(estado)
                else:
                    conditions.append("(R.IDESTADO = 'AP' OR R.IDESTADO = 'TP')")
                
                # Filtro por número
                if numero:
                    conditions.append("R.NUMERO LIKE ?")
                    params.append(f'%{numero}%')
                
                # Filtro por fecha desde
                if fecha_desde:
                    try:
                        from datetime import datetime
                        datetime.strptime(fecha_desde, '%Y-%m-%d')
                        conditions.append("R.FECHA >= ?")
                        params.append(fecha_desde)
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                        }, status=400)
                
                # Filtro por fecha hasta
                if fecha_hasta:
                    try:
                        from datetime import datetime
                        datetime.strptime(fecha_hasta, '%Y-%m-%d')
                        conditions.append("R.FECHA <= ?")
                        params.append(fecha_hasta)
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                        }, status=400)
            
            # Construir query final
            if conditions:
                query = base_query + " AND " + " AND ".join(conditions)
            else:
                query = base_query
            
            query += " ORDER BY R.FECHA DESC, R.NUMERO DESC"
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Procesar resultados
            results = []
            for row in cursor.fetchall():
                results.append({
                    'IDREQINTERNO': row[0],
                    'TD': row[1],
                    'SERIE': row[2],
                    'NUMERO': row[3],
                    'FECHA': row[4],
                    'RAZON_SOCIAL': row[5],
                    'IDESTADO': row[6],
                    'IDMOTIVO': row[7],
                    'DOC_ORIGEN': row[8],
                    'DOC': f"{row[1]} {row[2]} {row[3]} - {row[4]}",
                    'IDEMPRESA': row[9],
                    'OBSERVACION': row[10],
                    'TOTAL': row[11],
                    'IDRESPONSABLE': row[12]
                })
            
            # Generar mensaje
            filtros_aplicados = []
            if idreqinterno:
                filtros_aplicados.append(f'IDREQINTERNO "{idreqinterno}"')
            if numero:
                filtros_aplicados.append(f'número "{numero}"')
            if estado and estado != 'TODOS':
                filtros_aplicados.append(f'estado "{estado}"')
            if fecha_desde:
                filtros_aplicados.append(f'desde {fecha_desde}')
            if fecha_hasta:
                filtros_aplicados.append(f'hasta {fecha_hasta}')
            
            if filtros_aplicados:
                mensaje = f'Se encontraron {len(results)} requerimientos con filtros: {", ".join(filtros_aplicados)}'
            else:
                mensaje = f'Se encontraron {len(results)} requerimientos (AP/TP)'
            
            return JsonResponse({
                'status': 'success',
                'message': mensaje,
                'total_encontrados': len(results),
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al buscar requerimientos: {str(e)}'
            }, status=500)
        finally:
            if cursor:
                cursor.close()


#Funciones auxiliares para procesar detalles de requerimientos
def procesar_detalle_requerimientoCV(detalle):
    """
    Procesa y limpia los datos de un detalle de requerimiento
    
    Args:
        detalle (dict): Diccionario con los datos del detalle
        
    Returns:
        dict: Detalle procesado y limpio
    """
    from decimal import Decimal
    import datetime
    
    detalle_procesado = {}
    
    for key, value in detalle.items():
        # Mantener precisión decimal completa
        if isinstance(value, Decimal):
            # Formatear a 6 decimales para preservar precisión
            detalle_procesado[key] = float(f"{value:.6f}")
        # Procesar fechas
        elif isinstance(value, datetime.datetime):
            detalle_procesado[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            detalle_procesado[f'{key}_FORMATTED'] = value.strftime('%d/%m/%Y')
        elif isinstance(value, datetime.date):
            detalle_procesado[key] = value.strftime('%Y-%m-%d')
            detalle_procesado[f'{key}_FORMATTED'] = value.strftime('%d/%m/%Y')
        # Limpiar strings (ya se hace en SQL pero por seguridad)
        elif isinstance(value, str):
            detalle_procesado[key] = value.strip()
        # Manejar valores None
        elif value is None:
            detalle_procesado[key] = ""
        else:
            detalle_procesado[key] = value
    
    # Campos calculados adicionales
    cantidad = detalle_procesado.get('CANTIDAD', 0)
    cant_aprobada = detalle_procesado.get('CANTAPROBADA', 0)
    
    # Estado de atención
    if detalle_procesado.get('ATENDIDO', 0) == 1:
        detalle_procesado['ESTADO_ATENCION'] = 'ATENDIDO'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'success'
    elif detalle_procesado.get('genero_salida', 0) == 1:
        detalle_procesado['ESTADO_ATENCION'] = 'EN_PROCESO'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'warning'
    else:
        detalle_procesado['ESTADO_ATENCION'] = 'PENDIENTE'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'danger'
    
    # Porcentaje de atención
    if cant_aprobada > 0:
        porcentaje = (cantidad / cant_aprobada) * 100
        detalle_procesado['PORCENTAJE_ATENCION'] = round(porcentaje, 6)
    else:
        detalle_procesado['PORCENTAJE_ATENCION'] = 0
    
    # Formato de cantidades para mostrar con 6 decimales
    detalle_procesado['CANTIDAD_DISPLAY'] = f"{cantidad:.6f}"
    detalle_procesado['CANTAPROBADA_DISPLAY'] = f"{cant_aprobada:.6f}"
    
    if 'CANTIDAD_PENDIENTE' in detalle_procesado:
        pendiente = detalle_procesado['CANTIDAD_PENDIENTE']
        detalle_procesado['CANTIDAD_PENDIENTE_DISPLAY'] = f"{pendiente:.6f}"
    
    return detalle_procesado


def calcular_estadisticas_requerimientoCV(detalles):
    """
    Calcula estadísticas generales del requerimiento
    
    Args:
        detalles (list): Lista de detalles del requerimiento
        
    Returns:
        dict: Estadísticas calculadas
    """
    if not detalles:
        return {}
    
    total_items = len(detalles)
    items_atendidos = sum(1 for d in detalles if d.get('ATENDIDO', 0) == 1)
    items_en_proceso = sum(1 for d in detalles if d.get('genero_salida', 0) == 1 and d.get('ATENDIDO', 0) == 0)
    items_pendientes = total_items - items_atendidos - items_en_proceso
    
    # Calcular totales de cantidades
    total_cantidad_solicitada = sum(d.get('CANTAPROBADA', 0) for d in detalles)
    total_cantidad_atendida = sum(d.get('CANTIDAD', 0) for d in detalles if d.get('ATENDIDO', 0) == 1)
    
    # Porcentaje general de atención
    porcentaje_atencion = 0
    if total_cantidad_solicitada > 0:
        porcentaje_atencion = round((total_cantidad_atendida / total_cantidad_solicitada) * 100, 2)
    
    # Productos únicos
    productos_unicos = len(set(d.get('IDPRODUCTO', '') for d in detalles))
    
    return {
        'total_items': total_items,
        'items_atendidos': items_atendidos,
        'items_en_proceso': items_en_proceso,
        'items_pendientes': items_pendientes,
        'porcentaje_items_atendidos': round((items_atendidos / total_items) * 100, 2) if total_items > 0 else 0,
        'total_cantidad_solicitada': total_cantidad_solicitada,
        'total_cantidad_atendida': total_cantidad_atendida,
        'porcentaje_atencion_cantidad': porcentaje_atencion,
        'productos_unicos': productos_unicos,
        'estado_general': 'COMPLETADO' if items_atendidos == total_items else 'PARCIAL' if items_atendidos > 0 else 'PENDIENTE'
    }

class DetalleRequerimientoAPICV(View):
    def get(self, request, idreqinterno, *args, **kwargs):
        """
        Obtiene los detalles completos de un requerimiento interno por su IDREQINTERNO
        
        Args:
            idreqinterno (str): ID del requerimiento interno
            
        Returns:
            JsonResponse: Detalles del requerimiento o error
        """
        cursor = None
        try:
            # Validar que se proporcione el IDREQINTERNO
            if not idreqinterno or idreqinterno.strip() == '':
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDREQINTERNO es requerido'
                }, status=400)
            
            # Limpiar el parámetro de entrada
            idreqinterno_limpio = idreqinterno.strip()
            
            # Conectar a la base de datos
            cursor = connection_campoverde.cursor()
            
            # Query optimizada con función de cantidad por atender
            query = """
                SELECT 
                    D.IDEMPRESA,
                    D.IDREQINTERNO,
                    D.ITEM,
                    LTRIM(RTRIM(D.IDPRODUCTO)) AS IDPRODUCTO,
                    LTRIM(RTRIM(D.DESCRIPCION)) AS DESCRIPCION,
                    LTRIM(RTRIM(D.IDMEDIDA)) AS IDMEDIDA,
                    D.CANTIDAD,
                    D.CANTIDAD AS CANTAPROBADA,
                    LTRIM(RTRIM(D.IDCONSUMIDOR)) AS IDCONSUMIDOR,
                    LTRIM(RTRIM(D.IDRESPONSABLE)) AS IDRESPONSABLE,
                    D.ATENDIDO,
                    D.ESTADOS,
                    -- Campos adicionales útiles
                    D.IDCLIEPROV,
                    D.PARAFECHA,
                    D.genero_salida,
                    -- Cantidad pendiente usando la función
                    ISNULL(F.CANTIDAD_POR_ATENDER, D.CANTAPROBADA) AS CANTIDAD_PENDIENTE,
                    ISNULL(F.TOTAL_CANTIDAD_SALIDA, 0) AS TOTAL_SALIDAS_REALIZADAS
                FROM DREQINTERNO D WITH (NOLOCK)
                LEFT JOIN fn_CANTIDAD_POR_ATENDER_REQINTERNO('001', ?) F 
                    ON D.IDREQINTERNO = F.IDREQINTERNO 
                    AND D.ITEM = F.ITEM 
                    AND LTRIM(RTRIM(D.IDPRODUCTO)) = F.IDPRODUCTO
                WHERE D.ATENDIDO = '0' AND D.IDREQINTERNO = ?
                ORDER BY CAST(D.ITEM AS INT)
            """
            
            # Ejecutar consulta pasando el mismo parámetro dos veces
            cursor.execute(query, [idreqinterno_limpio, idreqinterno_limpio])
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener todos los resultados
            rows = cursor.fetchall()
            
            if rows:
                # Convertir resultados a lista de diccionarios
                detalles = []
                for row in rows:
                    detalle = dict(zip(columns, row))
                    
                    # Procesar y limpiar datos
                    detalle_procesado = procesar_detalle_requerimiento(detalle)
                    detalles.append(detalle_procesado)
                
                cursor.close()
                
                # Calcular estadísticas del requerimiento
                estadisticas = calcular_estadisticas_requerimiento(detalles)
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Se encontraron {len(detalles)} detalles para el requerimiento {idreqinterno_limpio}',
                    'data': detalles,
                    'estadisticas': estadisticas,
                    'idreqinterno': idreqinterno_limpio,
                    'total_items': len(detalles)
                })
            
            else:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No se encontraron detalles para el requerimiento con IDREQINTERNO: {idreqinterno_limpio}',
                    'idreqinterno': idreqinterno_limpio
                }, status=404)
                
        except Exception as e:
            # Cerrar cursor en caso de error
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
                
            return JsonResponse({
                'status': 'error',
                'message': f'Error al consultar los detalles del requerimiento: {str(e)}',
                'idreqinterno': idreqinterno
            }, status=500)

# Clase adicional para consultas específicas de salidas internas

@method_decorator(csrf_exempt, name='dispatch')
class ConsultaSalidaInternaAPICV(View):
    """
    API para consultas específicas de salidas internas
    """
    
    def get(self, request, *args, **kwargs):
        """
        Consultas especializadas para salidas internas
        """
        try:
            cursor = connection_campoverde.cursor()
            tipo_consulta = request.GET.get('tipo', '')
            
            if tipo_consulta == 'resumen_periodo':
                return self._resumen_por_periodo(cursor, request)
            elif tipo_consulta == 'productos_salida':
                return self._productos_por_salida(cursor, request)
            elif tipo_consulta == 'validar_stock':
                return self._validar_stock_productos(cursor, request)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de consulta no válido'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error en consulta: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    def _resumen_por_periodo(self, cursor, request):
        """Obtiene resumen de salidas por período"""
        periodo = request.GET.get('periodo', '')
        
        cursor.execute("""
            SELECT IDESTADO, COUNT(*) as CANTIDAD, 
                   SUM(ISNULL(TOTAL, 0)) as IMPORTE_TOTAL
            FROM INGRESOSALIDAALM
            WHERE PERIODO = ? AND IDOPERACION = 'SALM'
            GROUP BY IDESTADO
        """, [periodo])
        
        resultados = cursor.fetchall()
        resumen = [{'estado': row[0], 'cantidad': row[1], 'importe': float(row[2])} for row in resultados]
        
        return JsonResponse({
            'success': True,
            'resumen': resumen
        })
    
    def _productos_por_salida(self, cursor, request):
        """Obtiene productos de una salida específica"""
        idingresosalidaalm = request.GET.get('id', '')
        
        cursor.execute("""
            SELECT ITEM, IDPRODUCTO, DESCRIPCION, CANTIDAD, 
                   IDMEDIDA, PRECIO, IMPORTE, IDCONSUMIDOR
            FROM DINGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
            ORDER BY ITEM
        """, [idingresosalidaalm])
        
        resultados = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in resultados]
        
        return JsonResponse({
            'success': True,
            'productos': productos
        })
    
    def _validar_stock_productos(self, cursor, request):
        """Valida stock disponible de productos"""
        productos = request.GET.get('productos', '').split(',')
        almacen = request.GET.get('almacen', '')
        
        validaciones = []
        for producto in productos:
            cursor.execute("""
                SELECT IDPRODUCTO, SUM(ISNULL(STOCK, 0)) as STOCK_DISPONIBLE
                FROM STOCK_PRODUCTOS 
                WHERE IDPRODUCTO = ? AND IDALMACEN = ?
                GROUP BY IDPRODUCTO
            """, [producto.strip(), almacen])
            
            resultado = cursor.fetchone()
            if resultado:
                validaciones.append({
                    'producto': resultado[0],
                    'stock_disponible': float(resultado[1]),
                    'disponible': float(resultado[1]) > 0
                })
            else:
                validaciones.append({
                    'producto': producto.strip(),
                    'stock_disponible': 0,
                    'disponible': False
                })
        
        return JsonResponse({
            'success': True,
            'validaciones': validaciones
        })





#############################################################################################
# SALIDAS INTERNAS DOCUMENTO - DON LUIS 
##############################################################################################

class GetSalidaInternaDocument(View):
    """
    API para obtener los datos de una salida interna mediante procedimiento almacenado
    Devuelve dos conjuntos de datos: encabezado y detalle
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el ID de salida desde los parámetros de la URL
            id_salida = self.kwargs.get('id_salida')
            
            # Validar que se proporcione el ID
            if not id_salida:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'ID de salida interna es requerido'
                }, status=400)

            # Ejecutar el procedimiento almacenado
            with connection_donluis.cursor() as cursor:
                cursor.execute("EXEC PROC_GET_SALIDA_INTERNA_DOCUMENT ?", [id_salida])
                
                # Obtener el primer conjunto de resultados (encabezado)
                encabezado_raw = cursor.fetchall()
                encabezado_columns = [col[0] for col in cursor.description]
                
                # Avanzar al siguiente conjunto de resultados (detalle)
                cursor.nextset()
                detalle_raw = cursor.fetchall()
                detalle_columns = [col[0] for col in cursor.description]
                
                # ❌ REMOVER ESTA LÍNEA - el 'with' statement se encarga del cierre
                # cursor.close()

            # Procesar el encabezado (debe ser solo un registro)
            if not encabezado_raw:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'No se encontró la salida interna especificada'
                }, status=404)

            # Convertir encabezado a diccionario
            encabezado = dict(zip(encabezado_columns, encabezado_raw[0]))
            
            # Convertir detalle a lista de diccionarios
            detalle = []
            for row in detalle_raw:
                detalle.append(dict(zip(detalle_columns, row)))

            # Estructura de respuesta JSON
            response_data = {
                'status': 'SUCCESS',
                'message': 'Datos obtenidos correctamente',
                'data': {
                    'encabezado': encabezado,
                    'detalle': detalle,
                    'resumen': {
                        'total_items': len(detalle),
                        'fecha_consulta': encabezado.get('FECHA_IMPRESION', ''),
                        'hora_consulta': encabezado.get('HORA_IMPRESION', '')
                    }
                }
            }

            return JsonResponse(response_data, safe=False)

        except Exception as e:
            # Manejo de errores
            import logging
            logging.error(f"Error en GetSalidaInternaDocument: {str(e)}")
            
            return JsonResponse({
                'status': 'ERROR',
                'message': 'Error interno del servidor',
                'error_detail': str(e)
            }, status=500)


#############################################################################################
# SALIDAS INTERNAS DOCUMENTO - CAMPO VERDE
##############################################################################################

class GetSalidaInternaDocumentCV(View):
    """
    API para obtener los datos de una salida interna mediante procedimiento almacenado
    Devuelve dos conjuntos de datos: encabezado y detalle
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el ID de salida desde los parámetros de la URL
            id_salida = self.kwargs.get('id_salida')
            
            # Validar que se proporcione el ID
            if not id_salida:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'ID de salida interna es requerido'
                }, status=400)

            # Ejecutar el procedimiento almacenado
            with connection_campoverde.cursor() as cursor:
                cursor.execute("EXEC PROC_GET_SALIDA_INTERNA_DOCUMENT ?", [id_salida])
                
                # Obtener el primer conjunto de resultados (encabezado)
                encabezado_raw = cursor.fetchall()
                encabezado_columns = [col[0] for col in cursor.description]
                
                # Avanzar al siguiente conjunto de resultados (detalle)
                cursor.nextset()
                detalle_raw = cursor.fetchall()
                detalle_columns = [col[0] for col in cursor.description]
                
                # ❌ REMOVER ESTA LÍNEA - el 'with' statement se encarga del cierre
                # cursor.close()

            # Procesar el encabezado (debe ser solo un registro)
            if not encabezado_raw:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'No se encontró la salida interna especificada'
                }, status=404)

            # Convertir encabezado a diccionario
            encabezado = dict(zip(encabezado_columns, encabezado_raw[0]))
            
            # Convertir detalle a lista de diccionarios
            detalle = []
            for row in detalle_raw:
                detalle.append(dict(zip(detalle_columns, row)))

            # Estructura de respuesta JSON
            response_data = {
                'status': 'SUCCESS',
                'message': 'Datos obtenidos correctamente',
                'data': {
                    'encabezado': encabezado,
                    'detalle': detalle,
                    'resumen': {
                        'total_items': len(detalle),
                        'fecha_consulta': encabezado.get('FECHA_IMPRESION', ''),
                        'hora_consulta': encabezado.get('HORA_IMPRESION', '')
                    }
                }
            }

            return JsonResponse(response_data, safe=False)

        except Exception as e:
            # Manejo de errores
            import logging
            logging.error(f"Error en GetSalidaInternaDocument: {str(e)}")
            
            return JsonResponse({
                'status': 'ERROR',
                'message': 'Error interno del servidor',
                'error_detail': str(e)
            }, status=500)






#====================================================================================================================
    # REPORTE DE ALMACEN
#====================================================================================================================

class ReportesView_dl (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/components/DonLuis/report/reporte_productos.html'


#====================================================================================================================
    # REPORTE DE ALMACEN - CAMPO VERDE
#====================================================================================================================

class ReportesView_cv (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/components/CampoVerde/report/reporte_productos_cv.html'



####################################################################################################################################
# FASE INTERMEDIA
####################################################################################################################################


#Api para la fase intermedia tabla principal
@method_decorator(csrf_exempt, name='dispatch')
class FaseIntermediaEvaluacionesView(View):
    """
    Vista para manejar la fase intermedia de evaluaciones de desempeño
    Permite consultar evaluaciones con porcentajes de avance de objetivos y competencias
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros opcionales
            id_area = request.GET.get('id_area')
            id_evaluacion = request.GET.get('id_evaluacion')
            
            if id_evaluacion:
                # Si se solicita una evaluación específica, usar el procedimiento de detalles
                cursor.execute("EXEC SP_DETALLE_EVALUACION_FASE_INTERMEDIA ?", [id_evaluacion])
                
                # Obtener información general de la evaluación
                columns = [column[0] for column in cursor.description]
                evaluacion_info = cursor.fetchone()
                
                if not evaluacion_info:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Evaluación no encontrada'
                    }, status=404)
                
                evaluacion_data = dict(zip(columns, evaluacion_info))
                
                # Obtener objetivos (segundo resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    obj_columns = [column[0] for column in cursor.description]
                    objetivos = []
                    for row in cursor.fetchall():
                        objetivo = dict(zip(obj_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                            objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                        if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                            objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                        objetivos.append(objetivo)
                else:
                    objetivos = []
                
                # Obtener competencias (tercer resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    comp_columns = [column[0] for column in cursor.description]
                    competencias = []
                    for row in cursor.fetchall():
                        competencia = dict(zip(comp_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in competencia and competencia['fecha_inicio']:
                            competencia['fecha_inicio'] = competencia['fecha_inicio']
                        if 'fecha_fin' in competencia and competencia['fecha_fin']:
                            competencia['fecha_fin'] = competencia['fecha_fin']
                        competencias.append(competencia)
                else:
                    competencias = []
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Detalles de evaluación obtenidos correctamente',
                    'data': {
                        'evaluacion': evaluacion_data,
                        'objetivos': objetivos,
                        'competencias': competencias
                    }
                })
                
            else:
                # Obtener lista general de evaluaciones para la fase intermedia con filtro de periodo
                periodo = request.GET.get('campania', None)  # Mantener 'campania' como nombre del parámetro para compatibilidad
                
                # Si no se proporciona periodo, usar el año actual
                if not periodo:
                    anio_actual = date.today().year
                    periodo = str(anio_actual)
                
                # Extraer solo el año si viene en formato CAMP2026
                if periodo.startswith('CAMP'):
                    periodo = periodo.replace('CAMP', '')
                
                # Obtener lista general de evaluaciones para la fase intermedia
                if id_area:
                    cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES @id_area=?, @periodo=?", [id_area, periodo])
                else:
                    cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES @periodo=?", [periodo])
                
                # 🔥 ESTE BLOQUE FALTA
                if not cursor.description:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No hay evaluaciones de fase intermedia para el periodo',
                        'data': [],
                        'total_evaluaciones': 0,
                        'periodo': periodo,
                        'filtros_aplicados': {
                            'id_area': id_area,
                            'periodo': periodo
                        }
                    })
                
                # Obtener los nombres de las columnas
                columns = [column[0] for column in cursor.description]
                
                # Convertir los resultados a una lista de diccionarios
                evaluaciones = []
                for row in cursor.fetchall():
                    evaluacion = dict(zip(columns, row))
                    
                    # Convertir fecha a string para JSON si existe
                    if 'fecha_evaluacion' in evaluacion and evaluacion['fecha_evaluacion']:
                        evaluacion['fecha_evaluacion'] = evaluacion['fecha_evaluacion'].strftime('%Y-%m-%d')
                    
                    # Asegurar que los porcentajes sean números enteros
                    for field in ['porcentaje_objetivos', 'porcentaje_competencias', 'porcentaje_general']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(float(evaluacion[field]))
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que los contadores sean números enteros
                    for field in ['total_objetivos', 'objetivos_con_avance', 'total_competencias', 'competencias_con_avance']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(evaluacion[field])
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que el estado sea booleano
                    if 'estado' in evaluacion:
                        evaluacion['estado'] = bool(evaluacion['estado'])
                    
                    evaluaciones.append(evaluacion)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluaciones de fase intermedia obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'filtros_aplicados': {
                        'id_area': id_area,
                        'periodo': periodo
                    }
                })
                
        except Exception as e:
            print(f"Error en FaseIntermediaEvaluacionesView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener datos de fase intermedia: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


#Api para los detalles de la fase intermedia


@method_decorator(csrf_exempt, name='dispatch')
class DetallesEvaluacionModalView(View):
    """
    Vista para obtener detalles de objetivos o competencias para el modal de avance rápido
    Ejecuta el procedimiento almacenado SP_OBTENER_DETALLES_EVALUACION_MODAL
    
    Parámetros:
    - id_evaluacion: ID de la evaluación (requerido)
    - tipo: Tipo de tabla (1 = Objetivos, 2 = Competencias) (requerido)
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros de la URL
            id_evaluacion = request.GET.get('id_evaluacion')
            tipo_tabla = request.GET.get('tipo')  # 1 = Objetivos, 2 = Competencias
            cargar_comentarios = request.GET.get('cargar_comentarios')  # Para cargar solo comentarios
            
            # Si se solicita cargar solo comentarios
            if cargar_comentarios == 'true' and id_evaluacion:
                try:
                    id_evaluacion_int = int(id_evaluacion)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El parámetro id_evaluacion debe ser un número válido'
                    }, status=400)
                
                # Consultar comentarios de la tabla RRHH_EVALUACIONES
                cursor.execute("""
                    SELECT 
                        comentarios_objetivos_general,
                        comentarios_competencias_general
                    FROM RRHH_EVALUACIONES 
                    WHERE id = ? AND estado = 1
                """, [id_evaluacion_int])
                
                resultado = cursor.fetchone()
                
                if resultado:
                    comentarios = {
                        'comentarios_objetivos_general': resultado[0] or '',
                        'comentarios_competencias_general': resultado[1] or ''
                    }
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Comentarios obtenidos correctamente',
                        'comentarios': comentarios,
                        'id_evaluacion': id_evaluacion_int
                    })
                else:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No se encontraron comentarios para esta evaluación',
                        'comentarios': {
                            'comentarios_objetivos_general': '',
                            'comentarios_competencias_general': ''
                        },
                        'id_evaluacion': id_evaluacion_int
                    })
            
            # Validar parámetros requeridos para obtener detalles
            if not id_evaluacion or not tipo_tabla:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los parámetros id_evaluacion y tipo'
                }, status=400)
            
            # Validar que sean números válidos
            try:
                id_evaluacion_int = int(id_evaluacion)
                tipo_tabla_int = int(tipo_tabla)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Los parámetros id_evaluacion y tipo deben ser números válidos'
                }, status=400)
            
            # Validar que tipo_tabla sea 1 o 2
            if tipo_tabla_int not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El parámetro tipo debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            print(f"Ejecutando procedimiento con: id_evaluacion={id_evaluacion_int}, tipo_tabla={tipo_tabla_int}")
            
            # Ejecutar el procedimiento almacenado
            cursor.execute(
                "EXEC SP_OBTENER_DETALLES_EVALUACION_MODAL @id_evaluacion = ?, @tipo_tabla = ?", 
                [id_evaluacion_int, tipo_tabla_int]
            )
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(columns, row))
                
                # Procesar fechas para objetivos
                if tipo_tabla_int == 1:  # Objetivos
                    # Convertir fechas a string si existen y no son None
                    for fecha_field in ['fecha_inicio', 'fecha_fin']:
                        if fecha_field in detalle and detalle[fecha_field]:
                            if hasattr(detalle[fecha_field], 'strftime'):
                                detalle[fecha_field] = detalle[fecha_field].strftime('%Y-%m-%d')
                    
                    # Mantener fechas formateadas como string
                    for formato_field in ['fecha_inicio_formato', 'fecha_fin_formato']:
                        if formato_field in detalle and detalle[formato_field]:
                            detalle[formato_field] = str(detalle[formato_field])
                
                # Asegurar que los porcentajes sean números enteros
                if 'porcentaje_actual' in detalle:
                    detalle['porcentaje_actual'] = int(detalle['porcentaje_actual']) if detalle['porcentaje_actual'] is not None else 0
                
                # Asegurar que las puntuaciones sean números enteros
                for field in ['puntuacion_no_cumple', 'puntuacion_cumple', 'puntuacion_excede', 'puntuacion_sobresaliente']:
                    if field in detalle:
                        detalle[field] = int(detalle[field]) if detalle[field] is not None else 0
                
                # Asegurar que campos numéricos específicos sean enteros
                for field in ['duracion_dias', 'dias_restantes']:
                    if field in detalle and detalle[field] is not None:
                        detalle[field] = int(detalle[field])
                
                detalles.append(detalle)
            
            # Determinar el nombre del tipo para la respuesta
            tipo_nombre = "objetivos" if tipo_tabla_int == 1 else "competencias"
            
            print(f"Procedimiento ejecutado correctamente. Registros encontrados: {len(detalles)}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'{tipo_nombre.title()} obtenidos correctamente',
                'data': detalles,
                'total_registros': len(detalles),
                'id_evaluacion': id_evaluacion_int,
                'tipo': tipo_nombre
            })
            
        except Exception as e:
            print(f"Error en DetallesEvaluacionModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener detalles: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    

    def put(self, request, *args, **kwargs):
        """
        Actualizar porcentajes de avance para múltiples objetivos o competencias
        Incluye actualización de comentarios generales en la tabla RRHH_EVALUACIONES
        
        Estructura esperada del JSON:
        {
            "tipo": 1 o 2 (1=Objetivos, 2=Competencias),
            "id_evaluacion": 189,
            "actualizaciones": [
                {
                    "id": 123,
                    "porcentaje_avance": 85
                },
                {
                    "id": 124,
                    "porcentaje_avance": 70
                }
            ],
            "comentarios_objetivos_general": "Comentario general para objetivos...",
            "comentarios_competencias_general": "Comentario general para competencias..."
        }
        """
        cursor = None
        try:
            # Parsear los datos JSON del request
            data = json.loads(request.body)
            
            # Validar estructura básica de datos
            if 'tipo' not in data or 'actualizaciones' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los campos "tipo" y "actualizaciones"'
                }, status=400)
            
            tipo_tabla = data['tipo']
            actualizaciones = data['actualizaciones']
            id_evaluacion = data.get('id_evaluacion')
            
            # Obtener comentarios generales del request
            comentarios_objetivos_general = data.get('comentarios_objetivos_general', '')
            comentarios_competencias_general = data.get('comentarios_competencias_general', '')
            
            # Validar tipo de tabla
            if tipo_tabla not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El campo "tipo" debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            # Validar que hay actualizaciones
            if not actualizaciones or not isinstance(actualizaciones, list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requiere al menos una actualización en el array "actualizaciones"'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            # Determinar tabla y campo según el tipo
            if tipo_tabla == 1:  # Objetivos
                tabla = "RRHH_OBJETIVOS"
                id_campo = "id"
            else:  # Competencias
                tabla = "RRHH_COMPETENCIAS"
                id_campo = "id"
            
            actualizaciones_exitosas = []
            actualizaciones_fallidas = []
            
            # Procesar cada actualización de porcentajes
            for actualizacion in actualizaciones:
                try:
                    # Validar estructura de cada actualización
                    if 'id' not in actualizacion or 'porcentaje_avance' not in actualizacion:
                        actualizaciones_fallidas.append({
                            'registro': actualizacion,
                            'error': 'Faltan campos "id" o "porcentaje_avance"'
                        })
                        continue
                    
                    registro_id = actualizacion['id']
                    porcentaje_avance = actualizacion['porcentaje_avance']
                    
                    # Validar que el ID sea un número válido
                    try:
                        registro_id = int(registro_id)
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'ID debe ser un número válido'
                        })
                        continue
                    
                    # Validar que el porcentaje esté en el rango válido
                    try:
                        porcentaje_avance = float(porcentaje_avance)
                        if porcentaje_avance < 0 or porcentaje_avance > 100:
                            actualizaciones_fallidas.append({
                                'id': registro_id,
                                'error': 'El porcentaje debe estar entre 0 y 100'
                            })
                            continue
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'El porcentaje debe ser un número válido'
                        })
                        continue
                    
                    # Verificar que el registro existe
                    cursor.execute(f"""
                        SELECT {id_campo} FROM {tabla} 
                        WHERE {id_campo} = ? AND estado = 1
                    """, [registro_id])
                    
                    if not cursor.fetchone():
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': f'{"Objetivo" if tipo_tabla == 1 else "Competencia"} no encontrado o inactivo'
                        })
                        continue
                    
                    #agrego YERSON
                    if tipo_tabla == 1:  # Objetivos
                        comentarios_objetivo = actualizacion.get('comentarios_objetivos', '')
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porc_cumplimiento = ?, comentarios_objetivos = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_avance, comentarios_objetivo, registro_id])
                    else:  # Competencias
                        comentarios_competencia = actualizacion.get('comentarios_competencias', '')
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porc_cumplimiento = ?, comentarios_competencias = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_avance, comentarios_competencia, registro_id])
                    
                    # # Realizar la actualización del porcentaje
                    # cursor.execute(f"""
                    #     UPDATE {tabla} 
                    #     SET porc_cumplimiento = ?
                    #     WHERE {id_campo} = ?
                    # """, [porcentaje_avance, registro_id])
                    
                    # Verificar que se actualizó al menos una fila
                    if cursor.rowcount > 0:
                        actualizaciones_exitosas.append({
                            'id': registro_id,
                            'porcentaje_anterior': None,  # Podríamos obtenerlo antes de la actualización si es necesario
                            'porcentaje_nuevo': porcentaje_avance
                        })
                    else:
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'No se pudo actualizar el registro'
                        })
                    
                except Exception as e:
                    actualizaciones_fallidas.append({
                        'id': actualizacion.get('id', 'desconocido'),
                        'error': f'Error al procesar actualización: {str(e)}'
                    })
                    continue
            
            # Actualizar comentarios generales en la tabla RRHH_EVALUACIONES
            comentarios_actualizados = False
            if id_evaluacion:
                try:
                    # Verificar que la evaluación existe
                    cursor.execute("""
                        SELECT id FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion])
                    
                    if cursor.fetchone():
                        # Actualizar comentarios según el tipo
                        if tipo_tabla == 1:  # Objetivos
                            cursor.execute("""
                                UPDATE RRHH_EVALUACIONES 
                                SET comentarios_objetivos_general = ?
                                WHERE id = ?
                            """, [comentarios_objetivos_general, id_evaluacion])
                        else:  # Competencias
                            cursor.execute("""
                                UPDATE RRHH_EVALUACIONES 
                                SET comentarios_competencias_general = ?
                                WHERE id = ?
                            """, [comentarios_competencias_general, id_evaluacion])
                        
                        if cursor.rowcount > 0:
                            comentarios_actualizados = True
                            print(f"Comentarios generales actualizados para evaluación {id_evaluacion}")
                    else:
                        print(f"Evaluación {id_evaluacion} no encontrada o inactiva")
                        
                except Exception as e:
                    print(f"Error al actualizar comentarios generales: {str(e)}")
                    # No fallar toda la operación por comentarios, solo registrar el error
            
            # Confirmar todas las transacciones si hay al menos una actualización exitosa
            if actualizaciones_exitosas or comentarios_actualizados:
                connection_portalaei.commit()
            
            # Determinar el estado de la respuesta
            total_actualizaciones = len(actualizaciones)
            exitosas = len(actualizaciones_exitosas)
            fallidas = len(actualizaciones_fallidas)
            
            if exitosas == total_actualizaciones:
                status_code = 200
                message = f"Todas las actualizaciones fueron exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales actualizados"
                status = 'success'
            elif exitosas > 0:
                status_code = 207  # Multi-Status
                message = f"Actualizaciones parcialmente exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales actualizados"
                status = 'partial_success'
            else:
                if comentarios_actualizados:
                    status_code = 200
                    message = "Comentarios generales actualizados correctamente"
                    status = 'success'
                else:
                    status_code = 400
                    message = f"Ninguna actualización fue exitosa (0/{total_actualizaciones})"
                    status = 'error'
            
            tipo_nombre = "objetivos" if tipo_tabla == 1 else "competencias"
            
            print(f"Actualización de {tipo_nombre}: {exitosas} exitosas, {fallidas} fallidas, comentarios: {comentarios_actualizados}")
            
            return JsonResponse({
                'status': status,
                'message': message,
                'data': {
                    'tipo': tipo_nombre,
                    'total_procesadas': total_actualizaciones,
                    'exitosas': exitosas,
                    'fallidas': fallidas,
                    'comentarios_actualizados': comentarios_actualizados,
                    'id_evaluacion': id_evaluacion,
                    'actualizaciones_exitosas': actualizaciones_exitosas,
                    'actualizaciones_fallidas': actualizaciones_fallidas
                }
            }, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)
            
        except Exception as e:
            # En caso de error general, hacer rollback
            if cursor:
                try:
                    connection_portalaei.rollback()
                except:
                    pass
            
            print(f"Error en PUT DetallesEvaluacionModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()




#================================================================================================================
# CAMPO VERDE - TECNOLOGIA DE LA INFORMACION
#================================================================================================================

#=================================================================================================================
#MODULO PRESUPUESTOS
#AUTOR: JHON GUTIERREZ
#FECHA: 06/01/2025
#MODIFICACIONES: 
# 01/01/2025: Se crea el modulo de presupuestos
#=================================================================================================================







# PRESUPUESTO

class presupuesto_cv(TemplateView):
    permission_required = 'modulo_almacen'
    template_name = 'ALMACEN/pages/almacen_presupuesto_cv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return context

#==============================================================================================
# SERVICIOS
# AUTOR: JHON GUTIERREZ
#==============================================================================================

#REPORTE DE TOTALES DE SERVICIOS

def Costo_servicio_totals_cv(request):
     # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:

        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '8', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '8'
            """)

        # Obtener los nombres de las columnas
        columns = [col[0] for col in cursor.description]

        # Obtener la primera fila
        row = cursor.fetchone()

        results = {}

        if row:
            for i, value in enumerate(row):
                if isinstance(value, Decimal):
                    value = float(value)
                results[columns[i]] = value if value is not None else 0

    return JsonResponse(results)




# CRUD DE SERVICIOS
@method_decorator(csrf_exempt, name='dispatch')
class Costo_Servicios_View_cv(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Verificar si ya existe la observación para esta área
            check_query = """
            SELECT COUNT(*) 
                FROM SERVICIOS_CV 
                WHERE observacion = ? 
                AND id_area = ? 
                AND observacion IS NOT NULL
            """
            observacion = data.get('observacion', '').strip()  # Eliminar espacios en blanco
            area_id = data.get('id_area', 8)
            if observacion:  # Solo verificar si hay una observación
                cursor.execute(check_query, [observacion, area_id])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)

            id_campania = data.get('ID_CAMPANIA')

            query = """
            INSERT INTO SERVICIOS_CV (
                idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO,id_area, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Valores base
            values = [
                data['idproducto'],
                data['grupo_servicio'],
                data['subgrupo_servicio'],
                data['descripcion'],
                float(data.get('precio_unitario', 0)),
                data.get('observacion', ''),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = int(data.get(f'{mes}_cantidad', 0))
                precio = cantidad * float(data.get('precio_unitario', 0))
                values.extend([cantidad, precio])
            
            # Agregar usuario
            """ nombre_usuario = f"{request.user.first_name} {request.user.last_name}".strip()
            if not nombre_usuario:
                nombre_usuario = request.user.username
            values.append(nombre_usuario) """
            
            values.append(request.user.id) # ID DEL USUARIO
            values.append(8) # ID DEL AREA 
            values.append(id_campania) # ID DE LA CAMPANIA


            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio registrado correctamente'})
        
        
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Ya existe un servicio con esta observación en esta área'
            }, status=400)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            campania = request.GET.get('year', '')

            if id:
                query = """
                SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SERVICIOS_CV
                WHERE id = ?  AND id_area = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SERVICIOS_CV 
                    WHERE id_area = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SERVICIOS_CV 
                    WHERE id_area = 8
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM SERVICIOS_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM SERVICIOS_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

             # Verificar si ya existe la observación para esta área (excluyendo el registro actual)
            check_query = """
            SELECT COUNT(*) 
                FROM SERVICIOS_CV 
                WHERE observacion = ? 
                AND id_area = ? 
                AND id != ?
                AND observacion IS NOT NULL
            """
            observacion = data.get('observacion', '').strip()
            area_id = data.get('id_area', 8)
            if observacion:
                cursor.execute(check_query, [observacion, area_id, id])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)
            
            cursor.execute("SELECT id FROM SERVICIOS_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            
            query = """
            UPDATE SERVICIOS_CV
            SET idproducto = ?, grupo_servicio = ?, subgrupo_servicio = ?, descripcion = ?, precio_unitario = ?, observacion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?
            WHERE id = ?
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['grupo_servicio'],
                data['subgrupo_servicio'],
                data['descripcion'],
                precio_unitario,
                data.get('observacion', ''),
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = int(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            
            values.extend([request.user.id,8, id])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio actualizado correctamente'})
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Ya existe un servicio con esta observación en esta área'
            }, status=400)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
#==============================================================================================
# SUMINISTROS
# AUTOR: JHON GUTIERREZ
#==============================================================================================



#REPORTE DE TOTALES DE SUMINISTROS

def Costos_suministros_totals_cv(request):
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:
        if campania:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s, %s", [8, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s", [8])

        rows = cursor.fetchall()

    results = {k: v for (k, v) in rows}
    return JsonResponse(results)



#TIPOS DE SUMINISTROS

@method_decorator(csrf_exempt, name='dispatch')
class CombustiblesLubricantesView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,1,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parametro de campaña del request
            campania = request.GET.get('year', '')
            
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 1
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 1
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 1
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,1])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     
    

@method_decorator(csrf_exempt, name='dispatch')
class UtilesOficinaView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,5,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? 
                AND id_area = 8
                AND id_tipo_suministro = 5 
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Obtener el parametro de campaña del request
                campania = request.GET.get('year', '')
                
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 5
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ?
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,5])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class EquiposComputoView_cv(View): 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            


            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,7,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 7
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 7
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? 
            AND id_area = 8 
            AND id_tipo_suministro = 7
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,7])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    

@method_decorator(csrf_exempt, name='dispatch')
class OtrosSuministrosView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8,id_campania])

            # Agregar el nombre completo del usuario al final de la lista de valores
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 8
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8])


            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class MaterialConstruccionView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,4,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 4
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 4
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 4
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,4])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
      

@method_decorator(csrf_exempt, name='dispatch')
class RepuestosAccesoriosView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,2,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 2
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 2
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
            try:
                data = json.loads(request.body)
                cursor = connection_portalaei.cursor()
                
                # Primero, verificamos si el producto existe
                cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
                if cursor.fetchone() is None:
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
                
                # Si el producto existe, lo actualizamos
                query = """
                    UPDATE SUMINISTRO_CV
                SET idproducto = ?, descripcion = ?,
                    enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                    marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                    mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                    julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                    septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                    noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                    USUARIO = ?, id_area = ?, id_tipo_suministro = ?
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 2
                """
                
                precio_unitario = float(data.get('precio_unitario', 0))
                values = [
                    data['idproducto'],
                    data['descripcion'],
                ]
                
                for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                    cantidad = float(data.get(f'{mes}_cantidad', 0))
                    precio = precio_unitario * cantidad if cantidad > 0 else 0
                    values.extend([cantidad, precio])

                # Agregar el nombre completo del usuario al final de la lista de valores
                values.extend([request.user.id,8,2])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     
     

@method_decorator(csrf_exempt, name='dispatch')
class EquiposUITView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,9,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 9
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 9
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
            try:
                data = json.loads(request.body)
                cursor = connection_portalaei.cursor()
                
                # Primero, verificamos si el producto existe
                cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
                if cursor.fetchone() is None:
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
                
                # Si el producto existe, lo actualizamos
                query = """
                    UPDATE SUMINISTRO_CV
                SET idproducto = ?, descripcion = ?,
                    enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                    marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                    mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                    julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                    septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                    noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                    USUARIO = ?, id_area = ?, id_tipo_suministro = ?
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 9
                """
                
                precio_unitario = float(data.get('precio_unitario', 0))
                values = [
                    data['idproducto'],
                    data['descripcion'],
                ]
                
                for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                    cantidad = float(data.get(f'{mes}_cantidad', 0))
                    precio = precio_unitario * cantidad if cantidad > 0 else 0
                    values.extend([cantidad, precio])

                # Agregar el nombre completo del usuario al final de la lista de valores
                values.extend([request.user.id,8,9])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
       
          

@method_decorator(csrf_exempt, name='dispatch')
class MaterialesAgriculturaView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')

            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,3,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 3
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 3
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 3
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,3])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class EquiposProteccionView_cv(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_CV (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,6,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 6
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id_area = 8 AND id_tipo_suministro = 6
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 8 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_CV
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 6
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,6])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     



#==============================================================================================
# MODULO: CAPEX
# AUTOR: JHON GUTIERREZ
# FECHA: 27/11/2024
#==============================================================================================


def Costos_capex_totals_cv(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '8', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '8'
            """)
        
        # Obtener los nombres de las columnas
        columns = [col[0] for col in cursor.description]
        # Obtener la primera fila de resultados
        row = cursor.fetchone()
        
        # Crear el diccionario combinando columnas con valores
        results = {}
        if row:
            for i, value in enumerate(row):
                # Convertir Decimal a float si es necesario
                if isinstance(value, Decimal):
                    value = float(value)
                results[columns[i]] = value if value is not None else 0
                
    return JsonResponse(results)



@method_decorator(csrf_exempt, name='dispatch')
class CapexView_cv(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            idproducto = data.get('idproducto')
            id_area = data.get('id_area', 8)
            id_campania = data.get('ID_CAMPANIA')

            if idproducto == '11111111111':
                # Para productos nuevos, validar que tenga observación
                observacion = data.get('observacion', '').strip()
                if not observacion:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'La observación es requerida para productos nuevos'
                    }, status=400)
            else:
                # Para productos normales, verificar que no exista el mismo producto en la misma área
                check_query = """
                SELECT COUNT(*) 
                FROM CAPEX_CV 
                WHERE idproducto = ? 
                AND id_area = ?
                AND idproducto <> '11111111111'
                """
                cursor.execute(check_query, [idproducto, id_area])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Este producto ya existe en esta área. Por favor, seleccione un producto diferente.'
                    }, status=400)
            
            # Continuar con la inserción si pasa las validaciones
            query = """
            INSERT INTO CAPEX_CV (
                idproducto, descripcion, precio_unitario, observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO, id_area, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                idproducto,
                data['descripcion'],
                precio_unitario,
                data.get('observacion', ''),  # Puede ser vacío si no es producto nuevo
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            values.extend([request.user.id, id_area, id_campania])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'CAPEX registrado correctamente'})
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parametro de campaña del request
            campania = request.GET.get('year', '')
            
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,observacion
                FROM CAPEX_CV
                WHERE id = ? AND id_area = 8 
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                           observacion
                    FROM CAPEX_CV
                    WHERE id_area = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                           observacion
                    FROM CAPEX_CV
                    WHERE id_area = 8
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM CAPEX_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM CAPEX_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM CAPEX_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE CAPEX_CV
            SET idproducto = ?, descripcion = ?, precio_unitario = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, observacion = ?
            WHERE id = ? AND id_area = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            # Procesar los meses
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar usuario, área y observación
            values.extend([
                request.user.id,
                8,
                data.get('observacion', '')  # Movido aquí para coincidir con el orden del query
            ])
            
            # Agregar el id al final
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)





#==============================================================================================
# MODULO: REMUNERACION
# AUTOR: JHON GUTIERREZ
# FECHA: 27/11/2024
#==============================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CostoSueldosView_cv(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            id_campania = data.get('ID_CAMPANIA')

            query = """
            INSERT INTO REMUNERACION_CV (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion, ID_CAMPANIA
           ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?, ?)
            """

            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                1,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id_campania # ID_CAMPANIA

            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Sueldo registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM REMUNERACION_CV
                WHERE id = ? AND id_area = 8 AND id_remuneracion = 1
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            else:
                campania = request.GET.get('year', '')
                print(f"DEBUG SUELDOS: Recibido year={campania}, GET params={dict(request.GET)}")
                
                # Primero verificar qué valores de ID_CAMPANIA existen
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 8 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 8 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    print(f"DEBUG SUELDOS: Ejecutando query con campania={campania}")
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 8 AND id_remuneracion = 1
                    """
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                print(f"DEBUG SUELDOS: Encontrados {len(data)} registros")
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            print(f"DEBUG SUELDOS ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM REMUNERACION_CV WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Sueldo eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')

            query = """
            UPDATE REMUNERACION_CV
            SET dni = ?, nombre = ?, regimen_laboral = ?, cargo = ?, fecha_ingreso = ?,
                enero = ?, febrero = ?, marzo = ?, abril = ?, mayo = ?, junio = ?,
                julio = ?, agosto = ?, septiembre = ?, octubre = ?, noviembre = ?, diciembre = ?,
                asignacion = ?, USUARIO = ?, id_area = ?, id_remuneracion = ?, fecha = GETDATE(), vacacion = ?
            WHERE id = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario y id
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                1,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id # id
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSueldos_cv(View):
     def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [8, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [8, 1])
                        # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            # Obtener los resultados
            results = cursor.fetchall()
            # Convertir los resultados a un diccionario y asegurar que 'id' esté presente
            data = []
            for row in results:
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                # Si no existe 'id', agregarlo como None
                if 'id' not in item:
                    item['id'] = None
                data.append(item)
            cursor.close()
            return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CostoSalariosView_cv(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            
            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            id_campania = data.get('ID_CAMPANIA')


            query = """
            INSERT INTO REMUNERACION_CV (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?, ?)
            """
                
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                2,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id_campania # ID_CAMPANIA
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM REMUNERACION_CV
                WHERE id = ? AND id_area = 8 AND id_remuneracion = 2
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            else:
                campania = request.GET.get('year', '')
                print(f"DEBUG SALARIOS: Recibido year={campania}, GET params={dict(request.GET)}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 8 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 8 AND id_remuneracion = 2
                    """
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                print(f"DEBUG SALARIOS: Encontrados {len(data)} registros")
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            print(f"DEBUG SALARIOS ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_CV WHERE id = ? ", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM REMUNERACION_CV WHERE id = ? ", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')

            query = """
            UPDATE REMUNERACION_CV
            SET dni = ?, nombre = ?, regimen_laboral = ?, cargo = ?, fecha_ingreso = ?,
                enero = ?, febrero = ?, marzo = ?, abril = ?, mayo = ?, junio = ?,
                julio = ?, agosto = ?, septiembre = ?, octubre = ?, noviembre = ?, diciembre = ?,
                asignacion = ?, USUARIO = ?, id_area = ?, id_remuneracion = ?, fecha = GETDATE(), vacacion = ?
            WHERE id = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario y id
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                2,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id # id
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSalarios_cv(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [8, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [8, 2])
                        
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener los resultados
            results = cursor.fetchall()
            
            # Convertir los resultados a un diccionario
            data = []
            for row in results:
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                data.append(item)
            
            cursor.close()
            return JsonResponse({"data": data})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)






#================================================================================================================
# INVERSIONES AJS - TECNOLOGIA DE LA INFORMACION
#================================================================================================================

#=================================================================================================================
#MODULO PRESUPUESTOS
#AUTOR: JHON GUTIERREZ
#FECHA: 06/01/2025
#MODIFICACIONES: 
# 01/01/2025: Se crea el modulo de presupuestos
#=================================================================================================================







# PRESUPUESTO

class presupuesto_ajs(TemplateView):
    permission_required = 'modulo_almacen'
    template_name = 'ALMACEN/pages/almacen_presupuesto_ajs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return context

#==============================================================================================
# SERVICIOS
# AUTOR: JHON GUTIERREZ
#==============================================================================================


#REPORTE DE TOTALES DE SERVICIOS

def Costo_servicio_totals_ajs(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:

        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_AJS '8', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_AJS '8'
            """)

        # Obtener los nombres de las columnas
        columns = [col[0] for col in cursor.description]

        # Obtener la primera fila
        row = cursor.fetchone()

        results = {}

        if row:
            for i, value in enumerate(row):
                if isinstance(value, Decimal):
                    value = float(value)
                results[columns[i]] = value if value is not None else 0

    return JsonResponse(results)





# CRUD DE SERVICIOS
@method_decorator(csrf_exempt, name='dispatch')
class Costo_Servicios_View_ajs(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Verificar si ya existe la observación para esta área
            check_query = """
            SELECT COUNT(*) 
                FROM SERVICIOS_AJS 
                WHERE observacion = ? 
                AND id_area = ? 
                AND observacion IS NOT NULL
            """
            observacion = data.get('observacion', '').strip()  # Eliminar espacios en blanco
            area_id = data.get('id_area', 8)
            if observacion:  # Solo verificar si hay una observación
                cursor.execute(check_query, [observacion, area_id])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)

            id_campania = data.get('ID_CAMPANIA')

            query = """
            INSERT INTO SERVICIOS_AJS (
                idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO,id_area, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Valores base
            values = [
                data['idproducto'],
                data['grupo_servicio'],
                data['subgrupo_servicio'],
                data['descripcion'],
                float(data.get('precio_unitario', 0)),
                data.get('observacion', ''),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = int(data.get(f'{mes}_cantidad', 0))
                precio = cantidad * float(data.get('precio_unitario', 0))
                values.extend([cantidad, precio])
            
            # Agregar usuario
            """ nombre_usuario = f"{request.user.first_name} {request.user.last_name}".strip()
            if not nombre_usuario:
                nombre_usuario = request.user.username
            values.append(nombre_usuario) """
            
            values.append(request.user.id) # ID DEL USUARIO
            values.append(8) # ID DEL AREA 
            values.append(id_campania) # ID DE LA CAMPANIA


            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio registrado correctamente'})
        
        
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Ya existe un servicio con esta observación en esta área'
            }, status=400)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            campania = request.GET.get('year', '')

            if id:
                query = """
                SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SERVICIOS_AJS
                WHERE id = ?  AND id_area = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SERVICIOS_AJS 
                    WHERE id_area = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SERVICIOS_AJS 
                    WHERE id_area = 8
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM SERVICIOS_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM SERVICIOS_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

             # Verificar si ya existe la observación para esta área (excluyendo el registro actual)
            check_query = """
            SELECT COUNT(*) 
                FROM SERVICIOS_AJS 
                WHERE observacion = ? 
                AND id_area = ? 
                AND id != ?
                AND observacion IS NOT NULL
            """
            observacion = data.get('observacion', '').strip()
            area_id = data.get('id_area', 8)
            if observacion:
                cursor.execute(check_query, [observacion, area_id, id])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)
            
            cursor.execute("SELECT id FROM SERVICIOS_CV WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Servicio no encontrado'}, status=404)
            
            query = """
            UPDATE SERVICIOS_AJS
            SET idproducto = ?, grupo_servicio = ?, subgrupo_servicio = ?, descripcion = ?, precio_unitario = ?, observacion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?
            WHERE id = ?
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['grupo_servicio'],
                data['subgrupo_servicio'],
                data['descripcion'],
                precio_unitario,
                data.get('observacion', ''),
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = int(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            
            values.extend([request.user.id,8, id])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Servicio actualizado correctamente'})
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Ya existe un servicio con esta observación en esta área'
            }, status=400)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
    
#==============================================================================================
# SUMINISTROS
# AUTOR: JHON GUTIERREZ
#==============================================================================================



#REPORTE DE TOTALES DE SUMINISTROS

def Costos_suministros_totals_ajs(request):
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:
        if campania:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s, %s", [8, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s", [8])

        rows = cursor.fetchall()

    results = {k: v for (k, v) in rows}
    return JsonResponse(results)




#TIPOS DE SUMINISTROS

@method_decorator(csrf_exempt, name='dispatch')
class CombustiblesLubricantesView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,1,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parametro de campaña del request
            campania = request.GET.get('year', '')
            
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 1
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 1
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 1
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,1])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     
    

@method_decorator(csrf_exempt, name='dispatch')
class UtilesOficinaView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,5,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? 
                AND id_area = 8
                AND id_tipo_suministro = 5 
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Obtener el parametro de campaña del request
                campania = request.GET.get('year', '')
                
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 5
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ?
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,5])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    
@method_decorator(csrf_exempt, name='dispatch')
class EquiposComputoView_ajs(View): 
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            


            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 7
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 7
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? 
            AND id_area = 8 
            AND id_tipo_suministro = 7
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
     

@method_decorator(csrf_exempt, name='dispatch')
class OtrosSuministrosView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8,id_campania])

            # Agregar el nombre completo del usuario al final de la lista de valores
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 8
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8])


            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class MaterialConstruccionView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            
            values.extend([request.user.id,8,4,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 4
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 4
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 4
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,4])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
 
    

@method_decorator(csrf_exempt, name='dispatch')
class RepuestosAccesoriosView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,2,id_campania])

            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 2
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 2
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
            try:
                data = json.loads(request.body)
                cursor = connection_portalaei.cursor()
                
                # Primero, verificamos si el producto existe
                cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
                if cursor.fetchone() is None:
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
                
                # Si el producto existe, lo actualizamos
                query = """
                    UPDATE SUMINISTRO_AJS
                SET idproducto = ?, descripcion = ?,
                    enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                    marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                    mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                    julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                    septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                    noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                    USUARIO = ?, id_area = ?, id_tipo_suministro = ?
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 2
                """
                
                precio_unitario = float(data.get('precio_unitario', 0))
                values = [
                    data['idproducto'],
                    data['descripcion'],
                ]
                
                for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                    cantidad = float(data.get(f'{mes}_cantidad', 0))
                    precio = precio_unitario * cantidad if cantidad > 0 else 0
                    values.extend([cantidad, precio])

                # Agregar el nombre completo del usuario al final de la lista de valores
                values.extend([request.user.id,8,2])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

      

@method_decorator(csrf_exempt, name='dispatch')
class EquiposUITView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,9,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 9
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (codigo existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 9
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
            try:
                data = json.loads(request.body)
                cursor = connection_portalaei.cursor()
                
                # Primero, verificamos si el producto existe
                cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
                if cursor.fetchone() is None:
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
                
                # Si el producto existe, lo actualizamos
                query = """
                    UPDATE SUMINISTRO_AJS
                SET idproducto = ?, descripcion = ?,
                    enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                    marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                    mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                    julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                    septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                    noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                    USUARIO = ?, id_area = ?, id_tipo_suministro = ?
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 9
                """
                
                precio_unitario = float(data.get('precio_unitario', 0))
                values = [
                    data['idproducto'],
                    data['descripcion'],
                ]
                
                for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                    cantidad = float(data.get(f'{mes}_cantidad', 0))
                    precio = precio_unitario * cantidad if cantidad > 0 else 0
                    values.extend([cantidad, precio])

                # Agregar el nombre completo del usuario al final de la lista de valores
                values.extend([request.user.id,8,9])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
   
         

@method_decorator(csrf_exempt, name='dispatch')
class MaterialesAgriculturaView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')

            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 8
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,8])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class EquiposProteccionView_ajs(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()
            
            query = """
            INSERT INTO SUMINISTRO_AJS (idproducto, descripcion,precio_unitario,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro,ID_CAMPANIA)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            id_campania = data.get('ID_CAMPANIA')
            values = [
                
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,6,id_campania])
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 6
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_AJS
                WHERE id_area = 8 AND id_tipo_suministro = 6
                """
                # Filtrar por campaña si se proporciona el parametro year
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_AJS
                    WHERE id_area = 8 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM SUMINISTRO_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM SUMINISTRO_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE SUMINISTRO_AJS
            SET idproducto = ?, descripcion = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, id_tipo_suministro = ?
            WHERE id = ? AND id_area = 8 AND id_tipo_suministro = 6
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
            ]
            
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar el nombre completo del usuario al final de la lista de valores
            values.extend([request.user.id,8,6])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     



#==============================================================================================
# MODULO: CAPEX
# AUTOR: JHON GUTIERREZ
# FECHA: 28/11/208
#==============================================================================================


def Costos_capex_totals_ajs(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '8', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '8'
            """)
        
        # Obtener los nombres de las columnas
        columns = [col[0] for col in cursor.description]
        # Obtener la primera fila de resultados
        row = cursor.fetchone()
        
        # Crear el diccionario combinando columnas con valores
        results = {}
        if row:
            for i, value in enumerate(row):
                # Convertir Decimal a float si es necesario
                if isinstance(value, Decimal):
                    value = float(value)
                results[columns[i]] = value if value is not None else 0
                
    return JsonResponse(results)

@method_decorator(csrf_exempt, name='dispatch')
class CapexView_ajs(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            idproducto = data.get('idproducto')
            id_area = data.get('id_area', 8)
            id_campania = data.get('ID_CAMPANIA')

            if idproducto == '11111111111':
                # Para productos nuevos, validar que tenga observación
                observacion = data.get('observacion', '').strip()
                if not observacion:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'La observación es requerida para productos nuevos'
                    }, status=400)
            else:
                # Para productos normales, verificar que no exista el mismo producto en la misma área
                check_query = """
                SELECT COUNT(*) 
                FROM CAPEX_AJS 
                WHERE idproducto = ? 
                AND id_area = ?
                AND idproducto <> '11111111111'
                """
                cursor.execute(check_query, [idproducto, id_area])
                if cursor.fetchone()[0] > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Este producto ya existe en esta área. Por favor, seleccione un producto diferente.'
                    }, status=400)
            
            # Continuar con la inserción si pasa las validaciones
            query = """
            INSERT INTO CAPEX_AJS (
                idproducto, descripcion, precio_unitario, observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO, id_area, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                idproducto,
                data['descripcion'],
                precio_unitario,
                data.get('observacion', ''),  # Puede ser vacío si no es producto nuevo
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])
            
            values.extend([request.user.id, id_area, id_campania])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'CAPEX registrado correctamente'})
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parametro de campaña del request
            campania = request.GET.get('year', '')
            
            if id:
                # Si se proporciona un ID, devolver solo ese producto
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,observacion
                FROM CAPEX_AJS
                WHERE id = ? AND id_area = 8 
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Filtrar por campaña si se proporciona el parametro year
                if campania:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                           observacion
                    FROM CAPEX_AJS
                    WHERE id_area = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                           observacion
                    FROM CAPEX_AJS
                    WHERE id_area = 8
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serializacion JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM CAPEX_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo eliminamos
            cursor.execute("DELETE FROM CAPEX_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Primero, verificamos si el producto existe
            cursor.execute("SELECT id FROM CAPEX_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            
            # Si el producto existe, lo actualizamos
            query = """
            UPDATE CAPEX_AJS
            SET idproducto = ?, descripcion = ?, precio_unitario = ?,
                enero_cantidad = ?, enero_precio = ?, febrero_cantidad = ?, febrero_precio = ?,
                marzo_cantidad = ?, marzo_precio = ?, abril_cantidad = ?, abril_precio = ?,
                mayo_cantidad = ?, mayo_precio = ?, junio_cantidad = ?, junio_precio = ?,
                julio_cantidad = ?, julio_precio = ?, agosto_cantidad = ?, agosto_precio = ?,
                septiembre_cantidad = ?, septiembre_precio = ?, octubre_cantidad = ?, octubre_precio = ?,
                noviembre_cantidad = ?, noviembre_precio = ?, diciembre_cantidad = ?, diciembre_precio = ?,
                USUARIO = ?, id_area = ?, observacion = ?
            WHERE id = ? AND id_area = 8
            """
            
            precio_unitario = float(data.get('precio_unitario', 0))
            values = [
                data['idproducto'],
                data['descripcion'],
                precio_unitario,
            ]
            
            # Procesar los meses
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                cantidad = float(data.get(f'{mes}_cantidad', 0))
                precio = precio_unitario * cantidad if cantidad > 0 else 0
                values.extend([cantidad, precio])

            # Agregar usuario, área y observación
            values.extend([
                request.user.id,
                8,
                data.get('observacion', '')  # Movido aquí para coincidir con el orden del query
            ])
            
            # Agregar el id al final
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


#==============================================================================================
# MODULO: REMUNERACION
# AUTOR: JHON GUTIERREZ
# FECHA: 28/11/208
#==============================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CostoSueldosView_ajs(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            id_campania = data.get('ID_CAMPANIA')

            query = """
            INSERT INTO REMUNERACION_AJS (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion, ID_CAMPANIA
           ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?, ?)
            """

            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                1,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id_campania # ID_CAMPANIA

            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Sueldo registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM REMUNERACION_AJS
                WHERE id = ? AND id_area = 8 AND id_remuneracion = 1
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            else:
                campania = request.GET.get('year', '')
                print(f"DEBUG SUELDOS: Recibido year={campania}, GET params={dict(request.GET)}")
                
                # Primero verificar qué valores de ID_CAMPANIA existen
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 8 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 8 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    print(f"DEBUG SUELDOS: Ejecutando query con campania={campania}")
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 8 AND id_remuneracion = 1
                    """
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                print(f"DEBUG SUELDOS: Encontrados {len(data)} registros")
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            print(f"DEBUG SUELDOS ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM REMUNERACION_AJS WHERE id = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Sueldo eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')

            query = """
            UPDATE REMUNERACION_AJS
            SET dni = ?, nombre = ?, regimen_laboral = ?, cargo = ?, fecha_ingreso = ?,
                enero = ?, febrero = ?, marzo = ?, abril = ?, mayo = ?, junio = ?,
                julio = ?, agosto = ?, septiembre = ?, octubre = ?, noviembre = ?, diciembre = ?,
                asignacion = ?, USUARIO = ?, id_area = ?, id_remuneracion = ?, fecha = GETDATE(), vacacion = ?
            WHERE id = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario y id
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                1,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id # id
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSueldos_ajs(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [8, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [8, 1])
                        # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            # Obtener los resultados
            results = cursor.fetchall()
            # Convertir los resultados a un diccionario y asegurar que 'id' esté presente
            data = []
            for row in results:
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                # Si no existe 'id', agregarlo como None
                if 'id' not in item:
                    item['id'] = None
                data.append(item)
            cursor.close()
            return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class CostoSalariosView_ajs(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            
            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            id_campania = data.get('ID_CAMPANIA')


            query = """
            INSERT INTO REMUNERACION_AJS (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion, ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?, ?)
            """
                
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                2,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id_campania # ID_CAMPANIA
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM REMUNERACION_AJS
                WHERE id = ? AND id_area = 8 AND id_remuneracion = 2
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            else:
                campania = request.GET.get('year', '')
                print(f"DEBUG SALARIOS: Recibido year={campania}, GET params={dict(request.GET)}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 8 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 8 AND id_remuneracion = 2
                    """
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    for key, value in item.items():
                        if isinstance(value, Decimal):
                            item[key] = float(value)
                    data.append(item)
                
                print(f"DEBUG SALARIOS: Encontrados {len(data)} registros")
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            print(f"DEBUG SALARIOS ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_AJS WHERE id = ? ", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            cursor.execute("DELETE FROM REMUNERACION_AJS WHERE id = ? ", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            cursor.execute("SELECT id FROM REMUNERACION_AJS WHERE id = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
            
            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')

            query = """
            UPDATE REMUNERACION_AJS
            SET dni = ?, nombre = ?, regimen_laboral = ?, cargo = ?, fecha_ingreso = ?,
                enero = ?, febrero = ?, marzo = ?, abril = ?, mayo = ?, junio = ?,
                julio = ?, agosto = ?, septiembre = ?, octubre = ?, noviembre = ?, diciembre = ?,
                asignacion = ?, USUARIO = ?, id_area = ?, id_remuneracion = ?, fecha = GETDATE(), vacacion = ?
            WHERE id = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombre'),
                data.get('regimen_laboral'),
                data.get('cargo'),
                data.get('fecha_ingreso'),
            ]
            
            # Agregar valores mensuales
            for mes in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']:
                values.append(float(data.get(mes, 0)))
            
            # Agregar usuario y id
            asignacion = '1' if data.get('asignacion') == '1' else '0'
            values.extend([
                asignacion,
                request.user.id,  # USUARIO
                8,  # id_area
                2,   # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id # id
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSalarios_ajs(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [8, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [8, 2])
                        
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener los resultados
            results = cursor.fetchall()
            
            # Convertir los resultados a un diccionario
            data = []
            for row in results:
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                data.append(item)
            
            cursor.close()
            return JsonResponse({"data": data})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)



######################## INVERSIONES AJS ################

#==============================================================================================
# ROTACION DE PRODUCTOS - INVERSIONES AJS
# AUTOR: YERSON GARCIA
#==============================================================================================

class rotacion_productos_ajs (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/pages/almacen_rotacion_productos_ajs.html'

#==============================================================================================
# REPORTE DE ROTACION DE PRODUCTOS - INVERSIONES AJS
# AUTOR: YERSON GARCIA
#==============================================================================================



@method_decorator(csrf_exempt, name='dispatch')
class RotacionProductosViewAJS(View):
    """
    Vista para el reporte de rotación de productos
    Ejecuta el procedimiento SP_OBTENER_SALIDAS_POR_RANGO_FECHAS
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener parámetros de la solicitud
            fecha_inicio = request.GET.get('fecha_inicio')
            fecha_fin = request.GET.get('fecha_fin')
            
            print(f"🔍 Rotación de productos - Parámetros recibidos:")
            print(f"   - Fecha inicio: {fecha_inicio}")
            print(f"   - Fecha fin: {fecha_fin}")
            
            # Validar parámetros obligatorios
            if not fecha_inicio or not fecha_fin:
                return JsonResponse({
                    'success': False,
                    'message': 'Las fechas de inicio y fin son obligatorias'
                }, status=400)
            
            # Ejecutar consulta
            resultados, estadisticas = self._ejecutar_procedimiento_rotacion(fecha_inicio, fecha_fin)
            
            # Retornar datos en JSON
            return JsonResponse({
                'success': True,
                'data': resultados,
                'estadisticas': estadisticas,
                'info': {
                    'total_registros': len(resultados),
                    'fecha_consulta': fecha_inicio + ' al ' + fecha_fin,
                    'procedimiento': 'SP_OBTENER_SALIDAS_POR_RANGO_FECHAS'
                }
            })
            
        except Exception as e:
            print(f"❌ Error en RotacionProductosView: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def _ejecutar_procedimiento_rotacion(self, fecha_inicio, fecha_fin):
        """
        Ejecuta el procedimiento almacenado SP_OBTENER_SALIDAS_POR_RANGO_FECHAS
        """
        try:
            cursor = connection_inversioneajs.cursor()
            
            print(f"🔄 Ejecutando procedimiento SP_OBTENER_SALIDAS_POR_RANGO_FECHAS...")
            
            # Ejecutar el procedimiento almacenado
            cursor.execute("""
                EXEC SP_OBTENER_SALIDAS_POR_RANGO_FECHAS 
                    @FECHA_INICIO = ?, 
                    @FECHA_FIN = ?
            """, [fecha_inicio, fecha_fin])
            
            # Obtener los resultados principales
            columns = [desc[0] for desc in cursor.description]
            resultados_raw = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(resultados_raw)} productos")
            
            # Convertir resultados a lista de diccionarios
            resultados = []
            for row in resultados_raw:
                resultado = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fechas
                    if isinstance(value, datetime) and value:
                        resultado[column_name] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, date) and value:
                        resultado[column_name] = value.strftime('%Y-%m-%d')
                    else:
                        # Limpiar strings
                        if isinstance(value, str):
                            resultado[column_name] = value.strip()
                        else:
                            resultado[column_name] = value
                
                resultados.append(resultado)
            
            # Obtener estadísticas (segundo conjunto de resultados)
            cursor.nextset()
            estadisticas = {}
            if cursor.description:
                stats_columns = [desc[0] for desc in cursor.description]
                stats_row = cursor.fetchone()
                
                if stats_row:
                    for i, value in enumerate(stats_row):
                        estadisticas[stats_columns[i]] = value
            
            cursor.close()
            return resultados, estadisticas
            
        except Exception as e:
            print(f"❌ Error ejecutando procedimiento: {str(e)}")
            raise


#==============================================================================================
# CONSULTA SALIDA INTERNA - INVERSIONES AJS
# AUTOR: YERSON GARCIA
#==============================================================================================


@method_decorator(csrf_exempt, name='dispatch')
class ConsultaSalidaInternaAPIAJS(View):
    """
    API para consultas específicas de salidas internas
    """
    
    def get(self, request, *args, **kwargs):
        """
        Consultas especializadas para salidas internas
        """
        try:
            cursor = connection_inversioneajs.cursor()
            tipo_consulta = request.GET.get('tipo', '')
            
            if tipo_consulta == 'resumen_periodo':
                return self._resumen_por_periodo(cursor, request)
            elif tipo_consulta == 'productos_salida':
                return self._productos_por_salida(cursor, request)
            elif tipo_consulta == 'validar_stock':
                return self._validar_stock_productos(cursor, request)
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Tipo de consulta no válido'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error en consulta: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    def _resumen_por_periodo(self, cursor, request):
        """Obtiene resumen de salidas por período"""
        periodo = request.GET.get('periodo', '')
        
        cursor.execute("""
            SELECT IDESTADO, COUNT(*) as CANTIDAD, 
                   SUM(ISNULL(TOTAL, 0)) as IMPORTE_TOTAL
            FROM INGRESOSALIDAALM
            WHERE PERIODO = ? AND IDOPERACION = 'SALM'
            GROUP BY IDESTADO
        """, [periodo])
        
        resultados = cursor.fetchall()
        resumen = [{'estado': row[0], 'cantidad': row[1], 'importe': float(row[2])} for row in resultados]
        
        return JsonResponse({
            'success': True,
            'resumen': resumen
        })
    
    def _productos_por_salida(self, cursor, request):
        """Obtiene productos de una salida específica"""
        idingresosalidaalm = request.GET.get('id', '')
        
        cursor.execute("""
            SELECT ITEM, IDPRODUCTO, DESCRIPCION, CANTIDAD, 
                   IDMEDIDA, PRECIO, IMPORTE, IDCONSUMIDOR
            FROM DINGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
            ORDER BY ITEM
        """, [idingresosalidaalm])
        
        resultados = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        productos = [dict(zip(columns, row)) for row in resultados]
        
        return JsonResponse({
            'success': True,
            'productos': productos
        })
    
    def _validar_stock_productos(self, cursor, request):
        """Valida stock disponible de productos"""
        productos = request.GET.get('productos', '').split(',')
        almacen = request.GET.get('almacen', '')
        
        validaciones = []
        for producto in productos:
            cursor.execute("""
                SELECT IDPRODUCTO, SUM(ISNULL(STOCK, 0)) as STOCK_DISPONIBLE
                FROM STOCK_PRODUCTOS 
                WHERE IDPRODUCTO = ? AND IDALMACEN = ?
                GROUP BY IDPRODUCTO
            """, [producto.strip(), almacen])
            
            resultado = cursor.fetchone()
            if resultado:
                validaciones.append({
                    'producto': resultado[0],
                    'stock_disponible': float(resultado[1]),
                    'disponible': float(resultado[1]) > 0
                })
            else:
                validaciones.append({
                    'producto': producto.strip(),
                    'stock_disponible': 0,
                    'disponible': False
                })
        
        return JsonResponse({
            'success': True,
            'validaciones': validaciones
        })





#================================================================================================================   
# REQ. INTERNOS - INVERSIONES AJS
#================================================================================================================



@method_decorator(csrf_exempt, name='dispatch')
class RequerimientosInternosViewAJS(View):
    

    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            # Obtener parámetros de filtro desde la URL
            estado = request.GET.get('estado', None)
            area = request.GET.get('area', None)
            motivo = request.GET.get('motivo', None)
            cliente = request.GET.get('cliente', None)
            fecha_desde = request.GET.get('desde', None)
            fecha_hasta = request.GET.get('hasta', None)
            
            cursor = connection_inversioneajs.cursor()
            
            # Consulta optimizada proporcionada
            query = """
            SELECT TOP 500
                R.IDREQINTERNO,
                CONVERT(VARCHAR(10), R.FECHA, 103) AS fecha,
                E.RAZON_SOCIAL AS sucursal,
                A.DESCRIPCION AS almacen,
                CONCAT(R.IDDOCUMENTO,' ' ,R.SERIE ,' ',R.NUMERO) AS documento,
                RE.NOMBRE AS responsable,
                AR.DESCRIPCION AS area,
                M.DESCRIPCION AS motivo,
                ES.DESCRIPCION AS estado,
                R.OBSERVACION AS nota_uso,
                R.IDESTADO,
                EM.IDEMISOR,
                EM.DESCRIPCION AS PUNTO_EMISION,
                -- Periodo en formato "MES - AÑO"
                (CASE RIGHT(R.PERIODO, 2)
                    WHEN '01' THEN 'ENERO'
                    WHEN '02' THEN 'FEBRERO'
                    WHEN '03' THEN 'MARZO'
                    WHEN '04' THEN 'ABRIL'
                    WHEN '05' THEN 'MAYO'
                    WHEN '06' THEN 'JUNIO'
                    WHEN '07' THEN 'JULIO'
                    WHEN '08' THEN 'AGOSTO'
                    WHEN '09' THEN 'SEPTIEMBRE'
                    WHEN '10' THEN 'OCTUBRE'
                    WHEN '11' THEN 'NOVIEMBRE'
                    WHEN '12' THEN 'DICIEMBRE'
                    ELSE 'DESCONOCIDO'
                END + ' - ' + LEFT(R.PERIODO, 4)) AS PERIODO
            FROM REQINTERNO R WITH (NOLOCK)
            INNER JOIN EMPRESAS E WITH (NOLOCK) ON E.IDEMPRESA = R.IDEMPRESA
            INNER JOIN ALMACENES A WITH (NOLOCK) ON A.IDALMACEN = R.IDALMACEN AND A.IDSUCURSAL ='001'
            INNER JOIN RESPONSABLE RE WITH (NOLOCK) ON RE.IDRESPONSABLE = R.IDRESPONSABLE
            INNER JOIN AREAS AR WITH (NOLOCK) ON AR.IDAREA = R.IDAREA
            INNER JOIN MOTIVOSREQINTERNO M WITH (NOLOCK) ON M.IDMOTIVO = R.IDMOTIVO
            INNER JOIN ESTADOS ES WITH (NOLOCK) ON ES.IDESTADO = R.IDESTADO
            INNER JOIN EMISOR EM ON EM.IDEMISOR = R.IDEMISOR
            WHERE 1=1
            """
            
            # Modificar la condición de estado si se especifica en la URL
            # if estado and estado != '(Todos)':
            #     if estado == 'atendido_total':
            #         query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AT'")
            #     elif estado == 'atendido_parcial':
            #         query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AP'")
            #     elif estado == 'aprobado':
            #         query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'AP'")
            #     elif estado == 'pendiente':
            #         query = query.replace("R.IDESTADO IN ('PE', 'AP')", "R.IDESTADO = 'PE'")
            #     elif estado == 'todos':
            #         query = query.replace("R.IDESTADO IN ('PE', 'AP')", "1=1")
            
            # Añadir filtros adicionales
            params = []
            
            if area and area != '(Todos)':
                query += " AND AR.DESCRIPCION LIKE ?"
                params.append(f'%{area}%')
            
            if motivo and motivo != '(Todos)':
                query += " AND M.DESCRIPCION LIKE ?"
                params.append(f'%{motivo}%')
            
            if cliente:
                query += " AND E.RAZON_SOCIAL LIKE ?"
                params.append(f'%{cliente}%')
            
            # if fecha_desde:
            #     query += " AND R.FECHA >= CONVERT(DATETIME, ?, 103)"
            #     params.append(fecha_desde)
            
            # if fecha_hasta:
            #     query += " AND R.FECHA <= CONVERT(DATETIME, ?, 103)"
            #     params.append(fecha_hasta)
            
            if fecha_desde:
                query += " AND R.FECHA >= ?"
                params.append(fecha_desde)

            if fecha_hasta:
                query += " AND R.FECHA <= ?"
                params.append(fecha_hasta)
            
            # Ordenar por fecha más reciente primero
            query += " ORDER BY R.FECHA DESC"
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Obtener resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            # Procesar los resultados
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                
                # Agregar clase CSS según el estado para formateo en frontend
                if item['IDESTADO'] == 'AT':
                    item['estado_clase'] = 'bg-info text-white'
                elif item['IDESTADO'] == 'AP':
                    item['estado_clase'] = 'bg-success text-white'
                elif item['IDESTADO'] == 'PE':
                    item['estado_clase'] = 'bg-warning text-dark'
                else:
                    item['estado_clase'] = 'bg-secondary text-white'
                
                # Eliminar el IDESTADO ya que no es necesario en el frontend
                item.pop('IDESTADO', None)
                
                results.append(item)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Requerimientos internos obtenidos correctamente',
                'total_registros': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()




@method_decorator(csrf_exempt, name='dispatch')
class DetalleRequerimientoInternoAPIAJS(View):
    

    def get(self, request, idreqinterno):
        cursor = None
        try:
            cursor = connection_inversioneajs.cursor()
            # 1. Limpiamos el parámetro para evitar inyección SQL
            idreqinterno_limpio = idreqinterno.strip()
            
            # 2. Consulta SQL con parámetro correcto y TRIM para evitar problemas con espacios
            query = """
                SELECT 
                    TRIM(R.IDREQINTERNO) AS IDREQINTERNO,
                    TRIM(R.ITEM) AS ITEM,
                    TRIM(R.IDPRODUCTO) AS IDPRODUCTO,
                    TRIM(R.DESCRIPCION) AS PRODUCTO,
                    TRIM(R.IDMEDIDA) AS IDMEDIDA,
                    CONVERT(VARCHAR(20), R.CANTIDAD) AS CANTIDAD,
                    TRIM(R.IDCLIEPROV) AS IDDESTINO,
                    TRIM(C.RAZON_SOCIAL) AS DESTINO,
                    TRIM(R.IDCONSUMIDOR) AS IDCONSUMIDOR,
                    TRIM(CO.DESCRIPCION) AS CONSUMIDOR,
                    ISNULL(TRIM(R.OBSERVACIONES), '') AS OBSERVACIONES,
                    CONVERT(VARCHAR(1), R.ATENDIDO) AS ATENDIDO,
                    TRIM(R.IDACTIVIDAD) AS IDACTIVIDAD,
                    TRIM(AC.DESCRIPCION) AS ACTIVIDAD,
                    TRIM(R.ESTADOS) AS ESTADOS,
					ISNULL(F.CANTIDAD_POR_ATENDER, R.CANTAPROBADA) AS CANTIDAD_PENDIENTE,
                    ISNULL(F.TOTAL_CANTIDAD_SALIDA, 0) AS TOTAL_SALIDAS_REALIZADAS
                FROM DREQINTERNO R
				LEFT JOIN fn_CANTIDAD_POR_ATENDER_REQINTERNO('001','?') F 
				ON R.IDREQINTERNO = F.IDREQINTERNO 
                    AND R.ITEM = F.ITEM 
                    AND LTRIM(RTRIM(R.IDPRODUCTO)) = F.IDPRODUCTO
                LEFT JOIN CLIEPROV C ON C.IDCLIEPROV = R.IDCLIEPROV
                LEFT JOIN RESPONSABLE RE ON RE.IDRESPONSABLE = R.IDRESPONSABLE
                LEFT JOIN ACTIVIDAD AC ON AC.IDACTIVIDAD = R.IDACTIVIDAD
                LEFT JOIN CONSUMIDOR CO ON CO.IDCONSUMIDOR = R.IDCONSUMIDOR
                WHERE TRIM(R.IDREQINTERNO) = ?
                ORDER BY R.ITEM
            """
            
            # 3. Ejecutamos la consulta con el parámetro
            cursor.execute(query, [idreqinterno_limpio])
            
            # 4. Procesamos los resultados
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                results.append(item)
            
            # 5. Respuesta JSON con información útil
            return JsonResponse({
                'status': 'success',
                'message': 'Detalles del requerimiento obtenidos correctamente',
                'id_consultado': idreqinterno_limpio,
                'total_items': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'id_consultado': idreqinterno if 'idreqinterno' in locals() else 'no disponible',
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()



@method_decorator(csrf_exempt, name='dispatch')
class ConsultaStockProductoAPIAJS(View):
    def get(self, request, idproducto):
        cursor = None
        try:
            # 1. Limpiamos el parámetro para evitar inyección SQL
            idproducto_limpio = idproducto.strip()
            
            # 2. Usamos connection_inversioneajs que parece ser la conexión específica para este caso
            cursor = connection_inversioneajs.cursor()
            
            # 3. Consulta exactamente como has pedido
            query = """
                SELECT * FROM VIEW_STOCKALMACEN WHERE IDPRODUCTO = ?
            """
            
            # 4. Ejecutamos la consulta con el parámetro limpio
            cursor.execute(query, [idproducto_limpio])
            
            # 5. Procesamos los resultados
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                results.append(item)
            
            # 6. Respuesta JSON con metadatos útiles
            return JsonResponse({
                'status': 'success',
                'message': f'Stock del producto {idproducto_limpio} obtenido correctamente',
                'producto_consultado': idproducto_limpio,
                'almacenes_encontrados': len(results),
                'data': results
            })
        
        except Exception as e:
            import traceback
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'producto_consultado': idproducto if 'idproducto' in locals() else 'no disponible',
                'traceback': traceback.format_exc()
            }, status=500)
        
        finally:
            if cursor:
                cursor.close()


#================================================================================================================   
# REQUERIMIENTOS INTERNOS - INVERSIONES AJS
#================================================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class SalidaInternaViewAJS(View):
    """
    Vista para manejar las salidas internas de almacén en el sistema Nisira
    Maneja el registro completo: encabezado, detalles y referencias
    """
    
    def post(self, request, *args, **kwargs):
        """
        Crea una nueva salida interna completa siguiendo el flujo del ERP Nisira
        """
        try:
            data = json.loads(request.body)
            cursor = connection_inversioneajs.cursor()
            
            # VERIFICAR ESTADO DE AUTOCOMMIT
            print(f"🔧 Autocommit inicial: {connection_inversioneajs.autocommit}")
            
            # FORZAR AUTOCOMMIT=True para evitar problemas de transacción
            connection_inversioneajs.autocommit = True
            print("🔧 Autocommit forzado a True")
            
            # Validar datos del encabezado
            encabezado = data.get('encabezado', {})
            productos = data.get('productos', [])
            doc_referencia = data.get('documento_referencia', {})
            
            self._validar_datos_encabezado(encabezado)
            
            if not productos:
                return JsonResponse({
                    'success': False,
                    'message': 'Debe incluir al menos un producto'
                })
            
            # PASO 1: OBTENER DATOS DE CABECERA POR DEFECTO (como hace el ERP)
            print("🔄 Paso 1: Obteniendo datos de cabecera por defecto...")
            self._obtener_datos_cabecera_defecto(cursor, encabezado)
            
            # PASO 2: OBTENER SERIES DISPONIBLES (como hace el ERP)
            print("🔄 Paso 2: Obteniendo series disponibles...")
            series_disponibles = self._obtener_series_disponibles(cursor, encabezado)
            
            if not series_disponibles:
                return JsonResponse({
                    'success': False,
                    'message': 'No hay series disponibles para este usuario/documento'
                })
            
            # PASO 3: USAR LA PRIMERA SERIE DISPONIBLE
            serie_usar = series_disponibles[0]
            encabezado['SERIE'] = serie_usar['SERIE']
            print(f"🔄 Paso 3: Usando serie {serie_usar['SERIE']}")
            
            # CON AUTOCOMMIT=True NO NECESITAMOS TRANSACCIONES EXPLÍCITAS
            print("🔄 Procesando con autocommit...")
            
            try:
                # PASO 4: Insertar encabezado
                print("🔄 Paso 4: Insertando encabezado...")
                id_generado = self._insertar_encabezado(cursor, encabezado)
                
                # PASO 5: Insertar detalles de productos
                print("🔄 Paso 5: Insertando detalles...")
                self._insertar_detalles(cursor, id_generado, productos)
                
                # PASO 6: Insertar documento de referencia si existe
                if doc_referencia:
                    print("🔄 Paso 6: Insertando documento referencia...")
                    self._insertar_documento_referencia(cursor, id_generado, doc_referencia)
                
                
                
                # PASO 9: Obtener documento creado ANTES del commit
                print("🔄 Paso 9: Obteniendo documento creado...")
                try:
                    documento_creado = self._obtener_documento_creado(cursor, id_generado)
                    print(f"📋 Documento obtenido: {documento_creado}")
                except Exception as doc_error:
                    print(f"❌ Error al obtener documento: {str(doc_error)}")
                    documento_creado = None
                
                # CON AUTOCOMMIT=True CADA COMANDO YA SE CONFIRMA AUTOMÁTICAMENTE
                print("🔄 Verificando registros en base de datos...")
                
                # VERIFICAR SI EL REGISTRO PERSISTE
                cursor.execute("""
                    SELECT COUNT(*) FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [id_generado, encabezado['IDEMPRESA']])
                result = cursor.fetchone()
                count_final = result[0] if result else 0
                print(f"📈 Registros en BD: {count_final}")
                
                if count_final == 0:
                    print("❌ ADVERTENCIA: El registro no se encontró en la BD")
                else:
                    print("✅ Registro confirmado en base de datos")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Salida interna registrada exitosamente',
                    'data': documento_creado
                })
                
            except Exception as e:
                # CON AUTOCOMMIT=True NO NECESITAMOS ROLLBACK MANUAL
                print(f"❌ Error en procesamiento: {str(e)}")
                raise e
                
        except ValueError as ve:
            return JsonResponse({
                'success': False,
                'message': f'Error de validación: {str(ve)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al registrar salida interna: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    def get(self, request, id=None, *args, **kwargs):
        """
        Obtiene salidas internas - lista o detalle específico
        """
        try:
            cursor = connection_inversioneajs.cursor()
            
            if id:
                # Obtener salida específica con sus detalles
                return self._obtener_salida_detalle(cursor, id)
            else:
                # Obtener lista de salidas con filtros usando procedimiento almacenado
                return self._obtener_lista_salidas(cursor, request)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al consultar salidas: {str(e)}'
            }, status=500)
        finally:
            cursor.close()
    
    # MÉTODOS PRIVADOS AUXILIARES
    
    def _obtener_series_disponibles(self, cursor, encabezado):
        """Obtiene las series disponibles para el usuario usando el procedimiento del ERP"""
        try:
            print(f"🔍 Ejecutando objtablas_returnSeries con parámetros:")
            print(f"   - IDEMPRESA: {encabezado['IDEMPRESA']}")
            print(f"   - IDEMISOR: {encabezado['IDEMISOR']}")
            print(f"   - IDDOCUMENTO: {encabezado['IDDOCUMENTO']}")
            print(f"   - IDUSUARIO: {encabezado['IDUSUARIO']}")
            
            # MÉTODO 1: Intentar con el procedimiento
            try:
                cursor.execute("""
                    EXEC objtablas_returnSeries ?, ?, ?, ?, ?
                """, [
                    encabezado['IDEMPRESA'],    # @C_EMP
                    encabezado['IDEMISOR'],     # @C_EMI  
                    encabezado['IDDOCUMENTO'],  # @C_DOC (SAL)
                    '',                         # @C_TIPOVENTA (vacío para almacén)
                    encabezado['IDUSUARIO']     # @C_USU
                ])
                
                resultados = cursor.fetchall()
                series_disponibles = []
                
                for row in resultados:
                    numero_raw = str(row[1]).strip()  # Eliminar espacios en blanco
                    # Formatear el número con padding si es necesario
                    if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                        numero_formateado = numero_raw
                    else:
                        numero_int = int(numero_raw) if numero_raw else 1
                        numero_formateado = f"{numero_int:07d}"  # 7 dígitos con padding
                    
                    series_disponibles.append({
                        'SERIE': row[0],
                        'NUMERO': numero_formateado
                    })
                
                if series_disponibles:
                    print(f"✅ Series encontradas vía procedimiento: {len(series_disponibles)}")
                    for serie in series_disponibles:
                        print(f"   - Serie: {serie['SERIE']}, Próximo número: {serie['NUMERO']}")
                    return series_disponibles
                    
            except Exception as proc_error:
                print(f"⚠️ Error en procedimiento: {str(proc_error)}")
            
            # MÉTODO 2: Consulta directa a NUMEMISOR como fallback
            print("🔄 Intentando consulta directa a NUMEMISOR...")
            cursor.execute("""
                SELECT SERIE, NUMERO 
                FROM NUMEMISOR 
                WHERE IDEMPRESA = ? 
                AND IDEMISOR = ? 
                AND IDDOCUMENTO = ? 
                AND ESTADO = 1
                ORDER BY SERIE
            """, [
                encabezado['IDEMPRESA'],
                encabezado['IDEMISOR'], 
                encabezado['IDDOCUMENTO']
            ])
            
            resultados = cursor.fetchall()
            series_disponibles = []
            
            for row in resultados:
                numero_raw = str(row[1]).strip()  # Eliminar espacios en blanco
                # Formatear el número con padding si es necesario
                if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                    numero_formateado = numero_raw
                else:
                    numero_int = int(numero_raw) if numero_raw else 1
                    numero_formateado = f"{numero_int:07d}"  # 7 dígitos con padding
                
                series_disponibles.append({
                    'SERIE': row[0],
                    'NUMERO': numero_formateado
                })
            
            print(f"📋 Series disponibles encontradas (consulta directa): {len(series_disponibles)}")
            for serie in series_disponibles:
                print(f"   - Serie: {serie['SERIE']}, Próximo número: {serie['NUMERO']}")
            
            return series_disponibles
            
        except Exception as e:
            print(f"❌ Error al obtener series: {str(e)}")
            return []
    
    def _obtener_datos_cabecera_defecto(self, cursor, encabezado):
        """Obtiene datos por defecto de cabecera como hace el ERP"""
        try:
            # Construir XML similar al del ERP (simplificado)
            xml_data = f"""<?xml version = "1.0" encoding="Windows-1252" standalone="yes"?>
            <VFPData>
                <torigen>
                    <ctabla>emisor</ctabla>
                    <cid>{encabezado['IDEMISOR']}</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdemisor</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>operaciones</ctabla>
                    <cid>SALM</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdoperacion</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>estados</ctabla>
                    <cid>PE</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>txtdestado</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>monedas</ctabla>
                    <cid>{encabezado['IDMONEDA']}</cid>
                    <cpropiedad>descripcion</cpropiedad>
                    <ccontenedor>cntmoneda.txtdescripcion</ccontenedor>
                </torigen>
                <torigen>
                    <ctabla>responsable</ctabla>
                    <cid>{encabezado['IDRESPONSABLE']}</cid>
                    <cpropiedad>nombre</cpropiedad>
                    <ccontenedor>cntresponsable.txtdescripcion</ccontenedor>
                </torigen>
            </VFPData>"""
            
            cursor.execute("""
                EXEC GETRECORD_DATOSCABECERA_SALIDASINTERNAS ?, ?
            """, [encabezado['IDEMPRESA'], xml_data])
            
            # El procedimiento puede devolver datos, pero por ahora solo lo ejecutamos
            print("✅ Datos de cabecera por defecto obtenidos")
            return True
            
        except Exception as e:
            print(f"⚠️ Advertencia al obtener datos cabecera defecto: {str(e)}")
            return False
    
    def _generar_idingresosalidaalm(self, cursor, encabezado):
        """Genera el IDINGRESOSALIDAALM usando DPARAMS como hace el ERP"""
        try:
            # Obtener el siguiente ID desde DPARAMS
            cursor.execute("""
                SELECT id FROM DPARAMS 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = '_'
            """, [encabezado['IDEMPRESA']])
            
            resultado = cursor.fetchone()
            if resultado:
                siguiente_id = resultado[0]
            else:
                siguiente_id = 39860  # Valor base observado en los ejemplos
                
            # Generar ID con formato observado: _76F0TDC7939860
            # Formato: _[3chars][1digit][4chars][6digits]
            import random, string
            parte1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))  # 76F
            parte2 = random.choice(string.digits)  # 0
            parte3 = ''.join(random.choices(string.ascii_uppercase, k=4))  # TDCR
            parte4 = f"{siguiente_id}"  # 39860
            
            id_generado = f"_{parte1}{parte2}{parte3}{parte4}"
            
            print(f"🔢 ID generado: {id_generado}")
            return id_generado
            
        except Exception as e:
            # Fallback: generar ID aleatorio con formato correcto
            import random, string
            parte1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            parte2 = random.choice(string.digits)
            parte3 = ''.join(random.choices(string.ascii_uppercase, k=4))
            parte4 = f"{random.randint(39860, 99999)}"
            
            id_generado = f"_{parte1}{parte2}{parte3}{parte4}"
            print(f"⚠️ Error en DPARAMS, usando ID aleatorio: {id_generado}")
            return id_generado
    


    def _generar_numoperacion(self, cursor, encabezado):
        """
        Genera el NUMOPERACION con lógica mensual simplificada:
        - Nuevo mes = 0000000001
        - Mismo mes = siguiente número
        """
        try:
            # Obtener datos básicos
            periodo_actual = encabezado.get('PERIODO')
            idempresa = encabezado.get('IDEMPRESA', '001')
            
            if not periodo_actual:
                from datetime import datetime
                fecha_actual = datetime.now()
                periodo_actual = f"{fecha_actual.year}{fecha_actual.month:02d}"
            
            # Buscar el último NUMOPERACION del mes actual
            cursor.execute("""
                SELECT MAX(CAST(NUMOPERACION AS INTEGER)) 
                FROM INGRESOSALIDAALM 
                WHERE IDEMPRESA = ? AND PERIODO = ?
                AND NUMOPERACION IS NOT NULL AND NUMOPERACION != ''
            """, [idempresa, periodo_actual])
            
            resultado = cursor.fetchone()
            ultimo_numero = resultado[0] if resultado and resultado[0] else 0
            
            # Generar siguiente número
            siguiente_numero = ultimo_numero + 1
            numoperacion_generado = f"{siguiente_numero:010d}"
            
            # Log simple
            if ultimo_numero == 0:
                print(f"🆕 Nuevo mes {periodo_actual}: {numoperacion_generado}")
            else:
                print(f"📈 Mes {periodo_actual}: {ultimo_numero} → {numoperacion_generado}")
            
            return numoperacion_generado
            
        except Exception as e:
            # Fallback simple: número aleatorio con formato correcto
            import random
            numero_emergencia = random.randint(1, 999999)
            fallback = f"{numero_emergencia:010d}"
            print(f"❌ Error: {str(e)} | Usando: {fallback}")
            return fallback    


    
    def _obtener_siguiente_numero(self, cursor, encabezado, serie):
        """Obtiene el siguiente número para la serie"""
        try:
            # Ya tenemos el número desde _obtener_series_disponibles
            cursor.execute("""
                SELECT NUMERO FROM NUMEMISOR 
                WHERE IDEMPRESA = ? AND IDEMISOR = ? AND IDDOCUMENTO = ? AND SERIE = ?
            """, [encabezado['IDEMPRESA'], encabezado['IDEMISOR'], encabezado['IDDOCUMENTO'], serie])
            
            resultado = cursor.fetchone()
            if resultado:
                numero_raw = str(resultado[0]).strip()  # Eliminar espacios en blanco
                # Si el número es una cadena y ya tiene formato, usarlo tal cual
                if len(numero_raw) >= 7 and numero_raw.startswith('0'):
                    numero_formateado = numero_raw
                    print(f"📝 Número ya formateado: {numero_formateado}")
                else:
                    # Si es número entero o cadena corta, formatear con padding de ceros
                    numero_int = int(numero_raw) if numero_raw else 1
                    numero_formateado = f"{numero_int:07d}"  # Formato: 0061752 (7 dígitos)
                    print(f"📝 Número formateado: {numero_formateado}")
                
                print(f"🔢 Número obtenido: {numero_formateado}")
                return numero_formateado
            else:
                print("⚠️ No se encontró número en NUMEMISOR, usando 0000001")
                return "0000001"
                
        except Exception as e:
            print(f"⚠️ Error obteniendo número: {str(e)}")
            return "0000001"
    
    def _actualizar_dparams(self, cursor, encabezado, id_usado, numoperacion_usado):
        """Actualiza DPARAMS con los valores usados"""
        try:
            # Actualizar contador de IDINGRESOSALIDAALM
            cursor.execute("""
                UPDATE DPARAMS SET id = id + 1 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = '_'
            """, [encabezado['IDEMPRESA']])
            
            # Actualizar contador de NUMOPERACION
            cursor.execute("""
                UPDATE DPARAMS SET id = id + 1 
                WHERE idempresa = ? AND idtabla = 'INGRESOSALIDAALM' AND prefijo = 'SALM'
            """, [encabezado['IDEMPRESA']])
            
            # Actualizar NUMEMISOR con formato de 7 dígitos
            cursor.execute("""
                UPDATE NUMEMISOR 
                SET NUMERO = RIGHT('0000000' + CAST((CAST(NUMERO AS INT) + 1) AS VARCHAR), 7)
                WHERE IDEMPRESA = ? AND IDEMISOR = ? AND IDDOCUMENTO = ? AND SERIE = ?
            """, [encabezado['IDEMPRESA'], encabezado['IDEMISOR'], encabezado['IDDOCUMENTO'], encabezado['SERIE']])
            
            print("✅ DPARAMS y NUMEMISOR actualizados")
            
        except Exception as e:
            print(f"⚠️ Error actualizando contadores: {str(e)}")

    def _validar_datos_encabezado(self, encabezado):
        """Valida que los datos del encabezado sean correctos"""
        campos_requeridos = [
            'IDEMPRESA', 'IDEMISOR', 'PERIODO', 'IDALMACEN', 
            'IDDOCUMENTO', 'FECHA', 'IDRESPONSABLE', 
            'GLOSA', 'IDMONEDA', 'TCAMBIO', 'IDSUCURSAL', 'IDUSUARIO'
        ]
        
        for campo in campos_requeridos:
            if campo not in encabezado or not encabezado[campo]:
                raise ValueError(f'El campo {campo} es requerido')
    



    
    def _insertar_encabezado(self, cursor, encabezado):
        """Inserta el encabezado en INGRESOSALIDAALM generando previamente los valores como hace el ERP"""
        
        # PASO 1: GENERAR IDINGRESOSALIDAALM usando DPARAMS
        idingresosalidaalm_generado = self._generar_idingresosalidaalm(cursor, encabezado)
        
        # PASO 2: GENERAR NUMOPERACION usando DPARAMS  
        numoperacion_generado = self._generar_numoperacion(cursor, encabezado)
        
        # PASO 3: OBTENER SERIE Y NÚMERO (ya tenemos desde _obtener_series_disponibles)
        serie_usar = encabezado['SERIE']
        numero_usar = self._obtener_siguiente_numero(cursor, encabezado, serie_usar)
        
        # PASO 4: INSERTAR CON TODOS LOS CAMPOS OBLIGATORIOS Y VALORES POR DEFECTO
        sql = """
        INSERT INTO INGRESOSALIDAALM (
            IDEMPRESA, IDINGRESOSALIDAALM, IDEMISOR, PERIODO, IDOPERACION, 
            NUMOPERACION, IDSUBDIARIO, VOUCHER, IDALMACEN, IDDOCUMENTO, SERIE, NUMERO, FECHA,
            IDRESPONSABLE, GLOSA, IDMONEDA, TCAMBIO, TCMONEDA, IDMOTIVO,
            IDALMACEND, FECHADOCORIGEN, SINCRONIZA, IDESTADO, FECHACREACION, 
            CONTABILIZADO, IDSUCURSALD, IDSUCURSAL, VENTANA, IDPARTEPRODUCCION, 
            TOTAL, IDUSUARIO, IDCONSUMIDOR, IMPRESO, IMPORTADO, ES_COSTOS,
            pesodocorigen3, IDREGISTROVAR, AREA_HA, IMPORTADO_EXTERNO, automatico_asociaop,
            numversion, PTOPARTIDA, MOTIVO_TRASLADO, transferir_comprometido, idviaje,
            dni, precio_generado, IDCHOFER, CMA30EQPID_CAMION, CMA30EQPID_CARRETA,
            IDRUTA, IDLUGAR_O, IDLUGAR_D, ITEM_RUTA, fecha_syncro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """
        
        parametros = [
            encabezado['IDEMPRESA'],                    # 1. IDEMPRESA
            idingresosalidaalm_generado,                # 2. IDINGRESOSALIDAALM (GENERADO)
            encabezado['IDEMISOR'],                     # 3. IDEMISOR  
            encabezado['PERIODO'],                      # 4. PERIODO
            'SALM',                                     # 5. IDOPERACION (Salidas Almacén)
            numoperacion_generado,                      # 6. NUMOPERACION (GENERADO)
            '004',                                      # 7. IDSUBDIARIO (OBLIGATORIO para salidas)
            numoperacion_generado,                      # 8. VOUCHER (mismo que NUMOPERACION)
            encabezado['IDALMACEN'],                    # 9. IDALMACEN
            encabezado['IDDOCUMENTO'],                  # 10. IDDOCUMENTO (SAL)
            serie_usar,                                 # 11. SERIE (GENERADA)
            numero_usar,                                # 12. NUMERO (GENERADO)
            encabezado['FECHA'],                        # 13. FECHA
            encabezado['IDRESPONSABLE'],                # 14. IDRESPONSABLE
            encabezado['GLOSA'],                        # 15. GLOSA
            encabezado['IDMONEDA'],                     # 16. IDMONEDA
            encabezado['TCAMBIO'],                      # 17. TCAMBIO
            encabezado.get('TCMONEDA', 1.000000),       # 18. TCMONEDA
            encabezado['IDMOTIVO'],                     # 19. IDMOTIVO
            encabezado.get('IDALMACEND'),               # 20. IDALMACEND (puede ser NULL)
            encabezado.get('FECHADOCORIGEN', encabezado['FECHA']),  # 21. FECHADOCORIGEN
            encabezado.get('SINCRONIZA', 'N'),          # 22. SINCRONIZA
            encabezado.get('IDESTADO', 'PE'),           # 23. IDESTADO (Pendiente)
            # 24. FECHACREACION = GETDATE() - no parámetro
            encabezado.get('CONTABILIZADO', 0),         # 24. CONTABILIZADO
            encabezado.get('IDSUCURSALD'),              # 25. IDSUCURSALD (puede ser NULL)
            encabezado['IDSUCURSAL'],                   # 26. IDSUCURSAL
            encabezado.get('VENTANA', 'EDT_SALIDAS'),   # 27. VENTANA
            encabezado.get('IDPARTEPRODUCCION'),        # 28. IDPARTEPRODUCCION (puede ser NULL)
            0.0000,                                     # 29. TOTAL (OBLIGATORIO, inicia en 0)
            encabezado['IDUSUARIO'],                    # 30. IDUSUARIO
            '',                                         # 31. IDCONSUMIDOR (DEFAULT '')
            0,                                          # 32. IMPRESO (DEFAULT 0)
            0,                                          # 33. IMPORTADO (DEFAULT 0)
            0,                                          # 34. ES_COSTOS (DEFAULT 0)
            0,                                          # 35. pesodocorigen3 (DEFAULT 0)
            0,                                          # 36. IDREGISTROVAR (DEFAULT 0)
            0,                                          # 37. AREA_HA (DEFAULT 0)
            0,                                          # 38. IMPORTADO_EXTERNO (DEFAULT 0)
            0,                                          # 39. automatico_asociaop (DEFAULT 0)
            0,                                          # 40. numversion (DEFAULT 0)
            '',                                         # 41. PTOPARTIDA (DEFAULT '')
            '',                                         # 42. MOTIVO_TRASLADO (DEFAULT '')
            0,                                          # 43. transferir_comprometido (DEFAULT 0)
            '',                                         # 44. idviaje (DEFAULT '')
            '',                                         # 45. dni (DEFAULT '')
            0,                                          # 46. precio_generado (DEFAULT 0)
            '',                                         # 47. IDCHOFER (DEFAULT '')
            '',                                         # 48. CMA30EQPID_CAMION (DEFAULT '')
            '',                                         # 49. CMA30EQPID_CARRETA (DEFAULT '')
            '',                                         # 50. IDRUTA (DEFAULT '')
            '',                                         # 51. IDLUGAR_O (DEFAULT '')
            '',                                         # 52. IDLUGAR_D (DEFAULT '')
            ''                                          # 53. ITEM_RUTA (DEFAULT '')
            # fecha_syncro = GETDATE() - no parámetro
        ]
        
        print(f"📝 Insertando registro con valores generados:")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm_generado}")
        print(f"   - NUMOPERACION: {numoperacion_generado}")  
        print(f"   - SERIE: {serie_usar}")
        print(f"   - NUMERO: {numero_usar}")
        
        try:
            print(f"🔄 Ejecutando INSERT en INGRESOSALIDAALM...")
            print(f"📊 Total de parámetros: {len(parametros)}")
            cursor.execute(sql, parametros)
            print(f"✅ INSERT ejecutado exitosamente")
            
            # Verificar que se insertó
            cursor.execute("SELECT @@ROWCOUNT")
            rows_affected = cursor.fetchone()[0]
            print(f"📈 Filas afectadas: {rows_affected}")
            
            if rows_affected == 0:
                print("❌ ADVERTENCIA: No se insertaron filas")
            
        except Exception as insert_error:
            print(f"❌ ERROR en INSERT: {str(insert_error)}")
            raise insert_error
        
        # ACTUALIZAR DPARAMS con los nuevos valores usados
        try:
            print(f"🔄 Actualizando DPARAMS...")
            self._actualizar_dparams(cursor, encabezado, idingresosalidaalm_generado, numoperacion_generado)
            print(f"✅ DPARAMS actualizado")
        except Exception as dparams_error:
            print(f"❌ ERROR en DPARAMS: {str(dparams_error)}")
            raise dparams_error
        
        print(f"✅ Encabezado creado: ID={idingresosalidaalm_generado}, Serie={serie_usar}, Número={numero_usar}")
        
        return idingresosalidaalm_generado



    def _insertar_detalles(self, cursor, idingresosalidaalm, productos):
        """Inserta los detalles de productos en DINGRESOSALIDAALM"""
        
        # VERIFICAR QUE NO EXISTAN DETALLES PREVIAMENTE
        cursor.execute("""
            SELECT COUNT(*) FROM DINGRESOSALIDAALM 
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Advertencia: Ya existen {count} detalles para {idingresosalidaalm}")
            # Eliminar detalles existentes
            cursor.execute("""
                DELETE FROM DINGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ?
            """, [idingresosalidaalm])
        
        sql = """
        INSERT INTO DINGRESOSALIDAALM (
            IDEMPRESA, IDINGRESOSALIDAALM, ITEM, IDPRODUCTO, DESCRIPCION,
            IDSERIE, IDLOTEP, IDMEDIDA, IDESTADOPRODUCTO, IDPROYECTO,
            IDACTIVIDAD, IDLABOR, IDCONSUMIDOR, TCAMBIO, COMPROMETIDO,
            IDEMPAQUE, CANTEMPAQUE, CANTIDAD, AREA, NUMPALETA, PRECIO,
            IMPORTE, IDREFERENCIA, ITEMREF, TABLAREF, PRECIOMOF,
            PRECIOMEX, IMPORTEMOF, IMPORTEMEX, IDPARTIDAPSTAL,
            CODINTERNO, CODIGOBARRA, IDUBICACION, LOTEORIGEN,
            PRODUCTOORIGEN, OBSERVACIONES, IDFALLA, IDPRODUCTOPROCESO,
            IDMOVCOMPROMETIDO, MERMA, FACTORINSUMO, CANTINSUMO,
            CANTIPRODUCIDA, IDSIEMBRA, IDCAMPANA, IDORDENPRODUCCION,
            IDLOTEPRODUCCION, DOCORDENPRODUCCION, VOLUMEN, IDACTIVO,
            IDCULTIVO, IDPRODUCTODESTINO, DSC_PRODUCTODESTINO, IDMEDIDA2,
            CANTIDAD2, idvehiculo, docreqinterno, idreqinterno,
            ITEMREF_ORDENPRODUCCION, placa, kilometraje, chofer,
            NRO_VALE, SEMANA, DOSISLOTE, estructura, itemreqinterno,
            DSC_DOCVENTA, IDDOC_VENTA, idchofer, cMA30EqpID,
            NROENVASES, idinvernadero, idnave, idcampanainvernadero, horometro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for i, producto in enumerate(productos, 1):
            # GENERAR ITEM ÚNICO
            item_numero = f"{i:03d}"
            
            try:
                parametros = [
                    producto.get('IDEMPRESA'),
                    idingresosalidaalm,
                    item_numero,  # ITEM con formato 001, 002, etc.
                    producto.get('IDPRODUCTO'),
                    producto.get('DESCRIPCION'),
                    producto.get('IDSERIE'),
                    producto.get('IDLOTEP'),
                    producto.get('IDMEDIDA'),
                    producto.get('IDESTADOPRODUCTO', '0'),
                    producto.get('IDPROYECTO'),
                    producto.get('IDACTIVIDAD'),
                    producto.get('IDLABOR'),
                    producto.get('IDCONSUMIDOR'),
                    producto.get('TCAMBIO'),
                    producto.get('COMPROMETIDO', 1),
                    producto.get('IDEMPAQUE'),
                    producto.get('CANTEMPAQUE', 0),
                    producto.get('CANTIDAD'),
                    producto.get('AREA'),
                    producto.get('NUMPALETA'),
                    producto.get('PRECIO', 0),
                    producto.get('IMPORTE', 0),
                    producto.get('IDREFERENCIA'),
                    producto.get('ITEMREF'),
                    producto.get('TABLAREF'),
                    producto.get('PRECIOMOF', 0),
                    producto.get('PRECIOMEX', 0),
                    producto.get('IMPORTEMOF', 0),
                    producto.get('IMPORTEMEX', 0),
                    producto.get('IDPARTIDAPSTAL'),
                    producto.get('CODINTERNO'),
                    producto.get('CODIGOBARRA'),
                    producto.get('IDUBICACION'),
                    producto.get('LOTEORIGEN'),
                    producto.get('PRODUCTOORIGEN'),
                    producto.get('OBSERVACIONES'),
                    producto.get('IDFALLA'),
                    producto.get('IDPRODUCTOPROCESO'),
                    producto.get('IDMOVCOMPROMETIDO'),
                    producto.get('MERMA', 0),
                    producto.get('FACTORINSUMO', 0),
                    producto.get('CANTINSUMO', 0),
                    producto.get('CANTIPRODUCIDA', 0),
                    producto.get('IDSIEMBRA'),
                    producto.get('IDCAMPANA'),
                    producto.get('IDORDENPRODUCCION'),
                    producto.get('IDLOTEPRODUCCION'),
                    producto.get('DOCORDENPRODUCCION'),
                    producto.get('VOLUMEN'),
                    producto.get('IDACTIVO'),
                    producto.get('IDCULTIVO'),
                    producto.get('IDPRODUCTODESTINO'),
                    producto.get('DSC_PRODUCTODESTINO'),
                    producto.get('IDMEDIDA2'),
                    producto.get('CANTIDAD2', 0),
                    producto.get('idvehiculo'),
                    producto.get('docreqinterno'),
                    producto.get('idreqinterno'),
                    producto.get('ITEMREF_ORDENPRODUCCION'),
                    producto.get('placa'),
                    producto.get('kilometraje'),
                    producto.get('chofer'),
                    producto.get('NRO_VALE'),
                    producto.get('SEMANA'),
                    producto.get('DOSISLOTE'),
                    producto.get('estructura'),
                    producto.get('itemreqinterno'),
                    producto.get('DSC_DOCVENTA'),
                    producto.get('IDDOC_VENTA'),
                    producto.get('idchofer'),
                    producto.get('cMA30EqpID'),
                    producto.get('NROENVASES', 0),
                    producto.get('idinvernadero'),
                    producto.get('idnave'),
                    producto.get('idcampanainvernadero'),
                    producto.get('horometro', 0)
                ]
                
                cursor.execute(sql, parametros)
                print(f"Detalle insertado: ITEM {item_numero} - Producto {producto.get('IDPRODUCTO')}")
                
            except Exception as e:
                print(f"Error insertando item {item_numero}: {str(e)}")
                raise e


    


    def _insertar_documento_referencia(self, cursor, idingresosalidaalm, doc_referencia):
        """Inserta la referencia al documento origen en DOCREFERENCIA"""
        sql = """
        INSERT INTO DOCREFERENCIA (
            IDEMPRESA, IDORIGEN, TABLA, IDREFERENCIA,
            IDDOCUMENTO, SERIE, NUMERO, FECHA
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        parametros = [
            doc_referencia['IDEMPRESA'],
            idingresosalidaalm,
            doc_referencia.get('TABLA', 'REQINTERNO'),
            doc_referencia['IDREFERENCIA'],
            doc_referencia['IDDOCUMENTO'],
            doc_referencia['SERIE'],
            doc_referencia['NUMERO'],
            doc_referencia['FECHA']
        ]
        
        cursor.execute(sql, parametros)
    
    
    
    
    
    
    def _obtener_documento_creado(self, cursor, idingresosalidaalm):
        """Obtiene los datos del documento recién creado"""
        print(f"🔍 Buscando documento con ID: {idingresosalidaalm}")
        
        try:
            # Usar consulta con NOLOCK para leer datos no confirmados en la misma transacción
            cursor.execute("""
                SELECT IDINGRESOSALIDAALM, SERIE, NUMERO, FECHA, GLOSA, IDESTADO
                FROM INGRESOSALIDAALM WITH (NOLOCK)
                WHERE IDINGRESOSALIDAALM = ?
            """, [idingresosalidaalm])
            
            row = cursor.fetchone()
            print(f"🔍 Resultado de consulta: {row}")
            
            if row:
                documento = {
                    'idingresosalidaalm': row[0],
                    'serie': row[1],
                    'numero': row[2],
                    'fecha': row[3].strftime('%Y-%m-%d') if row[3] else None,
                    'glosa': row[4],
                    'estado': row[5]
                }
                print(f"✅ Documento encontrado: {documento}")
                return documento
            else:
                print("❌ No se encontró el documento con NOLOCK")
                
                # Intentar sin NOLOCK como fallback
                cursor.execute("""
                    SELECT IDINGRESOSALIDAALM, SERIE, NUMERO, FECHA, GLOSA, IDESTADO
                    FROM INGRESOSALIDAALM
                    WHERE IDINGRESOSALIDAALM = ?
                """, [idingresosalidaalm])
                
                row = cursor.fetchone()
                print(f"🔍 Resultado sin NOLOCK: {row}")
                
                if row:
                    documento = {
                        'idingresosalidaalm': row[0],
                        'serie': row[1],
                        'numero': row[2],
                        'fecha': row[3].strftime('%Y-%m-%d') if row[3] else None,
                        'glosa': row[4],
                        'estado': row[5]
                    }
                    print(f"✅ Documento encontrado sin NOLOCK: {documento}")
                    return documento
                else:
                    print("❌ No se encontró el documento en ninguna consulta")
                    return None
                    
        except Exception as e:
            print(f"❌ Error en consulta: {str(e)}")
            return None
    
    
    def _obtener_salida_detalle(self, cursor, idingresosalidaalm):
        """
        Obtiene el detalle completo de una salida específica usando consultas directas
        """
        try:
            # Consulta principal para obtener el encabezado de la salida interna
            cursor.execute("""
                SELECT * FROM INGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = '001'
            """, [idingresosalidaalm])
            
            encabezado_rows = cursor.fetchall()
            if not encabezado_rows:
                return JsonResponse({
                    'success': False,
                    'message': 'Salida interna no encontrada'
                }, status=404)
        
            # Convertir encabezado a diccionario
            encabezado_columns = [col[0] for col in cursor.description]
            encabezado_dict = dict(zip(encabezado_columns, encabezado_rows[0]))
            
            # Procesar fechas en el encabezado
            fecha_fields = ['FECHA', 'FECHACREACION', 'FECHADOCORIGEN', 'FECHATRASLADO', 'FECHADOCORIGEN2', 'FECHADOCORIGEN3', 'FECHACOSECHA', 'FECHAEXPIRACION', 'FECHA1', 'FECHA2']
            for field in fecha_fields:
                if field in encabezado_dict and encabezado_dict[field] is not None:
                    if hasattr(encabezado_dict[field], 'strftime'):
                        encabezado_dict[field] = encabezado_dict[field].strftime('%Y-%m-%d %H:%M:%S')
            
            # Obtener los detalles de la salida interna
            cursor.execute("""
                SELECT d.*, p.DESCRIPCION as DESCRIPCION_PRODUCTO
                FROM DINGRESOSALIDAALM d
                LEFT JOIN PRODUCTOS p ON d.IDPRODUCTO = p.IDPRODUCTO AND d.IDEMPRESA = p.IDEMPRESA
                WHERE d.IDINGRESOSALIDAALM = ? AND d.IDEMPRESA = '001'
                ORDER BY d.ITEM
            """, [idingresosalidaalm])
            
            detalles_rows = cursor.fetchall()
            detalles_columns = [col[0] for col in cursor.description]
            
            # Convertir detalles a lista de diccionarios
            detalles_list = []
            for detalle_row in detalles_rows:
                detalle_dict = dict(zip(detalles_columns, detalle_row))
                
                # Procesar fechas en los detalles
                fecha_fields_detalle = ['FECHA', 'VENCEPRODU', 'FECHA_SALIDA', 'FECHAETIQUETA', 'fecha_produccion', 'fecha_d']
                for field in fecha_fields_detalle:
                    if field in detalle_dict and detalle_dict[field] is not None:
                        if hasattr(detalle_dict[field], 'strftime'):
                            detalle_dict[field] = detalle_dict[field].strftime('%Y-%m-%d %H:%M:%S')
                
                # Procesar campos numéricos para evitar problemas de serialización
                numeric_fields = [
                    'TCAMBIO', 'COMPROMETIDO', 'CANTEMPAQUE', 'TARA', 'CANTBRUTA', 'CANTREMITIDA', 
                    'CANTREFERENCIAL', 'LIQUIDADO', 'DEVUELTO', 'DESCUENTO_I', 'DESCUENTO', 'ARANCEL',
                    'PESO', 'CANTIDAD', 'AREA', 'COSTODESCUENTO', 'DISTRIBUCION', 'REVISADO', 
                    'DESPACHADO', 'PRECIO', 'IMPORTE', 'VVENTA', 'IMPUESTO', 'IMPUESTO_I', 
                    'PRECIOMOF', 'PRECIOMEX', 'IMPORTEMOF', 'IMPORTEMEX', 'KGSELECCION', 'KGDEVOLUCION',
                    'KGPELADOS', 'KGTROZO', 'KGPELADILLA', 'TOTALCORTADO', 'RENDPELADO', 'KGENVASADO',
                    'KGDRENADOS', 'RENDENVASADO', 'MERMA', 'FACTORINSUMO', 'CANTINSUMO', 'CANTIPRODUCIDA',
                    'FACTURABLE', 'VOLUMEN', 'PRECIOVENTA', 'TARA2', 'CANTIDAD2', 'con_insumos',
                    'muestrabotonveh', 'liberado', 'BRUTO', 'NETO', 'JABAS', 'REB_A', 'CST_RECURSIVO',
                    'ALM_CAB', 'kilometraje', 'automatico_asociaop', 'GRATUITO', 'DOSISLOTE',
                    'por_oc_importado', 'con_certificacion', 'CANTEMPAQUE2', 'PESOPROMEDIO', 
                    'taraxempaque', 'Cant_Recibida', 'CANTIDAD_HISTORICO', 'preciofactura', 
                    'vventafactura', 'importefactura', 'impuestofac', 'NROENVASES', 'PESO_HISTORICO',
                    'ES_DRAWBACK', 'AUTOMATICO', 'dosis_tanque', 'nrotanque', 'horometro', 
                    'SOPLETEADO', 'cantidad_d', 'TCMONEDA'
                ]
                
                for field in numeric_fields:
                    if field in detalle_dict:
                        try:
                            if detalle_dict[field] is not None:
                                detalle_dict[field] = float(detalle_dict[field])
                            else:
                                detalle_dict[field] = 0.0
                        except (ValueError, TypeError):
                            detalle_dict[field] = 0.0
                
                # Procesar campos de texto para limpiar espacios
                text_fields = [
                    'IDPRODUCTO', 'DESCRIPCION', 'DESCRIPCION_PRODUCTO', 'IDKIT', 'IDSERIE', 
                    'IDLOTEP', 'IDMEDIDA', 'IDESTADOPRODUCTO', 'IDPROYECTO', 'IDACTIVIDAD', 
                    'IDLABOR', 'IDCONSUMIDOR', 'IDCAMPANA_P', 'IDCONSUMIDORO', 'IDDOCUMENTO',
                    'SERIE', 'NUMERO', 'IDEMPAQUE', 'NUMPALETA', 'IDREFERENCIA', 'ITEMREF',
                    'TABLAREF', 'IDPARTIDAPSTAL', 'JULRECEPCION', 'JULCOSECHA', 'DESCCALIBRE',
                    'FORMATO', 'CODFABRICA', 'CODINTERNO', 'CODIGOBARRA', 'IDUBICACION',
                    'IDPROCESO', 'IDSUBPROCESO', 'LOTEORIGEN', 'PRODUCTOORIGEN', 'OBSERVACIONES',
                    'HORA', 'NROVIAJE', 'OBSERVACION', 'IDFALLA', 'IDPRODUCTOPROCESO', 
                    'IDMOVCOMPROMETIDO', 'DUA', 'SERIEDUA', 'IDDEVOLUCION', 'ITEMDEVO',
                    'IDSIEMBRA', 'IDCAMPANA', 'IDORDENPRODUCCION', 'IDLOTEPRODUCCION', 
                    'DOCORDENPRODUCCION', 'DOCLOTEPRODUCCION', 'IDMEDIDAEQ', 'IDUNIDADCOSTO',
                    'IDUNIDADNEGOCIO', 'IDACTIVO', 'IDCULTIVO', 'IDVARIEDAD', 'IDTIPOCOSECHA',
                    'IDCABEZAL', 'IDPRODUCTODESTINO', 'DSC_PRODUCTODESTINO', 'IDMEDIDA2', 'DM',
                    'IDCAMARA', 'idvehiculo', 'anio', 'idcolor', 'IDORDENMANTENIMIENTO',
                    'DOCORDENMANTENIMIENTO', 'docreqinterno', 'idreqinterno', 'ITEMREF_ORDENPRODUCCION',
                    'IDTALLA', 'IDENVASE', 'IDCONDICION', 'IDPRESENTACION', 'DSC_CULTIVO',
                    'DSC_VARIEDAD', 'DSC_COLOR', 'DSC_TALLA', 'DSC_ENVASE', 'DSC_CONDICION',
                    'DSC_PRESENTACION', 'IDREFERENCIA2', 'ITEMREF2', 'TABLAREF2', 'IDACTIVO_AVICOLA',
                    'placa', 'chofer', 'NRO_VALE', 'ITEM1', 'IDUBICACIONA', 'SEMANA',
                    'IDTIPOAFECTACION', 'estructura', 'itemreqinterno', 'dato1', 'idestadoc',
                    'DSC_DOCVENTA', 'IDDOC_VENTA', 'idlotep_o', 'idempaque2', 'IDCUENTA',
                    'idchofer', 'cMA30EqpID', 'IDRECOLECCION', 'IDTURNORIE', 'zonificacion',
                    'idproductod', 'descripciond', 'idconsumidord', 'idlotepd', 'IDUBICACIOND',
                    'ccalidad', 'idccalidad', 'idproductor', 'idarea', 'idresponsable',
                    'idinvernadero', 'idnave', 'idcampanainvernadero', 'IDESTADO', 'idembarcacion',
                    'LDP', 'item_d'
                ]
                
                for field in text_fields:
                    if field in detalle_dict and detalle_dict[field] is not None:
                        detalle_dict[field] = str(detalle_dict[field]).strip()
                    elif field in detalle_dict:
                        detalle_dict[field] = ''
                
                detalles_list.append(detalle_dict)
            
            # Calcular totales
            totales_dict = {
                'TOTAL_CANTIDAD': sum(float(d.get('CANTIDAD', 0) or 0) for d in detalles_list),
                'TOTAL_PESO': sum(float(d.get('PESO', 0) or 0) for d in detalles_list),
                'TOTAL_IMPORTE': sum(float(d.get('IMPORTE', 0) or 0) for d in detalles_list),
                'TotalDetalles': len(detalles_list)
            }
            
            # Procesar campos de texto en encabezado para limpiar espacios
            text_fields_encabezado = [
                'IDEMPRESA', 'IDINGRESOSALIDAALM', 'IDEMISOR', 'PERIODO', 'IDOPERACION', 
                'NUMOPERACION', 'IDSUBDIARIO', 'VOUCHER', 'IDALMACEN', 'IDDOCUMENTO', 
                'SERIE', 'NUMERO', 'IDCLIEPROV', 'IDPROYECTO', 'IDRESPONSABLE', 'GLOSA',
                'IDMONEDA', 'IDMOTIVO', 'IDALMACEND', 'IDDOCORIGEN', 'SERIEDOCORIGEN',
                'NUMDOCORIGEN', 'IDFLETE', 'IDTRANSPORTISTA', 'CERTIFTRANSPORTE', 
                'CERTIFTRANSPORTE1', 'PLACA', 'PLACA1', 'MARCA', 'MARCA1', 'CHOFER',
                'BREVETE', 'LLEVADOPOR', 'DIRECLLEGADA', 'SINCRONIZA', 'IDESTADO',
                'IDCONTABILIZADO', 'IDCONSUMIDOR', 'IDLINEAPRODUC', 'IDLOTE', 'IDSUCURSALD',
                'IDDOCORIGEN2', 'SERIEDOCORIGEN2', 'NUMDOCORIGEN2', 'IDSUCURSAL', 'VENTANA',
                'OCCLIENTE', 'OTRADIRECCION', 'HORA', 'IDMONEDA_FLETE', 'IDCONTROLADOR',
                'IDCLIEPROVDEST', 'IDCOMPRA', 'IDUBIGEOLLEGADA', 'IDDOCORIGEN3', 'SERIEDOCORIGEN3',
                'NUMDOCORIGEN3', 'IDUNIDADNEGOCIO', 'IDCNFDISTRIBUCION', 'IDTURNOTRABAJO',
                'IDPRODUCTO', 'IDREFERENCIAPROCESO', 'IDPROCESO', 'IDSUBPROCESO', 'NRO_PRECINTO',
                'IDPARTEPRODUCCION', 'IDSUBUNIDADNEGOCIO', 'itemptollegada', 'IDCLIEPROV2',
                'Idtipoenvioremision', 'IDREFERENCIA_EXTERNO', 'IDTIPOPRECINTO', 'IDAGRICULTOR',
                'IDSOLICITANTE', 'DESTINO', 'IDPTGENERADO', 'IDSALIDAMP', 'LINEA_EMBARQUE',
                'NRO_CONTENEDOR', 'NRO_DER', 'NRO_INSTRUCCION', 'NRO_PEDIDO', 'idcamara',
                'NROEMBARQUE', 'IDPACKINGLIST', 'IDUSUARIO1', 'IDUSUARIO2', 'IDREFERENCIA1',
                'IDREFERENCIA2', 'DOCREF2', 'VENTANAREF2', 'Codigo_Spring', 'IDBALANZA',
                'NROMATRICULA', 'idtipocamion', 'idalmacenmp', 'IDSALIDA_RECLASIF', 
                'IDINGRESO_RECLASIF', 'MODULO', 'idordenpro', 'idingresosalidaactivo',
                'IDMOTIVO_TRASLADO_SUNAT', 'PTOPARTIDA', 'MOTIVO_TRASLADO', 'IDUBIGEO1',
                'IDUBIGEO2', 'idviaje', 'dni', 'IDMOTIVO_AN', 'MOTIVO_AN', 'IDRESPONSABLE_AN',
                'OBSERVACION_AN', 'idusuario', 'IDVEHICULO', 'IDCHOFER', 'CMA30EQPID_CAMION',
                'CMA30EQPID_CARRETA', 'IDRUTA', 'IDLUGAR_O', 'IDLUGAR_D', 'ITEM_RUTA',
                'Ini_Desc_Usr', 'Fin_Desc_Usr', 'Lugar_Descarga', 'env_tipo_proceso',
                'env_idsuc_proceso', 'env_idalm_proceso', 'env_idsalida_proceso', 
                'env_idingreso_proceso', 'config_veh', 'GUIATRANSPORTISTA', 'NRO_BOOKING',
                'archivo_signed_ce', 'archivo_ce', 'idmodalidad_transporte', 'IDUBIGEOPARTIDA',
                'IDAREA', 'idcontrato', 'sello_ggn', 'sello_codProductor', 'sello_ProductoTransf',
                'IDESTADO2', 'IDTIPO_OPERACION_VOLCADO', 'IDINGRESOSALIDAALM_GENERAL', 'dua',
                'llevadopor_dni', 'IDUSUARIO_ULTIMO', 'origen_formulario', 'idingresosalidaalm_ajuste_inv',
                'NUM_EXPORTACION', 'CONSIGNATARIO', 'idingreso', 'idsalida', 'ticket_acopio',
                'NROPRESINTOCAMPO', 'idtipodesc', 'IDFPAGO', 'idmedida_peso', 'qr_sunat',
                'NUMPALLETMATPRIMA', 'chofer_apellido', 'IDORIGEN3', 'productor_ggn',
                'certificado_por', 'codigolp', 'idcomprador', 'idembarcacion', 'chofer_iddocidentidad',
                'DEPOSITORETIRO', 'CANAL', 'duadam'
            ]
            
            for field in text_fields_encabezado:
                if field in encabezado_dict and encabezado_dict[field] is not None:
                    encabezado_dict[field] = str(encabezado_dict[field]).strip()
                elif field in encabezado_dict:
                    encabezado_dict[field] = ''
            
            # Procesar campos numéricos en encabezado
            numeric_fields_encabezado = [
                'TCAMBIO', 'TCMONEDA', 'PRECIOIGV', 'REDONDEO', 'TOTAL', 'ES_GASTOS', 
                'ES_PROVISION', 'ES_RIEGO', 'CONTABILIZADO', 'VVENTA', 'IMPUESTO', 
                'DESCUENTO', 'VOLUMEN', 'NUMBATCH', 'NUMAUTOCLAVE', 'IMPRESO', 'IMPORTE_FLETE',
                'PESO_TOTAL', 'IMPORTADO', 'ES_COSTOS', 'pesodocorigen3', 'IDREGISTROVAR',
                'AREA_HA', 'IMPORTADO_EXTERNO', 'contador', 'PESO1', 'PESO2', 'automatico_asociaop',
                'numversion', 'transferir_comprometido', 'precio_generado', 'estado_ce',
                'ticket_pesada', 'ticket_pesada1', 'solicita_analisis', 'generado_x_distri',
                'nro_bultos', 'total_distribucion', 'mostrar_sellos', 'sello_estadoCertific',
                'importado_nsprov', 'cerrado', 'peso_descuento_comercial', 'precioun_desc_ajustado',
                'ind_retorno_vehiculo_envase_vacio', 'ind_retorno_vehiculo_vacio', 
                'ind_traslado_programado', 'ind_traslado_total_damods', 'ind_traslado_vehiculo_m1l',
                'ind_trasporte_subcontrado', 'ind_vehiculo_conductores_trasporte'
            ]
            
            for field in numeric_fields_encabezado:
                if field in encabezado_dict:
                    try:
                        if encabezado_dict[field] is not None:
                            encabezado_dict[field] = float(encabezado_dict[field])
                        else:
                            encabezado_dict[field] = 0.0
                    except (ValueError, TypeError):
                        encabezado_dict[field] = 0.0
            
            # Procesar campos booleanos/numéricos (0/1)
            boolean_fields_encabezado = ['CONTABILIZADO', 'CERRADO', 'IMPRESO']
            for field in boolean_fields_encabezado:
                if field in encabezado_dict:
                    try:
                        if encabezado_dict[field] is not None:
                            encabezado_dict[field] = bool(int(float(encabezado_dict[field])))
                        else:
                            encabezado_dict[field] = False
                    except (ValueError, TypeError):
                        encabezado_dict[field] = False

            return JsonResponse({
                'success': True,
                'message': 'Detalle de salida interna obtenido correctamente',
                'encabezado': encabezado_dict,
                'detalles': detalles_list,
                'totales': totales_dict,
                'total_items': len(detalles_list)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener el detalle de la salida interna: {str(e)}'
            }, status=500)
    
    def _obtener_lista_salidas(self, cursor, request):
        """Obtiene lista de salidas internas con filtros usando el procedimiento almacenado"""
        try:
            # Obtener parámetros de la request
            idempresa = request.GET.get('idempresa', '001')  # Default empresa
            fecha_desde = request.GET.get('fecha_desde')
            fecha_hasta = request.GET.get('fecha_hasta')
            idestado = request.GET.get('idestado')
            idmotivo = request.GET.get('idmotivo')
            
            # Convertir fechas si se proporcionan
            fecha_desde_param = None
            fecha_hasta_param = None
            
            
        
            if fecha_desde:
                try:
                    fecha_desde_param = datetime.strptime(fecha_desde, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                    }, status=400)
        
            if fecha_hasta:
                try:
                    fecha_hasta_param = datetime.strptime(fecha_hasta, '%Y-%m-%d')
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                    }, status=400)
            
            print(f"🔍 Ejecutando consulta de salidas internas con parámetros:")
            print(f"   - IDEMPRESA: {idempresa}")
            print(f"   - FECHA_DESDE: {fecha_desde_param}")
            print(f"   - FECHA_HASTA: {fecha_hasta_param}")
            print(f"   - IDESTADO: {idestado}")
            print(f"   - IDMOTIVO: {idmotivo}")
            
            # Ejecutar procedimiento almacenado
            cursor.execute("""
                EXEC SP_GET_SALIDAS_INTERNAS_ALMACEN ?, ?, ?, ?, ?
            """, [
                idempresa,
                fecha_desde_param,
                fecha_hasta_param,
                idestado if idestado and idestado != 'todos' else None,
                idmotivo if idmotivo and idmotivo != 'todos' else None
            ])
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(results)} registros")
        
            # Convertir a lista de diccionarios
            salidas = []
            for row in results:
                salida = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fechas
                    if isinstance(value, datetime) and value:
                        salida[column_name.lower()] = value.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(value, date) and value:
                        salida[column_name.lower()] = value.strftime('%Y-%m-%d')
                    else:
                        # Limpiar strings (quitar espacios)
                        if isinstance(value, str):
                            salida[column_name.lower()] = value.strip()
                        else:
                            salida[column_name.lower()] = value
                
                salidas.append(salida)
        
            return JsonResponse({
                'success': True,
                'data': salidas,
                'total': len(salidas),
                'filtros_aplicados': {
                    'idempresa': idempresa,
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta,
                    'idestado': idestado,
                    'idmotivo': idmotivo
                },
                'info': {
                    'procedimiento_usado': 'SP_GET_SALIDAS_INTERNAS_ALMACEN',
                    'descripcion': 'Salidas internas obtenidas mediante procedimiento almacenado optimizado'
                }
            })
            
        except Exception as e:
            print(f"❌ Error en consulta de salidas: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al consultar salidas: {str(e)}'
            }, status=500)
    
    def _verificar_salida_modificable(self, cursor, idingresosalidaalm):
        """Verifica si una salida puede ser modificada"""
        cursor.execute("""
            SELECT IDESTADO FROM INGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        resultado = cursor.fetchone()
        if not resultado:
            return False
        
        # Solo permitir modificar si está en estado Pendiente
        return resultado[0] == 'PE'
    
    def _verificar_salida_anulable(self, cursor, idingresosalidaalm):
        """Verifica si una salida puede ser anulada"""
        cursor.execute("""
            SELECT IDESTADO, CONTABILIZADO FROM INGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        resultado = cursor.fetchone()
        if not resultado:
            return False
        
        estado, contabilizado = resultado
        # No permitir anular si ya está anulado o contabilizado
        return estado != 'AN' and contabilizado != 1
    
    def _actualizar_encabezado(self, cursor, idingresosalidaalm, datos_encabezado):
        """Actualiza el encabezado de una salida existente"""
        sql = """
        UPDATE INGRESOSALIDAALM 
        SET GLOSA = ?, IDRESPONSABLE = ?, IDMOTIVO = ?,
            FECHACREACION = GETDATE(), IDUSUARIO = ?
        WHERE IDINGRESOSALIDAALM = ?
        """
        
        cursor.execute(sql, [
            datos_encabezado.get('GLOSA'),
            datos_encabezado.get('IDRESPONSABLE'),
            datos_encabezado.get('IDMOTIVO'),
            datos_encabezado.get('IDUSUARIO'),
            idingresosalidaalm
        ])
    
    def _actualizar_detalles(self, cursor, idingresosalidaalm, productos):
        """Actualiza los detalles de una salida existente"""
        # Eliminar detalles existentes
        cursor.execute("""
            DELETE FROM DINGRESOSALIDAALM
            WHERE IDINGRESOSALIDAALM = ?
        """, [idingresosalidaalm])
        
        # Insertar nuevos detalles
        self._insertar_detalles(cursor, idingresosalidaalm, productos)



@method_decorator(csrf_exempt, name='dispatch')
class ProcesarSalidaInternaViewAJS(View):
    """
    Clase para procesar la contabilización y centralización de salidas internas
    Ejecuta los procedimientos CONTAB_INGRESOSALIDAALM y CENTRALIZA_ALMACENES
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa la contabilización y centralización de una salida interna
        """
        data = json.loads(request.body)
        
        idingresosalidaalm = data.get('IDINGRESOSALIDAALM', '')
        idempresa = data.get('IDEMPRESA', '001')
        ventana = data.get('VENTANA', 'EDT_SALIDAS')
        idemisor = data.get('IDEMISOR', '001')
        
        print(f"🔄 Iniciando contabilización...")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm}")
        print(f"   - IDEMPRESA: {idempresa}")
        print(f"   - VENTANA: {ventana}")
        print(f"   - IDEMISOR: {idemisor}")
        
        # Crear conexión principal
        cursor = connection_inversioneajs.cursor()
        
        try:
            # 1. Verificar existencia y validaciones previas
            print("🔍 Validando documento...")
            
            # Verificar existencia del documento
            cursor.execute("""
                SELECT CONTABILIZADO, IDESTADO, IDMOTIVO, VENTANA 
                FROM INGRESOSALIDAALM 
                WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
            """, [idingresosalidaalm, idempresa])
            
            resultado = cursor.fetchone()
            if not resultado:
                return JsonResponse({
                    'success': False,
                    'error': f'No se encontró el documento {idingresosalidaalm}'
                })
            
            contabilizado_actual, estado_actual, idmotivo, ventana_doc = resultado
            print(f"📋 Estado actual - CONTABILIZADO: {contabilizado_actual}, ESTADO: {estado_actual}, MOTIVO: {idmotivo}")
            
            # Si ya está contabilizado, solo intentar centralizar
            if contabilizado_actual == 1:
                print("📋 Documento ya contabilizado, procediendo solo con centralización...")
                return self._centralizar_documento(idingresosalidaalm, idempresa, idemisor)
            
            if estado_actual == 'AN':
                return JsonResponse({
                    'success': False,
                    'error': 'No se puede contabilizar un documento anulado'
                })
            
            # 2. Validar parámetros que pueden impedir la contabilización
            print("🔍 Validando parámetros internos...")
            
            # Verificar parámetro AL_EVITAR_CONTAB_ALM_CE
            cursor.execute("""
                SELECT ISNULL(VALOR,'NO') 
                FROM PARAMETRO 
                WHERE IDPARAMETRO = 'AL_EVITAR_CONTAB_ALM_EST_CE' AND IDEMPRESA = ?
            """, [idempresa])
            
            evitar_contab_ce = cursor.fetchone()
            evitar_contab_ce = evitar_contab_ce[0] if evitar_contab_ce else 'NO'
            
            if estado_actual == 'CE' and evitar_contab_ce == 'SI':
                return JsonResponse({
                    'success': False,
                    'error': f'No se puede contabilizar documentos con estado CE según parámetro AL_EVITAR_CONTAB_ALM_EST_CE'
                })
            
            # Verificar si el motivo permite contabilización
            cursor.execute("""
                SELECT ISNULL(CONTAB_MOVALM,0) as KARDEX, TIPO_MOTIVO, ISNULL(ES_TRANSFERENCIA,0) as ES_TRANSFERENCIA
                FROM MOTIVOS 
                WHERE IDMOTIVO = ?
            """, [idmotivo])
            
            motivo_info = cursor.fetchone()
            if motivo_info:
                kardex, tipo_motivo, es_transferencia = motivo_info
                print(f"📋 Motivo info - KARDEX: {kardex}, TIPO: {tipo_motivo}, ES_TRANSFERENCIA: {es_transferencia}")
                
                if kardex == 1:
                    return JsonResponse({
                        'success': False,
                        'error': f'El motivo {idmotivo} no permite generar movimientos de almacén (KARDEX=1)'
                    })
            
            # 3. Validar transferencias pendientes de aprobación
            if motivo_info and es_transferencia == 1:
                cursor.execute("""
                    SELECT ISNULL(VALOR,'NO') 
                    FROM PARAMETRO 
                    WHERE IDPARAMETRO = 'AL_TRANSF_CONTAB_APROB' AND IDEMPRESA = ?
                """, [idempresa])
                
                transf_aprob = cursor.fetchone()
                transf_aprob = transf_aprob[0] if transf_aprob else 'NO'
                
                if transf_aprob == 'SI':
                    print("⚠️ Documento de transferencia con validación de aprobación habilitada")
            
            # 4. Ejecutar el procedimiento de contabilización
            print(f"🔄 Ejecutando procedimiento CONTAB_INGRESOSALIDAALM...")
            
            import pyodbc
            
            # Crear nueva conexión independiente
            host = '192.168.0.5'
            database = 'INVERSIONESAJS'  # Para prueba
            user = 'sa'
            password = '@SADL.2023'
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};MARS_Connection=yes'
            
            conn = pyodbc.connect(conn_str)
            cursor_proc = conn.cursor()
            
            try:
                # Habilitar PRINT messages de SQL Server
                cursor_proc.execute("SET NOCOUNT OFF")
                
                # Ejecutar el procedimiento
                print(f"📤 Ejecutando: EXEC CONTAB_INGRESOSALIDAALM '{idingresosalidaalm}', '{idempresa}', '{ventana}', 'A', '{idemisor}'")
                
                cursor_proc.execute("""
                    EXEC CONTAB_INGRESOSALIDAALM ?, ?, ?, ?, ?
                """, [idingresosalidaalm, idempresa, ventana, 'A', idemisor])
                
                # Capturar mensajes del procedimiento
                messages = []
                while cursor_proc.nextset():
                    try:
                        results = cursor_proc.fetchall()
                        if results:
                            messages.extend([str(row) for row in results])
                    except:
                        pass
                
                # Confirmar transacción
                conn.commit()
                print("✅ Procedimiento de contabilización ejecutado y confirmado")
                
                if messages:
                    print(f"📝 Mensajes del procedimiento: {messages}")
                
                # 5. Verificar resultado de contabilización
                cursor_proc.execute("""
                    SELECT CONTABILIZADO 
                    FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [idingresosalidaalm, idempresa])
                
                resultado_final = cursor_proc.fetchone()
                contabilizado_final = resultado_final[0] if resultado_final else 0
                
                print(f"🔍 Verificación contabilización - CONTABILIZADO: {contabilizado_final}")
                
                cursor_proc.close()
                conn.close()
                
                if contabilizado_final == 1:
                    print("✅ Contabilización exitosa, procediendo con centralización...")
                    
                    # 6. Ejecutar centralización
                    resultado_centralizacion = self._centralizar_documento(idingresosalidaalm, idempresa, idemisor)
                    
                    # Combinar resultados
                    if resultado_centralizacion.status_code == 200:
                        data_centralizacion = json.loads(resultado_centralizacion.content)
                        if data_centralizacion.get('success'):
                            return JsonResponse({
                                'success': True,
                                'message': 'Procesos ejecutados exitosamente',
                                'data': {
                                    'IDINGRESOSALIDAALM': idingresosalidaalm,
                                    'CONTABILIZADO': contabilizado_final,
                                    'ESTADO': 'PE',
                                    'procesos_ejecutados': [
                                        'CONTAB_INGRESOSALIDAALM',
                                        'CENTRALIZA_ALMACENES'
                                    ]
                                }
                            })
                        else:
                            return JsonResponse({
                                'success': True,
                                'message': 'Contabilización exitosa, pero centralización falló',
                                'warning': data_centralizacion.get('error', 'Error desconocido en centralización'),
                                'data': {
                                    'IDINGRESOSALIDAALM': idingresosalidaalm,
                                    'CONTABILIZADO': contabilizado_final,
                                    'procesos_ejecutados': ['CONTAB_INGRESOSALIDAALM']
                                }
                            })
                    else:
                        return JsonResponse({
                            'success': True,
                            'message': 'Contabilización exitosa, pero error en centralización',
                            'warning': 'No se pudo ejecutar la centralización',
                            'data': {
                                'IDINGRESOSALIDAALM': idingresosalidaalm,
                                'CONTABILIZADO': contabilizado_final,
                                'procesos_ejecutados': ['CONTAB_INGRESOSALIDAALM']
                            }
                        })
                else:
                    # Intentar obtener más información sobre por qué falló
                    cursor.execute("""
                        SELECT TOP 1 
                            I.IDESTADO, I.IDESTADO2, M.CONTAB_MOVALM, M.TIPO_MOTIVO,
                            I.VENTANA, M.GRUPO_MOTIVO
                        FROM INGRESOSALIDAALM I
                        LEFT JOIN MOTIVOS M ON I.IDMOTIVO = M.IDMOTIVO
                        WHERE I.IDINGRESOSALIDAALM = ? AND I.IDEMPRESA = ?
                    """, [idingresosalidaalm, idempresa])
                    
                    debug_info = cursor.fetchone()
                    debug_msg = f"Debug info: {debug_info}" if debug_info else "No debug info available"
                    
                    return JsonResponse({
                        'success': False,
                        'error': 'El procedimiento se ejecutó pero no contabilizó el documento. Posibles causas: validaciones internas del procedimiento, estado del documento, configuración de parámetros.',
                        'debug': debug_msg,
                        'messages': messages,
                        'data': {
                            'IDINGRESOSALIDAALM': idingresosalidaalm,
                            'CONTABILIZADO': contabilizado_final
                        }
                    })
                    
            except Exception as proc_error:
                conn.rollback()
                cursor_proc.close()
                conn.close()
                print(f"❌ Error en procedimiento de contabilización: {str(proc_error)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al ejecutar procedimiento de contabilización: {str(proc_error)}'
                })
                
        except Exception as e:
            print(f"❌ Error general: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el proceso: {str(e)}'
            })
        finally:
            if cursor:
                cursor.close()

    def _centralizar_documento(self, idingresosalidaalm, idempresa, idemisor):
        """
        Ejecuta el procedimiento de centralización de almacenes
        EXEC CENTRALIZA_ALMACENES idempresa, idingresosalidaalm, '', idemisor
        """
        print(f"🔄 Iniciando centralización de almacenes...")
        print(f"   - IDEMPRESA: {idempresa}")
        print(f"   - IDINGRESOSALIDAALM: {idingresosalidaalm}")
        print(f"   - IDEMISOR: {idemisor}")
        
        import pyodbc
        
        try:
            # Crear nueva conexión independiente para centralización
            host = '192.168.0.5'
            database = 'INVERSIONESAJS'  # Para prueba
            user = 'sa'
            password = '@SADL.2023'
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={database};UID={user};PWD={password};MARS_Connection=yes'
            
            conn = pyodbc.connect(conn_str)
            cursor_proc = conn.cursor()
            
            try:
                # Habilitar PRINT messages de SQL Server
                cursor_proc.execute("SET NOCOUNT OFF")
                
                # Ejecutar el procedimiento de centralización
                print(f"📤 Ejecutando: EXEC CENTRALIZA_ALMACENES '{idempresa}', '{idingresosalidaalm}', '', '{idemisor}'")
                
                cursor_proc.execute("""
                    EXEC CENTRALIZA_ALMACENES ?, ?, ?, ?
                """, [idempresa, idingresosalidaalm, '', idemisor])
                
                # Capturar mensajes del procedimiento
                messages = []
                while cursor_proc.nextset():
                    try:
                        results = cursor_proc.fetchall()
                        if results:
                            messages.extend([str(row) for row in results])
                    except:
                        pass
                
                # Confirmar transacción
                conn.commit()
                print("✅ Procedimiento de centralización ejecutado y confirmado")
                
                if messages:
                    print(f"📝 Mensajes del procedimiento de centralización: {messages}")
                
                # Verificar estado final del documento
                cursor_proc.execute("""
                    SELECT IDESTADO 
                    FROM INGRESOSALIDAALM 
                    WHERE IDINGRESOSALIDAALM = ? AND IDEMPRESA = ?
                """, [idingresosalidaalm, idempresa])
                
                resultado_estado = cursor_proc.fetchone()
                estado_final = resultado_estado[0] if resultado_estado else 'Desconocido'
                
                print(f"🔍 Verificación centralización - ESTADO: {estado_final}")
                
                cursor_proc.close()
                conn.close()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Centralización ejecutada exitosamente',
                    'data': {
                        'IDINGRESOSALIDAALM': idingresosalidaalm,
                        'ESTADO': estado_final,
                        'messages': messages
                    }
                })
                
            except Exception as proc_error:
                conn.rollback()
                cursor_proc.close()
                conn.close()
                print(f"❌ Error en procedimiento de centralización: {str(proc_error)}")
                return JsonResponse({
                    'success': False,
                    'error': f'Error al ejecutar procedimiento de centralización: {str(proc_error)}'
                })
                
        except Exception as e:
            print(f"❌ Error general en centralización: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el proceso de centralización: {str(e)}'
            })


@method_decorator(csrf_exempt, name='dispatch')
class BuscarRequerimientoInternoAPIAJS(View):
    """
    API para buscar requerimientos internos por número de documento
    Por defecto muestra todos los requerimientos pendientes para seleccionar
    """
    def get(self, request, *args, **kwargs):
        """
        Obtiene requerimientos internos con filtros avanzados
        
        Parámetros GET:
        - numero: número del requerimiento a buscar (opcional)
        - idreqinterno: ID del requerimiento interno exacto (opcional)
        - estado: estado del requerimiento (opcional - 'AP', 'TP', 'todos')
        - fecha_desde: fecha desde (formato YYYY-MM-DD, opcional)
        - fecha_hasta: fecha hasta (formato YYYY-MM-DD, opcional)
        - limit: límite de resultados (opcional, por defecto 50, máximo 100)
        """
        cursor = None
        try:
            # Obtener parámetros de búsqueda
            numero = request.GET.get('numero', '').strip()
            idreqinterno = request.GET.get('idreqinterno', '').strip()  # ✅ NUEVO PARÁMETRO
            estado = request.GET.get('estado', '').strip().upper()
            fecha_desde = request.GET.get('fecha_desde', '').strip()
            fecha_hasta = request.GET.get('fecha_hasta', '').strip()
            
            # Convertir limit a entero con validación
            try:
                limit = min(int(request.GET.get('limit', 50)), 100)
            except (ValueError, TypeError):
                limit = 50
            
            cursor = connection_inversioneajs.cursor()
            
            # Query base sin parametrizar TOP
            base_query = f"""
                SELECT TOP {limit}
                    R.IDREQINTERNO,
                    R.IDDOCUMENTO AS TD,
                    R.SERIE,
                    R.NUMERO,
                    FORMAT(R.FECHA, 'dd/MM/yy') AS FECHA,
                    B.NOMBRE AS RAZON_SOCIAL,
                    R.IDESTADO,
                    R.IDMOTIVO,
                    R.IDDOCUMENTO AS DOC_ORIGEN,
                    R.IDEMPRESA,
                    R.OBSERVACION,
                    R.TOTAL,
                    R.IDRESPONSABLE
                FROM REQINTERNO R
                INNER JOIN RESPONSABLE B ON B.IDRESPONSABLE = R.IDRESPONSABLE
                WHERE 1=1
            """
            
            # Lista para parámetros (sin incluir limit)
            params = []
            conditions = []
            
            # ✅ FILTRO POR IDREQINTERNO EXACTO (NUEVA FUNCIONALIDAD)
            if idreqinterno:
                conditions.append("R.IDREQINTERNO = ?")
                params.append(idreqinterno)
                # Si buscamos por IDREQINTERNO exacto, ignoramos otros filtros para mejor performance
                # y devolvemos directamente el resultado
            else:
                # Filtro por estado
                if estado and estado != 'TODOS':
                    if estado == 'APROBADO':
                        conditions.append("R.IDESTADO = 'AP'")
                    elif estado == 'PENDIENTE':
                        conditions.append("R.IDESTADO = 'TP'")
                    else:
                        conditions.append("R.IDESTADO = ?")
                        params.append(estado)
                else:
                    conditions.append("(R.IDESTADO = 'AP' OR R.IDESTADO = 'TP')")
                
                # Filtro por número
                if numero:
                    conditions.append("R.NUMERO LIKE ?")
                    params.append(f'%{numero}%')
                
                # Filtro por fecha desde
                if fecha_desde:
                    try:
                        from datetime import datetime
                        datetime.strptime(fecha_desde, '%Y-%m-%d')
                        conditions.append("R.FECHA >= ?")
                        params.append(fecha_desde)
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'
                        }, status=400)
                
                # Filtro por fecha hasta
                if fecha_hasta:
                    try:
                        from datetime import datetime
                        datetime.strptime(fecha_hasta, '%Y-%m-%d')
                        conditions.append("R.FECHA <= ?")
                        params.append(fecha_hasta)
                    except ValueError:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'
                        }, status=400)
            
            # Construir query final
            if conditions:
                query = base_query + " AND " + " AND ".join(conditions)
            else:
                query = base_query
            
            query += " ORDER BY R.FECHA DESC, R.NUMERO DESC"
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Procesar resultados
            results = []
            for row in cursor.fetchall():
                results.append({
                    'IDREQINTERNO': row[0],
                    'TD': row[1],
                    'SERIE': row[2],
                    'NUMERO': row[3],
                    'FECHA': row[4],
                    'RAZON_SOCIAL': row[5],
                    'IDESTADO': row[6],
                    'IDMOTIVO': row[7],
                    'DOC_ORIGEN': row[8],
                    'DOC': f"{row[1]} {row[2]} {row[3]} - {row[4]}",
                    'IDEMPRESA': row[9],
                    'OBSERVACION': row[10],
                    'TOTAL': row[11],
                    'IDRESPONSABLE': row[12]
                })
            
            # Generar mensaje
            filtros_aplicados = []
            if idreqinterno:
                filtros_aplicados.append(f'IDREQINTERNO "{idreqinterno}"')
            if numero:
                filtros_aplicados.append(f'número "{numero}"')
            if estado and estado != 'TODOS':
                filtros_aplicados.append(f'estado "{estado}"')
            if fecha_desde:
                filtros_aplicados.append(f'desde {fecha_desde}')
            if fecha_hasta:
                filtros_aplicados.append(f'hasta {fecha_hasta}')
            
            if filtros_aplicados:
                mensaje = f'Se encontraron {len(results)} requerimientos con filtros: {", ".join(filtros_aplicados)}'
            else:
                mensaje = f'Se encontraron {len(results)} requerimientos (AP/TP)'
            
            return JsonResponse({
                'status': 'success',
                'message': mensaje,
                'total_encontrados': len(results),
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al buscar requerimientos: {str(e)}'
            }, status=500)
        finally:
            if cursor:
                cursor.close()

# Funciones auxiliares para procesar detalles de requerimientos

def procesar_detalle_requerimiento(detalle):
    """
    Procesa y limpia los datos de un detalle de requerimiento
    
    Args:
        detalle (dict): Diccionario con los datos del detalle
        
    Returns:
        dict: Detalle procesado y limpio
    """
    from decimal import Decimal
    import datetime
    
    detalle_procesado = {}
    
    for key, value in detalle.items():
        # Mantener precisión decimal completa
        if isinstance(value, Decimal):
            # Formatear a 6 decimales para preservar precisión
            detalle_procesado[key] = float(f"{value:.6f}")
        # Procesar fechas
        elif isinstance(value, datetime.datetime):
            detalle_procesado[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            detalle_procesado[f'{key}_FORMATTED'] = value.strftime('%d/%m/%Y')
        elif isinstance(value, datetime.date):
            detalle_procesado[key] = value.strftime('%Y-%m-%d')
            detalle_procesado[f'{key}_FORMATTED'] = value.strftime('%d/%m/%Y')
        # Limpiar strings (ya se hace en SQL pero por seguridad)
        elif isinstance(value, str):
            detalle_procesado[key] = value.strip()
        # Manejar valores None
        elif value is None:
            detalle_procesado[key] = ""
        else:
            detalle_procesado[key] = value
    
    # Campos calculados adicionales
    cantidad = detalle_procesado.get('CANTIDAD', 0)
    cant_aprobada = detalle_procesado.get('CANTAPROBADA', 0)
    
    # Estado de atención
    if detalle_procesado.get('ATENDIDO', 0) == 1:
        detalle_procesado['ESTADO_ATENCION'] = 'ATENDIDO'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'success'
    elif detalle_procesado.get('genero_salida', 0) == 1:
        detalle_procesado['ESTADO_ATENCION'] = 'EN_PROCESO'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'warning'
    else:
        detalle_procesado['ESTADO_ATENCION'] = 'PENDIENTE'
        detalle_procesado['ESTADO_ATENCION_BADGE'] = 'danger'
    
    # Porcentaje de atención
    if cant_aprobada > 0:
        porcentaje = (cantidad / cant_aprobada) * 100
        detalle_procesado['PORCENTAJE_ATENCION'] = round(porcentaje, 6)
    else:
        detalle_procesado['PORCENTAJE_ATENCION'] = 0
    
    # Formato de cantidades para mostrar con 6 decimales
    detalle_procesado['CANTIDAD_DISPLAY'] = f"{cantidad:.6f}"
    detalle_procesado['CANTAPROBADA_DISPLAY'] = f"{cant_aprobada:.6f}"
    
    if 'CANTIDAD_PENDIENTE' in detalle_procesado:
        pendiente = detalle_procesado['CANTIDAD_PENDIENTE']
        detalle_procesado['CANTIDAD_PENDIENTE_DISPLAY'] = f"{pendiente:.6f}"
    
    return detalle_procesado


def calcular_estadisticas_requerimiento(detalles):
    """
    Calcula estadísticas generales del requerimiento
    
    Args:
        detalles (list): Lista de detalles del requerimiento
        
    Returns:
        dict: Estadísticas calculadas
    """
    if not detalles:
        return {}
    
    total_items = len(detalles)
    items_atendidos = sum(1 for d in detalles if d.get('ATENDIDO', 0) == 1)
    items_en_proceso = sum(1 for d in detalles if d.get('genero_salida', 0) == 1 and d.get('ATENDIDO', 0) == 0)
    items_pendientes = total_items - items_atendidos - items_en_proceso
    
    # Calcular totales de cantidades
    total_cantidad_solicitada = sum(d.get('CANTAPROBADA', 0) for d in detalles)
    total_cantidad_atendida = sum(d.get('CANTIDAD', 0) for d in detalles if d.get('ATENDIDO', 0) == 1)
    
    # Porcentaje general de atención
    porcentaje_atencion = 0
    if total_cantidad_solicitada > 0:
        porcentaje_atencion = round((total_cantidad_atendida / total_cantidad_solicitada) * 100, 2)
    
    # Productos únicos
    productos_unicos = len(set(d.get('IDPRODUCTO', '') for d in detalles))
    
    return {
        'total_items': total_items,
        'items_atendidos': items_atendidos,
        'items_en_proceso': items_en_proceso,
        'items_pendientes': items_pendientes,
        'porcentaje_items_atendidos': round((items_atendidos / total_items) * 100, 2) if total_items > 0 else 0,
        'total_cantidad_solicitada': total_cantidad_solicitada,
        'total_cantidad_atendida': total_cantidad_atendida,
        'porcentaje_atencion_cantidad': porcentaje_atencion,
        'productos_unicos': productos_unicos,
        'estado_general': 'COMPLETADO' if items_atendidos == total_items else 'PARCIAL' if items_atendidos > 0 else 'PENDIENTE'
    }


class DetalleRequerimientoAPIAJS(View):
    def get(self, request, idreqinterno, *args, **kwargs):
        """
        Obtiene los detalles completos de un requerimiento interno por su IDREQINTERNO
        
        Args:
            idreqinterno (str): ID del requerimiento interno
            
        Returns:
            JsonResponse: Detalles del requerimiento o error
        """
        cursor = None
        try:
            # Validar que se proporcione el IDREQINTERNO
            if not idreqinterno or idreqinterno.strip() == '':
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDREQINTERNO es requerido'
                }, status=400)
            
            # Limpiar el parámetro de entrada
            idreqinterno_limpio = idreqinterno.strip()
            
            # Conectar a la base de datos
            cursor = connection_inversioneajs.cursor()
            
            # Query optimizada con función de cantidad por atender
            query = """
                SELECT 
                    D.IDEMPRESA,
                    D.IDREQINTERNO,
                    D.ITEM,
                    LTRIM(RTRIM(D.IDPRODUCTO)) AS IDPRODUCTO,
                    LTRIM(RTRIM(D.DESCRIPCION)) AS DESCRIPCION,
                    LTRIM(RTRIM(D.IDMEDIDA)) AS IDMEDIDA,
                    D.CANTIDAD,
                    D.CANTIDAD AS CANTAPROBADA,
                    LTRIM(RTRIM(D.IDCONSUMIDOR)) AS IDCONSUMIDOR,
                    LTRIM(RTRIM(D.IDRESPONSABLE)) AS IDRESPONSABLE,
                    D.ATENDIDO,
                    D.ESTADOS,
                    -- Campos adicionales útiles
                    D.IDCLIEPROV,
                    D.PARAFECHA,
                    D.genero_salida,
                    -- Cantidad pendiente usando la función
                    ISNULL(F.CANTIDAD_POR_ATENDER, D.CANTAPROBADA) AS CANTIDAD_PENDIENTE,
                    ISNULL(F.TOTAL_CANTIDAD_SALIDA, 0) AS TOTAL_SALIDAS_REALIZADAS
                FROM DREQINTERNO D WITH (NOLOCK)
                LEFT JOIN fn_CANTIDAD_POR_ATENDER_REQINTERNO('001', ?) F 
                    ON D.IDREQINTERNO = F.IDREQINTERNO 
                    AND D.ITEM = F.ITEM 
                    AND LTRIM(RTRIM(D.IDPRODUCTO)) = F.IDPRODUCTO
                WHERE D.ATENDIDO = '0' AND D.IDREQINTERNO = ?
                ORDER BY CAST(D.ITEM AS INT)
            """
            
            # Ejecutar consulta pasando el mismo parámetro dos veces
            cursor.execute(query, [idreqinterno_limpio, idreqinterno_limpio])
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Obtener todos los resultados
            rows = cursor.fetchall()
            
            if rows:
                # Convertir resultados a lista de diccionarios
                detalles = []
                for row in rows:
                    detalle = dict(zip(columns, row))
                    
                    # Procesar y limpiar datos
                    detalle_procesado = procesar_detalle_requerimiento(detalle)
                    detalles.append(detalle_procesado)
                
                cursor.close()
                
                # Calcular estadísticas del requerimiento
                estadisticas = calcular_estadisticas_requerimiento(detalles)
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'Se encontraron {len(detalles)} detalles para el requerimiento {idreqinterno_limpio}',
                    'data': detalles,
                    'estadisticas': estadisticas,
                    'idreqinterno': idreqinterno_limpio,
                    'total_items': len(detalles)
                })
            
            else:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No se encontraron detalles para el requerimiento con IDREQINTERNO: {idreqinterno_limpio}',
                    'idreqinterno': idreqinterno_limpio
                }, status=404)
                
        except Exception as e:
            # Cerrar cursor en caso de error
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
                
            return JsonResponse({
                'status': 'error',
                'message': f'Error al consultar los detalles del requerimiento: {str(e)}',
                'idreqinterno': idreqinterno
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ProcesarRequerimientoInternoAPIAJS(View):
    """
    Vista simplificada para procesar productos REQINTERNO
    Ejecuta stored procedures: CAMBIA_ESTADOREQINTERNO_DET y ACTUALIZA_ESTADO_REQINTERNO
    """
    
    def post(self, request, *args, **kwargs):
        """
        Procesa requerimientos internos con la estructura enviada desde JavaScript
        """
        cursor = None
        
        try:
            print("🚀 ===== INICIANDO PROCESAMIENTO REQINTERNO API =====")
            
            # Parsear JSON del request
            data = json.loads(request.body)
            print(f"📋 Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Extraer secciones principales
            encabezado = data.get('encabezado', {})
            productos = data.get('productos', [])
            documento_referencia = data.get('documento_referencia', {})
            idingresosalidaalm = data.get('idingresosalidaalm', '')
            
            # Validaciones básicas
            if not encabezado.get('IDEMPRESA'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDEMPRESA faltante en encabezado',
                    'code': 'MISSING_IDEMPRESA'
                }, status=400)
            
            if not productos:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Lista de productos está vacía',
                    'code': 'MISSING_PRODUCTOS'
                }, status=400)
            
            if not documento_referencia.get('IDREFERENCIA'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDREFERENCIA faltante en documento_referencia',
                    'code': 'MISSING_IDREFERENCIA'
                }, status=400)
            
            if not idingresosalidaalm:
                return JsonResponse({
                    'status': 'error',
                    'message': 'IDINGRESOSALIDAALM está vacío',
                    'code': 'MISSING_IDINGRESOSALIDAALM'
                }, status=400)
            
            print("✅ Validaciones básicas exitosas")
            
            # Procesar con conexión fresca
            resultado = self._procesar_requerimiento_simplificado(
                encabezado, productos, documento_referencia, idingresosalidaalm
            )
            
            if resultado['success']:
                return JsonResponse({
                    'status': 'success',
                    'message': resultado['message'],
                    'data': {
                        'productos_procesados': resultado['productos_procesados'],
                        'idempresa': encabezado.get('IDEMPRESA'),
                        'idreferencia': documento_referencia.get('IDREFERENCIA'),
                        'idingresosalidaalm': idingresosalidaalm
                    }
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': resultado['message'],
                    'code': 'PROCESSING_ERROR'
                }, status=500)
                
        except json.JSONDecodeError as e:
            print(f"❌ Error JSON: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'JSON inválido: {str(e)}',
                'code': 'INVALID_JSON'
            }, status=400)
            
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            print(f"📊 Stack trace: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=500)
    
    def _procesar_requerimiento_simplificado(self, encabezado, productos, documento_referencia, idingresosalidaalm):
        """
        Procesa el requerimiento con conexión fresca usando el patrón de SalidaInternaView
        """
        try:
            # Obtener parámetros principales
            idempresa = encabezado.get('IDEMPRESA')
            idreferencia = documento_referencia.get('IDREFERENCIA')
            
            print(f"📋 ===== PROCESANDO REQUERIMIENTO =====")
            print(f"🏢 IDEMPRESA: {idempresa}")
            print(f"📄 IDREFERENCIA: {idreferencia}")
            print(f"🆔 IDINGRESOSALIDAALM: {idingresosalidaalm}")
            print(f"📦 Total productos: {len(productos)}")
            
            # Usar el mismo patrón que SalidaInternaView
            cursor = connection_inversioneajs.cursor()
            
            # Forzar autocommit=True (igual que SalidaInternaView)
            connection_inversioneajs.autocommit = True
            print("🔧 Autocommit configurado a True")
            
            productos_procesados = 0
            
            # PASO 1: Ejecutar CAMBIA_ESTADOREQINTERNO_DET para cada producto
            print("📋 ===== PASO 1: CAMBIA_ESTADOREQINTERNO_DET =====")
            
            for i, producto in enumerate(productos, 1):
                idproducto = producto.get('IDPRODUCTO', '')
                itemref = producto.get('ITEMREF', '')
                tablaref = producto.get('TABLAREF', 'REQINTERNO')
                
                print(f"📦 Producto {i}/{len(productos)}: {idproducto} - Item: {itemref}")
                
                if not idproducto or not itemref:
                    print(f"⚠️ Saltando producto {i} - datos incompletos")
                    continue
                
                # Generar XML
                xml_antes, xml_ahora = self._generar_xml_simple(
                    idproducto, idreferencia, itemref, tablaref
                )
                
                # Ejecutar procedimiento
                try:
                    cursor.execute(
                        "EXEC CAMBIA_ESTADOREQINTERNO_DET ?, ?, ?",
                        [idempresa, xml_antes, xml_ahora]
                    )
                    
                    # Consumir resultados
                    while cursor.nextset():
                        pass
                    
                    productos_procesados += 1
                    print(f"✅ Producto {i} procesado exitosamente")
                    
                except Exception as prod_error:
                    print(f"❌ Error procesando producto {i}: {str(prod_error)}")
                    raise prod_error
            
            print(f"✅ PASO 1 completado: {productos_procesados} productos")
            
            # PASO 2: Ejecutar ACTUALIZA_ESTADO_REQINTERNO
            print("📋 ===== PASO 2: ACTUALIZA_ESTADO_REQINTERNO =====")
            
            cursor.execute(
                "EXEC ACTUALIZA_ESTADO_REQINTERNO ?, ?, ?",
                [idempresa, idingresosalidaalm, idreferencia]
            )
            
            # Consumir resultados
            while cursor.nextset():
                pass
            
            print("✅ PASO 2 completado exitosamente")
            
            # Verificar resultados
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM REQINTERNO 
                    WHERE IDREFERENCIA = ? AND IDEMPRESA = ?
                """, [idreferencia, idempresa])
                result = cursor.fetchone()
                count_reqs = result[0] if result else 0
                print(f"📈 Requerimientos en BD: {count_reqs}")
            except Exception as verification_error:
                print(f"⚠️ Error en verificación: {str(verification_error)}")
            
            # Cerrar cursor
            cursor.close()
            print("🔄 Cursor cerrado")
            
            return {
                'success': True,
                'message': f'Procesamiento exitoso: {productos_procesados} productos',
                'productos_procesados': productos_procesados
            }
            
        except Exception as e:
            print(f"❌ Error en procesamiento: {str(e)}")
            
            # Limpiar cursor
            try:
                if 'cursor' in locals():
                    cursor.close()
            except:
                pass
            
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'productos_procesados': 0
            }
    
    def _generar_xml_simple(self, idproducto, idreferencia, itemref, tablaref="REQINTERNO"):
        """
        Genera XML para los procedimientos almacenados
        """
        def escape_xml(texto):
            if texto is None:
                return ""
            return str(texto).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Limpiar valores
        idproducto_clean = escape_xml(idproducto)
        idreferencia_clean = escape_xml(idreferencia)
        itemref_clean = escape_xml(itemref)
        tablaref_clean = escape_xml(tablaref)
        
        # XML Antes
        xml_antes = (
            f'<VFPData><disa_antes><record>'
            f'<idproducto>{idproducto_clean}</idproducto>'
            f'<idreferencia>{idreferencia_clean}</idreferencia>'
            f'<itemref>{itemref_clean}</itemref>'
            f'<tablaref>{tablaref_clean}</tablaref>'
            f'</record></disa_antes></VFPData>'
        )
        
        # XML Ahora
        xml_ahora = (
            f'<VFPData><disa_ahora><record>'
            f'<idproducto>{idproducto_clean}</idproducto>'
            f'<idreferencia>{idreferencia_clean}</idreferencia>'
            f'<itemref>{itemref_clean}</itemref>'
            f'<tablaref>{tablaref_clean}</tablaref>'
            f'</record></disa_ahora></VFPData>'
        )
        
        return xml_antes, xml_ahora


@method_decorator(csrf_exempt, name='dispatch')
class ResponsablesAPIAJS(View):
    """
    API para obtener responsables de la base de datos
    """
    
    def get(self, request, *args, **kwargs):
        """
        Obtiene lista de responsables con filtros opcionales
        """
        try:
            # Obtener parámetros de búsqueda
            idresponsable = request.GET.get('idresponsable', '').strip()
            nombre = request.GET.get('nombre', '').strip()
            
            cursor = connection_inversioneajs.cursor()
            
            # Si se proporciona un ID específico, buscar solo ese responsable
            if idresponsable:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE idresponsable = ?
                """, [idresponsable])
            
            # Si se proporciona un nombre, buscar por coincidencia parcial
            elif nombre:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE nombre LIKE ?
                    ORDER BY nombre
                """, [f'%{nombre}%'])
            
            # Si no se proporcionan filtros, obtener todos los responsables
            else:
                cursor.execute("""
                    SELECT idresponsable, nombre
                    FROM RESPONSABLE
                    WHERE idresponsable IS NOT NULL AND nombre IS NOT NULL
                    ORDER BY nombre
                """)
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            responsables = []
            for row in results:
                responsable = {}
                for i, value in enumerate(row):
                    column_name = columns[i].lower()
                    
                    # Limpiar strings (quitar espacios)
                    if isinstance(value, str):
                        responsable[column_name] = value.strip()
                    else:
                        responsable[column_name] = value
                
                responsables.append(responsable)
            
            cursor.close()
            
            return JsonResponse({
                'success': True,
                'data': responsables,
                'total': len(responsables),
                'message': f'Se encontraron {len(responsables)} responsables'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener responsables: {str(e)}',
                'data': []
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TipoCambioViewAJS(View):
    """
    Clase para obtener el tipo de cambio según la fecha
    Ejecuta la consulta: SELECT FECHA,T_COMPRA FROM TCAMBIO WHERE FECHA = ?
    """
    
    def get(self, request, *args, **kwargs):
        """
        Método GET para obtener el tipo de cambio
        Parámetros esperados:
        - fecha: fecha en formato YYYY-MM-DD
        """
        try:
            # Obtener la fecha del request
            fecha = request.GET.get('fecha')
            
            print(f"🔍 Consultando tipo de cambio para fecha: {fecha}")
            
            # Validar que se proporcione la fecha
            if not fecha:
                return JsonResponse({
                    'success': False,
                    'message': 'El parámetro fecha es obligatorio'
                }, status=400)
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Ejecutar consulta
            resultado = self._obtener_tipo_cambio(fecha)
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'data': resultado,
                    'message': 'Tipo de cambio obtenido correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró tipo de cambio para la fecha {fecha}',
                    'data': []
                })
                
        except Exception as e:
            print(f"❌ Error en TipoCambioView: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def post(self, request, *args, **kwargs):
        """
        Método POST para obtener el tipo de cambio
        Permite enviar la fecha en el body del request
        """
        try:
            # Obtener datos del body
            data = json.loads(request.body)
            fecha = data.get('fecha')
            
            print(f"🔍 Consultando tipo de cambio (POST) para fecha: {fecha}")
            
            # Validar que se proporcione la fecha
            if not fecha:
                return JsonResponse({
                    'success': False,
                    'message': 'El parámetro fecha es obligatorio'
                }, status=400)
            
            # Validar formato de fecha
            try:
                datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)
            
            # Ejecutar consulta
            resultado = self._obtener_tipo_cambio(fecha)
            
            if resultado:
                return JsonResponse({
                    'success': True,
                    'data': resultado,
                    'message': 'Tipo de cambio obtenido correctamente'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'No se encontró tipo de cambio para la fecha {fecha}',
                    'data': []
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            print(f"❌ Error en TipoCambioView (POST): {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
    
    def _obtener_tipo_cambio(self, fecha):
        """
        Ejecuta la consulta SQL para obtener el tipo de cambio
        """
        try:
            cursor = connection_inversioneajs.cursor()
            
            print(f"🔄 Ejecutando consulta SQL para fecha: {fecha}")
            
            # Ejecutar la consulta exacta que proporcionaste
            query = "SELECT FECHA, T_VENTA FROM TCAMBIO WHERE FECHA = ?"
            cursor.execute(query, [fecha])
            
            # Obtener resultados
            columns = [desc[0] for desc in cursor.description]
            resultados_raw = cursor.fetchall()
            
            print(f"📊 Resultados obtenidos: {len(resultados_raw)} registros")
            
            # Convertir resultados a lista de diccionarios (formato JSON)
            resultados = []
            for row in resultados_raw:
                resultado = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Formatear fecha para que coincida con el formato esperado
                    if column_name == 'FECHA' and isinstance(value, datetime):
                        resultado[column_name] = value.strftime('%Y-%m-%dT%H:%M:%S')
                    else:
                        resultado[column_name] = value
                
                resultados.append(resultado)
            
            cursor.close()
            return resultados
            
        except Exception as e:
            print(f"❌ Error ejecutando consulta de tipo de cambio: {str(e)}")
            raise


#############################################################################################
# SALIDAS INTERNAS DOCUMENTO - INVERSIONES AJS
##############################################################################################

class GetSalidaInternaDocumentAJS(View):
    """
    API para obtener los datos de una salida interna mediante procedimiento almacenado
    Devuelve dos conjuntos de datos: encabezado y detalle
    """
    
    def get(self, request, *args, **kwargs):
        try:
            # Obtener el ID de salida desde los parámetros de la URL
            id_salida = self.kwargs.get('id_salida')
            
            # Validar que se proporcione el ID
            if not id_salida:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'ID de salida interna es requerido'
                }, status=400)

            # Ejecutar el procedimiento almacenado
            with connection_inversioneajs.cursor() as cursor:
                cursor.execute("EXEC PROC_GET_SALIDA_INTERNA_DOCUMENT ?", [id_salida])
                
                # Obtener el primer conjunto de resultados (encabezado)
                encabezado_raw = cursor.fetchall()
                encabezado_columns = [col[0] for col in cursor.description]
                
                # Avanzar al siguiente conjunto de resultados (detalle)
                cursor.nextset()
                detalle_raw = cursor.fetchall()
                detalle_columns = [col[0] for col in cursor.description]
                
                # ❌ REMOVER ESTA LÍNEA - el 'with' statement se encarga del cierre
                # cursor.close()

            # Procesar el encabezado (debe ser solo un registro)
            if not encabezado_raw:
                return JsonResponse({
                    'status': 'ERROR',
                    'message': 'No se encontró la salida interna especificada'
                }, status=404)

            # Convertir encabezado a diccionario
            encabezado = dict(zip(encabezado_columns, encabezado_raw[0]))
            
            # Convertir detalle a lista de diccionarios
            detalle = []
            for row in detalle_raw:
                detalle.append(dict(zip(detalle_columns, row)))

            # Estructura de respuesta JSON
            response_data = {
                'status': 'SUCCESS',
                'message': 'Datos obtenidos correctamente',
                'data': {
                    'encabezado': encabezado,
                    'detalle': detalle,
                    'resumen': {
                        'total_items': len(detalle),
                        'fecha_consulta': encabezado.get('FECHA_IMPRESION', ''),
                        'hora_consulta': encabezado.get('HORA_IMPRESION', '')
                    }
                }
            }

            return JsonResponse(response_data, safe=False)

        except Exception as e:
            # Manejo de errores
            import logging
            logging.error(f"Error en GetSalidaInternaDocument: {str(e)}")
            
            return JsonResponse({
                'status': 'ERROR',
                'message': 'Error interno del servidor',
                'error_detail': str(e)
            }, status=500)

#====================================================================================================================
    # REPORTE DE ALMACEN
#====================================================================================================================

class ReportesView_ajs (TemplateView):
    permission_required = 'modulo_almacen' 
    template_name = 'ALMACEN/components/InversionesAJS/report/reporte_productos_ajs.html'

####################################################################################################################################
# FASE FINAL
####################################################################################################################################

# API para la fase final tabla principal
@method_decorator(csrf_exempt, name='dispatch')
class FaseFinalEvaluacionesView(View):
    """
    Vista para manejar la fase final de evaluaciones de desempeno
    Permite consultar evaluaciones con porcentajes de avance final de objetivos y competencias
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros opcionales
            id_area = request.GET.get('id_area')
            id_evaluacion = request.GET.get('id_evaluacion')
            periodo = request.GET.get('campania')  # Mantener 'campania' como nombre del parámetro para compatibilidad
            
            # Si no se proporciona periodo, usar el año actual
            if not periodo:
                periodo = '2025'
            
            # Extraer solo el año si viene en formato CAMP2026
            if periodo.startswith('CAMP'):
                periodo = periodo.replace('CAMP', '')
            
            if id_evaluacion:
                # Si se solicita una evaluacion específica, usar el procedimiento de detalles
                cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES @id_evaluacion=?, @periodo=?", [id_evaluacion, periodo])
                
                # Obtener informacion general de la evaluacion
                columns = [column[0] for column in cursor.description]
                evaluacion_info = cursor.fetchone()
                
                if not evaluacion_info:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Evaluacion no encontrada'
                    }, status=404)
                
                evaluacion_data = dict(zip(columns, evaluacion_info))
                
                # Obtener objetivos (segundo resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    obj_columns = [column[0] for column in cursor.description]
                    objetivos = []
                    for row in cursor.fetchall():
                        objetivo = dict(zip(obj_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                            objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                        if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                            objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                        objetivos.append(objetivo)
                else:
                    objetivos = []
                
                # Obtener competencias (tercer resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    comp_columns = [column[0] for column in cursor.description]
                    competencias = []
                    for row in cursor.fetchall():
                        competencia = dict(zip(comp_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in competencia and competencia['fecha_inicio']:
                            competencia['fecha_inicio'] = competencia['fecha_inicio']
                        if 'fecha_fin' in competencia and competencia['fecha_fin']:
                            competencia['fecha_fin'] = competencia['fecha_fin']
                        competencias.append(competencia)
                else:
                    competencias = []
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Detalles de evaluacion final obtenidos correctamente',
                    'data': {
                        'evaluacion': evaluacion_data,
                        'objetivos': objetivos,
                        'competencias': competencias
                    }
                })
                
            else:
                # Obtener lista general de evaluaciones para la fase final
                if id_area:
                    cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES @id_area=?, @periodo=?", [id_area, periodo])
                else:
                    cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES @periodo=?", [periodo])
                
                # ✅ FIX: proteger cuando el SP no devuelve columnas (ej: CAMP2025)
                if not cursor.description:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No hay evaluaciones para el periodo seleccionado',
                        'data': [],
                        'total_evaluaciones': 0,
                        'filtros_aplicados': {
                            'id_area': id_area,
                            'periodo': periodo
                        }
                    })
                # Obtener los nombres de las columnas
                columns = [column[0] for column in cursor.description]
                
                # Convertir los resultados a una lista de diccionarios
                evaluaciones = []
                for row in cursor.fetchall():
                    evaluacion = dict(zip(columns, row))
                    
                    # Convertir fecha a string para JSON si existe
                    if 'fecha_evaluacion' in evaluacion and evaluacion['fecha_evaluacion']:
                        evaluacion['fecha_evaluacion'] = evaluacion['fecha_evaluacion'].strftime('%Y-%m-%d')
                    
                    # Asegurar que los porcentajes sean ne�meros enteros (usar los mismos campos que fase intermedia)
                    for field in ['porcentaje_objetivos', 'porcentaje_competencias', 'porcentaje_general']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(float(evaluacion[field]))
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que los contadores sean ne�meros enteros
                    for field in ['total_objetivos', 'objetivos_con_avance', 'total_competencias', 'competencias_con_avance']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(evaluacion[field])
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que el estado sea booleano
                    if 'estado' in evaluacion:
                        evaluacion['estado'] = bool(evaluacion['estado'])
                    
                    evaluaciones.append(evaluacion)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluaciones de fase final obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'filtros_aplicados': {
                        'id_area': id_area,
                        'periodo': periodo
                    },
                    'debug_info': {
                        'columns_found': columns,
                        'sample_data': evaluaciones[0] if evaluaciones else None
                    }
                })
                
        except Exception as e:
            print(f"Error en FaseFinalEvaluacionesView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener datos de fase final: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


# API para los detalles de la fase final
@method_decorator(csrf_exempt, name='dispatch')
class DetallesEvaluacionFinalModalView(View):
    """
    Vista para obtener detalles finales de objetivos o competencias para el modal de avance final
    Ejecuta el procedimiento almacenado SP_OBTENER_DETALLES_EVALUACION_FINAL_MODAL
    
    Pare�metros:
    - id_evaluacion: ID de la evaluacion (requerido)
    - tipo: Tipo de tabla (1 = Objetivos, 2 = Competencias) (requerido)
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener pare�metros de la URL
            id_evaluacion = request.GET.get('id_evaluacion')
            tipo_tabla = request.GET.get('tipo')  # 1 = Objetivos, 2 = Competencias
            cargar_comentarios = request.GET.get('cargar_comentarios')  # Para cargar solo comentarios finales
            
            # Si se solicita cargar solo comentarios finales
            if cargar_comentarios == 'true' and id_evaluacion:
                try:
                    id_evaluacion_int = int(id_evaluacion)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El pare�metro id_evaluacion debe ser un ne�mero ve�lido'
                    }, status=400)
                
                # Consultar comentarios finales de la tabla RRHH_EVALUACIONES
                try:
                    cursor.execute("""
                        SELECT 
                            comentarios_objetivos_general_final,
                            comentarios_competencias_general_final
                        FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion_int])
                except Exception as query_error:
                    print(f"Error al consultar campos espece�ficos, usando campos este�ndar: {query_error}")
                    # Si falla, usar campos este�ndar
                    cursor.execute("""
                        SELECT 
                            comentarios_objetivos_general,
                            comentarios_competencias_general
                        FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion_int])
                
                resultado = cursor.fetchone()
                
                if resultado:
                    comentarios = {
                        'comentarios_objetivos_general_final': resultado[0] or '',
                        'comentarios_competencias_general_final': resultado[1] or ''
                    }
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Comentarios finales obtenidos correctamente',
                        'comentarios': comentarios,
                        'id_evaluacion': id_evaluacion_int
                    })
                else:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No se encontraron comentarios finales para esta evaluacion',
                        'comentarios': {
                            'comentarios_objetivos_general_final': '',
                            'comentarios_competencias_general_final': ''
                        },
                        'id_evaluacion': id_evaluacion_int
                    })
            
            # Validar pare�metros requeridos para obtener detalles
            if not id_evaluacion or not tipo_tabla:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los pare�metros id_evaluacion y tipo'
                }, status=400)
            
            # Validar que sean ne�meros ve�lidos
            try:
                id_evaluacion_int = int(id_evaluacion)
                tipo_tabla_int = int(tipo_tabla)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Los pare�metros id_evaluacion y tipo deben ser ne�meros ve�lidos'
                }, status=400)
            
            # Validar que tipo_tabla sea 1 o 2
            if tipo_tabla_int not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El pare�metro tipo debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            print(f"Ejecutando procedimiento final con: id_evaluacion={id_evaluacion_int}, tipo_tabla={tipo_tabla_int}")
            
            # Ejecutar el mismo procedimiento almacenado que la fase intermedia
            cursor.execute(
                "EXEC SP_OBTENER_DETALLES_EVALUACION_MODAL @id_evaluacion = ?, @tipo_tabla = ?", 
                [id_evaluacion_int, tipo_tabla_int]
            )
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            # Convertir los resultados a una lista de diccionarios
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(columns, row))
                
                # Procesar fechas para objetivos
                if tipo_tabla_int == 1:  # Objetivos
                    # Convertir fechas a string si existen y no son None
                    for fecha_field in ['fecha_inicio', 'fecha_fin']:
                        if fecha_field in detalle and detalle[fecha_field]:
                            if hasattr(detalle[fecha_field], 'strftime'):
                                detalle[fecha_field] = detalle[fecha_field].strftime('%Y-%m-%d')
                    
                    # Mantener fechas formateadas como string
                    for formato_field in ['fecha_inicio_formato', 'fecha_fin_formato']:
                        if formato_field in detalle and detalle[formato_field]:
                            detalle[formato_field] = str(detalle[formato_field])
                
                # Asegurar que los porcentajes sean ne�meros enteros
                # Para fase final, usar el campo porc_etapa_final si existe, sino usar porcentaje_actual
                if 'porc_etapa_final' in detalle:
                    detalle['porc_etapa_final'] = int(detalle['porc_etapa_final']) if detalle['porc_etapa_final'] is not None else 0
                else:
                    # Si no existe porc_etapa_final, usar porcentaje_actual como base
                    detalle['porc_etapa_final'] = int(detalle.get('porcentaje_actual', 0)) if detalle.get('porcentaje_actual') is not None else 0
                
                if 'porcentaje_actual' in detalle:
                    detalle['porcentaje_actual'] = int(detalle['porcentaje_actual']) if detalle['porcentaje_actual'] is not None else 0
                
                # Asegurar que los campos de comentarios finales existen sege�n el tipo
                if tipo_tabla_int == 1:  # Objetivos
                    if 'coment_objetivo_ff' not in detalle:
                        detalle['coment_objetivo_ff'] = ''  # Solo usar campo espece�fico, sin fallback
                else:  # Competencias
                    if 'coment_competencia_ff' not in detalle:
                        detalle['coment_competencia_ff'] = ''  # Solo usar campo espece�fico, sin fallback
                
                # Consulta adicional para obtener comentarios finales espece�ficos de este registro
                try:
                    registro_id = detalle.get('id')
                    if registro_id:
                        tabla_consulta = "RRHH_OBJETIVOS" if tipo_tabla_int == 1 else "RRHH_COMPETENCIAS"
                        cursor_extra = connection_portalaei.cursor()
                        
                        # Usar el campo correcto sege�n el tipo de tabla
                        if tipo_tabla_int == 1:  # Objetivos
                            cursor_extra.execute(f"""
                                SELECT coment_objetivo_ff, porc_etapa_final 
                                FROM {tabla_consulta} 
                                WHERE id = ? AND estado = 1
                            """, [registro_id])
                        else:  # Competencias
                            cursor_extra.execute(f"""
                                SELECT coment_competencia_ff, porc_etapa_final 
                                FROM {tabla_consulta} 
                                WHERE id = ? AND estado = 1
                            """, [registro_id])
                        
                        resultado_extra = cursor_extra.fetchone()
                        if resultado_extra:
                            # Sobreescribir con datos espece�ficos de fase final (sin fallbacks)
                            if tipo_tabla_int == 1:  # Objetivos
                                detalle['coment_objetivo_ff'] = resultado_extra[0] or ''
                            else:  # Competencias
                                detalle['coment_competencia_ff'] = resultado_extra[0] or ''
                            if resultado_extra[1] is not None:
                                detalle['porc_etapa_final'] = int(resultado_extra[1])
                        cursor_extra.close()
                except Exception as e:
                    print(f"Error al consultar datos espece�ficos de fase final: {e}")
                    # Continuar con los datos be�sicos
                
                # Asegurar que las puntuaciones sean ne�meros enteros
                for field in ['puntuacion_no_cumple', 'puntuacion_cumple', 'puntuacion_excede', 'puntuacion_sobresaliente']:
                    if field in detalle:
                        detalle[field] = int(detalle[field]) if detalle[field] is not None else 0
                
                # Asegurar que campos nume�ricos espece�ficos sean enteros
                for field in ['duracion_dias', 'dias_restantes']:
                    if field in detalle and detalle[field] is not None:
                        detalle[field] = int(detalle[field])
                
                detalles.append(detalle)
            
            # Determinar el nombre del tipo para la respuesta
            tipo_nombre = "objetivos" if tipo_tabla_int == 1 else "competencias"
            
            print(f"Procedimiento final ejecutado correctamente. Registros encontrados: {len(detalles)}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'{tipo_nombre.title()} finales obtenidos correctamente',
                'data': detalles,
                'total_registros': len(detalles),
                'id_evaluacion': id_evaluacion_int,
                'tipo': tipo_nombre
            })
            
        except Exception as e:
            print(f"Error en DetallesEvaluacionFinalModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener detalles finales: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def put(self, request, *args, **kwargs):
        """
        Actualizar porcentajes de avance final para me�ltiples objetivos o competencias
        Incluye actualizacion de comentarios generales finales en la tabla RRHH_EVALUACIONES
        
        Estructura esperada del JSON:
        {
            "tipo": 1 o 2 (1=Objetivos, 2=Competencias),
            "id_evaluacion": 189,
            "actualizaciones": [
                {
                    "id": 123,
                    "porc_etapa_final": 85,
                    "coment_objetivo_ff": "Comentario final del objetivo"
                },
                {
                    "id": 124,
                    "porc_etapa_final": 70,
                    "coment_objetivo_ff": "Otro comentario final"
                }
            ],
            "comentarios_objetivos_general_final": "Comentario general final para objetivos...",
            "comentarios_competencias_general_final": "Comentario general final para competencias..."
        }
        """
        cursor = None
        try:
            # Parsear los datos JSON del request
            data = json.loads(request.body)
            
            # Validar estructura be�sica de datos
            if 'tipo' not in data or 'actualizaciones' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los campos "tipo" y "actualizaciones"'
                }, status=400)
            
            tipo_tabla = data['tipo']
            actualizaciones = data['actualizaciones']
            id_evaluacion = data.get('id_evaluacion')
            
            # Obtener comentarios generales finales del request
            comentarios_objetivos_general_final = data.get('comentarios_objetivos_general_final', '')
            comentarios_competencias_general_final = data.get('comentarios_competencias_general_final', '')
            
            # Validar tipo de tabla
            if tipo_tabla not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El campo "tipo" debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            # Validar que hay actualizaciones
            if not actualizaciones or not isinstance(actualizaciones, list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requiere al menos una actualizacion en el array "actualizaciones"'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            # Determinar tabla y campo sege�n el tipo
            if tipo_tabla == 1:  # Objetivos
                tabla = "RRHH_OBJETIVOS"
                id_campo = "id"
            else:  # Competencias
                tabla = "RRHH_COMPETENCIAS"
                id_campo = "id"
            
            actualizaciones_exitosas = []
            actualizaciones_fallidas = []
            
            # Procesar cada actualizacion de porcentajes finales
            for actualizacion in actualizaciones:
                try:
                    # Validar estructura de cada actualizacion
                    if 'id' not in actualizacion or 'porc_etapa_final' not in actualizacion:
                        actualizaciones_fallidas.append({
                            'registro': actualizacion,
                            'error': 'Faltan campos "id" o "porc_etapa_final"'
                        })
                        continue
                    
                    registro_id = actualizacion['id']
                    porcentaje_final = actualizacion['porc_etapa_final']
                    # Usar el campo correcto sege�n el tipo de tabla
                    if tipo_tabla == 1:  # Objetivos
                        comentario_final = actualizacion.get('coment_objetivo_ff', '')
                    else:  # Competencias
                        comentario_final = actualizacion.get('coment_competencia_ff', '')
                    
                    # Validar que el ID sea un ne�mero ve�lido
                    try:
                        registro_id = int(registro_id)
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'ID debe ser un ne�mero ve�lido'
                        })
                        continue
                    
                    # Validar que el porcentaje este� en el rango ve�lido
                    try:
                        porcentaje_final = float(porcentaje_final)
                        if porcentaje_final < 0 or porcentaje_final > 130:
                            actualizaciones_fallidas.append({
                                'id': registro_id,
                                'error': 'El porcentaje debe estar entre 0 y 130'
                            })
                            continue
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'El porcentaje debe ser un ne�mero ve�lido'
                        })
                        continue
                    
                    # Verificar que el registro existe
                    cursor.execute(f"""
                        SELECT {id_campo} FROM {tabla} 
                        WHERE {id_campo} = ? AND estado = 1
                    """, [registro_id])
                    
                    if not cursor.fetchone():
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': f'{"Objetivo" if tipo_tabla == 1 else "Competencia"} no encontrado o inactivo'
                        })
                        continue
                    
                    # Realizar la actualizacion del porcentaje final y comentario final
                    # Usar el campo correcto sege�n el tipo de tabla
                    try:
                        if tipo_tabla == 1:  # Objetivos
                            cursor.execute(f"""
                                UPDATE {tabla} 
                                SET porc_etapa_final = ?, coment_objetivo_ff = ?
                                WHERE {id_campo} = ?
                            """, [porcentaje_final, comentario_final, registro_id])
                        else:  # Competencias
                            cursor.execute(f"""
                                UPDATE {tabla} 
                                SET porc_etapa_final = ?, coment_competencia_ff = ?
                                WHERE {id_campo} = ?
                            """, [porcentaje_final, comentario_final, registro_id])
                    except Exception as update_error:
                        print(f"Error al actualizar con campos espece�ficos, intentando con campos este�ndar: {update_error}")
                        # Si falla, usar campos este�ndar de la fase intermedia
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porcentaje_actual = ?, comentarios = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_final, comentario_final, registro_id])
                    
                    # Verificar que se actualizo al menos una fila
                    if cursor.rowcount > 0:
                        # Usar el campo correcto en el log sege�n el tipo de tabla
                        if tipo_tabla == 1:  # Objetivos
                            campo_comentario = 'coment_objetivo_ff'
                        else:  # Competencias
                            campo_comentario = 'coment_competencia_ff'
                        
                        actualizaciones_exitosas.append({
                            'id': registro_id,
                            'porc_etapa_final_anterior': None,
                            'porc_etapa_final_nuevo': porcentaje_final,
                            campo_comentario: comentario_final
                        })
                    else:
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'No se pudo actualizar el registro'
                        })
                    
                except Exception as e:
                    actualizaciones_fallidas.append({
                        'id': actualizacion.get('id', 'desconocido'),
                        'error': f'Error al procesar actualizacion final: {str(e)}'
                    })
                    continue
            
            # Actualizar comentarios generales finales en la tabla RRHH_EVALUACIONES
            comentarios_actualizados = False
            if id_evaluacion:
                try:
                    # Verificar que la evaluacion existe
                    cursor.execute("""
                        SELECT id FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion])
                    
                    if cursor.fetchone():
                        # Actualizar comentarios finales sege�n el tipo
                        try:
                            if tipo_tabla == 1:  # Objetivos
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_objetivos_general_final = ?
                                    WHERE id = ?
                                """, [comentarios_objetivos_general_final, id_evaluacion])
                            else:  # Competencias
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_competencias_general_final = ?
                                    WHERE id = ?
                                """, [comentarios_competencias_general_final, id_evaluacion])
                        except Exception as comment_error:
                            print(f"Error al actualizar comentarios espece�ficos, usando campos este�ndar: {comment_error}")
                            # Si falla, usar campos este�ndar
                            if tipo_tabla == 1:  # Objetivos
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_objetivos_general = ?
                                    WHERE id = ?
                                """, [comentarios_objetivos_general_final, id_evaluacion])
                            else:  # Competencias
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_competencias_general = ?
                                    WHERE id = ?
                                """, [comentarios_competencias_general_final, id_evaluacion])
                        
                        if cursor.rowcount > 0:
                            comentarios_actualizados = True
                            print(f"Comentarios generales finales actualizados para evaluacion {id_evaluacion}")
                    else:
                        print(f"Evaluacion {id_evaluacion} no encontrada o inactiva")
                        
                except Exception as e:
                    print(f"Error al actualizar comentarios generales finales: {str(e)}")
                    # No fallar toda la operacion por comentarios, solo registrar el error
            
            # Confirmar todas las transacciones si hay al menos una actualizacion exitosa
            if actualizaciones_exitosas or comentarios_actualizados:
                connection_portalaei.commit()
            
            # Determinar el estado de la respuesta
            total_actualizaciones = len(actualizaciones)
            exitosas = len(actualizaciones_exitosas)
            fallidas = len(actualizaciones_fallidas)
            
            if exitosas == total_actualizaciones:
                status_code = 200
                message = f"Todas las actualizaciones finales fueron exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales finales actualizados"
                status = 'success'
            elif exitosas > 0:
                status_code = 207  # Multi-Status
                message = f"Actualizaciones finales parcialmente exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales finales actualizados"
                status = 'partial_success'
            else:
                if comentarios_actualizados:
                    status_code = 200
                    message = "Comentarios generales finales actualizados correctamente"
                    status = 'success'
                else:
                    status_code = 400
                    message = f"Ninguna actualizacion final fue exitosa (0/{total_actualizaciones})"
                    status = 'error'
            
            tipo_nombre = "objetivos" if tipo_tabla == 1 else "competencias"
            
            print(f"Actualizacion final de {tipo_nombre}: {exitosas} exitosas, {fallidas} fallidas, comentarios: {comentarios_actualizados}")
            
            return JsonResponse({
                'status': status,
                'message': message,
                'data': {
                    'tipo': tipo_nombre,
                    'total_procesadas': total_actualizaciones,
                    'exitosas': exitosas,
                    'fallidas': fallidas,
                    'comentarios_actualizados': comentarios_actualizados,
                    'id_evaluacion': id_evaluacion,
                    'actualizaciones_exitosas': actualizaciones_exitosas,
                    'actualizaciones_fallidas': actualizaciones_fallidas
                }
            }, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inve�lido'
            }, status=400)
            
        except Exception as e:
            # En caso de error general, hacer rollback
            if cursor:
                try:
                    connection_portalaei.rollback()
                except:
                    pass
            
            print(f"Error en PUT DetallesEvaluacionFinalModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


