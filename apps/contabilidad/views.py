from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import View
from django.http import JsonResponse
from apps.connection.connect_donluis import connection_donluis
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.connection.connect_portalaei import connection_portalaei
from decimal import Decimal
from datetime import datetime
import json
from django.db import connection
from django.db import IntegrityError
from django.db import transaction
from apps.rrhh.views import DetallesEvaluacionFinalModalView
from datetime import date
from datetime import datetime


# Create your views here.
class Contabilidad_libro_af(TemplateView):
    permission_required = 'modulo_contabilidad'
    template_name = 'contabilidad/contabilidad_libro_af.html'




class Script_Contabilidad_libro_af(View):
    
    def get(self, request, *args, **kwargs):
        year = request.GET.get('year', '')
        month = request.GET.get('month', '')
        reportType = request.GET.get('reportType', 'T')

        query = """
        EXEC NSP_AF_RPT_LIBRO_AF_DINAMICO '001', '', '{year}', '{month}', '', NULL, '01', '{reportType}'
        """.format(year=year, month=month, reportType=reportType)

        try:
            with connection_donluis.cursor() as cursor:
                cursor.execute(query)
                data_object = cursor.fetchall()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        data_json = []
        for data in data_object:
            data_json.append({
                'IDTIPOACTIVO': data[0],
                'DSC_TIPOACTIVO': data[1],
                'IDACTIVO': data[2],
                'CODALTERNO': data[3],
                'CODMANUAL': data[4],
                'IDCTAACTIVO': data[5],
                'DESCRIPCION': data[6],
                'FECHACOMPRA': data[7],
                'FECHAACTIVACION': data[8],
                'IDMARCA': data[9],
                'MARCA': data[10],
                'IDMODELO': data[11],
                'MODELO': data[12],
                'SERIE': data[13],
                'FUNCION': data[14],
                'VIDAUTIL': data[15],
                'IDMEDIDA': data[16],
                'TASA_ANUAL': data[17],
                'HCOMPRASMOF': data[18],
                'HCOMPRASMEX': data[19],
                'ACOMPRASMOF': data[20],
                'ACOMPRASMEX': data[21],
                'MCOMPRASMOF': data[22],
                'MCOMPRASMEX': data[23],
                'AINFLACION': data[24],
                'HBAJAMOF': data[25],
                'HBAJAMEX': data[26],
                'OAJUSTESMOF': data[27],
                'OAJUSTESMEX': data[28],
                'LIBACTIMOF': data[29],
                'LIBACTIMEX': data[30],
                'HDEPRECIACIONESMOF': data[31],
                'HDEPRECIACIONESMEX': data[32],
                'ADEPRECIACIONESMOF': data[33],
                'ADEPRECIACIONESMEX': data[34],
                'BDEPRECIACIONESMOF': data[35],
                'BDEPRECIACIONESMEX': data[36],
                'ODEPRECIACIONESMOF': data[37],
                'ODEPRECIACIONESMEX': data[38],
                'DLIBACTIMOF': data[39],
                'DLIBACTIMEX': data[40],
                'ULTIMO_CCOSTO': data[41],
                'DSC_CUENTA': data[42],
                'DSC_UBICACION': data[43],
                'PROVEEDOR': data[44],
                'DSC_FACTURA': data[45],
                'CANTIDADI': data[46],
                'CANTIDADS': data[47],
                'CANTIDAD': data[48],
                'IDPRODUCTO': data[49]
            })
        
        return JsonResponse(data_json, safe=False)
    

#=================================================================================================================
#MODULO PRESUPUESTOS
#AUTOR: JHON GUTIERREZ
#FECHA: 06/01/2025
#MODIFICACIONES: 
# 06/01/2025: Se crea el modulo de presupuestos
#=================================================================================================================




# PRESUPUESTO

class presupuesto_dl(TemplateView):
    permission_required = 'modulo_contabilidad'
    template_name = 'contabilidad/pages/contabilidad_presupuesto_dl.html'

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
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        #TOTAL DE SERVICIOS PARA EL AREA TIC
        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '1', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '1' 
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
            area_id = data.get('id_area', 1)
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
            values.append(1) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 1
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
                # Obtener el parámetro de campaña del request
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
                    WHERE id_area = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1
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
            area_id = data.get('id_area', 1)
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

            
            values.extend([request.user.id,1, id])
            
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



# =====================================================================================
# REPORTE DE TOTALES DE SUMINISTROS
# =====================================================================================
# Descripción: Obtiene los totales de todos los tipos de suministros para las cards
# Autor: JHON GUTIERREZ
# Área: CONTABILIDAD (id_area = 1)
# =====================================================================================
# FILTRO POR CAMPAÑA:
# - El parámetro 'year' se recibe en la URL (ej: ?year=CAMP2026)
# - Si se proporciona, se pasa al stored procedure para filtrar
# - Si NO se proporciona, el SP devuelve todos los totales sin filtro
# =====================================================================================
# ENDPOINT: GET /contabilidad/contabilidad_suministros_totals_dl/?year=CAMP2026
# =====================================================================================
def Costos_suministros_totals_dl(request):
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s, %s
            """, [1, campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s
            """, [1])

        results = dict(cursor.fetchall())

    return JsonResponse(results)

#TIPOS DE SUMINISTROS

# =====================================================================================
# VISTA: CombustiblesLubricantesView
# =====================================================================================
# Descripción: CRUD para suministros de tipo Combustibles y Lubricantes
# Autor: JHON GUTIERREZ
# Área: CONTABILIDAD (id_area = 1)
# Tipo de suministro: Combustibles y Lubricantes (id_tipo_suministro = 1)
# =====================================================================================
# FILTRO POR CAMPAÑA:
# - El parámetro 'year' se recibe en la URL (ej: ?year=CAMP2026)
# - Si se proporciona, filtra por el campo ID_CAMPANIA en la tabla TIC_suministros
# - Si NO se proporciona, devuelve TODOS los registros del área y tipo
# =====================================================================================
# ENDPOINTS:
# - GET /contabilidad/contabilidad_combustibles-lubricantes/          -> Lista todos
# - GET /contabilidad/contabilidad_combustibles-lubricantes/?year=X   -> Lista filtrado por campaña
# - GET /contabilidad/contabilidad_combustibles-lubricantes/<id>/     -> Obtiene uno por ID
# - POST /contabilidad/contabilidad_combustibles-lubricantes/         -> Crea nuevo
# - PUT /contabilidad/contabilidad_combustibles-lubricantes/<id>/     -> Actualiza
# - DELETE /contabilidad/contabilidad_combustibles-lubricantes/<id>/  -> Elimina
# =====================================================================================
@method_decorator(csrf_exempt, name='dispatch')
class CombustiblesLubricantesView(View):
    """
    Vista para gestionar suministros de Combustibles y Lubricantes.
    
    Atributos de filtrado:
        - id_area: 1 (CONTABILIDAD)
        - id_tipo_suministro: 1 (Combustibles y Lubricantes)
        - ID_CAMPANIA: Filtro opcional por campaña (ej: CAMP2026)
    """
    
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
            
            values.extend([request.user.id,1,1,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    
    def get(self, request, id=None, *args, **kwargs):
        """
        Obtiene registros de combustibles/lubricantes.
        
        Parámetros:
            - id (opcional): ID específico del registro a obtener
            - year (query param): Campaña para filtrar (ej: CAMP2026)
            
        Retorna:
            - Si id: Un solo registro
            - Si year: Lista filtrada por campaña
            - Si ninguno: TODOS los registros (sin filtro de campaña)
        """
        try:
            cursor = connection_portalaei.cursor()

            # -------------------------------------------------------------------------
            # OBTENER PARÁMETRO DE CAMPAÑA
            # -------------------------------------------------------------------------
            # El parámetro 'year' viene en la URL como query string
            # Ejemplo: /contabilidad/contabilidad_combustibles-lubricantes/?year=CAMP2026
            # -------------------------------------------------------------------------
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
                # -------------------------------------------------------------------------
                # FILTRAR POR CAMPAÑA
                # -------------------------------------------------------------------------
                # Si se proporciona el parámetro 'year', filtra por ID_CAMPANIA
                # Si NO se proporciona, devuelve TODOS los registros del área
                # -------------------------------------------------------------------------
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
                    WHERE id_area = 1 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    # SIN FILTRO DE CAMPAÑA - Devuelve todos los registros
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM TIC_suministros
                    WHERE id_area = 1 AND id_tipo_suministro = 1
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
        """Elimina un registro de combustible/lubricante por ID."""
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
            values.extend([request.user.id, 1, 1])
            
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
            
            values.extend([request.user.id,1,5,id_campania])
            
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
                FROM TIC_suministros
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 5 
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
                    WHERE id_area = 1 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,1,5])
            
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
            values.extend([request.user.id,1,7,id_campania])

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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 7
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
                WHERE id_area = 1 AND id_tipo_suministro = 7
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
                    WHERE id_area = 1 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 1
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
            values.extend([request.user.id,1,7])
            
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
            values.extend([request.user.id, 1, 8, id_campania])
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
                        params = []
                        if campania:
                            query += " AND ID_CAMPANIA = ?"
                            params.append(campania)
                        cursor.execute(query, params)
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM TIC_suministros
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 8
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
                WHERE id_area = 1 AND id_tipo_suministro = 8
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
                    WHERE id_area = 1 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,1,8])


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
            values.extend([request.user.id,1,4,id_campania])
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 4
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
                WHERE id_area = 1 AND id_tipo_suministro = 4
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
                    WHERE id_area = 1 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,1,4])
            
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
            values.extend([request.user.id,1,2,id_campania])
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 2
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
                WHERE id_area = 1 AND id_tipo_suministro = 2
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
                    WHERE id_area = 1 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,1,2])
                
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
            values.extend([request.user.id,1,9,id_campania])
            
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 9
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
                WHERE id_area = 1 AND id_tipo_suministro = 9
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
                    WHERE id_area = 1 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,1,9])
                
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
            values.extend([request.user.id,1,3,id_campania])


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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 3
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
                WHERE id_area = 1 AND id_tipo_suministro = 3
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
                    WHERE id_area = 1 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,1,3])
            
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
            values.extend([request.user.id,1,6,id_campania])
            
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 6 
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
                    WHERE id_area = 1 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_tipo_suministro = 6 
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,1,6])
            
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
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX '1', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX '1'
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
            id_area = data.get('id_area', 1)
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
                WHERE id = ? AND id_area = 1 
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
                # Obtener el parámetro de campaña del request
                campania = request.GET.get('year', '')
                
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
                    WHERE id_area = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1
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
            WHERE id = ? AND id_area = 1
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
                1,
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
                1,  # id_area
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
                WHERE id = ? AND id_area = 1 AND id_remuneracion = 1
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
                # Obtener el parámetro de campaña del request
                campania = request.GET.get('year', '')
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 1 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 1 AND id_remuneracion = 1
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
                1,  # id_area
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


def get_sueldos_totals(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            
            SELECT
                ISNULL(Mes, 'TotalGeneral') AS Mes,
                SUM(Sueldo) AS TotalSueldo
            FROM
            (
                SELECT
                    [enero],
                    [febrero],
                    [marzo],
                    [abril],
                    [mayo],
                    [junio],
                    [julio],
                    [agosto],
                    [septiembre],
                    [octubre],
                    [noviembre],
                    [diciembre]
                FROM [PORTAL_AEI].[dbo].[sueldo]
            ) AS p
            UNPIVOT
            (
                Sueldo FOR Mes IN (
                    [enero],
                    [febrero],
                    [marzo],
                    [abril],
                    [mayo],
                    [junio],
                    [julio],
                    [agosto],
                    [septiembre],
                    [octubre],
                    [noviembre],
                    [diciembre]
                )
            ) AS unpvt
            GROUP BY ROLLUP(Mes)
            HAVING Mes IS NOT NULL OR GROUPING(Mes) = 1
            ORDER BY
                CASE WHEN Mes = 'TotalGeneral' THEN 1 ELSE 0 END, Mes;
        """)
        results = dict(cursor.fetchall())
    
    return JsonResponse(results)



@method_decorator(csrf_exempt, name='dispatch')
class ApiMensualSueldos(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [1, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [1, 1])
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
                1,  # id_area
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
                WHERE id = ? AND id_area = 1 AND id_remuneracion = 2
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
                # Obtener el parámetro de campaña del request
                campania = request.GET.get('year', '')
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 1 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 1 AND id_remuneracion = 2
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
                1,  # id_area
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
            cursor.execute("exec rpt_pst_remuneracion '1','2'")
            
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
    permission_required = 'modulo_contabilidad' 
    template_name = 'contabilidad/components/DonLuis/eva_desempeno/rrhh_evaluacion_desempeño.html'


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
                cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @periodo=?", [1, periodo])
            
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
                """, [1, periodo])
            
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
                cursor.execute("EXEC RRHH_EV_OBJETIVOS_MEJORA 1")
            
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
                cursor.execute("EXEC RRHH_EV_COMPETENCIAS_MEJORA 1")
            
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
# PLAN DE CUENTAS
#================================================================================================================
class PlanCuentasView(TemplateView):
    permission_required = 'modulo_contabilidad' 
    template_name = 'contabilidad/components/DonLuis/reportes/contabilidad_plan_cuentas.html'


@method_decorator(csrf_exempt, name='dispatch')
class PlanCuentasAPIView(View):
    
    
    def get(self, request, *args, **kwargs):
        """
        Método GET que ejecuta SELECT * FROM PLANCTAS
        """
        cursor = None
        try:
            # Obtener conexión a la base de datos
            cursor = connection_donluis.cursor()
            
            # Ejecutar consulta simple
            query = "SELECT * FROM PLANCTAS"
            cursor.execute(query)
            
            # Obtener nombres de columnas
            columns = [col[0] for col in cursor.description]
            
            # Obtener todos los datos
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            data = []
            for row in rows:
                record = dict(zip(columns, row))
                
                # Formatear fecha si existe
                if 'FECHACREACION' in record and record['FECHACREACION']:
                    record['FECHACREACION'] = record['FECHACREACION'].strftime('%d/%m/%Y %H:%M')
                
                data.append(record)
            
            # Preparar respuesta
            response_data = {
                'status': 'success',
                'total_records': len(data),
                'data': data,
                'columns': columns
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'message': f'Error al ejecutar consulta: {str(e)}'
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()
    
    def post(self, request, *args, **kwargs):
        """
        Método POST para DataTable con filtros y paginación
        """
        cursor = None
        try:
            # Obtener parámetros de DataTable
            draw = int(request.POST.get('draw', 1))
            start = int(request.POST.get('start', 0))
            length = int(request.POST.get('length', 10))
            search_value = request.POST.get('search[value]', '')
            
            # Obtener filtros personalizados
            filtros = {
                'empresa': request.POST.get('empresa', ''),
                'cuenta': request.POST.get('cuenta', ''),
                'descripcion': request.POST.get('descripcion', ''),
                'tipo_cuenta': request.POST.get('tipo_cuenta', ''),
                'naturaleza': request.POST.get('naturaleza', ''),
                'estado': request.POST.get('estado', ''),
                'moneda': request.POST.get('moneda', ''),
                'codigo_sap': request.POST.get('codigo_sap', ''),
                'es_ctacte': request.POST.get('es_ctacte', ''),
                'es_monetaria': request.POST.get('es_monetaria', ''),
                'es_titulo': request.POST.get('es_titulo', ''),
                'pide_ccosto': request.POST.get('pide_ccosto', ''),
                'es_ingreso': request.POST.get('es_ingreso', ''),
                'es_costo': request.POST.get('es_costo', '')
            }
            
            # Obtener conexión a la base de datos
            cursor = connection_donluis.cursor()
            
            # Construir consulta base
            where_conditions = []
            params = []
            
            # Aplicar filtros
            if filtros['empresa']:
                where_conditions.append("IDEMPRESA = %s")
                params.append(filtros['empresa'])
                
            if filtros['cuenta']:
                where_conditions.append("IDCUENTA LIKE %s")
                params.append(f"%{filtros['cuenta']}%")
                
            if filtros['descripcion']:
                where_conditions.append("DESCRIPCION LIKE %s")
                params.append(f"%{filtros['descripcion']}%")
                
            if filtros['tipo_cuenta']:
                where_conditions.append("TIPO_CUENTA = %s")
                params.append(filtros['tipo_cuenta'])
                
            if filtros['naturaleza']:
                where_conditions.append("NATURALEZA = %s")
                params.append(filtros['naturaleza'])
                
            if filtros['estado']:
                where_conditions.append("ESTADO = %s")
                params.append(filtros['estado'])
                
            if filtros['moneda']:
                where_conditions.append("IDMONEDA = %s")
                params.append(filtros['moneda'])
                
            if filtros['codigo_sap']:
                where_conditions.append("CODIGO_SAP LIKE %s")
                params.append(f"%{filtros['codigo_sap']}%")
            
            # Búsqueda general
            if search_value:
                search_conditions = [
                    "IDCUENTA LIKE %s",
                    "DESCRIPCION LIKE %s",
                    "CODIGO_SAP LIKE %s"
                ]
                where_conditions.append(f"({' OR '.join(search_conditions)})")
                params.extend([f"%{search_value}%"] * 3)
            
            # Construir WHERE clause
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Consulta para contar total de registros
            count_query = f"""
                SELECT COUNT(*) as total
                FROM PLANCTAS
                WHERE {where_clause}
            """
            
            cursor.execute(count_query, params)
            result = cursor.fetchone()
            total_records = result[0] if result else 0
            
            # Obtener ordenamiento
            order_column = request.POST.get('order[0][column]', '1')
            order_direction = request.POST.get('order[0][dir]', 'asc')
            
            # Mapeo de columnas para ordenamiento
            columnas = [
                'IDEMPRESA', 'IDCUENTA', 'DESCRIPCION', 'ESTRUCTURA',
                'TIPO_CUENTA', 'NATURALEZA', 'ESTADO', 'IDMONEDA',
                'CODIGO_SAP', 'ES_CTACTE', 'ES_MONETARIA', 'ES_TITULO',
                'PIDE_CCOSTO', 'ES_INGRESO', 'ES_COSTO', 'idcuenta_sunat'
            ]
            
            orden_columna = columnas[int(order_column)] if int(order_column) < len(columnas) else 'IDCUENTA'
            
            # Consulta para obtener datos paginados
            data_query = f"""
                SELECT 
                    IDEMPRESA,
                    IDCUENTA,
                    DESCRIPCION,
                    ESTRUCTURA,
                    TIPO_CUENTA,
                    NATURALEZA,
                    ESTADO,
                    IDMONEDA,
                    CODIGO_SAP,
                    ES_CTACTE,
                    ES_MONETARIA,
                    ES_TITULO,
                    PIDE_CCOSTO,
                    ES_INGRESO,
                    ES_COSTO,
                    idcuenta_sunat,
                    FECHACREACION
                FROM PLANCTAS
                WHERE {where_clause}
                ORDER BY {orden_columna} {order_direction}
                OFFSET {start} ROWS FETCH NEXT {length} ROWS ONLY
            """
            
            cursor.execute(data_query, params)
            
            # Convertir resultados a lista de diccionarios
            columns = [col[0] for col in cursor.description]
            data = []
            
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                
                # Formatear fecha si existe
                if 'FECHACREACION' in record and record['FECHACREACION']:
                    record['FECHACREACION'] = record['FECHACREACION'].strftime('%d/%m/%Y %H:%M')
                
                data.append(record)
            
            # Preparar respuesta para DataTable
            response_data = {
                'draw': draw,
                'recordsTotal': total_records,
                'recordsFiltered': total_records,
                'data': data
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'draw': request.POST.get('draw', 1),
                'recordsTotal': 0,
                'recordsFiltered': 0,
                'data': []
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


####################################################################################################################################
# RESUMEN DE COMPETENCIAS - CONTABILIDAD
####################################################################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class ResumenCompetenciasView(View):
    @transaction.atomic
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetro de periodo (año)
            periodo = request.GET.get('campania')  # Mantener 'campania' como nombre del parámetro para compatibilidad
            if not periodo:
                # Si no se proporciona periodo, usar el año actual
                periodo = str(datetime.now().year)
            
            # Extraer solo el año si viene en formato CAMP2026
            if periodo.startswith('CAMP'):
                periodo = periodo.replace('CAMP', '')
            
            # Ejecutar el procedimiento almacenado con el parámetro de periodo
            # CONTABILIDAD usa id_area=1
            cursor.execute("EXEC SP_RESUMEN_RRHH_COMPETENCIAS @id_area=?, @periodo=?", [1, periodo])
            
            # Obtener los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            competencias = []
            for row in cursor.fetchall():
                competencia = dict(zip(columns, row))
                # Convertir fechas a formato string para JSON si existen
                if 'fecha_inicio' in competencia and competencia['fecha_inicio']:
                    competencia['fecha_inicio'] = competencia['fecha_inicio'].strftime('%Y-%m-%d')
                if 'fecha_fin' in competencia and competencia['fecha_fin']:
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
            campania = request.GET.get('campania', None)
            
            # DEBUG: Imprimir parámetros recibidos
            print(f"[CONTABILIDAD DEBUG] Parámetros recibidos:")
            print(f"  - id_area: {id_area}")
            print(f"  - id_evaluacion: {id_evaluacion}")
            print(f"  - campania: {campania}")
            
            # Si no se proporciona campaña, usar la campaña actual
            if not campania:
                anio_actual = date.today().year
                campania = str(anio_actual)
                print(f"[CONTABILIDAD DEBUG] No se proporcionó campaña, usando año actual: {campania}")
            else:
                # Extraer solo el año si viene en formato CAMP2026
                if campania.startswith('CAMP'):
                    campania = campania.replace('CAMP', '')
                print(f"[CONTABILIDAD DEBUG] Campaña procesada: {campania}")
            
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
                # Obtener lista general de evaluaciones para la fase intermedia con filtro de campaña
                print(f"[CONTABILIDAD DEBUG] Ejecutando SP_FASE_INTERMEDIA_EVALUACIONES")
                print(f"  - id_area: {id_area}")
                print(f"  - periodo: {campania}")
                
                if id_area:
                    cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES @id_area=?, @periodo=?", [id_area, campania])
                else:
                    cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES @periodo=?", [campania])
                
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
                
                print(f"[CONTABILIDAD DEBUG] Total de evaluaciones encontradas: {len(evaluaciones)}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluaciones de fase intermedia obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'campania': campania,
                    'filtros_aplicados': {
                        'id_area': id_area,
                        'campania': campania
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

                    
                    # Realizar la actualización del porcentaje
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
    permission_required = 'modulo_contabilidad'
    template_name = 'contabilidad/pages/contabilidad_presupuesto_cv.html'   

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
        #TOTAL DE SERVICIOS PARA EL AREA TIC
        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '1', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '1' 
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
            area_id = data.get('id_area', 1)
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
                USUARIO,id_area,ID_CAMPANIA
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
            values.append(1) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 1
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
                # Obtener el parámetro de campaña del request
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
                    FROM SERVICIOS_CV 
                    WHERE id_area = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1
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
            area_id = data.get('id_area', 1)
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

            
            values.extend([request.user.id,1, id])
            
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
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_CV %s, %s
            """, [1, campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_CV %s
            """, [1])

        results = dict(cursor.fetchall())

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
            
            values.extend([request.user.id,1,1,id_campania])


            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Material registrado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)})

    
    def get(self, request, id=None, *args, **kwargs):
        """
        Obtiene registros de combustibles/lubricantes.
        
        Parámetros:
            - id (opcional): ID específico del registro a obtener
            - year (query param): Campaña para filtrar (ej: CAMP2026)
            
        Retorna:
            - Si id: Un solo registro
            - Si year: Lista filtrada por campaña
            - Si ninguno: TODOS los registros (sin filtro de campaña)
        """
        try:
            cursor = connection_portalaei.cursor()

            # -------------------------------------------------------------------------
            # OBTENER PARÁMETRO DE CAMPAÑA
            # -------------------------------------------------------------------------
            # El parámetro 'year' viene en la URL como query string
            # Ejemplo: /contabilidad/contabilidad_combustibles-lubricantes/?year=CAMP2026
            # -------------------------------------------------------------------------
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
                # -------------------------------------------------------------------------
                # FILTRAR POR CAMPAÑA
                # -------------------------------------------------------------------------
                # Si se proporciona el parámetro 'year', filtra por ID_CAMPANIA
                # Si NO se proporciona, devuelve TODOS los registros del área
                # -------------------------------------------------------------------------
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
                    WHERE id_area = 1 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    # SIN FILTRO DE CAMPAÑA - Devuelve todos los registros
                    query = """
                    SELECT id, idproducto, descripcion,precio_unitario,
                           enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                           marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                           mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                           julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                           septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                           noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                    FROM SUMINISTRO_CV
                    WHERE id_area = 1 AND id_tipo_suministro = 1
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
        """Elimina un registro de combustible/lubricante por ID."""
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
            values.extend([request.user.id, 1, 1])
            
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
            
            values.extend([request.user.id,1,5,id_campania])
            
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 5 
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
                    WHERE id_area = 1 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,1,5])
            
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
            values.extend([request.user.id,1,7,id_campania])

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
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 7
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
                WHERE id_area = 1 AND id_tipo_suministro = 7
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
                    WHERE id_area = 1 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 1
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
            values.extend([request.user.id,1,7])
            
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
            values.extend([request.user.id, 1, 8, id_campania])
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
                        params = []
                        if campania:
                            query += " AND ID_CAMPANIA = ?"
                            params.append(campania)
                        cursor.execute(query, params)
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 8
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
                FROM SUMINISTRO_CV
                WHERE id_area = 1 AND id_tipo_suministro = 8
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
                    WHERE id_area = 1 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,1,8])


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
            values.extend([request.user.id,1,4,id_campania])
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
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 4
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
                WHERE id_area = 1 AND id_tipo_suministro = 4
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
                    WHERE id_area = 1 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,1,4])
            
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
            values.extend([request.user.id,1,2,id_campania])
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 2
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
                WHERE id_area = 1 AND id_tipo_suministro = 2
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
                    WHERE id_area = 1 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,1,2])
                
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
            values.extend([request.user.id,1,9,id_campania])
            
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
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 9
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
                WHERE id_area = 1 AND id_tipo_suministro = 9
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
                    WHERE id_area = 1 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,1,9])
                
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
            values.extend([request.user.id,1,3,id_campania])


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
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 3
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
                WHERE id_area = 1 AND id_tipo_suministro = 3
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
                    WHERE id_area = 1 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,1,3])
            
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
            values.extend([request.user.id,1,6,id_campania])
            
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
                FROM SUMINISTRO_CV
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 6 
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
                    WHERE id_area = 1 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_tipo_suministro = 6 
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,1,6])
            
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
                EXEC RPT_PST_CAPEX_CV '1', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '1'
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
            id_area = data.get('id_area', 1)
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
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio,observacion
                FROM CAPEX_CV
                WHERE id = ? AND id_area = 1 
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
                # Obtener el parámetro de campaña del request
                campania = request.GET.get('year', '')
                
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
                    WHERE id_area = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1
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
            WHERE id = ? AND id_area = 1
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
                1,
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
                1,  # id_area
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
                WHERE id = ? AND id_area = 1 AND id_remuneracion = 1
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
                # Obtener el parámetro de campaña del request
                campania = request.GET.get('year', '')
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 1 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 1 AND id_remuneracion = 1
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
                1,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [1, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [1, 1])
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
                1,  # id_area
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
                WHERE id = ? AND id_area = 1 AND id_remuneracion = 2
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
                # Obtener el parámetro de campaña del request
                campania = request.GET.get('year', '')
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV
                    WHERE id_area = 1 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV
                    WHERE id_area = 1 AND id_remuneracion = 2
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
                1,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [1, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [1, 2])
                        
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
    permission_required = 'modulo_contabilidad'
    template_name = 'contabilidad/pages/contabilidad_presupuesto_ajs.html'

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
                EXEC TOTAL_SERVICIOS_AJS '1', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_AJS '1'
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
            area_id = data.get('id_area', 1)
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
            values.append(1) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 1
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
                    WHERE id_area = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1
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
            area_id = data.get('id_area', 1)
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

            
            values.extend([request.user.id,1, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s, %s", [1, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s", [1])

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
            
            values.extend([request.user.id,1,1,id_campania])


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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
                    WHERE id_area = 1 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,1,1])
            
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
            
            values.extend([request.user.id,1,5,id_campania])
            
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
                AND id_area = 1
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
                    WHERE id_area = 1 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,1,5])
            
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
            values.extend([request.user.id,1,1,id_campania])

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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 7
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
                WHERE id_area = 1 AND id_tipo_suministro = 7
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
                    WHERE id_area = 1 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 1 
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
            values.extend([request.user.id,1,1])
            
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
            values.extend([request.user.id,1,1,id_campania])

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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
                WHERE id_area = 1 AND id_tipo_suministro = 1
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
                    WHERE id_area = 1 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,1,1])


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
            
            values.extend([request.user.id,1,4,id_campania])

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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 4
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
                WHERE id_area = 1 AND id_tipo_suministro = 4
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
                    WHERE id_area = 1 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,1,4])
            
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
            values.extend([request.user.id,1,2,id_campania])

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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 2
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
                WHERE id_area = 1 AND id_tipo_suministro = 2
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
                    WHERE id_area = 1 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,1,2])
                
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
            values.extend([request.user.id,1,9,id_campania])
            
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 9
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
                WHERE id_area = 1 AND id_tipo_suministro = 9
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
                    WHERE id_area = 1 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,1,9])
                
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
            values.extend([request.user.id,1,1,id_campania])


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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
                WHERE id_area = 1 AND id_tipo_suministro = 1
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
                    WHERE id_area = 1 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,1,1])
            
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
            values.extend([request.user.id,1,6,id_campania])
            
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
                WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 6
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
                WHERE id_area = 1 AND id_tipo_suministro = 6
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
                    WHERE id_area = 1 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 1 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,1,6])
            
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
# FECHA: 21/11/201
#==============================================================================================


def Costos_capex_totals_ajs(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '1', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '1'
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
            id_area = data.get('id_area', 1)
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
                WHERE id = ? AND id_area = 1 
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
                    WHERE id_area = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1
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
            WHERE id = ? AND id_area = 1
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
                1,
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
# FECHA: 21/11/201
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
                1,  # id_area
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
                WHERE id = ? AND id_area = 1 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 1 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 1 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 1 AND id_remuneracion = 1
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
                1,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [1, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [1, 1])
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
                1,  # id_area
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
                WHERE id = ? AND id_area = 1 AND id_remuneracion = 2
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
                    WHERE id_area = 1 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 1 AND id_remuneracion = 2
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
                1,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [1, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [1, 2])
                        
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




##########################################################################3
# REPORTE DE INGRESOS Y SALIDAS ALMACEN
##########################################################################3

class Contabilidad_libro_af(TemplateView):
    permission_required = 'modulo_contabilidad'
    template_name = 'contabilidad/pages/conta_ingreso_salida_alm_dl.html'





@method_decorator(csrf_exempt, name='dispatch')
class IngresoSalidaAlmView(View):
    # Nombre correcto de la tabla
    NOMBRE_TABLA = "INGRESOSALIDAALM"
    
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_donluis.cursor()
            
            # Verificar si la tabla existe
            cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{self.NOMBRE_TABLA}'")
            if cursor.fetchone()[0] == 0:
                return JsonResponse({
                    'status': 'error',
                    'message': f'La tabla {self.NOMBRE_TABLA} no existe en la base de datos'
                }, status=404)
            
            # Si se solicita un registro específico por ID
            if id:
                return self.obtener_registro_por_id(id, cursor)
            
            # Si es solicitud de exportación
            if 'exportar' in request.path:
                return self.exportar_datos(request, cursor)
            
            # Obtener parámetros de filtrado
            periodo = request.GET.get('periodo', '')
            estado = request.GET.get('estado', '')
            operacion = request.GET.get('operacion', '')
            
            # Obtener parámetros de paginación
            pagina = int(request.GET.get('pagina', 1))
            registros_por_pagina = int(request.GET.get('registros', 100))
            
            # Construir la consulta base
            query = f"SELECT * FROM {self.NOMBRE_TABLA} WHERE 1=1"
            params = []
            
            # Aplicar filtros si existen
            if periodo:
                query += " AND PERIODO = ?"
                params.append(periodo)
                
            if estado:
                query += " AND IDESTADO = ?"
                params.append(estado)
                
            if operacion:
                query += " AND IDOPERACION = ?"
                params.append(operacion)
            
            # Obtener total de registros con filtros aplicados
            count_query = f"SELECT COUNT(*) FROM {self.NOMBRE_TABLA} WHERE 1=1"
            count_params = []
            
            if periodo:
                count_query += " AND PERIODO = ?"
                count_params.append(periodo)
                
            if estado:
                count_query += " AND IDESTADO = ?"
                count_params.append(estado)
                
            if operacion:
                count_query += " AND IDOPERACION = ?"
                count_params.append(operacion)
                
            cursor.execute(count_query, count_params)
            total_registros = cursor.fetchone()[0]
            
            # Calcular offset para paginación
            offset = (pagina - 1) * registros_por_pagina
            
            # Añadir ordenamiento y paginación
            query += " ORDER BY IDINGRESOSALIDAALM DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            params.append(offset)
            params.append(registros_por_pagina)
            
            # Ejecutar consulta final
            cursor.execute(query, params)
            
            columns = [column[0] for column in cursor.description]
            data = []
            
            for row in cursor.fetchall():
                item = dict(zip(columns, row))
                # Convertir valores Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                data.append(item)
            
            cursor.close()
            
            # Devolver respuesta en formato adecuado
            return JsonResponse({
                "tabla_utilizada": self.NOMBRE_TABLA,
                "data": data,
                "total_registros": total_registros,
                "pagina_actual": pagina,
                "total_paginas": (total_registros + registros_por_pagina - 1) // registros_por_pagina,
                "registros_por_pagina": registros_por_pagina
            })
                
        except Exception as e:
            # Añadir más detalles sobre el error
            import traceback
            error_traceback = traceback.format_exc()
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'traceback': error_traceback
            }, status=500)
    
    def obtener_registro_por_id(self, id, cursor):
        """Obtiene un registro específico por su ID"""
        query = f"""
        SELECT * FROM {self.NOMBRE_TABLA}
        WHERE IDINGRESOSALIDAALM = ?
        """
        cursor.execute(query, [id])
        
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        
        if row:
            item = dict(zip(columns, row))
            # Convertir valores Decimal a float para serialización JSON
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
            cursor.close()
            return JsonResponse(item)
        else:
            cursor.close()
            return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
    
    def exportar_datos(self, request, cursor):
        """Exporta todos los datos según los filtros aplicados"""
        # Obtener parámetros de filtrado
        periodo = request.GET.get('periodo', '')
        estado = request.GET.get('estado', '')
        operacion = request.GET.get('operacion', '')
        
        # Construir la consulta con filtros
        query = f"SELECT * FROM {self.NOMBRE_TABLA} WHERE 1=1"
        params = []
        
        if periodo:
            query += " AND PERIODO = ?"
            params.append(periodo)
            
        if estado:
            query += " AND IDESTADO = ?"
            params.append(estado)
            
        if operacion:
            query += " AND IDOPERACION = ?"
            params.append(operacion)
        
        # Limitar a un máximo de registros para exportación
        max_exportar = 5000
        query += f" ORDER BY IDINGRESOSALIDAALM DESC OFFSET 0 ROWS FETCH NEXT {max_exportar} ROWS ONLY"
        
        # Ejecutar consulta
        cursor.execute(query, params)
        
        columns = [column[0] for column in cursor.description]
        data = []
        
        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            # Convertir valores Decimal a float para serialización JSON
            for key, value in item.items():
                if isinstance(value, Decimal):
                    item[key] = float(value)
            data.append(item)
        
        cursor.close()
        
        return JsonResponse({
            "tabla_utilizada": self.NOMBRE_TABLA,
            "data": data,
            "filtros": {
                "periodo": periodo,
                "estado": estado,
                "operacion": operacion
            },
            "total_registros": len(data),
            "limite_exportacion": max_exportar
        })

# ============================================
#   FASE FINAL – CONTABILIDAD
# ============================================

# API para la fase final tabla principal
@method_decorator(csrf_exempt, name='dispatch')
class FaseFinalEvaluacionesContaView(View):
    """
    Vista para manejar la fase final de evaluaciones de desempeño
    Permite consultar evaluaciones con porcentajes de avance final de objetivos y competencias
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros opcionales
            id_area = request.GET.get('id_area')
            id_evaluacion = request.GET.get('id_evaluacion')
            campania = request.GET.get('campania', None)
            
            # DEBUG: Imprimir parámetros recibidos
            print(f"[CONTABILIDAD FASE FINAL DEBUG] Parámetros recibidos:")
            print(f"  - id_area: {id_area}")
            print(f"  - id_evaluacion: {id_evaluacion}")
            print(f"  - campania: {campania}")
            
            # Si no se proporciona campaña, usar la campaña actual
            if not campania:
                anio_actual = date.today().year
                campania = str(anio_actual)
                print(f"[CONTABILIDAD FASE FINAL DEBUG] No se proporcionó campaña, usando año actual: {campania}")
            else:
                # Extraer solo el año si viene en formato CAMP2026
                if campania.startswith('CAMP'):
                    campania = campania.replace('CAMP', '')
                print(f"[CONTABILIDAD FASE FINAL DEBUG] Campaña procesada: {campania}")
            
            if id_evaluacion:
                # Si se solicita una evaluación específica, usar el procedimiento de detalles
                cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES ?", [id_evaluacion])
                
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
                    'message': 'Detalles de evaluación final obtenidos correctamente',
                    'data': {
                        'evaluacion': evaluacion_data,
                        'objetivos': objetivos,
                        'competencias': competencias
                    }
                })
                
            else:
                # Obtener lista general de evaluaciones para la fase final con filtro de campaña
                print(f"[CONTABILIDAD FASE FINAL DEBUG] Ejecutando SP_FASE_FINAL_EVALUACIONES")
                print(f"  - id_area: {id_area}")
                print(f"  - periodo: {campania}")
                
                if id_area:
                    cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES @id_area=?, @periodo=?", [id_area, campania])
                else:
                    cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES @periodo=?", [campania])
                
                # Obtener los nombres de las columnas
                columns = [column[0] for column in cursor.description]
                
                # Convertir los resultados a una lista de diccionarios
                evaluaciones = []
                for row in cursor.fetchall():
                    evaluacion = dict(zip(columns, row))
                    
                    # Convertir fecha a string para JSON si existe
                    if 'fecha_evaluacion' in evaluacion and evaluacion['fecha_evaluacion']:
                        evaluacion['fecha_evaluacion'] = evaluacion['fecha_evaluacion'].strftime('%Y-%m-%d')
                    
                    # Asegurar que los porcentajes sean números enteros (usar los mismos campos que fase intermedia)
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
                
                print(f"[CONTABILIDAD FASE FINAL DEBUG] Total de evaluaciones encontradas: {len(evaluaciones)}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluaciones de fase final obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'campania': campania,
                    'filtros_aplicados': {
                        'id_area': id_area,
                        'campania': campania
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
class DetallesEvaluacionFinalContaView(View):
    """
    Vista para obtener detalles finales de objetivos o competencias para el modal de avance final
    Ejecuta el procedimiento almacenado SP_OBTENER_DETALLES_EVALUACION_FINAL_MODAL
    
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
            cargar_comentarios = request.GET.get('cargar_comentarios')  # Para cargar solo comentarios finales
            
            # Si se solicita cargar solo comentarios finales
            if cargar_comentarios == 'true' and id_evaluacion:
                try:
                    id_evaluacion_int = int(id_evaluacion)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El parámetro id_evaluacion debe ser un número válido'
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
                    print(f"Error al consultar campos específicos, usando campos estándar: {query_error}")
                    # Si falla, usar campos estándar
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
                        'message': 'No se encontraron comentarios finales para esta evaluación',
                        'comentarios': {
                            'comentarios_objetivos_general_final': '',
                            'comentarios_competencias_general_final': ''
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
                
                # Asegurar que los porcentajes sean números enteros
                # Para fase final, usar el campo porc_etapa_final si existe, sino usar porcentaje_actual
                if 'porc_etapa_final' in detalle:
                    detalle['porc_etapa_final'] = int(detalle['porc_etapa_final']) if detalle['porc_etapa_final'] is not None else 0
                else:
                    # Si no existe porc_etapa_final, usar porcentaje_actual como base
                    detalle['porc_etapa_final'] = int(detalle.get('porcentaje_actual', 0)) if detalle.get('porcentaje_actual') is not None else 0
                
                if 'porcentaje_actual' in detalle:
                    detalle['porcentaje_actual'] = int(detalle['porcentaje_actual']) if detalle['porcentaje_actual'] is not None else 0
                
                # Asegurar que los campos de comentarios finales existen según el tipo
                if tipo_tabla_int == 1:  # Objetivos
                    if 'coment_objetivo_ff' not in detalle:
                        detalle['coment_objetivo_ff'] = ''  # Solo usar campo específico, sin fallback
                else:  # Competencias
                    if 'coment_competencia_ff' not in detalle:
                        detalle['coment_competencia_ff'] = ''  # Solo usar campo específico, sin fallback
                
                # Consulta adicional para obtener comentarios finales específicos de este registro
                try:
                    registro_id = detalle.get('id')
                    if registro_id:
                        tabla_consulta = "RRHH_OBJETIVOS" if tipo_tabla_int == 1 else "RRHH_COMPETENCIAS"
                        cursor_extra = connection_portalaei.cursor()
                        
                        # Usar el campo correcto según el tipo de tabla
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
                            # Sobreescribir con datos específicos de fase final (sin fallbacks)
                            if tipo_tabla_int == 1:  # Objetivos
                                detalle['coment_objetivo_ff'] = resultado_extra[0] or ''
                            else:  # Competencias
                                detalle['coment_competencia_ff'] = resultado_extra[0] or ''
                            if resultado_extra[1] is not None:
                                detalle['porc_etapa_final'] = int(resultado_extra[1])
                        cursor_extra.close()
                except Exception as e:
                    print(f"Error al consultar datos específicos de fase final: {e}")
                    # Continuar con los datos básicos
                
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
        Actualizar porcentajes de avance final para múltiples objetivos o competencias
        Incluye actualización de comentarios generales finales en la tabla RRHH_EVALUACIONES
        
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
            
            # Validar estructura básica de datos
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
            
            # Procesar cada actualización de porcentajes finales
            for actualizacion in actualizaciones:
                try:
                    # Validar estructura de cada actualización
                    if 'id' not in actualizacion or 'porc_etapa_final' not in actualizacion:
                        actualizaciones_fallidas.append({
                            'registro': actualizacion,
                            'error': 'Faltan campos "id" o "porc_etapa_final"'
                        })
                        continue
                    
                    registro_id = actualizacion['id']
                    porcentaje_final = actualizacion['porc_etapa_final']
                    # Usar el campo correcto según el tipo de tabla
                    if tipo_tabla == 1:  # Objetivos
                        comentario_final = actualizacion.get('coment_objetivo_ff', '')
                    else:  # Competencias
                        comentario_final = actualizacion.get('coment_competencia_ff', '')
                    
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
                    
                    # Realizar la actualización del porcentaje final y comentario final
                    # Usar el campo correcto según el tipo de tabla
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
                        print(f"Error al actualizar con campos específicos, intentando con campos estándar: {update_error}")
                        # Si falla, usar campos estándar de la fase intermedia
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porcentaje_actual = ?, comentarios = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_final, comentario_final, registro_id])
                    
                    # Verificar que se actualizó al menos una fila
                    if cursor.rowcount > 0:
                        # Usar el campo correcto en el log según el tipo de tabla
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
                        'error': f'Error al procesar actualización final: {str(e)}'
                    })
                    continue
            
            # Actualizar comentarios generales finales en la tabla RRHH_EVALUACIONES
            comentarios_actualizados = False
            if id_evaluacion:
                try:
                    # Verificar que la evaluación existe
                    cursor.execute("""
                        SELECT id FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion])
                    
                    if cursor.fetchone():
                        # Actualizar comentarios finales según el tipo
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
                            print(f"Error al actualizar comentarios específicos, usando campos estándar: {comment_error}")
                            # Si falla, usar campos estándar
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
                            print(f"Comentarios generales finales actualizados para evaluación {id_evaluacion}")
                    else:
                        print(f"Evaluación {id_evaluacion} no encontrada o inactiva")
                        
                except Exception as e:
                    print(f"Error al actualizar comentarios generales finales: {str(e)}")
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
                    message = f"Ninguna actualización final fue exitosa (0/{total_actualizaciones})"
                    status = 'error'
            
            tipo_nombre = "objetivos" if tipo_tabla == 1 else "competencias"
            
            print(f"Actualización final de {tipo_nombre}: {exitosas} exitosas, {fallidas} fallidas, comentarios: {comentarios_actualizados}")
            
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















