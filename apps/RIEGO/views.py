

from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from apps.connection.connect_donluis import connection_donluis, get_thread_connection
from apps.connection.connect_campoverde import connection_campoverde
from apps.connection.connect_inversioneajs import connection_inversioneajs
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.connection.connect_portalaei import connection_portalaei
from decimal import Decimal
import json
from django.db import connection
from django.db import IntegrityError
from django.db import transaction













#=================================================================================================================
#MODULO PRESUPUESTOS
#AUTOR: JHON GUTIERREZ
#FECHA: 06/01/2025
#MODIFICACIONES: 
# 06/01/2025: Se crea el modulo de presupuestos
#=================================================================================================================





# PRESUPUESTO

class presupuesto_dl(TemplateView):
    permission_required = 'modulo_riego'
    template_name = 'RIEGO/pages/riego_presupuesto_dl.html'

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

def Costo_servicio_totals(request):
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:

        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '11', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '11'
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
            # area_id = data.get('id_area', 11)
            # if observacion:  # Solo verificar si hay una observación
            #     cursor.execute(check_query, [observacion, area_id])
            #     count = cursor.fetchone()[0]
                
            #     if count > 0:
            #         return JsonResponse({
            #             'status': 'error',
            #             'message': 'Ya existe un servicio con esta observación en esta área'
            #         }, status=400)
            
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
            
            values.extend([request.user.id,11,id_campania]) 

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
                WHERE id = ?  AND id_area = 11
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
                    WHERE id_area = 11 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query,[campania])
                else:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio, ID_CAMPANIA
                    FROM TIC_servicios 
                    WHERE id_area = 11
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
            area_id = data.get('id_area', 11)
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

            
            values.extend([request.user.id,11, id])
            
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
            """, [11, campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s
            """, [11])

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
            
            values.extend([request.user.id,11,1,id_campania])


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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 1
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
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
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
                    WHERE id_area = 11 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query,[campania])
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
                    WHERE id_area = 11 AND id_tipo_suministro = 1
                        """
                    cursor.execute(query)   
                     
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,11,1])
            
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
            
            values.extend([request.user.id,11,5,id_campania])
            
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
                AND id_area = 11
                AND id_tipo_suministro = 5 
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
                    WHERE id_area = 11
                    AND id_tipo_suministro = 5  AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query,[campania])
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
                    WHERE id_area = 11 AND id_tipo_suministro = 5
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            values.extend([request.user.id,11,5])
            
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
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro, ID_CAMPANIA)
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
            values.extend([request.user.id,11,7,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 7
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
                WHERE id_area = 11 AND id_tipo_suministro = 7
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
                    WHERE id_area = 11 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            AND id_area = 11 
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
            values.extend([request.user.id,11,7])
            
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
            values.extend([request.user.id,11,8,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 8
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
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (código existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 11 AND id_tipo_suministro = 8
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
                    WHERE id_area = 11 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,11,8])


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
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro, ID_CAMPANIA)
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
            
            values.extend([request.user.id,11,4,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 4
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
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (código existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 11 AND id_tipo_suministro = 4
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
                    WHERE id_area = 11 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)

                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,11,4])
            
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
            values.extend([request.user.id,11,2,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 2
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
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (código existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 11 AND id_tipo_suministro = 2
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
                    WHERE id_area = 11 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,11,2])
                
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
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro, ID_CAMPANIA)
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
            values.extend([request.user.id,11,9,id_campania])
            
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 9
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
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
                # Si no se proporciona ID, devolver todos los productos (código existente)
                query = """
                SELECT id, idproducto, descripcion,precio_unitario,
                       enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                       marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                       mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                       julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                       septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id_area = 11 AND id_tipo_suministro = 9
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
                    WHERE id_area = 11 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:    
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,11,9])
                
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
            values.extend([request.user.id,11,3,id_campania])


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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 3
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
                WHERE id_area = 11 AND id_tipo_suministro = 3
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
                    WHERE id_area = 11 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,11,3])
            
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
                noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,USUARIO,id_area,id_tipo_suministro, ID_CAMPANIA)
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
            values.extend([request.user.id,11,6,id_campania])
            
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 6
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
                    return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
            else:
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
                    WHERE id_area = 11 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_tipo_suministro = 6
                    """
                    cursor.execute(query)
                    
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,11,6])
            
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
# FECHA: 211/11/2024
#==============================================================================================


def Costos_capex_totals(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            EXEC RPT_PST_CAPEX '11'

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
            id_area = data.get('id_area', 11)
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
                WHERE id = ? AND id_area = 11 
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
                    WHERE id_area = 11 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11
                    """
                    cursor.execute(query)
            
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Convertir Decimal a float para serialización JSON
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
            WHERE id = ? AND id_area = 11
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
                11,
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
# FECHA: 211/11/2024
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
                11,  # id_area
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
                WHERE id = ? AND id_area = 11 AND id_remuneracion = 1
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
                 # Filtrar por campaña si se proporciona
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                        enero, febrero, marzo, abril, mayo, junio,
                        julio, agosto, septiembre, octubre, noviembre, diciembre,
                        usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 11 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query,[campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 11 AND id_remuneracion = 1
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
                11,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [11, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [11, 1])
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
                11,  # id_area
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
                WHERE id = ? AND id_area = 11 AND id_remuneracion = 2 
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
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                        enero, febrero, marzo, abril, mayo, junio,
                        julio, agosto, septiembre, octubre, noviembre, diciembre,
                        usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 11 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query,[campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 11 AND id_remuneracion = 2
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
                11,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [11, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [11, 2])
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



#================================================================================================================
# PRESUPUESTO DE FERTILIZACION
#================================================================================================================

# API PARA RESUMEN DE FERTILIZACION



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



#########################################
####### CAMPO VERDE #####################
#########################################

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


######################################################
################## INVERSIONES AJS ###################
######################################################

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


#================================================================================================================
# MATERIA ORGANICA 
#================================================================================================================

# API PARA RESUMEN DE MATERIA ORGANICA


@method_decorator(csrf_exempt, name='dispatch')
class OrgResumenMateriaOrganicaView(View):
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
                FROM MATERIA_ORGANICA p
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
                FROM MATERIA_ORGANICA p
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
            INSERT INTO MATERIA_ORGANICA 
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

            cursor.execute("SELECT IDENT_CURRENT('MATERIA_ORGANICA')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE MATERIA_ORGANICA 
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

            cursor.execute("DELETE FROM MATERIA_ORGANICA WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class OrgDetalleMateriaOrganicaView(View):
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro id_fertilizacion de la solicitud
            id_fertilizacion = request.GET.get('id_fertilizacion')
            
            if id:
                # Consulta para un registro específico por ID
                query = """
                SELECT d.ID, d.IDMATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM MATERIA_DORGANICA d
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
                SELECT d.ID, d.MATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM MATERIA_DORGANICA d
                WHERE d.IDMATERIA_ORGANICA = ?
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
                SELECT d.ID, d.IDMATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION,
                       p.NOMBRE as PLAN_FERTILIZACION
                FROM MATERIA_DORGANICA d
                INNER JOIN MATERIA_ORGANICA p ON d.IDMATERIA_ORGANICA = p.ID
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
            if not data.get('IDMATERIA_ORGANICA'):
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
            INSERT INTO MATERIA_DORGANICA (
                IDMATERIA_ORGANICA, IDPRODUCTO, IDSUBGRUPO, 
                SUBGRUPO, PRODUCTO, MATERIA_ACTIVA, 
                NECESIDADXHA, UND, PRECIO_LTKG, 
                PRECIO_HA, OBSERVACIONES, FECHA_CREACION
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Valores para la consulta
            params = [
                data.get('IDMATERIA_ORGANICA'),
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
            cursor.execute("SELECT COUNT(*) FROM MATERIA_DORGANICA WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para actualizar el producto
            query = """
            UPDATE MATERIA_DORGANICA SET
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
            cursor.execute("SELECT COUNT(*) FROM MATERIA_DORGANICA WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para eliminar el producto
            query = "DELETE FROM MATERIA_DORGANICA WHERE ID = ?"
            
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


#### CAMPO VERDE
    
@method_decorator(csrf_exempt, name='dispatch')
class OrgResumenMateriaOrganicaCVView(View):
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
                FROM MATERIA_ORGANICA_CV p
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
                FROM MATERIA_ORGANICA_CV p
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
            INSERT INTO MATERIA_ORGANICA_CV 
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

            cursor.execute("SELECT IDENT_CURRENT('MATERIA_ORGANICA_CV')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE MATERIA_ORGANICA_CV 
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

            cursor.execute("DELETE FROM MATERIA_ORGANICA_CV WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class OrgDetalleMateriaOrganicaCVView(View):
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro id_fertilizacion de la solicitud
            id_fertilizacion = request.GET.get('id_fertilizacion')
            
            if id:
                # Consulta para un registro específico por ID
                query = """
                SELECT d.ID, d.IDMATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM MATERIA_DORGANICA_CV d
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
                SELECT d.ID, d.MATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM MATERIA_DORGANICA_CV d
                WHERE d.IDMATERIA_ORGANICA = ?
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
                SELECT d.ID, d.IDMATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION,
                       p.NOMBRE as PLAN_FERTILIZACION
                FROM MATERIA_DORGANICA_CV d
                INNER JOIN MATERIA_ORGANICA_CV p ON d.IDMATERIA_ORGANICA = p.ID
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
            if not data.get('IDMATERIA_ORGANICA'):
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
            INSERT INTO MATERIA_DORGANICA_CV (
                IDMATERIA_ORGANICA, IDPRODUCTO, IDSUBGRUPO, 
                SUBGRUPO, PRODUCTO, MATERIA_ACTIVA, 
                NECESIDADXHA, UND, PRECIO_LTKG, 
                PRECIO_HA, OBSERVACIONES, FECHA_CREACION
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Valores para la consulta
            params = [
                data.get('IDMATERIA_ORGANICA'),
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
            cursor.execute("SELECT COUNT(*) FROM MATERIA_DORGANICA_CV WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para actualizar el producto
            query = """
            UPDATE MATERIA_DORGANICA_CV SET
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
            cursor.execute("SELECT COUNT(*) FROM MATERIA_DORGANICA_CV WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para eliminar el producto
            query = "DELETE FROM MATERIA_DORGANICA_CV WHERE ID = ?"
            
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

    
#### INVERSIONES AJS
    
@method_decorator(csrf_exempt, name='dispatch')
class OrgResumenMateriaOrganicaAJSView(View):
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
                FROM MATERIA_ORGANICA_AJS p
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
                FROM MATERIA_ORGANICA_AJS p
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
            INSERT INTO MATERIA_ORGANICA_AJS 
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

            cursor.execute("SELECT IDENT_CURRENT('MATERIA_ORGANICA_AJS')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE MATERIA_ORGANICA_AJS 
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

            cursor.execute("DELETE FROM MATERIA_ORGANICA_AJS WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    

@method_decorator(csrf_exempt, name='dispatch')
class OrgDetalleMateriaOrganicaAJSView(View):
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro id_fertilizacion de la solicitud
            id_fertilizacion = request.GET.get('id_fertilizacion')
            
            if id:
                # Consulta para un registro específico por ID
                query = """
                SELECT d.ID, d.IDMATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM MATERIA_DORGANICA_AJS d
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
                SELECT d.ID, d.MATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION
                FROM MATERIA_DORGANICA_AJS d
                WHERE d.IDMATERIA_ORGANICA = ?
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
                SELECT d.ID, d.IDMATERIA_ORGANICA, d.IDPRODUCTO, d.IDSUBGRUPO, 
                       d.SUBGRUPO, d.PRODUCTO, d.MATERIA_ACTIVA, d.NECESIDADXHA, 
                       d.UND, d.PRECIO_LTKG, d.PRECIO_HA, d.OBSERVACIONES, d.FECHA_CREACION,
                       p.NOMBRE as PLAN_FERTILIZACION
                FROM MATERIA_DORGANICA_AJS d
                INNER JOIN MATERIA_ORGANICA_AJS p ON d.IDMATERIA_ORGANICA = p.ID
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
            if not data.get('IDMATERIA_ORGANICA'):
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
            INSERT INTO MATERIA_DORGANICA_AJS (
                IDMATERIA_ORGANICA, IDPRODUCTO, IDSUBGRUPO, 
                SUBGRUPO, PRODUCTO, MATERIA_ACTIVA, 
                NECESIDADXHA, UND, PRECIO_LTKG, 
                PRECIO_HA, OBSERVACIONES, FECHA_CREACION
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Valores para la consulta
            params = [
                data.get('IDMATERIA_ORGANICA'),
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
            cursor.execute("SELECT COUNT(*) FROM MATERIA_DORGANICA_AJS WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para actualizar el producto
            query = """
            UPDATE MATERIA_DORGANICA_AJS SET
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
            cursor.execute("SELECT COUNT(*) FROM MATERIA_DORGANICA_AJS WHERE ID = ?", [id])
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'error',
                    'message': f'No existe un producto con el ID {id}'
                }, status=404)
            
            # Preparar la consulta SQL para eliminar el producto
            query = "DELETE FROM MATERIA_DORGANICA_AJS WHERE ID = ?"
            
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


#====================================================================================================================
    #EVALUACION DE DESEMPEÑO
#====================================================================================================================

class evaluacion_desempeño(TemplateView):
    permission_required = 'modulo_riego' 
    template_name = 'RIEGO/components/DonLuis/eva_desempeno/rrhh_evaluacion_desempeño.html'


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
                cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @periodo=?", [11, periodo])
            
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
                """, [11, periodo])
            
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
                    WHERE id_evaluado = ? AND periodo = ?
                """, [data['id_evaluado'], data['periodo']])

                count = cursor.fetchone()[0]
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
                id_evaluacion = cursor.fetchone()[0]
                
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
                cursor.execute("EXEC RRHH_EV_OBJETIVOS_MEJORA 11")
            
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
            
            cantidad_objetivos = cursor.fetchone()[0]
            
            # 3. Si es el último objetivo, verificar si hay competencias asociadas
            if cantidad_objetivos == 1:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM RRHH_COMPETENCIAS 
                    WHERE id_evaluacion = ? AND estado = 1
                """, [id_evaluacion])
                
                cantidad_competencias = cursor.fetchone()[0]
                
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


class ResumenRRHHObjetivosView(View):
    def get(self, request, *args, **kwargs):
        # Ejecutar el procedimiento almacenado
        with connection.cursor() as cursor:
            cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS")
            resultados = cursor.fetchall()
        
        # Devolver la respuesta
        return JsonResponse(resultados, safe=False)


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
                cursor.execute("EXEC RRHH_EV_COMPETENCIAS_MEJORA 11")
            
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

@method_decorator(csrf_exempt, name='dispatch')
class ResumenCompetenciasView(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros
            id_area = request.GET.get('id_area', 11)  # Por defecto área 12 (RRHH)
            periodo = request.GET.get('campania')  # Mantener 'campania' como nombre del parámetro para compatibilidad
            if not periodo:
                # Si no se proporciona periodo, usar el año actual
                from datetime import datetime
                periodo = str(datetime.now().year)
            
            # Extraer solo el año si viene en formato CAMP2026
            if periodo.startswith('CAMP'):
                periodo = periodo.replace('CAMP', '')
            
            # Ejecutar el procedimiento almacenado con el parámetro de periodo y área
            cursor.execute("EXEC SP_RESUMEN_RRHH_COMPETENCIAS @id_area=?, @periodo=?", [id_area, periodo])
            
            # Obtener los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            competencias = []
            for row in cursor.fetchall():
                competencia = dict(zip(columns, row))
                # Convertir fechas a formato string para JSON si existen
                if 'fecha_inicio' in competencia:
                    competencia['fecha_inicio'] = competencia['fecha_inicio'].strftime('%Y-%m-%d')
                if 'fecha_fin' in competencia:
                    competencia['fecha_fin'] = competencia['fecha_fin'].strftime('%Y-%m-%d')
                competencias.append(competencia)

            return JsonResponse({
                'status': 'success',
                'data': competencias
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

        finally:
            if cursor:
                cursor.close()


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
                    "porcentaje_avance": 110
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
                status_code = 2011  # Multi-Status
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
    permission_required = 'modulo_riego'
    template_name = 'RIEGO/pages/riego_presupuesto_cv.html'

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
                EXEC TOTAL_SERVICIOS_CV '11', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '11'
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
            area_id = data.get('id_area', 11)
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
            values.append(11) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 11
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
                    WHERE id_area = 11 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11
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
            area_id = data.get('id_area', 11)
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

            
            values.extend([request.user.id,11, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s, %s", [11, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s", [11])

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
            
            values.extend([request.user.id,11,1,id_campania])


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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 1
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
                    WHERE id_area = 11 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,11,1])
            
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
            
            values.extend([request.user.id,11,5,id_campania])
            
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
                AND id_area = 11
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
                    WHERE id_area = 11 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,11,5])
            
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
            values.extend([request.user.id,11,7,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 7
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
                WHERE id_area = 11 AND id_tipo_suministro = 7
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
                    WHERE id_area = 11 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 11 
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
            values.extend([request.user.id,11,7])
            
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
            values.extend([request.user.id,11,8,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 8
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
                WHERE id_area = 11 AND id_tipo_suministro = 8
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
                    WHERE id_area = 11 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,11,8])


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
            
            values.extend([request.user.id,11,4,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 4
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
                WHERE id_area = 11 AND id_tipo_suministro = 4
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
                    WHERE id_area = 11 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,11,4])
            
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
            values.extend([request.user.id,11,2,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 2
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
                WHERE id_area = 11 AND id_tipo_suministro = 2
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
                    WHERE id_area = 11 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,11,2])
                
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
            values.extend([request.user.id,11,9,id_campania])
            
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 9
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
                WHERE id_area = 11 AND id_tipo_suministro = 9
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
                    WHERE id_area = 11 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,11,9])
                
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
            values.extend([request.user.id,11,3,id_campania])


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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 3
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
                WHERE id_area = 11 AND id_tipo_suministro = 3
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
                    WHERE id_area = 11 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,11,3])
            
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
            values.extend([request.user.id,11,6,id_campania])
            
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 6
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
                WHERE id_area = 11 AND id_tipo_suministro = 6
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
                    WHERE id_area = 11 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,11,6])
            
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
# FECHA: 211/11/2024
#==============================================================================================


def Costos_capex_totals_cv(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '11', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '11'
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
            id_area = data.get('id_area', 11)
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
                WHERE id = ? AND id_area = 11
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
                    WHERE id_area = 11 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11
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
            WHERE id = ? AND id_area = 11
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
                11,
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
# FECHA: 211/11/2024
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
                11,  # id_area
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
                WHERE id = ? AND id_area = 11 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 11 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 11 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_remuneracion = 1
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
                11,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [11, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [11, 1])
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
                11,  # id_area
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
                WHERE id = ? AND id_area = 11 AND id_remuneracion = 2
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
                    WHERE id_area = 11 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 11 AND id_remuneracion = 2
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
                11,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [11, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [11, 2])
                        
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
    permission_required = 'modulo_riego'
    template_name = 'RIEGO/pages/riego_presupuesto_ajs.html'

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
                EXEC TOTAL_SERVICIOS_AJS '11', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_AJS '11'
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
            area_id = data.get('id_area', 11)
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
            values.append(11) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 11
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
                    WHERE id_area = 11 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11
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
            area_id = data.get('id_area', 11)
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

            
            values.extend([request.user.id,11, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s, %s", [11, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s", [11])

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
            
            values.extend([request.user.id,11,1,id_campania])


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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 1
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
                    WHERE id_area = 11 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,11,1])
            
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
            
            values.extend([request.user.id,11,5,id_campania])
            
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
                AND id_area = 11
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
                    WHERE id_area = 11 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,11,5])
            
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
            values.extend([request.user.id,11,7,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 7
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
                WHERE id_area = 11 AND id_tipo_suministro = 7
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
                    WHERE id_area = 11 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 11 
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
            values.extend([request.user.id,11,7])
            
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
            values.extend([request.user.id,11,8,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 8
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
                WHERE id_area = 11 AND id_tipo_suministro = 8
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
                    WHERE id_area = 11 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,11,8])


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
            
            values.extend([request.user.id,11,4,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 4
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
                WHERE id_area = 11 AND id_tipo_suministro = 4
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
                    WHERE id_area = 11 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,11,4])
            
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
            values.extend([request.user.id,11,2,id_campania])

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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 2
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
                WHERE id_area = 11 AND id_tipo_suministro = 2
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
                    WHERE id_area = 11 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,11,2])
                
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
            values.extend([request.user.id,11,9,id_campania])
            
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 9
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
                WHERE id_area = 11 AND id_tipo_suministro = 9
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
                    WHERE id_area = 11 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,11,9])
                
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
            values.extend([request.user.id,11,3,id_campania])


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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 3
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
                WHERE id_area = 11 AND id_tipo_suministro = 3
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
                    WHERE id_area = 11 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,11,3])
            
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
            values.extend([request.user.id,11,6,id_campania])
            
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
                WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 6
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
                WHERE id_area = 11 AND id_tipo_suministro = 6
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
                    WHERE id_area = 11 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 11 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,11,6])
            
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
# FECHA: 211/11/2024
#==============================================================================================


def Costos_capex_totals_ajs(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '11', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '11'
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
            id_area = data.get('id_area', 11)
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
                WHERE id = ? AND id_area = 11 
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
                    WHERE id_area = 11 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11
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
            WHERE id = ? AND id_area = 11
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
                11,
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
# FECHA: 211/11/2024
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
                11,  # id_area
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
                WHERE id = ? AND id_area = 11 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 11 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 11 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 11 AND id_remuneracion = 1
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
                11,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [11, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [11, 1])
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
                11,  # id_area
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
                WHERE id = ? AND id_area = 11 AND id_remuneracion = 2
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
                    WHERE id_area = 11 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 11 AND id_remuneracion = 2
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
                11,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [11, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [11, 2])
                        
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

## AQUI YA ESTA CON LA TABLA CORRECTA - PRODUCTO_AGRICOLA
@method_decorator(csrf_exempt, name='dispatch')
class ResumenMaterialAgricolaView(View):
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
                FROM PRODUCTO_AGRICOLA p
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
                FROM PRODUCTO_AGRICOLA p
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
            INSERT INTO PRODUCTO_AGRICOLA 
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

            cursor.execute("SELECT IDENT_CURRENT('PRODUCTO_AGRICOLA')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE PRODUCTO_AGRICOLA 
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

            cursor.execute("DELETE FROM PRODUCTO_AGRICOLA WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SuministroAgricolaListView(View):
    """GET: lista por PRODUCTO_AGRICOLA. POST: inserta fila en SUMINISTRO_AGRICOLA."""

    _meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

    def get(self, request, *args, **kwargs):
        id_pa = request.GET.get('id_producto_agricola')
        if id_pa is None or str(id_pa).strip() == '':
            return JsonResponse({'data': []})
        try:
            id_pa_int = int(id_pa)
        except (TypeError, ValueError):
            return JsonResponse({'data': [], 'message': 'id_producto_agricola inválido'}, status=400)

        try:
            cursor = connection_portalaei.cursor()
            query = """
                SELECT
                    s.id,
                    s.idproducto,
                    s.descripcion,
                    s.precio_unitario,
                    s.enero_cantidad,
                    s.enero_precio,
                    s.febrero_cantidad,
                    s.febrero_precio,
                    s.marzo_cantidad,
                    s.marzo_precio,
                    s.abril_cantidad,
                    s.abril_precio,
                    s.mayo_cantidad,
                    s.mayo_precio,
                    s.junio_cantidad,
                    s.junio_precio,
                    s.julio_cantidad,
                    s.julio_precio,
                    s.agosto_cantidad,
                    s.agosto_precio,
                    s.septiembre_cantidad,
                    s.septiembre_precio,
                    s.octubre_cantidad,
                    s.octubre_precio,
                    s.noviembre_cantidad,
                    s.noviembre_precio,
                    s.diciembre_cantidad,
                    s.diciembre_precio
                FROM SUMINISTRO_AGRICOLA s
                WHERE s.IDPRODUCTO_AGRICOLA = ?
                ORDER BY s.id
            """
            cursor.execute(query, [id_pa_int])
            columns = [column[0] for column in cursor.description]
            data = []
            for row in cursor.fetchall():
                item = {}
                for col, val in zip(columns, row):
                    key = col.lower() if isinstance(col, str) else str(col).lower()
                    if isinstance(val, Decimal):
                        item[key] = float(val)
                    else:
                        item[key] = val
                data.append(item)
            cursor.close()
            return JsonResponse({'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'data': []}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        id_pa = data.get('IDPRODUCTO_AGRICOLA')
        if id_pa is None:
            return JsonResponse({'status': 'error', 'message': 'IDPRODUCTO_AGRICOLA es obligatorio'}, status=400)

        idproducto = str(data.get('idproducto') or '').strip()
        descripcion = str(data.get('descripcion') or '').strip()
        if not idproducto or not descripcion:
            return JsonResponse({'status': 'error', 'message': 'idproducto y descripcion son obligatorios'}, status=400)

        try:
            id_pa_int = int(id_pa)
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'IDPRODUCTO_AGRICOLA inválido'}, status=400)

        precio_unitario = float(data.get('precio_unitario', 0) or 0)
        id_area = int(data.get('id_area', 11))
        id_tipo_suministro = int(data.get('id_tipo_suministro', 1))
        usuario_id = int(request.user.id) if request.user.is_authenticated else 0

        values = [id_pa_int, idproducto, descripcion, precio_unitario]
        for mes in self._meses:
            cant = float(data.get(f'{mes}_cantidad', 0) or 0)
            precio = precio_unitario * cant if cant > 0 else 0.0
            values.extend([cant, precio])
        values.extend([usuario_id, id_area, id_tipo_suministro])

        cols = ', '.join(['IDPRODUCTO_AGRICOLA', 'idproducto', 'descripcion', 'precio_unitario'] +
                         [f'{m}_cantidad, {m}_precio' for m in self._meses] +
                         ['USUARIO', 'id_area', 'id_tipo_suministro'])
        placeholders = ', '.join(['?'] * (4 + 12 * 2 + 3))
        # OUTPUT INSERTED.id evita un segundo execute en el mismo cursor (pyodbc / ODBC a veces falla con @@IDENTITY).
        sql = f'INSERT INTO SUMINISTRO_AGRICOLA ({cols}) OUTPUT INSERTED.id AS inserted_id VALUES ({placeholders})'

        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute(sql, values)
            row = cursor.fetchone()
            if not row or row[0] is None:
                connection_portalaei.rollback()
                return JsonResponse(
                    {'status': 'error', 'message': 'No se pudo obtener el ID del registro insertado'},
                    status=500,
                )
            new_id = row[0]
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Registro guardado correctamente', 'id': new_id})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass


@method_decorator(csrf_exempt, name='dispatch')
class SuministroAgricolaDetailView(View):
    """GET/PUT/DELETE de una fila de SUMINISTRO_AGRICOLA por PK id."""

    _meses = SuministroAgricolaListView._meses

    def get(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT
                    s.id,
                    s.IDPRODUCTO_AGRICOLA,
                    s.idproducto,
                    s.descripcion,
                    s.precio_unitario,
                    s.enero_cantidad, s.enero_precio,
                    s.febrero_cantidad, s.febrero_precio,
                    s.marzo_cantidad, s.marzo_precio,
                    s.abril_cantidad, s.abril_precio,
                    s.mayo_cantidad, s.mayo_precio,
                    s.junio_cantidad, s.junio_precio,
                    s.julio_cantidad, s.julio_precio,
                    s.agosto_cantidad, s.agosto_precio,
                    s.septiembre_cantidad, s.septiembre_precio,
                    s.octubre_cantidad, s.octubre_precio,
                    s.noviembre_cantidad, s.noviembre_precio,
                    s.diciembre_cantidad, s.diciembre_precio,
                    s.id_area, s.id_tipo_suministro
                FROM SUMINISTRO_AGRICOLA s
                WHERE s.id = ?
            """, [id])
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            item = {}
            for col, val in zip(columns, row):
                key = col.lower() if isinstance(col, str) else str(col).lower()
                if isinstance(val, Decimal):
                    item[key] = float(val)
                else:
                    item[key] = val
            return JsonResponse({'data': item})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        idproducto = str(data.get('idproducto') or '').strip()
        descripcion = str(data.get('descripcion') or '').strip()
        if not idproducto or not descripcion:
            return JsonResponse({'status': 'error', 'message': 'idproducto y descripcion son obligatorios'}, status=400)

        precio_unitario = float(data.get('precio_unitario', 0) or 0)
        id_area = int(data.get('id_area', 11))
        id_tipo_suministro = int(data.get('id_tipo_suministro', 1))
        usuario_id = int(request.user.id) if request.user.is_authenticated else 0

        sets = ['idproducto = ?', 'descripcion = ?', 'precio_unitario = ?']
        values = [idproducto, descripcion, precio_unitario]
        for mes in self._meses:
            cant = float(data.get(f'{mes}_cantidad', 0) or 0)
            precio = precio_unitario * cant if cant > 0 else 0.0
            sets.append(f'{mes}_cantidad = ?')
            sets.append(f'{mes}_precio = ?')
            values.extend([cant, precio])
        sets.extend(['USUARIO = ?', 'id_area = ?', 'id_tipo_suministro = ?'])
        values.extend([usuario_id, id_area, id_tipo_suministro, id])

        sql = 'UPDATE SUMINISTRO_AGRICOLA SET ' + ', '.join(sets) + ' WHERE id = ?'
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute(sql, values)
            if cursor.rowcount == 0:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Registro actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute('DELETE FROM SUMINISTRO_AGRICOLA WHERE id = ?', [id])
            if cursor.rowcount == 0:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class ApiproductosAgricolas(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        cursor = None
        try:
            # Conexión por hilo: la conexión global compartida provoca "Invalid cursor state" con peticiones concurrentes.
            conn = get_thread_connection()
            cursor = conn.cursor()
            like_pattern = '%' + query.strip() + '%' if query.strip() else '%'
            cursor.execute("""
                        SELECT * FROM (
                            SELECT p.IDPRODUCTO, p.DESCRIPCION,
                            COALESCE((
                            SELECT TOP 1 
                            CASE 
                            WHEN OC.idmoneda = '02' THEN pch.precio * OC.tipocambio
                            ELSE pch.precio
                            END
                            FROM PRECIO_COMPRA_HISTORICO pch
                            INNER JOIN ORDENCOMPRA OC ON OC.idcompra = pch.idcompra
                            WHERE pch.idproducto = p.IDPRODUCTO
                            AND pch.precio > 0
                            ORDER BY pch.fecha DESC
                            ), 0) AS ultimo_precio
                            FROM PRODUCTOS p
                            WHERE p.IDGRUPO IN ('2400', '2600')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, [like_pattern])

            data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass

###### CAMPO VERDE - MATERIA AGRICOLA ######

@method_decorator(csrf_exempt, name='dispatch')
class ResumenMaterialAgricolaCVView(View):
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
                FROM PRODUCTO_AGRICOLA_CV p
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
                FROM PRODUCTO_AGRICOLA_CV p
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
            INSERT INTO PRODUCTO_AGRICOLA_CV 
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

            cursor.execute("SELECT IDENT_CURRENT('PRODUCTO_AGRICOLA_CV')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE PRODUCTO_AGRICOLA_CV 
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

            cursor.execute("DELETE FROM PRODUCTO_AGRICOLA_CV WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SuministroAgricolaListCVView(View):
    """GET: lista por PRODUCTO_AGRICOLA_CV. POST: inserta fila en SUMINISTRO_AGRICOLA_CV."""

    _meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

    def get(self, request, *args, **kwargs):
        id_pa = request.GET.get('id_producto_agricola')
        if id_pa is None or str(id_pa).strip() == '':
            return JsonResponse({'data': []})
        try:
            id_pa_int = int(id_pa)
        except (TypeError, ValueError):
            return JsonResponse({'data': [], 'message': 'id_producto_agricola inválido'}, status=400)

        try:
            cursor = connection_portalaei.cursor()
            query = """
                SELECT
                    s.id,
                    s.idproducto,
                    s.descripcion,
                    s.precio_unitario,
                    s.enero_cantidad,
                    s.enero_precio,
                    s.febrero_cantidad,
                    s.febrero_precio,
                    s.marzo_cantidad,
                    s.marzo_precio,
                    s.abril_cantidad,
                    s.abril_precio,
                    s.mayo_cantidad,
                    s.mayo_precio,
                    s.junio_cantidad,
                    s.junio_precio,
                    s.julio_cantidad,
                    s.julio_precio,
                    s.agosto_cantidad,
                    s.agosto_precio,
                    s.septiembre_cantidad,
                    s.septiembre_precio,
                    s.octubre_cantidad,
                    s.octubre_precio,
                    s.noviembre_cantidad,
                    s.noviembre_precio,
                    s.diciembre_cantidad,
                    s.diciembre_precio
                FROM SUMINISTRO_AGRICOLA_CV s
                WHERE s.IDPRODUCTO_AGRICOLA = ?
                ORDER BY s.id
            """
            cursor.execute(query, [id_pa_int])
            columns = [column[0] for column in cursor.description]
            data = []
            for row in cursor.fetchall():
                item = {}
                for col, val in zip(columns, row):
                    key = col.lower() if isinstance(col, str) else str(col).lower()
                    if isinstance(val, Decimal):
                        item[key] = float(val)
                    else:
                        item[key] = val
                data.append(item)
            cursor.close()
            return JsonResponse({'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'data': []}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        id_pa = data.get('IDPRODUCTO_AGRICOLA')
        if id_pa is None:
            return JsonResponse({'status': 'error', 'message': 'IDPRODUCTO_AGRICOLA es obligatorio'}, status=400)

        idproducto = str(data.get('idproducto') or '').strip()
        descripcion = str(data.get('descripcion') or '').strip()
        if not idproducto or not descripcion:
            return JsonResponse({'status': 'error', 'message': 'idproducto y descripcion son obligatorios'}, status=400)

        try:
            id_pa_int = int(id_pa)
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'IDPRODUCTO_AGRICOLA inválido'}, status=400)

        precio_unitario = float(data.get('precio_unitario', 0) or 0)
        id_area = int(data.get('id_area', 11))
        id_tipo_suministro = int(data.get('id_tipo_suministro', 1))
        usuario_id = int(request.user.id) if request.user.is_authenticated else 0

        values = [id_pa_int, idproducto, descripcion, precio_unitario]
        for mes in self._meses:
            cant = float(data.get(f'{mes}_cantidad', 0) or 0)
            precio = precio_unitario * cant if cant > 0 else 0.0
            values.extend([cant, precio])
        values.extend([usuario_id, id_area, id_tipo_suministro])

        cols = ', '.join(['IDPRODUCTO_AGRICOLA', 'idproducto', 'descripcion', 'precio_unitario'] +
                         [f'{m}_cantidad, {m}_precio' for m in self._meses] +
                         ['USUARIO', 'id_area', 'id_tipo_suministro'])
        placeholders = ', '.join(['?'] * (4 + 12 * 2 + 3))
        # OUTPUT INSERTED.id evita un segundo execute en el mismo cursor (pyodbc / ODBC a veces falla con @@IDENTITY).
        sql = f'INSERT INTO SUMINISTRO_AGRICOLA_CV ({cols}) OUTPUT INSERTED.id AS inserted_id VALUES ({placeholders})'

        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute(sql, values)
            row = cursor.fetchone()
            if not row or row[0] is None:
                connection_portalaei.rollback()
                return JsonResponse(
                    {'status': 'error', 'message': 'No se pudo obtener el ID del registro insertado'},
                    status=500,
                )
            new_id = row[0]
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Registro guardado correctamente', 'id': new_id})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass


@method_decorator(csrf_exempt, name='dispatch')
class SuministroAgricolaDetailCVView(View):
    """GET/PUT/DELETE de una fila de SUMINISTRO_AGRICOLA_CV por PK id."""

    _meses = SuministroAgricolaListCVView._meses

    def get(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT
                    s.id,
                    s.IDPRODUCTO_AGRICOLA,
                    s.idproducto,
                    s.descripcion,
                    s.precio_unitario,
                    s.enero_cantidad, s.enero_precio,
                    s.febrero_cantidad, s.febrero_precio,
                    s.marzo_cantidad, s.marzo_precio,
                    s.abril_cantidad, s.abril_precio,
                    s.mayo_cantidad, s.mayo_precio,
                    s.junio_cantidad, s.junio_precio,
                    s.julio_cantidad, s.julio_precio,
                    s.agosto_cantidad, s.agosto_precio,
                    s.septiembre_cantidad, s.septiembre_precio,
                    s.octubre_cantidad, s.octubre_precio,
                    s.noviembre_cantidad, s.noviembre_precio,
                    s.diciembre_cantidad, s.diciembre_precio,
                    s.id_area, s.id_tipo_suministro
                FROM SUMINISTRO_AGRICOLA_CV s
                WHERE s.id = ?
            """, [id])
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            item = {}
            for col, val in zip(columns, row):
                key = col.lower() if isinstance(col, str) else str(col).lower()
                if isinstance(val, Decimal):
                    item[key] = float(val)
                else:
                    item[key] = val
            return JsonResponse({'data': item})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        idproducto = str(data.get('idproducto') or '').strip()
        descripcion = str(data.get('descripcion') or '').strip()
        if not idproducto or not descripcion:
            return JsonResponse({'status': 'error', 'message': 'idproducto y descripcion son obligatorios'}, status=400)

        precio_unitario = float(data.get('precio_unitario', 0) or 0)
        id_area = int(data.get('id_area', 11))
        id_tipo_suministro = int(data.get('id_tipo_suministro', 1))
        usuario_id = int(request.user.id) if request.user.is_authenticated else 0

        sets = ['idproducto = ?', 'descripcion = ?', 'precio_unitario = ?']
        values = [idproducto, descripcion, precio_unitario]
        for mes in self._meses:
            cant = float(data.get(f'{mes}_cantidad', 0) or 0)
            precio = precio_unitario * cant if cant > 0 else 0.0
            sets.append(f'{mes}_cantidad = ?')
            sets.append(f'{mes}_precio = ?')
            values.extend([cant, precio])
        sets.extend(['USUARIO = ?', 'id_area = ?', 'id_tipo_suministro = ?'])
        values.extend([usuario_id, id_area, id_tipo_suministro, id])

        sql = 'UPDATE SUMINISTRO_AGRICOLA_CV SET ' + ', '.join(sets) + ' WHERE id = ?'
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute(sql, values)
            if cursor.rowcount == 0:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Registro actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute('DELETE FROM SUMINISTRO_AGRICOLA_CV WHERE id = ?', [id])
            if cursor.rowcount == 0:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


###### INVERSIONES AJS - MATERIA AGRICOLA ######

@method_decorator(csrf_exempt, name='dispatch')
class ResumenMaterialAgricolaAJSView(View):
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
                FROM PRODUCTO_AGRICOLA_AJS p
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
                FROM PRODUCTO_AGRICOLA_AJS p
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
            INSERT INTO PRODUCTO_AGRICOLA_AJS 
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

            cursor.execute("SELECT IDENT_CURRENT('PRODUCTO_AGRICOLA_AJS')")
            id_insertado = cursor.fetchone()[0]

            return JsonResponse({'status': 'success','id': id_insertado})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection_portalaei.cursor()

            query = """
            UPDATE PRODUCTO_AGRICOLA_AJS 
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

            cursor.execute("DELETE FROM PRODUCTO_AGRICOLA_AJS WHERE ID = ?", [id])
            connection_portalaei.commit()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error','message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SuministroAgricolaListAJSView(View):
    """GET: lista por PRODUCTO_AGRICOLA_AJS. POST: inserta fila en SUMINISTRO_AGRICOLA_AJS."""

    _meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

    def get(self, request, *args, **kwargs):
        id_pa = request.GET.get('id_producto_agricola')
        if id_pa is None or str(id_pa).strip() == '':
            return JsonResponse({'data': []})
        try:
            id_pa_int = int(id_pa)
        except (TypeError, ValueError):
            return JsonResponse({'data': [], 'message': 'id_producto_agricola inválido'}, status=400)

        try:
            cursor = connection_portalaei.cursor()
            query = """
                SELECT
                    s.id,
                    s.idproducto,
                    s.descripcion,
                    s.precio_unitario,
                    s.enero_cantidad,
                    s.enero_precio,
                    s.febrero_cantidad,
                    s.febrero_precio,
                    s.marzo_cantidad,
                    s.marzo_precio,
                    s.abril_cantidad,
                    s.abril_precio,
                    s.mayo_cantidad,
                    s.mayo_precio,
                    s.junio_cantidad,
                    s.junio_precio,
                    s.julio_cantidad,
                    s.julio_precio,
                    s.agosto_cantidad,
                    s.agosto_precio,
                    s.septiembre_cantidad,
                    s.septiembre_precio,
                    s.octubre_cantidad,
                    s.octubre_precio,
                    s.noviembre_cantidad,
                    s.noviembre_precio,
                    s.diciembre_cantidad,
                    s.diciembre_precio
                FROM SUMINISTRO_AGRICOLA_AJS s
                WHERE s.IDPRODUCTO_AGRICOLA = ?
                ORDER BY s.id
            """
            cursor.execute(query, [id_pa_int])
            columns = [column[0] for column in cursor.description]
            data = []
            for row in cursor.fetchall():
                item = {}
                for col, val in zip(columns, row):
                    key = col.lower() if isinstance(col, str) else str(col).lower()
                    if isinstance(val, Decimal):
                        item[key] = float(val)
                    else:
                        item[key] = val
                data.append(item)
            cursor.close()
            return JsonResponse({'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'data': []}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        id_pa = data.get('IDPRODUCTO_AGRICOLA')
        if id_pa is None:
            return JsonResponse({'status': 'error', 'message': 'IDPRODUCTO_AGRICOLA es obligatorio'}, status=400)

        idproducto = str(data.get('idproducto') or '').strip()
        descripcion = str(data.get('descripcion') or '').strip()
        if not idproducto or not descripcion:
            return JsonResponse({'status': 'error', 'message': 'idproducto y descripcion son obligatorios'}, status=400)

        try:
            id_pa_int = int(id_pa)
        except (TypeError, ValueError):
            return JsonResponse({'status': 'error', 'message': 'IDPRODUCTO_AGRICOLA inválido'}, status=400)

        precio_unitario = float(data.get('precio_unitario', 0) or 0)
        id_area = int(data.get('id_area', 11))
        id_tipo_suministro = int(data.get('id_tipo_suministro', 1))
        usuario_id = int(request.user.id) if request.user.is_authenticated else 0

        values = [id_pa_int, idproducto, descripcion, precio_unitario]
        for mes in self._meses:
            cant = float(data.get(f'{mes}_cantidad', 0) or 0)
            precio = precio_unitario * cant if cant > 0 else 0.0
            values.extend([cant, precio])
        values.extend([usuario_id, id_area, id_tipo_suministro])

        cols = ', '.join(['IDPRODUCTO_AGRICOLA', 'idproducto', 'descripcion', 'precio_unitario'] +
                         [f'{m}_cantidad, {m}_precio' for m in self._meses] +
                         ['USUARIO', 'id_area', 'id_tipo_suministro'])
        placeholders = ', '.join(['?'] * (4 + 12 * 2 + 3))
        # OUTPUT INSERTED.id evita un segundo execute en el mismo cursor (pyodbc / ODBC a veces falla con @@IDENTITY).
        sql = f'INSERT INTO SUMINISTRO_AGRICOLA_AJS ({cols}) OUTPUT INSERTED.id AS inserted_id VALUES ({placeholders})'

        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute(sql, values)
            row = cursor.fetchone()
            if not row or row[0] is None:
                connection_portalaei.rollback()
                return JsonResponse(
                    {'status': 'error', 'message': 'No se pudo obtener el ID del registro insertado'},
                    status=500,
                )
            new_id = row[0]
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Registro guardado correctamente', 'id': new_id})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass


@method_decorator(csrf_exempt, name='dispatch')
class SuministroAgricolaDetailAJSView(View):
    """GET/PUT/DELETE de una fila de SUMINISTRO_AGRICOLA_AJS por PK id."""

    _meses = SuministroAgricolaListCVView._meses

    def get(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT
                    s.id,
                    s.IDPRODUCTO_AGRICOLA,
                    s.idproducto,
                    s.descripcion,
                    s.precio_unitario,
                    s.enero_cantidad, s.enero_precio,
                    s.febrero_cantidad, s.febrero_precio,
                    s.marzo_cantidad, s.marzo_precio,
                    s.abril_cantidad, s.abril_precio,
                    s.mayo_cantidad, s.mayo_precio,
                    s.junio_cantidad, s.junio_precio,
                    s.julio_cantidad, s.julio_precio,
                    s.agosto_cantidad, s.agosto_precio,
                    s.septiembre_cantidad, s.septiembre_precio,
                    s.octubre_cantidad, s.octubre_precio,
                    s.noviembre_cantidad, s.noviembre_precio,
                    s.diciembre_cantidad, s.diciembre_precio,
                    s.id_area, s.id_tipo_suministro
                FROM SUMINISTRO_AGRICOLA_AJS s
                WHERE s.id = ?
            """, [id])
            columns = [column[0] for column in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            item = {}
            for col, val in zip(columns, row):
                key = col.lower() if isinstance(col, str) else str(col).lower()
                if isinstance(val, Decimal):
                    item[key] = float(val)
                else:
                    item[key] = val
            return JsonResponse({'data': item})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)

        idproducto = str(data.get('idproducto') or '').strip()
        descripcion = str(data.get('descripcion') or '').strip()
        if not idproducto or not descripcion:
            return JsonResponse({'status': 'error', 'message': 'idproducto y descripcion son obligatorios'}, status=400)

        precio_unitario = float(data.get('precio_unitario', 0) or 0)
        id_area = int(data.get('id_area', 11))
        id_tipo_suministro = int(data.get('id_tipo_suministro', 1))
        usuario_id = int(request.user.id) if request.user.is_authenticated else 0

        sets = ['idproducto = ?', 'descripcion = ?', 'precio_unitario = ?']
        values = [idproducto, descripcion, precio_unitario]
        for mes in self._meses:
            cant = float(data.get(f'{mes}_cantidad', 0) or 0)
            precio = precio_unitario * cant if cant > 0 else 0.0
            sets.append(f'{mes}_cantidad = ?')
            sets.append(f'{mes}_precio = ?')
            values.extend([cant, precio])
        sets.extend(['USUARIO = ?', 'id_area = ?', 'id_tipo_suministro = ?'])
        values.extend([usuario_id, id_area, id_tipo_suministro, id])

        sql = 'UPDATE SUMINISTRO_AGRICOLA_AJS SET ' + ', '.join(sets) + ' WHERE id = ?'
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute(sql, values)
            if cursor.rowcount == 0:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Registro actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute('DELETE FROM SUMINISTRO_AGRICOLA_AJS WHERE id = ?', [id])
            if cursor.rowcount == 0:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

