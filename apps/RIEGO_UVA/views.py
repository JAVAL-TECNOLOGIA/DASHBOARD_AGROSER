from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from apps.connection.connect_donluis import connection_donluis
from apps.connection.connect_campoverde import connection_campoverde
from apps.connection.connect_inversioneajs import connection_inversioneajs
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.connection.connect_portalaei import connection_portalaei
from decimal import Decimal
import json
from django.db import connection
from django.db import IntegrityError






# PRESUPUESTO

class presupuesto_dl(TemplateView):
    permission_required = 'modulo_produccion_palta'
    template_name = 'RIEGO_UVA/pages/riegouva_presupuesto_dl.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return context

#==============================================================================================
# SERVICIOS
#==============================================================================================


#REPORTE DE TOTALES DE SERVICIOS

def Costo_servicio_totals(request):
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:

        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '24', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '24'
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
        data = json.loads(request.body)
        try:
            cursor = connection_portalaei.cursor()

            # # Verificar si ya existe la observación para esta área
            # check_query = """
            # SELECT COUNT(*) 
            #     FROM TIC_servicios 
            #     WHERE observacion = ? 
            #     AND id_area = ? 
            #     AND observacion IS NOT NULL
            # """
            # observacion = data.get('observacion', '').strip()  # Eliminar espacios en blanco
            # area_id = data.get('id_area', 24)
            # if observacion:  # Solo verificar si hay una observación
            #     cursor.execute(check_query, [observacion, area_id])
            #     count = cursor.fetchone()[0]
                
            #     if count > 0:
            #         return JsonResponse({
            #             'status': 'error',
            #             'message': 'Ya existe un servicio con esta observación en esta área'
            #         }, status=400)
            
            # id_campania = data.get('ID_CAMPANIA')
            
            query = """
            INSERT INTO TIC_servicios (
                idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,
                USUARIO,id_area,ID_CAMPANIA
            ) VALUES (?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            id_campania = data.get('ID_CAMPANIA')
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
            
            values.extend([request.user.id,24,id_campania]) 

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
            # campania = request.GET.get('year', '')

            if id:
                query = """
                SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario,observacion,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio, ID_CAMPANIA
                FROM TIC_servicios
                WHERE id = ?  AND id_area = 24
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
                campania = request.GET.get('year', '')
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
                    WHERE id_area = 24 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24
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
            area_id = data.get('id_area', 24)
            if observacion:
                cursor.execute(check_query, [observacion, area_id, id])
                count = cursor.fetchone()[0]
                
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

            
            values.extend([request.user.id,24, id])
            
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
    campania = request.GET.get('year', '')  # valor por defecto

    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s, %s
            """, [24, campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s
            """, [24])

        results = dict(cursor.fetchall())
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
            # Obtener ID_CAMPANIA del body
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
            
            values.extend([request.user.id,24,1,id_campania])


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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 1
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
                    WHERE id_area = 24 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,24,1])
            
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
            
            values.extend([request.user.id,24,5,id_campania])
            
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
                AND id_area = 24
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
                    WHERE id_area = 24 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,24,5])
            
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
            values.extend([request.user.id,24,7,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 7
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
                WHERE id_area = 24 AND id_tipo_suministro = 7
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
                    WHERE id_area = 24 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 24 
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
            values.extend([request.user.id,24,7])
            
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
            values.extend([request.user.id,24,8,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 8
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
                WHERE id_area = 24 AND id_tipo_suministro = 8
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
                    WHERE id_area = 24 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,24,8])


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
            
            values.extend([request.user.id,24,4,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 4
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
                WHERE id_area = 24 AND id_tipo_suministro = 4
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
                    WHERE id_area = 24 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,24,4])
            
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
            values.extend([request.user.id,24,2,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 2
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
                WHERE id_area = 24 AND id_tipo_suministro = 2
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
                    WHERE id_area = 24 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,24,2])
                
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
            values.extend([request.user.id,24,9,id_campania])
            
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 9
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
                WHERE id_area = 24 AND id_tipo_suministro = 9
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
                    WHERE id_area = 24 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,24,9])
                
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
            values.extend([request.user.id,24,3,id_campania])


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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 3
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
                WHERE id_area = 24 AND id_tipo_suministro = 3
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
                    WHERE id_area = 24 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,24,3])
            
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
            values.extend([request.user.id,24,6,id_campania])
            
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 6
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
                WHERE id_area = 24 AND id_tipo_suministro = 6
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
                    WHERE id_area = 24 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,24,6])
            
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
# FECHA: 224/11/2024
#==============================================================================================


def Costos_capex_totals(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            EXEC RPT_PST_CAPEX '24'
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
            id_area = data.get('id_area', 24)
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
                if cursor.fetchone()[0] > 0:
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
                WHERE id = ? AND id_area = 24 
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
                    WHERE id_area = 24 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24
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
            WHERE id = ? AND id_area = 24
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
                24,
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
# FECHA: 224/11/2024
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
                24,  # id_area
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
                WHERE id = ? AND id_area = 24 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 24 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 24 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_remuneracion = 1
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
                24,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [24, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [24, 1])
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
                24,  # id_area
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
                WHERE id = ? AND id_area = 24 AND id_remuneracion = 2
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
                    WHERE id_area = 24 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 24 AND id_remuneracion = 2
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
                24,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [24, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [24, 2])
                        
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
# CAMPO VERDE - TECNOLOGIA DE LA INFORMACION
#================================================================================================================



class presupuesto_cv(TemplateView):
    permission_required = 'modulo_produccion_palta'
    template_name = 'RIEGO_UVA/pages/riegouva_presupuesto_cv.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return context

#==============================================================================================
# SERVICIOS
#==============================================================================================


class presupuesto_controller_cv(TemplateView):
    permission_required = 'modulo_calidad'
    template_name = 'CONTROLLER_PROD/pages/controller_presupuesto_cv.html'

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
                EXEC TOTAL_SERVICIOS_CV '24', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '24'
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
            area_id = data.get('id_area', 24)
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
            values.append(24) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 24
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
                    WHERE id_area = 24 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24
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
            area_id = data.get('id_area', 24)
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

            
            values.extend([request.user.id,24, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s, %s", [24, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s", [24])

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
            
            values.extend([request.user.id,24,1,id_campania])


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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 1
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
                    WHERE id_area = 24 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,24,1])
            
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
            
            values.extend([request.user.id,24,5,id_campania])
            
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
                AND id_area = 24
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
                    WHERE id_area = 24 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,24,5])
            
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
            values.extend([request.user.id,24,7,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 7
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
                WHERE id_area = 24 AND id_tipo_suministro = 7
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
                    WHERE id_area = 24 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 24 
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
            values.extend([request.user.id,24,7])
            
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
            values.extend([request.user.id,24,8,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 8
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
                WHERE id_area = 24 AND id_tipo_suministro = 8
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
                    WHERE id_area = 24 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,24,8])


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
            
            values.extend([request.user.id,24,4,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 4
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
                WHERE id_area = 24 AND id_tipo_suministro = 4
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
                    WHERE id_area = 24 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,24,4])
            
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
            values.extend([request.user.id,24,2,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 2
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
                WHERE id_area = 24 AND id_tipo_suministro = 2
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
                    WHERE id_area = 24 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,24,2])
                
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
            values.extend([request.user.id,24,9,id_campania])
            
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 9
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
                WHERE id_area = 24 AND id_tipo_suministro = 9
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
                    WHERE id_area = 24 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,24,9])
                
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
            values.extend([request.user.id,24,3,id_campania])


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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 3
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
                WHERE id_area = 24 AND id_tipo_suministro = 3
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
                    WHERE id_area = 24 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,24,3])
            
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
            values.extend([request.user.id,24,6,id_campania])
            
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 6
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
                WHERE id_area = 24 AND id_tipo_suministro = 6
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
                    WHERE id_area = 24 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,24,6])
            
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
# FECHA: 224/11/2024
#==============================================================================================


def Costos_capex_totals_cv(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '24', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '24'
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
            id_area = data.get('id_area', 24)
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
                WHERE id = ? AND id_area = 24 
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
                    WHERE id_area = 24 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24
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
            WHERE id = ? AND id_area = 24
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
                24,
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
# FECHA: 224/11/2024
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
                24,  # id_area
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
                WHERE id = ? AND id_area = 24 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 24 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 24 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_remuneracion = 1
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
                24,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [24, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [24, 1])
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
                24,  # id_area
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
                WHERE id = ? AND id_area = 24 AND id_remuneracion = 2
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
                    WHERE id_area = 24 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 24 AND id_remuneracion = 2
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
                24,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [24, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [24, 2])
                        
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
#FECHA: 06/01/2024
#MODIFICACIONES: 
# 01/01/2024: Se crea el modulo de presupuestos
#=================================================================================================================







# PRESUPUESTO

class presupuesto_ajs(TemplateView):
    permission_required = 'modulo_produccion_palta'
    template_name = 'RIEGO_UVA/pages/riegouva_presupuesto_ajs.html'

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
                EXEC TOTAL_SERVICIOS_AJS '24', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_AJS '24'
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
            area_id = data.get('id_area', 24)
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
            values.append(24) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 24
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
                    WHERE id_area = 24 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24
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
            area_id = data.get('id_area', 24)
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

            
            values.extend([request.user.id,24, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s, %s", [24, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s", [24])

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
            
            values.extend([request.user.id,24,1,id_campania])


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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 1
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
                    WHERE id_area = 24 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,24,1])
            
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
            
            values.extend([request.user.id,24,5,id_campania])
            
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
                AND id_area = 24
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
                    WHERE id_area = 24 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,24,5])
            
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
            values.extend([request.user.id,24,24,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 7
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
                WHERE id_area = 24 AND id_tipo_suministro = 7
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
                    WHERE id_area = 24 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 24 
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
            values.extend([request.user.id,24,24])
            
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
            values.extend([request.user.id,24,8,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 8
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
                WHERE id_area = 24 AND id_tipo_suministro = 8
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
                    WHERE id_area = 24 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,24,8])


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
            
            values.extend([request.user.id,24,4,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 4
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
                WHERE id_area = 24 AND id_tipo_suministro = 4
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
                    WHERE id_area = 24 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,24,4])
            
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
            values.extend([request.user.id,24,2,id_campania])

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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 2
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
                WHERE id_area = 24 AND id_tipo_suministro = 2
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
                    WHERE id_area = 24 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,24,2])
                
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
            values.extend([request.user.id,24,9,id_campania])
            
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 9
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
                WHERE id_area = 24 AND id_tipo_suministro = 9
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
                    WHERE id_area = 24 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,24,9])
                
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
            values.extend([request.user.id,24,3,id_campania])


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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 3
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
                WHERE id_area = 24 AND id_tipo_suministro = 3
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
                    WHERE id_area = 24 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,24,3])
            
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
            values.extend([request.user.id,24,6,id_campania])
            
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
                WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 6
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
                WHERE id_area = 24 AND id_tipo_suministro = 6
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
                    WHERE id_area = 24 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 24 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,24,6])
            
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
# FECHA: 224/11/2024
#==============================================================================================


def Costos_capex_totals_ajs(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '24', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '24'
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
            id_area = data.get('id_area', 24)
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
                WHERE id = ? AND id_area = 24 
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
                    WHERE id_area = 24 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24
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
            WHERE id = ? AND id_area = 24
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
                24,
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
# FECHA: 224/11/2024
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
                24,  # id_area
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
                WHERE id = ? AND id_area = 24 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 24 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 24 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 24 AND id_remuneracion = 1
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
                24,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [24, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [24, 1])
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
                24,  # id_area
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
                WHERE id = ? AND id_area = 24 AND id_remuneracion = 2
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
                    WHERE id_area = 24 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 24 AND id_remuneracion = 2
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
                24,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [24, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [24, 2])
                        
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


@method_decorator(csrf_exempt, name='dispatch')
class ResumenFertilizacionView(View):

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()

            if id:
                query = """
                SELECT p.ID, p.IDUSUARIO, p.IDVARIEDAD, p.IDFASE, p.IDLOTE, p.NOMBRE, 
                       p.FECHA_INICIO, p.FECHA_FIN, p.DESCRIPCION, p.FECHA_CREACION,
                       p.ID_CAMPANIA,
                       u.username, v.DESCRIPCION as VARIEDAD, f.DESCRIPCION as FASE,
                       CONCAT(lv.SECTOR, ' - ', lv.LOTE, ' - ', lv.CONDICION, ' (', lv.AREA_TOTAL, ' ha)') as LOTE_INFO,
                       lv.SECTOR, lv.LOTE as LOTE_NOMBRE, lv.CONDICION, lv.AREA_TOTAL
                FROM RIEGO_PREFERTILIZACION p
                INNER JOIN user_user u ON p.IDUSUARIO = u.id
                INNER JOIN VARIEDAD v ON p.IDVARIEDAD = v.ID
                INNER JOIN FACECULTIVO f ON p.IDFASE = f.ID
                LEFT JOIN LOTES_VARIEDAD lv ON p.IDLOTE = lv.ID
                WHERE p.ID = ?
                """
                cursor.execute(query, [id])

                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()

                if row:
                    return JsonResponse({"data": dict(zip(columns, row))})
                else:
                    return JsonResponse({'status': 'error','message': 'Registro no encontrado'}, status=404)

            else:
                idfase = request.GET.get('idfase')
                idvariedad = request.GET.get('idvariedad')
                idcampania = request.GET.get('idcampania')# 🔥

                query = """
                SELECT p.ID, p.IDUSUARIO, p.IDVARIEDAD, p.IDFASE, p.IDLOTE, p.NOMBRE, 
                       p.FECHA_INICIO, p.FECHA_FIN, p.DESCRIPCION, p.FECHA_CREACION,
                       p.ID_CAMPANIA,
                       u.username, v.DESCRIPCION as VARIEDAD, f.DESCRIPCION as FASE,
                       CONCAT(lv.SECTOR, ' - ', lv.LOTE, ' - ', lv.CONDICION, ' (', lv.AREA_TOTAL, ' ha)') as LOTE_INFO,
                       lv.SECTOR, lv.LOTE as LOTE_NOMBRE, lv.CONDICION, lv.AREA_TOTAL
                FROM RIEGO_PREFERTILIZACION p
                INNER JOIN user_user u ON p.IDUSUARIO = u.id
                INNER JOIN VARIEDAD v ON p.IDVARIEDAD = v.ID
                INNER JOIN FACECULTIVO f ON p.IDFASE = f.ID
                LEFT JOIN LOTES_VARIEDAD lv ON p.IDLOTE = lv.ID
                """

                where_clauses = []
                params = []

                if idfase:
                    where_clauses.append("p.IDFASE = ?")
                    params.append(idfase)

                if idvariedad:
                    where_clauses.append("p.IDVARIEDAD = ?")
                    params.append(idvariedad)

                if idcampania:
                    where_clauses.append("p.ID_CAMPANIA = ?")  # 🔥
                    params.append(idcampania)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY p.FECHA_CREACION DESC"

                cursor.execute(query, params)

                columns = [column[0] for column in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return JsonResponse({"data": data})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            INSERT INTO RIEGO_PREFERTILIZACION 
            (IDUSUARIO, IDVARIEDAD, IDFASE, IDLOTE, NOMBRE, FECHA_INICIO, FECHA_FIN, DESCRIPCION, ID_CAMPANIA) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, [
                data['IDUSUARIO'],
                data['IDVARIEDAD'],
                data['IDFASE'],
                data['IDLOTE'],
                data['NOMBRE'],
                data['FECHA_INICIO'],
                data['FECHA_FIN'],
                data.get('DESCRIPCION', ''),
                data.get('ID_CAMPANIA')  # 🔥
            ])

            connection_portalaei.commit()

            cursor.execute("SELECT IDENT_CURRENT('RIEGO_PREFERTILIZACION')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE RIEGO_PREFERTILIZACION 
            SET IDUSUARIO = ?, IDVARIEDAD = ?, IDFASE = ?, IDLOTE = ?, NOMBRE = ?, 
                FECHA_INICIO = ?, FECHA_FIN = ?, DESCRIPCION = ?, ID_CAMPANIA = ?
            WHERE ID = ?
            """

            cursor.execute(query, [
                data['IDUSUARIO'],
                data['IDVARIEDAD'],
                data['IDFASE'],
                data['IDLOTE'],
                data['NOMBRE'],
                data['FECHA_INICIO'],
                data['FECHA_FIN'],
                data.get('DESCRIPCION', ''),
                data.get('ID_CAMPANIA'),  # 🔥
                id
            ])

            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()

            cursor.execute("DELETE FROM RIEGO_PREFERTILIZACION WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DetallePreFertilizacionView(View):
    """
    Vista para manejar operaciones de la tabla RIEGO_DPREFERTILIZACION
    """
    
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro id_fertilizacion de la solicitud
            id_fertilizacion = request.GET.get('id_fertilizacion')
            
            if id:
                # Consulta para un registro específico por ID
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM RIEGO_DPREFERTILIZACION d
                WHERE d.ID = ?
                """
                cursor.execute(query, [id])
                
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    item = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({"data": item})
                else:
                    cursor.close()
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Registro no encontrado'
                    }, status=404)
            
            elif id_fertilizacion:
                # Consulta para obtener todos los detalles de un plan de fertilización específico
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM RIEGO_DPREFERTILIZACION d
                WHERE d.IDRIEGO_PREFERTILIZACION = ?
                ORDER BY d.PRODUCTO
                """
                cursor.execute(query, [id_fertilizacion])
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                cursor.close()
                return JsonResponse({"data": results})
            
            else:
                # Consulta para obtener todos los registros
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION,
                       p.NOMBRE as PLAN_FERTILIZACION
                FROM RIEGO_DPREFERTILIZACION d
                INNER JOIN RIEGO_PREFERTILIZACION p ON d.IDRIEGO_PREFERTILIZACION = p.ID
                ORDER BY d.FECHA_CREACION DESC
                """
                cursor.execute(query)
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                cursor.close()
                return JsonResponse({"data": results})
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request, *args, **kwargs):
        try:
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Validar que el ID del programa de fertilización esté presente
            if not data.get('IDRIEGO_PREFERTILIZACION'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'El ID del programa de fertilización es obligatorio'
                }, status=400)
            
            # Validar campos obligatorios
            required_fields = ['SUBGRUPO', 'PRODUCTO', 'MATERIA_ACTIVA', 'NECESIDADXHA', 'UND', 'PRECIO_LTKG', 'PRECIO_HA']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Preparar la consulta SQL para insertar el nuevo producto
            query = """
            INSERT INTO RIEGO_DPREFERTILIZACION (
                IDRIEGO_PREFERTILIZACION, IDPRODUCTO, IDSUBGRUPO, 
                SUBGRUPO, PRODUCTO, MATERIA_ACTIVA, 
                NECESIDADXHA, UND, PRECIO_LTKG, 
                PRECIO_HA, OBSERVACIONES, FECHA_CREACION
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Valores para la consulta
            params = [
                data.get('IDRIEGO_PREFERTILIZACION'),
                data.get('IDPRODUCTO', ''),
                data.get('IDSUBGRUPO', ''),
                data.get('SUBGRUPO'),
                data.get('PRODUCTO'),
                data.get('MATERIA_ACTIVA'),
                data.get('NECESIDADXHA'),
                data.get('UND'),
                data.get('PRECIO_LTKG'),
                data.get('PRECIO_HA'),
                data.get('OBSERVACIONES', '')
            ]
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            connection_portalaei.commit()
            
            # Obtener el ID del nuevo registro insertado
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Producto agregado exitosamente',
                'data': {
                    'ID': new_id,
                    **data
                }
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al agregar el producto: {str(e)}'
            }, status=500)

    def put(self, request, id, *args, **kwargs):
        """
        Método para actualizar un producto existente
        """
        try:
            # Verificar que el ID sea válido
            if not id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID del producto no especificado'
                }, status=400)
            
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Validar campos obligatorios
            required_fields = ['SUBGRUPO', 'PRODUCTO', 'MATERIA_ACTIVA', 'NECESIDADXHA', 'UND', 'PRECIO_LTKG', 'PRECIO_HA']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT COUNT(*) FROM RIEGO_DPREFERTILIZACION WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para actualizar el producto
            query = """
            UPDATE RIEGO_DPREFERTILIZACION SET
                SUBGRUPO = ?,
                PRODUCTO = ?,
                MATERIA_ACTIVA = ?,
                NECESIDADXHA = ?,
                UND = ?,
                PRECIO_LTKG = ?,
                PRECIO_HA = ?,
                OBSERVACIONES = ?
            WHERE ID = ?
            """
            
            # Valores para la consulta
            params = [
                data.get('SUBGRUPO'),
                data.get('PRODUCTO'),
                data.get('MATERIA_ACTIVA'),
                data.get('NECESIDADXHA'),
                data.get('UND'),
                data.get('PRECIO_LTKG'),
                data.get('PRECIO_HA'),
                data.get('OBSERVACIONES', ''),
                id
            ]
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            connection_portalaei.commit()
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Producto actualizado exitosamente',
                'data': {
                    'ID': id,
                    **data
                }
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al actualizar el producto: {str(e)}'
            }, status=500)

    def delete(self, request, id, *args, **kwargs):
        """
        Método para eliminar un producto existente
        """
        try:
            # Verificar que el ID sea válido
            if not id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID del producto no especificado'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT COUNT(*) FROM RIEGO_DPREFERTILIZACION WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para eliminar el producto
            query = "DELETE FROM RIEGO_DPREFERTILIZACION WHERE ID = ?"
            
            # Ejecutar la consulta
            cursor.execute(query, [id])
            connection_portalaei.commit()
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Producto con ID {id} eliminado exitosamente'
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al eliminar el producto: {str(e)}'
            }, status=500)


#====================================================================================================================
    #API PARA OBTENER LOTES
#====================================================================================================================


@method_decorator(csrf_exempt, name='dispatch')
# class LotesVariedadView(View):
    
#     def get(self, request, *args, **kwargs):
#         try:
#             # Obtener el parámetro de filtro por variedad
#             idvariedad = request.GET.get('idvariedad')
            
#             cursor = connection.cursor()
            
#             if idvariedad:
#                 # Filtrar por variedad específica
#                 cursor.execute("SELECT * FROM LOTES_VARIEDAD WHERE IDVARIEDAD = %s ORDER BY SECTOR, LOTE", [idvariedad])
#             else:
#                 # Obtener todos los lotes
#                 cursor.execute("SELECT * FROM LOTES_VARIEDAD ORDER BY SECTOR, LOTE")
            
#             rows = cursor.fetchall()
#             cursor.close()
            
#             lotes = []
#             for row in rows:
#                 lote = {
#                     'ID': row[0],
#                     'SECTOR': row[1],
#                     'CONDICION': row[2],
#                     'LOTE': row[3],
#                     'AREA_TOTAL': float(row[4]),
#                     'IDVARIEDAD': row[5],
#                     'FECHA_CREACION': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None
#                 }
#                 lotes.append(lote)
            
#             return JsonResponse({
#                 'status': 'success',
#                 'data': lotes
#             })
            
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f'Error al obtener los lotes: {str(e)}'
#             }, status=500)

class LotesVariedadView(View):

    def get(self, request, *args, **kwargs):
        try:

            idvariedad = request.GET.get('idvariedad') or None
            idcampania = request.GET.get('idcampania') or None
            idempresa = request.GET.get('idempresa') or None 

            cursor = connection_portalaei.cursor()

            cursor.execute(
                "EXEC SP_LOTES_VARIEDAD_LISTAR ?, ?, ?",
                [idvariedad, idcampania, idempresa]
            )

            rows = cursor.fetchall()
            cursor.close()

            data = []

            for row in rows:
                data.append({
                    "ID": row[0],
                    "SECTOR": row[1],
                    "CONDICION": row[2],
                    "LOTE": row[3],
                    "AREA_TOTAL": float(row[4]) if row[4] else 0,
                    "IDVARIEDAD": row[5],
                    "FECHA_CREACION": row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
                    "ID_CAMPANIA": row[7],
                    "IDEMPRESA": row[8]
                })

            return JsonResponse({
                "status": "success",
                "data": data
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })


##### CAMPO VERDE 

@method_decorator(csrf_exempt, name='dispatch')
class ResumenFertilizacionCVView(View):

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()

            if id:
                query = """
                SELECT p.ID, p.IDUSUARIO, p.IDVARIEDAD, p.IDFASE, p.IDLOTE, p.NOMBRE, 
                       p.FECHA_INICIO, p.FECHA_FIN, p.DESCRIPCION, p.FECHA_CREACION,
                       p.ID_CAMPANIA,
                       u.username, v.DESCRIPCION as VARIEDAD, f.DESCRIPCION as FASE,
                       CONCAT(lv.SECTOR, ' - ', lv.LOTE, ' - ', lv.CONDICION, ' (', lv.AREA_TOTAL, ' ha)') as LOTE_INFO,
                       lv.SECTOR, lv.LOTE as LOTE_NOMBRE, lv.CONDICION, lv.AREA_TOTAL
                FROM RIEGO_PREFERTILIZACION_CV p
                INNER JOIN user_user u ON p.IDUSUARIO = u.id
                INNER JOIN VARIEDAD v ON p.IDVARIEDAD = v.ID
                INNER JOIN FACECULTIVO f ON p.IDFASE = f.ID
                LEFT JOIN LOTES_VARIEDAD lv ON p.IDLOTE = lv.ID
                WHERE p.ID = ?
                """
                cursor.execute(query, [id])

                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()

                if row:
                    return JsonResponse({"data": dict(zip(columns, row))})
                else:
                    return JsonResponse({'status': 'error','message': 'Registro no encontrado'}, status=404)

            else:
                idfase = request.GET.get('idfase')
                idvariedad = request.GET.get('idvariedad')
                idcampania = request.GET.get('idcampania')# 🔥

                query = """
                SELECT p.ID, p.IDUSUARIO, p.IDVARIEDAD, p.IDFASE, p.IDLOTE, p.NOMBRE, 
                       p.FECHA_INICIO, p.FECHA_FIN, p.DESCRIPCION, p.FECHA_CREACION,
                       p.ID_CAMPANIA,
                       u.username, v.DESCRIPCION as VARIEDAD, f.DESCRIPCION as FASE,
                       CONCAT(lv.SECTOR, ' - ', lv.LOTE, ' - ', lv.CONDICION, ' (', lv.AREA_TOTAL, ' ha)') as LOTE_INFO,
                       lv.SECTOR, lv.LOTE as LOTE_NOMBRE, lv.CONDICION, lv.AREA_TOTAL
                FROM RIEGO_PREFERTILIZACION_CV p
                INNER JOIN user_user u ON p.IDUSUARIO = u.id
                INNER JOIN VARIEDAD v ON p.IDVARIEDAD = v.ID
                INNER JOIN FACECULTIVO f ON p.IDFASE = f.ID
                LEFT JOIN LOTES_VARIEDAD lv ON p.IDLOTE = lv.ID
                """

                where_clauses = []
                params = []

                if idfase:
                    where_clauses.append("p.IDFASE = ?")
                    params.append(idfase)

                if idvariedad:
                    where_clauses.append("p.IDVARIEDAD = ?")
                    params.append(idvariedad)

                if idcampania:
                    where_clauses.append("p.ID_CAMPANIA = ?")  # 🔥
                    params.append(idcampania)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY p.FECHA_CREACION DESC"

                cursor.execute(query, params)

                columns = [column[0] for column in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return JsonResponse({"data": data})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            INSERT INTO RIEGO_PREFERTILIZACION_CV 
            (IDUSUARIO, IDVARIEDAD, IDFASE, IDLOTE, NOMBRE, FECHA_INICIO, FECHA_FIN, DESCRIPCION, ID_CAMPANIA) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, [
                data['IDUSUARIO'],
                data['IDVARIEDAD'],
                data['IDFASE'],
                data['IDLOTE'],
                data['NOMBRE'],
                data['FECHA_INICIO'],
                data['FECHA_FIN'],
                data.get('DESCRIPCION', ''),
                data.get('ID_CAMPANIA')  # 🔥
            ])

            connection_portalaei.commit()

            cursor.execute("SELECT IDENT_CURRENT('RIEGO_PREFERTILIZACION_CV')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE RIEGO_PREFERTILIZACION_CV 
            SET IDUSUARIO = ?, IDVARIEDAD = ?, IDFASE = ?, IDLOTE = ?, NOMBRE = ?, 
                FECHA_INICIO = ?, FECHA_FIN = ?, DESCRIPCION = ?, ID_CAMPANIA = ?
            WHERE ID = ?
            """

            cursor.execute(query, [
                data['IDUSUARIO'],
                data['IDVARIEDAD'],
                data['IDFASE'],
                data['IDLOTE'],
                data['NOMBRE'],
                data['FECHA_INICIO'],
                data['FECHA_FIN'],
                data.get('DESCRIPCION', ''),
                data.get('ID_CAMPANIA'),  # 🔥
                id
            ])

            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()

            cursor.execute("DELETE FROM RIEGO_PREFERTILIZACION_CV WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DetallePreFertilizacionCVView(View):
    """
    Vista para manejar operaciones de la tabla RIEGO_DPREFERTILIZACION
    """
    
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro id_fertilizacion de la solicitud
            id_fertilizacion = request.GET.get('id_fertilizacion')
            
            if id:
                # Consulta para un registro específico por ID
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM RIEGO_DPREFERTILIZACION_CV d
                WHERE d.ID = ?
                """
                cursor.execute(query, [id])
                
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    item = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({"data": item})
                else:
                    cursor.close()
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Registro no encontrado'
                    }, status=404)
            
            elif id_fertilizacion:
                # Consulta para obtener todos los detalles de un plan de fertilización específico
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM RIEGO_DPREFERTILIZACION_CV d
                WHERE d.IDRIEGO_PREFERTILIZACION = ?
                ORDER BY d.PRODUCTO
                """
                cursor.execute(query, [id_fertilizacion])
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                cursor.close()
                return JsonResponse({"data": results})
            
            else:
                # Consulta para obtener todos los registros
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION,
                       p.NOMBRE as PLAN_FERTILIZACION
                FROM RIEGO_DPREFERTILIZACION_CV d
                INNER JOIN RIEGO_PREFERTILIZACION_CV p ON d.IDRIEGO_PREFERTILIZACION = p.ID
                ORDER BY d.FECHA_CREACION DESC
                """
                cursor.execute(query)
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                cursor.close()
                return JsonResponse({"data": results})
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request, *args, **kwargs):
        try:
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Validar que el ID del programa de fertilización esté presente
            if not data.get('IDRIEGO_PREFERTILIZACION'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'El ID del programa de fertilización es obligatorio'
                }, status=400)
            
            # Validar campos obligatorios
            required_fields = ['SUBGRUPO', 'PRODUCTO', 'MATERIA_ACTIVA', 'NECESIDADXHA', 'UND', 'PRECIO_LTKG', 'PRECIO_HA']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Preparar la consulta SQL para insertar el nuevo producto
            query = """
            INSERT INTO RIEGO_DPREFERTILIZACION_CV (
                IDRIEGO_PREFERTILIZACION, IDPRODUCTO, IDSUBGRUPO, 
                SUBGRUPO, PRODUCTO, MATERIA_ACTIVA, 
                NECESIDADXHA, UND, PRECIO_LTKG, 
                PRECIO_HA, OBSERVACIONES, FECHA_CREACION
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Valores para la consulta
            params = [
                data.get('IDRIEGO_PREFERTILIZACION'),
                data.get('IDPRODUCTO', ''),
                data.get('IDSUBGRUPO', ''),
                data.get('SUBGRUPO'),
                data.get('PRODUCTO'),
                data.get('MATERIA_ACTIVA'),
                data.get('NECESIDADXHA'),
                data.get('UND'),
                data.get('PRECIO_LTKG'),
                data.get('PRECIO_HA'),
                data.get('OBSERVACIONES', '')
            ]
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            connection_portalaei.commit()
            
            # Obtener el ID del nuevo registro insertado
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Producto agregado exitosamente',
                'data': {
                    'ID': new_id,
                    **data
                }
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al agregar el producto: {str(e)}'
            }, status=500)

    def put(self, request, id, *args, **kwargs):
        """
        Método para actualizar un producto existente
        """
        try:
            # Verificar que el ID sea válido
            if not id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID del producto no especificado'
                }, status=400)
            
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Validar campos obligatorios
            required_fields = ['SUBGRUPO', 'PRODUCTO', 'MATERIA_ACTIVA', 'NECESIDADXHA', 'UND', 'PRECIO_LTKG', 'PRECIO_HA']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT COUNT(*) FROM RIEGO_DPREFERTILIZACION_CV WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para actualizar el producto
            query = """
            UPDATE RIEGO_DPREFERTILIZACION_CV SET
                SUBGRUPO = ?,
                PRODUCTO = ?,
                MATERIA_ACTIVA = ?,
                NECESIDADXHA = ?,
                UND = ?,
                PRECIO_LTKG = ?,
                PRECIO_HA = ?,
                OBSERVACIONES = ?
            WHERE ID = ?
            """
            
            # Valores para la consulta
            params = [
                data.get('SUBGRUPO'),
                data.get('PRODUCTO'),
                data.get('MATERIA_ACTIVA'),
                data.get('NECESIDADXHA'),
                data.get('UND'),
                data.get('PRECIO_LTKG'),
                data.get('PRECIO_HA'),
                data.get('OBSERVACIONES', ''),
                id
            ]
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            connection_portalaei.commit()
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Producto actualizado exitosamente',
                'data': {
                    'ID': id,
                    **data
                }
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al actualizar el producto: {str(e)}'
            }, status=500)

    def delete(self, request, id, *args, **kwargs):
        """
        Método para eliminar un producto existente
        """
        try:
            # Verificar que el ID sea válido
            if not id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID del producto no especificado'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT COUNT(*) FROM RIEGO_DPREFERTILIZACION_CV WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para eliminar el producto
            query = "DELETE FROM RIEGO_DPREFERTILIZACION_CV WHERE ID = ?"
            
            # Ejecutar la consulta
            cursor.execute(query, [id])
            connection_portalaei.commit()
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Producto con ID {id} eliminado exitosamente'
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al eliminar el producto: {str(e)}'
            }, status=500)


###### INVERSIONES AJS 

@method_decorator(csrf_exempt, name='dispatch')
class ResumenFertilizacionAJSView(View):

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()

            if id:
                query = """
                SELECT p.ID, p.IDUSUARIO, p.IDVARIEDAD, p.IDFASE, p.IDLOTE, p.NOMBRE, 
                       p.FECHA_INICIO, p.FECHA_FIN, p.DESCRIPCION, p.FECHA_CREACION,
                       p.ID_CAMPANIA,
                       u.username, v.DESCRIPCION as VARIEDAD, f.DESCRIPCION as FASE,
                       CONCAT(lv.SECTOR, ' - ', lv.LOTE, ' - ', lv.CONDICION, ' (', lv.AREA_TOTAL, ' ha)') as LOTE_INFO,
                       lv.SECTOR, lv.LOTE as LOTE_NOMBRE, lv.CONDICION, lv.AREA_TOTAL
                FROM RIEGO_PREFERTILIZACION_AJS p
                INNER JOIN user_user u ON p.IDUSUARIO = u.id
                INNER JOIN VARIEDAD v ON p.IDVARIEDAD = v.ID
                INNER JOIN FACECULTIVO f ON p.IDFASE = f.ID
                LEFT JOIN LOTES_VARIEDAD lv ON p.IDLOTE = lv.ID
                WHERE p.ID = ?
                """
                cursor.execute(query, [id])

                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()

                if row:
                    return JsonResponse({"data": dict(zip(columns, row))})
                else:
                    return JsonResponse({'status': 'error','message': 'Registro no encontrado'}, status=404)

            else:
                idfase = request.GET.get('idfase')
                idvariedad = request.GET.get('idvariedad')
                idcampania = request.GET.get('idcampania')# 🔥

                query = """
                SELECT p.ID, p.IDUSUARIO, p.IDVARIEDAD, p.IDFASE, p.IDLOTE, p.NOMBRE, 
                       p.FECHA_INICIO, p.FECHA_FIN, p.DESCRIPCION, p.FECHA_CREACION,
                       p.ID_CAMPANIA,
                       u.username, v.DESCRIPCION as VARIEDAD, f.DESCRIPCION as FASE,
                       CONCAT(lv.SECTOR, ' - ', lv.LOTE, ' - ', lv.CONDICION, ' (', lv.AREA_TOTAL, ' ha)') as LOTE_INFO,
                       lv.SECTOR, lv.LOTE as LOTE_NOMBRE, lv.CONDICION, lv.AREA_TOTAL
                FROM RIEGO_PREFERTILIZACION_AJS p
                INNER JOIN user_user u ON p.IDUSUARIO = u.id
                INNER JOIN VARIEDAD v ON p.IDVARIEDAD = v.ID
                INNER JOIN FACECULTIVO f ON p.IDFASE = f.ID
                LEFT JOIN LOTES_VARIEDAD lv ON p.IDLOTE = lv.ID
                """

                where_clauses = []
                params = []

                if idfase:
                    where_clauses.append("p.IDFASE = ?")
                    params.append(idfase)

                if idvariedad:
                    where_clauses.append("p.IDVARIEDAD = ?")
                    params.append(idvariedad)

                if idcampania:
                    where_clauses.append("p.ID_CAMPANIA = ?")  # 🔥
                    params.append(idcampania)

                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)

                query += " ORDER BY p.FECHA_CREACION DESC"

                cursor.execute(query, params)

                columns = [column[0] for column in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]

                return JsonResponse({"data": data})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            INSERT INTO RIEGO_PREFERTILIZACION_AJS 
            (IDUSUARIO, IDVARIEDAD, IDFASE, IDLOTE, NOMBRE, FECHA_INICIO, FECHA_FIN, DESCRIPCION, ID_CAMPANIA) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            cursor.execute(query, [
                data['IDUSUARIO'],
                data['IDVARIEDAD'],
                data['IDFASE'],
                data['IDLOTE'],
                data['NOMBRE'],
                data['FECHA_INICIO'],
                data['FECHA_FIN'],
                data.get('DESCRIPCION', ''),
                data.get('ID_CAMPANIA')  # 🔥
            ])

            connection_portalaei.commit()

            cursor.execute("SELECT IDENT_CURRENT('RIEGO_PREFERTILIZACION_AJS')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE RIEGO_PREFERTILIZACION_AJS 
            SET IDUSUARIO = ?, IDVARIEDAD = ?, IDFASE = ?, IDLOTE = ?, NOMBRE = ?, 
                FECHA_INICIO = ?, FECHA_FIN = ?, DESCRIPCION = ?, ID_CAMPANIA = ?
            WHERE ID = ?
            """

            cursor.execute(query, [
                data['IDUSUARIO'],
                data['IDVARIEDAD'],
                data['IDFASE'],
                data['IDLOTE'],
                data['NOMBRE'],
                data['FECHA_INICIO'],
                data['FECHA_FIN'],
                data.get('DESCRIPCION', ''),
                data.get('ID_CAMPANIA'),  # 🔥
                id
            ])

            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()

            cursor.execute("DELETE FROM RIEGO_PREFERTILIZACION_AJS WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class DetallePreFertilizacionAJSView(View):
    """
    Vista para manejar operaciones de la tabla RIEGO_DPREFERTILIZACION_CV
    """
    
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro id_fertilizacion de la solicitud
            id_fertilizacion = request.GET.get('id_fertilizacion')
            
            if id:
                # Consulta para un registro específico por ID
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM RIEGO_DPREFERTILIZACION_AJS d
                WHERE d.ID = ?
                """
                cursor.execute(query, [id])
                
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                
                if row:
                    item = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({"data": item})
                else:
                    cursor.close()
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Registro no encontrado'
                    }, status=404)
            
            elif id_fertilizacion:
                # Consulta para obtener todos los detalles de un plan de fertilización específico
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM RIEGO_DPREFERTILIZACION_AJS d
                WHERE d.IDRIEGO_PREFERTILIZACION = ?
                ORDER BY d.PRODUCTO
                """
                cursor.execute(query, [id_fertilizacion])
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                cursor.close()
                return JsonResponse({"data": results})
            
            else:
                # Consulta para obtener todos los registros
                query = """
                SELECT d.ID, d.IDRIEGO_PREFERTILIZACION, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION,
                       p.NOMBRE as PLAN_FERTILIZACION
                FROM RIEGO_DPREFERTILIZACION_AJS d
                INNER JOIN RIEGO_PREFERTILIZACION_AJS p ON d.IDRIEGO_PREFERTILIZACION = p.ID
                ORDER BY d.FECHA_CREACION DESC
                """
                cursor.execute(query)
                
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                cursor.close()
                return JsonResponse({"data": results})
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    def post(self, request, *args, **kwargs):
        try:
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Validar que el ID del programa de fertilización esté presente
            if not data.get('IDRIEGO_PREFERTILIZACION'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'El ID del programa de fertilización es obligatorio'
                }, status=400)
            
            # Validar campos obligatorios
            required_fields = ['SUBGRUPO', 'PRODUCTO', 'MATERIA_ACTIVA', 'NECESIDADXHA', 'UND', 'PRECIO_LTKG', 'PRECIO_HA']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Preparar la consulta SQL para insertar el nuevo producto
            query = """
            INSERT INTO RIEGO_DPREFERTILIZACION_AJS (
                IDRIEGO_PREFERTILIZACION, IDPRODUCTO, IDSUBGRUPO, 
                SUBGRUPO, PRODUCTO, MATERIA_ACTIVA, 
                NECESIDADXHA, UND, PRECIO_LTKG, 
                PRECIO_HA, OBSERVACIONES, FECHA_CREACION
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Valores para la consulta
            params = [
                data.get('IDRIEGO_PREFERTILIZACION'),
                data.get('IDPRODUCTO', ''),
                data.get('IDSUBGRUPO', ''),
                data.get('SUBGRUPO'),
                data.get('PRODUCTO'),
                data.get('MATERIA_ACTIVA'),
                data.get('NECESIDADXHA'),
                data.get('UND'),
                data.get('PRECIO_LTKG'),
                data.get('PRECIO_HA'),
                data.get('OBSERVACIONES', '')
            ]
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            connection_portalaei.commit()
            
            # Obtener el ID del nuevo registro insertado
            cursor.execute("SELECT @@IDENTITY")
            new_id = cursor.fetchone()[0]
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Producto agregado exitosamente',
                'data': {
                    'ID': new_id,
                    **data
                }
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al agregar el producto: {str(e)}'
            }, status=500)

    def put(self, request, id, *args, **kwargs):
        """
        Método para actualizar un producto existente
        """
        try:
            # Verificar que el ID sea válido
            if not id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID del producto no especificado'
                }, status=400)
            
            # Obtener los datos del cuerpo de la solicitud
            data = json.loads(request.body)
            
            # Validar campos obligatorios
            required_fields = ['SUBGRUPO', 'PRODUCTO', 'MATERIA_ACTIVA', 'NECESIDADXHA', 'UND', 'PRECIO_LTKG', 'PRECIO_HA']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Los siguientes campos son obligatorios: {", ".join(missing_fields)}'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT COUNT(*) FROM RIEGO_DPREFERTILIZACION_AJS WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para actualizar el producto
            query = """
            UPDATE RIEGO_DPREFERTILIZACION_AJS SET
                SUBGRUPO = ?,
                PRODUCTO = ?,
                MATERIA_ACTIVA = ?,
                NECESIDADXHA = ?,
                UND = ?,
                PRECIO_LTKG = ?,
                PRECIO_HA = ?,
                OBSERVACIONES = ?
            WHERE ID = ?
            """
            
            # Valores para la consulta
            params = [
                data.get('SUBGRUPO'),
                data.get('PRODUCTO'),
                data.get('MATERIA_ACTIVA'),
                data.get('NECESIDADXHA'),
                data.get('UND'),
                data.get('PRECIO_LTKG'),
                data.get('PRECIO_HA'),
                data.get('OBSERVACIONES', ''),
                id
            ]
            
            # Ejecutar la consulta
            cursor.execute(query, params)
            connection_portalaei.commit()
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Producto actualizado exitosamente',
                'data': {
                    'ID': id,
                    **data
                }
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al actualizar el producto: {str(e)}'
            }, status=500)

    def delete(self, request, id, *args, **kwargs):
        """
        Método para eliminar un producto existente
        """
        try:
            # Verificar que el ID sea válido
            if not id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'ID del producto no especificado'
                }, status=400)
            
            # Abrir conexión a la base de datos
            cursor = connection_portalaei.cursor()
            
            # Verificar que el producto existe
            cursor.execute("SELECT COUNT(*) FROM RIEGO_DPREFERTILIZACION_AJS WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para eliminar el producto
            query = "DELETE FROM RIEGO_DPREFERTILIZACION_AJS WHERE ID = ?"
            
            # Ejecutar la consulta
            cursor.execute(query, [id])
            connection_portalaei.commit()
            
            # Cerrar el cursor
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Producto con ID {id} eliminado exitosamente'
            })
            
        except Exception as e:
            # Capturar cualquier excepción y devolver un mensaje de error
            return JsonResponse({
                'status': 'error',
                'message': f'Error al eliminar el producto: {str(e)}'
            }, status=500)
