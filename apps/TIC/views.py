from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.connection.connect_donluis import connection_donluis
from apps.connection.connect_campoverde import connection_campoverde
from apps.connection.connect_inversioneajs import connection_inversioneajs
from apps.connection.connect_portalaei import connection_portalaei
from django.views.generic import TemplateView
from decimal import Decimal
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
from django.db import connection
from django.db import IntegrityError
from django.db import transaction
from .forms import PDFFileForm
from .models import PDFFile
from django.contrib import messages

# Create your views here.

# VISTA PARA PROCESOS TIC - MANEJO DE PDFs
class tic(View):
    
    def get(self, request):
        form = PDFFileForm()
        pdf_files = PDFFile.objects.all().order_by('-uploaded_at')
        return render(request, 'TICS/procesos_tic.html', {'form': form, 'pdf_files': pdf_files})
    
    def post(self, request):
        form = PDFFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Archivo subido con éxito.')
            return redirect('procesos_tic')
        pdf_files = PDFFile.objects.all().order_by('-uploaded_at')
        return render(request, 'TICS/procesos_tic.html', {'form': form, 'pdf_files': pdf_files})

def eliminar_pdf_tic(request, pdf_id):
    pdf = get_object_or_404(PDFFile, id=pdf_id)
    pdf.delete()
    messages.success(request, 'Archivo eliminado con éxito.')
    return redirect('procesos_tic')


# VISTA PARA EL PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS


#======================================================================================================
# SECCION PRESUPUESTO
#=======================================================================================================

class Tic_presupuesto_dl(TemplateView):
    permission_required = 'ver_tic','tic_dl','tic_cv','tic_ajs','view_josep'
    template_name = 'TICS/pages/presupuesto_dl.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        return context


#======================================================================================================
# SECCION COSTOS
#=======================================================================================================

class Tic_costos_dl_view(TemplateView):
    permission_required = 'ver_tic','tic_dl','tic_cv','tic_ajs'
    template_name = 'TICS/pages/tic_costos_dl.html'

#======================================================================================================
# SECCION MANTENIMIENTO
#=======================================================================================================

class Tic_mantenimiento_dl_view(TemplateView):
    permission_required = 'ver_tic','tic_dl','tic_cv','tic_ajs'
    template_name = 'TICS/pages/tic_mantenimiento_dl.html'

#======================================================================================================
# SECCION EVALUACION DE DESEMPEÑO
#=======================================================================================================

class Tic_evaluacion_desempeño(TemplateView):
    permission_required = 'ver_tic','tic_dl','tic_cv','tic_ajs'
    template_name = 'TICS/pages/tic_evaluacion_desempeño.html'


@method_decorator(csrf_exempt, name='dispatch')
class EvaluacionesGeneralView(View):
    def get(self, request, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC RPT_EVALUACIONES_GENERAL_RRHH 4 ")
                
                # Obtener los nombres de las columnas
                columns = [col[0] for col in cursor.description]
                
                # Obtener los resultados y convertirlos a diccionario
                results = []
                for row in cursor.fetchall():
                    # Convertir valores None a tipos apropiados
                    processed_row = []
                    for value in row:
                        if value is None:
                            processed_row.append(0)  # o '' dependiendo del caso
                        else:
                            processed_row.append(value)
                    
                    results.append(dict(zip(columns, processed_row)))

            return JsonResponse({
                'status': 'success',
                'data': results
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'type': type(e).__name__
            }, status=500)

    def handle_none_values(self, value):
        """Maneja valores nulos según el tipo de dato esperado"""
        if value is None:
            return 0  # o '' dependiendo del caso
        return value


#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - TOTALES DE LOS SUMINISTROS  DE DON LUIS
#=====================================================================================================

def get_suministros_totals(request):
    campania = request.GET.get('year', '')  # valor por defecto

    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s, %s
            """, [4, campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_SUMINISTROS_MEJORA %s
            """, [4])

        results = dict(cursor.fetchall())
    return JsonResponse(results)



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

def get_salarios_totals(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            
            exec RPT_PST_REMUNERACION_TOTALES '4','2'
        """)
        results = dict(cursor.fetchall())
    


    return JsonResponse(results)

def get_capex_totals(request):
     # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX '4', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX '4'
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

def get_tic_servicio_totals(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')

    with connection.cursor() as cursor:

        if campania:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '4', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS '4'
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

#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - COMBUSTIBLES Y LUBRICANTES DE DON LUIS
#=====================================================================================================
@method_decorator(csrf_exempt, name='dispatch')
class MaterialOficinaView(View):
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
            
            values.extend([request.user.id,4,1,id_campania])


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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 1
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
                    WHERE id_area = 4 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,4,1])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     

class Apiproductos(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:
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
                            WHERE (IDGRUPO = '2500' AND (IDSUBGRUPO = '001' OR IDSUBGRUPO = '002' ))
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])
                
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        
#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - UTILES DE OFICINA DE DON LUIS
#=====================================================================================================

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
            
            values.extend([request.user.id,4,5,id_campania])
            
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
                AND id_area = 4 
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
                    WHERE id_area = 4 
                    AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,4,5])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
class ApiProductosUtiles(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:
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
                            WHERE (p.IDGRUPO = '2500' AND p.IDSUBGRUPO = '011' OR p.IDGRUPO = '2502' AND p.IDSUBGRUPO = '001')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])
                    
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        

#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - EQUIPOS DE COMPUTO DE DON LUIS
#=====================================================================================================


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
            values.extend([request.user.id,4,7,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 7
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
                WHERE id_area = 4 AND id_tipo_suministro = 7
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
                    WHERE id_area = 4 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 4 
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
            values.extend([request.user.id,4,7])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     

class ApiProductosComputo(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE (IDGRUPO = '2500'  AND IDSUBGRUPO = '013')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                            WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])

                    
                
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        
#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - OTROS SUMINISTROS DE DON LUIS
#=====================================================================================================

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
            values.extend([request.user.id,4,8, id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 8
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
                WHERE id_area = 4 AND id_tipo_suministro = 8
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
                    WHERE id_area = 4 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,4,8])


            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

class ApiProductosOtrosSuministros(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE (IDGRUPO = '2500'  AND IDSUBGRUPO = '010')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])

                    
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
       

#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - METERIAL DE CONSTRUCCION DE DON LUIS
#=====================================================================================================
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
            
            values.extend([request.user.id,4,4,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
                WHERE id_area = 4 AND id_tipo_suministro = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,4,4])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

class ApiProductosMaterialConstruccion(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE IDGRUPO = '2500'  AND (IDSUBGRUPO = '004' OR IDSUBGRUPO = '006' OR IDSUBGRUPO = '007' OR IDSUBGRUPO = '008')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])   

                    
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
       

#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - REPUESTOS Y ACCESORIOS DE DON LUIS
#=====================================================================================================

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
            values.extend([request.user.id,4,2,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 2
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
                WHERE id_area = 4 AND id_tipo_suministro = 2
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
                    WHERE id_area = 4 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,4,2])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
      

class ApiProductosRepuestosAccesorios(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE IDGRUPO = '2500'  AND (IDSUBGRUPO = '009' OR IDSUBGRUPO = '003')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;

                    """, ['%' + query + '%'])

                    
                
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)


#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - EQUIPOS < 1/4 de UIT DE DON LUIS
#=====================================================================================================

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
            values.extend([request.user.id,4,9,id_campania])
            
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 9
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
                WHERE id_area = 4 AND id_tipo_suministro = 9
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
                    WHERE id_area = 4 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,4,9])
                
                # Agregar el id al final de la lista de valores
                values.append(id)
                
                cursor.execute(query, values)
                
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

class ApiProductosEquiposUIT(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE (IDGRUPO = '2400'  AND p.IDSUBGRUPO ='015')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])

                    
                
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)

#=====================================================================================================
#VISTA PARA EL PRESUPUESTO - MATERIALES PARA AGRICULTURA DE DON LUIS
#=====================================================================================================

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
            values.extend([request.user.id,4,3,id_campania])


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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 3
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
                WHERE id_area = 4 AND id_tipo_suministro = 3
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
                    WHERE id_area = 4 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,4,3])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     

class ApiProductosMaterialesAgricultura(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE (IDGRUPO = '2500'  AND (p.IDSUBGRUPO ='005' OR p.IDSUBGRUPO ='014'))
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])

                    
                
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)


#=====================================================================================================
#  VISTA PARA EL PRESUPUESTO - EQUIPOS DE PROTECCION PERSONAL DE DON LUIS
#=====================================================================================================


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
            values.extend([request.user.id,4,6,id_campania])
            
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 6
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
                    WHERE id_area = 4 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 6
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,4,6])
            
            # Agregar el id al final de la lista de valores
            values.append(id)
            
            cursor.execute(query, values)
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Producto actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
     

class ApiProductosEquiposProteccion(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:

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
                            WHERE (IDGRUPO = '2500'  AND p.IDSUBGRUPO ='012')
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])

                
                
                data_object = cursor.fetchall()
            data_json = []
            for data in data_object:
                data_json.append({'id': data[0], 'value': data[1], 'ultimo_precio': float(data[2])})
            return JsonResponse(data_json, safe=False)
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)



#///////////////////////////////////////////////////////////////////////////////////////////////////////|
#  VISTA PARA EL PRESUPUESTO - SUELDOS Y PRESUPUESTOS  DE DON LUIS
#//////////////////////////////////////////////////////////////////////////////////////////////////////|


@method_decorator(csrf_exempt, name='dispatch')
class SueldosView(View):
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
                4,  # id_area
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
                WHERE id = ? AND id_area = 4 AND id_remuneracion = 1
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
                    WHERE id_area = 4 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                        enero, febrero, marzo, abril, mayo, junio,
                        julio, agosto, septiembre, octubre, noviembre, diciembre,
                        usuario, fecha,asignacion, vacacion
                    FROM tb_remuneracion 
                    WHERE id_area = 4 AND id_remuneracion = 1
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
                4,  # id_area
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









class ApiSueldos(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:
                    # Consulta SQL para obtener datos del empleado por DNI
                    cursor.execute("""
                        SELECT TOP 1
                            PG.NRODOCUMENTO AS DNI,
                            CONCAT(PG.NOMBRES, ' ', PG.A_PATERNO, ' ', PG.A_MATERNO) AS NOMBRE,
                            PL.DESCRIPCION AS REGIMENLABORAL,
                            CA.DESCRIPCION AS CARGO,
                            PE.FECHA_INICIOPLANILLA AS FECHA_INGRESO
                        FROM PERSONAL_GENERAL PG
                        INNER JOIN PERSONAL PE ON PE.IDCODIGOGENERAL = PG.IDCODIGOGENERAL
                        INNER JOIN CARGOS_PERSONAL CA ON CA.IDCARGO = PE.IDCARGO 
                        INNER JOIN PLANILLA PL ON PL.IDPLANILLA = PE.IDPLANILLA
                        WHERE PG.NRODOCUMENTO LIKE ?
                        ORDER BY PE.FECHA_INICIOPLANILLA DESC;
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],          # DNI
                            'nombre': data[1],       # NOMBRE
                            'regimen_laboral': data[2], # REGIMEN_LABORAL
                            'cargo': data[3],       # CARGO
                            'fecha_ingreso': data[4].strftime('%Y-%m-%d') if data[4] else None # FECHA_INGRESO
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)



@method_decorator(csrf_exempt, name='dispatch')
class ApiSueldoMensual(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            # Ejecutar el procedimiento almacenado
            campania = request.GET.get('year', '')
            
            # Ejecutar el procedimiento almacenado con o sin campaña
            if campania:
                cursor.execute("exec rpt_pst_remuneracion ?, ?, ?", [4, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion ?, ?", [4, 1])
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



#------------------------------------
#SALARIOS
#------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class SalariosView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Obtener el mes de vacaciones (0 si no hay vacaciones)
            mes_vacaciones = data.get('vacacion', '0')
            
            query = """
            INSERT INTO tb_remuneracion (
                dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                enero, febrero, marzo, abril, mayo, junio,
                julio, agosto, septiembre, octubre, noviembre, diciembre,
                asignacion, USUARIO, id_area, id_remuneracion, fecha, vacacion
            ) VALUES (?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, GETDATE(), ?)
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
                4,  # id_area
                2,   # id_remuneracion
                mes_vacaciones # mes_vacaciones
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
                WHERE id = ? AND id_area = 4 AND id_remuneracion = 2
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
                query = """
                SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                       enero, febrero, marzo, abril, mayo, junio,
                       julio, agosto, septiembre, octubre, noviembre, diciembre,
                       usuario, fecha,asignacion, vacacion
                FROM tb_remuneracion 
                WHERE id_area = 4 AND id_remuneracion = 2
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
                4,  # id_area
                2,  # id_remuneracion
                mes_vacaciones, # mes_vacaciones
                id, # id
                
            ])
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Salario actualizado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



class ApiSalarios(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:
                    # Consulta SQL para obtener datos del empleado por DNI
                    cursor.execute("""
                        SELECT TOP 1
                            PG.NRODOCUMENTO AS DNI,
                            CONCAT(PG.NOMBRES, ' ', PG.A_PATERNO, ' ', PG.A_MATERNO) AS NOMBRE,
                            PL.DESCRIPCION AS REGIMENLABORAL,
                            CA.DESCRIPCION AS CARGO,
                            PE.FECHA_INICIOPLANILLA AS FECHA_INGRESO
                        FROM PERSONAL_GENERAL PG
                        INNER JOIN PERSONAL PE ON PE.IDCODIGOGENERAL = PG.IDCODIGOGENERAL
                        INNER JOIN CARGOS_PERSONAL CA ON CA.IDCARGO = PE.IDCARGO 
                        INNER JOIN PLANILLA PL ON PL.IDPLANILLA = PE.IDPLANILLA
                        WHERE PG.NRODOCUMENTO LIKE ?
                        ORDER BY PE.FECHA_INICIOPLANILLA DESC;
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],          # DNI
                            'nombre': data[1],       # NOMBRE
                            'regimen_laboral': data[2], # REGIMEN_LABORAL
                            'cargo': data[3],       # CARGO
                            'fecha_ingreso': data[4].strftime('%Y-%m-%d') if data[4] else None # FECHA_INGRESO
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ApiSalarioMensual(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Ejecutar el procedimiento almacenado
            cursor.execute("exec rpt_pst_remuneracion '4','2'")
            
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


#------------------------------------
#CONFIGURACIONES SUELDOS Y SALARIOS
#------------------------------------

@method_decorator(csrf_exempt, name='dispatch')
class ConfiguracionesSueldosSalariosView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si existe algún registro
            cursor.execute("SELECT COUNT(*) FROM configuraciones_sueldos_salarios")
            count = cursor.fetchone()[0]
            
            # Si no hay registros, crear el registro inicial
            if count == 0:
                insert_query = """
                INSERT INTO configuraciones_sueldos_salarios (
                    tasa_carga_social_sueldo,
                    tasa_carga_social_salario,
                    sueldo_minimo,
                    monto_transporte,
                    monto_alimentacion,
                    usuario_actualizacion,
                    fecha_actualizacion
                ) VALUES (0.4430, 0.4430, 1025.00, 6.51, 5.05, ?, GETDATE())
                """
                cursor.execute(insert_query, [request.user.username])
                connection_portalaei.commit()
            
            # Obtener la configuración actual
            query = """
            SELECT TOP 1 
                id,
                tasa_carga_social_sueldo,
                tasa_carga_social_salario,
                sueldo_minimo,
                monto_transporte,
                monto_alimentacion,
                fecha_actualizacion,
                usuario_actualizacion
            FROM configuraciones_sueldos_salarios
            ORDER BY fecha_actualizacion DESC
            """
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                columns = [column[0] for column in cursor.description]
                item = dict(zip(columns, row))
                
                # Convertir Decimal a float para serialización JSON
                for key, value in item.items():
                    if isinstance(value, Decimal):
                        item[key] = float(value)
                
                cursor.close()
                return JsonResponse(item)
            else:
                return JsonResponse({
                    'tasa_carga_social_sueldo': 0.4430,
                    'tasa_carga_social_salario': 0.4430,
                    'sueldo_minimo': 1025.00,
                    'monto_transporte': 6.51,
                    'monto_alimentacion': 5.05,
                    'fecha_actualizacion': None,
                    'usuario_actualizacion': None
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Validar los datos recibidos
            tasa_sueldo = float(data.get('tasa_carga_social_sueldo'))
            tasa_salario = float(data.get('tasa_carga_social_salario'))
            sueldo_minimo = float(data.get('sueldo_minimo'))
            monto_transporte = float(data.get('monto_transporte'))
            monto_alimentacion = float(data.get('monto_alimentacion'))

            if not (0 <= tasa_sueldo <= 1) or not (0 <= tasa_salario <= 1):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Las tasas deben estar entre 0 y 1'
                }, status=400)
            
            if sueldo_minimo < 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El sueldo mínimo no puede ser negativo'
                }, status=400)
            
            # Insertar nuevo registro con las tasas actualizadas
            query = """
            INSERT INTO configuraciones_sueldos_salarios (
                tasa_carga_social_sueldo,
                tasa_carga_social_salario,
                sueldo_minimo,
                monto_transporte,
                monto_alimentacion,
                usuario_actualizacion,
                fecha_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """
            
            # Obtener nombre de usuario
            nombre_usuario = f"{request.user.first_name} {request.user.last_name}".strip()
            if not nombre_usuario:
                nombre_usuario = request.user.username
                
            cursor.execute(query, [
                tasa_sueldo,
                tasa_salario,
                sueldo_minimo,
                monto_transporte,
                monto_alimentacion,
                nombre_usuario
            ])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Configuraciones actualizadas correctamente'
            })
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({   
                'status': 'error',
                'message': str(e)
            }, status=500)

#==============================================================================================
#CAPEX
#============================================================================================== 


@method_decorator(csrf_exempt, name='dispatch')
class CapexView(View):


    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            idproducto = data.get('idproducto')
            id_area = data.get('id_area', 4)
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
                WHERE id = ? AND id_area = 4 
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
                    WHERE id_area = 4 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4
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
            WHERE id = ? AND id_area = 4
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
                4,
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








class ApiCapex(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_donluis.cursor() as cursor:
                if query:
                    # Primera consulta (con precios históricos)
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
                            WHERE IDGRUPO = '3300'
                            AND p.DESCRIPCION LIKE ?
                            ) AS sub
                        WHERE ultimo_precio >= 0;
                    """, ['%' + query + '%'])

                    data_object = cursor.fetchall()
                    
                    # Si no hay resultados, ejecutar la segunda consulta
                    if not data_object:
                        cursor.execute("""
                            SELECT 
                                IDPRODUCTO,
                                DESCRIPCION,
                                CAST('0.00' AS DECIMAL(18,2)) AS ultimo_precio
                            FROM 
                                PRODUCTOS
                            WHERE 
                                IDGRUPO = '3300' 
                                AND DESCRIPCION LIKE ?
                        """, ['%' + query + '%'])
                        data_object = cursor.fetchall()

                data_json = []
                for data in data_object:
                    data_json.append({
                        'id': data[0], 
                        'value': data[1], 
                        'ultimo_precio': float(data[2])
                    })
                return JsonResponse(data_json, safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)


#==============================================================================================
#SERVICIOS DE TERCEROS
#==============================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ServiciosView(View):
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
            area_id = data.get('id_area', 4)
            if observacion:  # Solo verificar si hay una observación
                cursor.execute(check_query, [observacion, area_id])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un servicio con esta observación en esta área'
                    }, status=400)

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
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )
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
            values.append(4) # ID DEL AREA
            values.append(data.get('ID_CAMPANIA'))  # campaña

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
                       noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio, ID_CAMPANIA
                FROM TIC_servicios
                WHERE id = ?  AND id_area = 4
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
                campania = request.GET.get('year', '')
                if campania:
                    query = """
                    SELECT id, idproducto, grupo_servicio, subgrupo_servicio, descripcion, precio_unitario, observacion,
                        enero_cantidad, enero_precio, febrero_cantidad, febrero_precio,
                        marzo_cantidad, marzo_precio, abril_cantidad, abril_precio,
                        mayo_cantidad, mayo_precio, junio_cantidad, junio_precio,
                        julio_cantidad, julio_precio, agosto_cantidad, agosto_precio,
                        septiembre_cantidad, septiembre_precio, octubre_cantidad, octubre_precio,
                        noviembre_cantidad, noviembre_precio, diciembre_cantidad, diciembre_precio, ID_CAMPANIA
                    FROM TIC_servicios 
                    WHERE id_area = 4 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4
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
            area_id = data.get('id_area', 4)
            
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

            
            values.extend([request.user.id,4, id])
            
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



@method_decorator(csrf_exempt, name='dispatch')
class ApiSubgruposServicios(View):
    def get(self, request, grupo_id, *args, **kwargs):
        try:
            cursor = connection_donluis.cursor()
            query = """
                SELECT DISTINCT 
                    P.IDGRUPO,
                    P.IDSUBGRUPO,
                    SG.DESCRIPCION
                FROM 
                    PRODUCTOS P
                INNER JOIN 
                    SUBGRUPOS SG 
                    ON P.IDGRUPO = SG.IDGRUPO AND P.IDSUBGRUPO = SG.IDSUBGRUPO
                WHERE 
                    P.IDGRUPO = ?
                ORDER BY 
                    P.IDSUBGRUPO
            """
            print("Ejecutando query con grupo_id:", grupo_id)  # Para debugging
            cursor.execute(query, [grupo_id])
            subgrupos = [{'id': row[1], 'descripcion': row[2]} for row in cursor.fetchall()]
            cursor.close()
            return JsonResponse({'subgrupos': subgrupos})
        except Exception as e:
            print("Error en ApiSubgruposServicios:", str(e))  # Para debugging
            return JsonResponse({'error': str(e)}, status=500)
        



@method_decorator(csrf_exempt, name='dispatch')
class ApiDescripcionesServicios(View):
    def get(self, request, *args, **kwargs):
        try:
            grupo_id = request.GET.get('grupo')
            subgrupo_id = request.GET.get('subgrupo')
            
            if not grupo_id or not subgrupo_id:
                return JsonResponse({'error': 'Grupo ID y Subgrupo ID son requeridos'}, status=400)
                
            cursor = connection_donluis.cursor()
            query = """
                SELECT * FROM (
                    SELECT 
                        p.idgrupo,
                        p.idsubgrupo,
                        p.DESCRIPCION, 
                        p.IDPRODUCTO,
                        COALESCE((
                            SELECT TOP 1 
                            CASE 
                                WHEN OC.idmoneda = '02' THEN pch.precio * OC.tipocambio
                                ELSE DOS.precio
                            END
                            FROM PRECIO_COMPRA_HISTORICO pch
                            INNER JOIN ORDENSERVICIO OC ON OC.idservicio = pch.idcompra
                            INNER JOIN DORDENSERVICIO DOS ON DOS.idservicio = OC.idservicio
                            WHERE pch.idproducto = p.IDPRODUCTO
                            AND DOS.precio > 0
                            ORDER BY pch.fecha DESC
                        ), 0) AS ultimo_precio
                    FROM PRODUCTOS p
                    WHERE IDGRUPO = ? AND IDSUBGRUPO = ?
                ) AS sub
                WHERE ultimo_precio >= 0
                ORDER BY DESCRIPCION
            """
            cursor.execute(query, [grupo_id, subgrupo_id])
            servicios = [
                {
                    'id': row[3],  # IDPRODUCTO
                    'descripcion': row[2],  # DESCRIPCION
                    'precio': float(row[4])  # ultimo_precio
                } 
                for row in cursor.fetchall()
            ]
            cursor.close()
            return JsonResponse({'servicios': servicios})
        except Exception as e:
            print("Error en ApiDescripcionesServicios:", str(e))
            return JsonResponse({'error': str(e)}, status=500)
        


#==============================================================================================
#GESTION DE TIC
#==============================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class MantenimientoUserDlView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Verificar si ya existe un usuario con el mismo DNI
            check_query = """
            SELECT COUNT(*) 
            FROM USUARIOS 
            WHERE DNI = ?
            """
            dni = data.get('dni')
            
            if dni:
                cursor.execute(check_query, [dni])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe un usuario con este DNI'
                    }, status=400)

            query = """
            INSERT INTO USUARIOS (
                DNI, NOMBRES, APATERNO, AMATERNO, CELULAR, FECHA_NACI
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            values = [
                data.get('dni'),
                data.get('nombres'),
                data.get('apaterno'),
                data.get('amaterno'),
                data.get('celular'),
                data.get('fecha_naci')
            ]
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Usuario registrado correctamente'})
        
        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad en los datos'
            }, status=400)
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            if id:
                query = """
                SELECT IDUSUARIO, DNI, NOMBRES, APATERNO, AMATERNO, CELULAR, FECHA_NACI
                FROM USUARIOS
                WHERE IDUSUARIO = ?
                """
                cursor.execute(query, [id])
                columns = [column[0] for column in cursor.description]
                row = cursor.fetchone()
                if row:
                    item = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse(item)
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'}, status=404)
            else:
                query = """
                SELECT IDUSUARIO, DNI, NOMBRES, APATERNO, AMATERNO, CELULAR, FECHA_NACI
                FROM USUARIOS
                """
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                data = []
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    data.append(item)
                
                cursor.close()
                return JsonResponse({"data": data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si el usuario existe
            cursor.execute("SELECT IDUSUARIO FROM USUARIOS WHERE IDUSUARIO = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'}, status=404)
            
            # Eliminar el usuario
            cursor.execute("DELETE FROM USUARIOS WHERE IDUSUARIO = ?", [id])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Usuario eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Verificar si existe otro usuario con el mismo DNI (excluyendo el usuario actual)
            check_query = """
            SELECT COUNT(*) 
            FROM USUARIOS 
            WHERE DNI = ? AND IDUSUARIO != ?
            """
            dni = data.get('dni')
            
            if dni:
                cursor.execute(check_query, [dni, id])
                count = cursor.fetchone()[0]
                
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe otro usuario con este DNI'
                    }, status=400)
            
            # Verificar si el usuario existe
            cursor.execute("SELECT IDUSUARIO FROM USUARIOS WHERE IDUSUARIO = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'}, status=404)
            
            query = """
            UPDATE USUARIOS
            SET DNI = ?, NOMBRES = ?, APATERNO = ?, AMATERNO = ?, CELULAR = ?, FECHA_NACI = ?
            WHERE IDUSUARIO = ?
            """
            
            values = [
                data.get('dni'),
                data.get('nombres'),
                data.get('apaterno'),
                data.get('amaterno'),
                data.get('celular'),
                data.get('fecha_naci'),
                id
            ]
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({'status': 'success', 'message': 'Usuario actualizado correctamente'})

        except IntegrityError:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': 'Error de integridad en los datos'
            }, status=400)    
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ApiUsuariosDL(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip().upper()
        try:
            with connection_donluis.cursor() as cursor:
                if query:
                    # Consulta SQL modificada para buscar en nombres y apellidos
                    cursor.execute("""
                        SELECT 
                            NRODOCUMENTO AS DNI,
                            NOMBRES, 
                            A_PATERNO AS APATERNO,
                            A_MATERNO AS APMATERNO,
                            CELULAR,
                            FECHA_NACIMIENTO AS FECH_NACI
                        FROM PERSONAL_GENERAL
                        WHERE UPPER(NOMBRES + ' ' + A_PATERNO + ' ' + A_MATERNO) LIKE ?
                        ORDER BY NOMBRES ASC
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],
                            'nombres': data[1],
                            'apellido_paterno': data[2],
                            'apellido_materno': data[3],
                            'celular': data[4],
                            'fecha_nacimiento': data[5].strftime('%Y-%m-%d') if data[5] else None
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
#==============================================================================================
#GESTION DE TIC - TRABAJADORES
#==============================================================================================


@method_decorator(csrf_exempt, name='dispatch')
class TrabajadorView(View):
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            if id:
                # Consulta para un trabajador específico
                query = """
                SELECT 
                    t.IDTRABAJADOR,
                    u.NOMBRES + ' ' + u.APATERNO + ' ' + u.AMATERNO as NOMBRE_USUARIO,
                    c.DESCRIPCION as CARGO,
                    a.DESCRIPCION as AREA,
                    g.DESCRIPCION as GERENCIA,
                    s.DESCRIPCION as SEDE,
                    e.DESCRIPCION as EMPRESA,
                    t.IDUSUARIO,
                    t.IDCARGO,
                    t.IDAREA,
                    t.IDGERENCIA,
                    t.IDSEDE,
                    t.IDEMPRESA
                FROM TRABAJADOR t
                INNER JOIN USUARIOS u ON t.IDUSUARIO = u.IDUSUARIO
                INNER JOIN CARGOS c ON t.IDCARGO = c.IDCARGO
                INNER JOIN AREAS a ON t.IDAREA = a.IDAREA
                INNER JOIN GERENCIAS g ON t.IDGERENCIA = g.IDGERENCIA
                INNER JOIN SEDES s ON t.IDSEDE = s.IDSEDE
                INNER JOIN EMPRESA e ON t.IDEMPRESA = e.IDEMPRESA
                WHERE t.IDTRABAJADOR = ?
                """
                cursor.execute(query, [id])
                row = cursor.fetchone()
                
                if row:
                    data = {
                        'idtrabajador': row[0],
                        'nombre_usuario': row[1],
                        'cargo': row[2],
                        'area': row[3],
                        'gerencia': row[4],
                        'sede': row[5],
                        'empresa': row[6],
                        'idusuario': row[7],
                        'idcargo': row[8],
                        'idarea': row[9],
                        'idgerencia': row[10],
                        'idsede': row[11],
                        'idempresa': row[4]
                    }
                    return JsonResponse(data)
                return JsonResponse({'error': 'Trabajador no encontrado'}, status=404)
            
            else:
                # Consulta para listar todos los trabajadores
                query = """
                SELECT 
                    t.IDTRABAJADOR,
                    u.NOMBRES + ' ' + u.APATERNO + ' ' + u.AMATERNO as NOMBRE_USUARIO,
                    c.DESCRIPCION as CARGO,
                    a.DESCRIPCION as AREA,
                    g.DESCRIPCION as GERENCIA,
                    s.DESCRIPCION as SEDE,
                    e.DESCRIPCION as EMPRESA
                FROM TRABAJADOR t
                INNER JOIN USUARIOS u ON t.IDUSUARIO = u.IDUSUARIO
                INNER JOIN CARGOS c ON t.IDCARGO = c.IDCARGO
                INNER JOIN AREAS a ON t.IDAREA = a.IDAREA
                INNER JOIN GERENCIAS g ON t.IDGERENCIA = g.IDGERENCIA
                INNER JOIN SEDES s ON t.IDSEDE = s.IDSEDE
                INNER JOIN EMPRESA e ON t.IDEMPRESA = e.IDEMPRESA
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append({
                        'idtrabajador': row[0],
                        'nombre_usuario': row[1],
                        'cargo': row[2],
                        'area': row[3],
                        'gerencia': row[4],
                        'sede': row[5],
                        'empresa': row[6]
                    })
                return JsonResponse({'data': data})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Verificar si ya existe un registro para este usuario
            cursor.execute("""
                SELECT COUNT(*) FROM TRABAJADOR WHERE IDUSUARIO = ?
            """, [data.get('idusuario')])
            
            if cursor.fetchone()[0] > 0:
                return JsonResponse({
                    'error': 'Ya existe un registro para este usuario'
                }, status=400)
            
            # Insertar nuevo trabajador
            query = """
            INSERT INTO TRABAJADOR (
                IDUSUARIO, IDCARGO, IDAREA, IDGERENCIA, IDSEDE, IDEMPRESA
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            values = [
                data.get('idusuario'),
                data.get('idcargo'),
                data.get('idarea'),
                data.get('idgerencia'),
                data.get('idsede'),
                data.get('idempresa')
            ]
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            
            return JsonResponse({
                'message': 'Trabajador registrado exitosamente'
            })
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()
            
            # Verificar si el trabajador existe
            cursor.execute("SELECT COUNT(*) FROM TRABAJADOR WHERE IDTRABAJADOR = ?", [id])
            if cursor.fetchone()[0] == 0:
                return JsonResponse({'error': 'Trabajador no encontrado'}, status=404)
            
            # Actualizar trabajador
            query = """
            UPDATE TRABAJADOR SET
                IDUSUARIO = ?,
                IDCARGO = ?,
                IDAREA = ?,
                IDGERENCIA = ?,
                IDSEDE = ?,
                IDEMPRESA = ?
            WHERE IDTRABAJADOR = ?
            """
            
            values = [
                data.get('idusuario'),
                data.get('idcargo'),
                data.get('idarea'),
                data.get('idgerencia'),
                data.get('idsede'),
                data.get('idempresa'),
                id
            ]
            
            cursor.execute(query, values)
            connection_portalaei.commit()
            
            return JsonResponse({
                'message': 'Trabajador actualizado exitosamente'
            })
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si el trabajador existe
            cursor.execute("SELECT COUNT(*) FROM TRABAJADOR WHERE IDTRABAJADOR = ?", [id])
            if cursor.fetchone()[0] == 0:
                return JsonResponse({'error': 'Trabajador no encontrado'}, status=404)
            
            # Eliminar trabajador
            cursor.execute("DELETE FROM TRABAJADOR WHERE IDTRABAJADOR = ?", [id])
            connection_portalaei.commit()
            
            return JsonResponse({
                'message': 'Trabajador eliminado exitosamente'
            })
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()


#==============================================================================================
# Vistas API para los selectores
#==============================================================================================
class ApiCargosView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT IDCARGO, DESCRIPCION FROM CARGOS")
            cargos = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'cargos': cargos})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

class ApiAreasView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT IDAREA, DESCRIPCION FROM AREAS")
            areas = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'areas': areas})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

class ApiGerenciasView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT IDGERENCIA, DESCRIPCION FROM GERENCIAS")
            gerencias = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'gerencias': gerencias})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

class ApiSedesView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT IDSEDE, DESCRIPCION FROM SEDES")
            sedes = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'sedes': sedes})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()

class ApiEmpresasView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT IDEMPRESA, DESCRIPCION FROM EMPRESA")
            empresas = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            return JsonResponse({'empresas': empresas})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            cursor.close()






#================================================================================================================
# CAMPO VERDE - TECNOLOGIA DE LA INFORMACION
#================================================================================================================

#=================================================================================================================
#MODULO PRESUPUESTOS
#AUTOR: JHON GUTIERREZ
#FECHA: 06/01/2025
#MODIFICACIONES: 
# 09/01/2025: Se crea el modulo de presupuestos
#=================================================================================================================





# PRESUPUESTO

class presupuesto_cv(TemplateView):
    permission_required = 'ver_tic','tic_dl','tic_cv','tic_ajs','view_josep'
    template_name = 'TICS/pages/presupuesto_cv.html'

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
                EXEC TOTAL_SERVICIOS_CV '4', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_CV '4'
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
            area_id = data.get('id_area', 4)
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
            values.append(4) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 4
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
                    WHERE id_area = 4 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4
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
            area_id = data.get('id_area', 7)
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

            
            values.extend([request.user.id,4, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s, %s", [4, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_CV %s", [4])

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
            
            values.extend([request.user.id,4,1,id_campania])


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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 1
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
                    WHERE id_area = 4 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,4,1])
            
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
            
            values.extend([request.user.id,4,5,id_campania])
            
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
                AND id_area = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,4,5])
            
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
            values.extend([request.user.id,4,7,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 7
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
                WHERE id_area = 4 AND id_tipo_suministro = 7
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
                    WHERE id_area = 4 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 4 
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
            values.extend([request.user.id,4,7])
            
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
            values.extend([request.user.id,4,8,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 8
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
                WHERE id_area = 4 AND id_tipo_suministro = 8
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
                    WHERE id_area = 4 AND id_tipo_suministro = 8 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 8
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
            values.extend([request.user.id,4,8])


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
            
            values.extend([request.user.id,4,4,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
                WHERE id_area = 4 AND id_tipo_suministro = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,4,4])
            
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
            values.extend([request.user.id,4,2,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 2
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
                WHERE id_area = 4 AND id_tipo_suministro = 2
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
                    WHERE id_area = 4 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,4,2])
                
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
            values.extend([request.user.id,4,9,id_campania])
            
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 9
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
                WHERE id_area = 4 AND id_tipo_suministro = 9
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
                    WHERE id_area = 4 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,4,9])
                
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
            values.extend([request.user.id,4,3,id_campania])


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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 3
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
                WHERE id_area = 4 AND id_tipo_suministro = 3
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
                    WHERE id_area = 4 AND id_tipo_suministro = 3 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 3
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
            values.extend([request.user.id,4,3])
            
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
            values.extend([request.user.id,4,6,id_campania])
            
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 6
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
                WHERE id_area = 4 AND id_tipo_suministro = 6
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
                    WHERE id_area = 4 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,4,6])
            
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
                EXEC RPT_PST_CAPEX_CV '4', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_CV '4'
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
            id_area = data.get('id_area', 4)
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
                WHERE id = ? AND id_area = 4 
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
                    WHERE id_area = 4 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4
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
            WHERE id = ? AND id_area = 4
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
                7,
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
                4,  # id_area
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
                WHERE id = ? AND id_area = 4 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 4 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 4 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_remuneracion = 1
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
                4,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [4, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [4, 1])
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
                4,  # id_area
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
                WHERE id = ? AND id_area = 4 AND id_remuneracion = 2
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
                    WHERE id_area = 4 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_CV 
                    WHERE id_area = 4 AND id_remuneracion = 2
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
                4,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?, ?", [4, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_cv ?, ?", [4, 2])
                        
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
    permission_required = 'ver_tic','tic_dl','tic_ajs','tic_ajs','view_josep'
    template_name = 'TICS/pages/presupuesto_ajs.html'

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
                EXEC TOTAL_SERVICIOS_AJS '4', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC TOTAL_SERVICIOS_AJS '4'
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
            area_id = data.get('id_area', 4)
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
            values.append(4) # ID DEL AREA 
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
                WHERE id = ?  AND id_area = 4
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
                    WHERE id_area = 4 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4
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
            area_id = data.get('id_area', 4)
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

            
            values.extend([request.user.id,4, id])
            
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
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s, %s", [4, campania])
        else:
            cursor.execute("EXEC RPT_PST_SUMINISTROS_AJS %s", [4])

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
            
            values.extend([request.user.id,4,1,id_campania])


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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 1
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
                    WHERE id_area = 4 AND id_tipo_suministro = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 1
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 1
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
            values.extend([request.user.id,4,1])
            
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
            
            values.extend([request.user.id,4,5,id_campania])
            
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
                AND id_area = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 5 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_tipo_suministro = 5
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
            values.extend([request.user.id,4,5])
            
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
            values.extend([request.user.id,4,4,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 7
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
                WHERE id_area = 4 AND id_tipo_suministro = 7
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
                    WHERE id_area = 4 AND id_tipo_suministro = 7 AND ID_CAMPANIA = ?
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
            AND id_area = 4 
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
            values.extend([request.user.id,4,4])
            
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
            values.extend([request.user.id,4,4,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
                WHERE id_area = 4 AND id_tipo_suministro = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,4,4])


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
            
            values.extend([request.user.id,4,4,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
                WHERE id_area = 4 AND id_tipo_suministro = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,4,4])
            
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
            values.extend([request.user.id,4,2,id_campania])

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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 2
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
                WHERE id_area = 4 AND id_tipo_suministro = 2
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
                    WHERE id_area = 4 AND id_tipo_suministro = 2 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 2
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
                values.extend([request.user.id,4,2])
                
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
            values.extend([request.user.id,4,9,id_campania])
            
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 9
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
                WHERE id_area = 4 AND id_tipo_suministro = 9
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
                    WHERE id_area = 4 AND id_tipo_suministro = 9 AND ID_CAMPANIA = ?
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 9
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
                values.extend([request.user.id,4,9])
                
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
            values.extend([request.user.id,4,4,id_campania])


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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
                WHERE id_area = 4 AND id_tipo_suministro = 4
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
                    WHERE id_area = 4 AND id_tipo_suministro = 4 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 4
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
            values.extend([request.user.id,4,4])
            
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
            values.extend([request.user.id,4,6,id_campania])
            
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
                WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 6
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
                WHERE id_area = 4 AND id_tipo_suministro = 6
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
                    WHERE id_area = 4 AND id_tipo_suministro = 6 AND ID_CAMPANIA = ?
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
            WHERE id = ? AND id_area = 4 AND id_tipo_suministro = 6
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
            values.extend([request.user.id,4,6])
            
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
# FECHA: 24/11/204
#==============================================================================================


def Costos_capex_totals_ajs(request):
    # Obtener el parámetro de campaña del request
    campania = request.GET.get('year', '')
    
    with connection.cursor() as cursor:
        if campania:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '4', %s
            """, [campania])
        else:
            cursor.execute("""
                EXEC RPT_PST_CAPEX_AJS '4'
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
            id_area = data.get('id_area', 4)
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
                WHERE id = ? AND id_area = 4 
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
                    WHERE id_area = 4 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4
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
            WHERE id = ? AND id_area = 4
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
                4,
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
# FECHA: 24/11/204
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
                4,  # id_area
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
                WHERE id = ? AND id_area = 4 AND id_remuneracion = 1
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
                cursor.execute("SELECT DISTINCT ID_CAMPANIA FROM tb_remuneracion WHERE id_area = 4 AND id_remuneracion = 1")
                campanias_existentes = [row[0] for row in cursor.fetchall()]
                print(f"DEBUG SUELDOS: Campañas existentes en BD: {campanias_existentes}")
                
                if campania:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 4 AND id_remuneracion = 1 AND ID_CAMPANIA = ?
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
                    WHERE id_area = 4 AND id_remuneracion = 1
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
                4,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [4, 1, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [4, 1])
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
                4,  # id_area
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
                WHERE id = ? AND id_area = 4 AND id_remuneracion = 2
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
                    WHERE id_area = 4 AND id_remuneracion = 2 AND ID_CAMPANIA = ?
                    """
                    cursor.execute(query, [campania])
                else:
                    query = """
                    SELECT id, dni, nombre, regimen_laboral, cargo, fecha_ingreso,
                           enero, febrero, marzo, abril, mayo, junio,
                           julio, agosto, septiembre, octubre, noviembre, diciembre,
                           usuario, fecha,asignacion, vacacion
                    FROM REMUNERACION_AJS 
                    WHERE id_area = 4 AND id_remuneracion = 2
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
                4,  # id_area
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
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?, ?", [4, 2, campania])
            else:
                cursor.execute("exec rpt_pst_remuneracion_ajs ?, ?", [4, 2])
                        
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








#===============================================================================
# API PARA EL AUTOCOMPLETADO DE SUELDOS Y SALARIOS - CAMPO VERDE 
#===============================================================================



class ApiSueldos_cv(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_campoverde.cursor() as cursor:
                if query:
                    # Consulta SQL para obtener datos del empleado por DNI
                    cursor.execute("""
                        SELECT TOP 1
                            PG.NRODOCUMENTO AS DNI,
                            CONCAT(PG.NOMBRES, ' ', PG.A_PATERNO, ' ', PG.A_MATERNO) AS NOMBRE,
                            PL.DESCRIPCION AS REGIMENLABORAL,
                            CA.DESCRIPCION AS CARGO,
                            PE.FECHA_INICIOPLANILLA AS FECHA_INGRESO
                        FROM PERSONAL_GENERAL PG
                        INNER JOIN PERSONAL PE ON PE.IDCODIGOGENERAL = PG.IDCODIGOGENERAL
                        INNER JOIN CARGOS_PERSONAL CA ON CA.IDCARGO = PE.IDCARGO 
                        INNER JOIN PLANILLA PL ON PL.IDPLANILLA = PE.IDPLANILLA
                        WHERE PG.NRODOCUMENTO LIKE ?
                        ORDER BY PE.FECHA_INICIOPLANILLA DESC;
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],          # DNI
                            'nombre': data[1],       # NOMBRE
                            'regimen_laboral': data[2], # REGIMEN_LABORAL
                            'cargo': data[3],       # CARGO
                            'fecha_ingreso': data[4].strftime('%Y-%m-%d') if data[4] else None # FECHA_INGRESO
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)





class ApiSalarios_cv(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_campoverde.cursor() as cursor:
                if query:
                    # Consulta SQL para obtener datos del empleado por DNI
                    cursor.execute("""
                        SELECT TOP 1
                            PG.NRODOCUMENTO AS DNI,
                            CONCAT(PG.NOMBRES, ' ', PG.A_PATERNO, ' ', PG.A_MATERNO) AS NOMBRE,
                            PL.DESCRIPCION AS REGIMENLABORAL,
                            CA.DESCRIPCION AS CARGO,
                            PE.FECHA_INICIOPLANILLA AS FECHA_INGRESO
                        FROM PERSONAL_GENERAL PG
                        INNER JOIN PERSONAL PE ON PE.IDCODIGOGENERAL = PG.IDCODIGOGENERAL
                        INNER JOIN CARGOS_PERSONAL CA ON CA.IDCARGO = PE.IDCARGO 
                        INNER JOIN PLANILLA PL ON PL.IDPLANILLA = PE.IDPLANILLA
                        WHERE PG.NRODOCUMENTO LIKE ?
                        ORDER BY PE.FECHA_INICIOPLANILLA DESC;
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],          # DNI
                            'nombre': data[1],       # NOMBRE
                            'regimen_laboral': data[2], # REGIMEN_LABORAL
                            'cargo': data[3],       # CARGO
                            'fecha_ingreso': data[4].strftime('%Y-%m-%d') if data[4] else None # FECHA_INGRESO
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)
        

#===============================================================================
# API PARA EL AUTOCOMPLETADO DE SUELDOS Y SALARIOS - INVERSIONES AJS 
#===============================================================================


class ApiSalarios_ajs(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_inversioneajs.cursor() as cursor:
                if query:
                    # Consulta SQL para obtener datos del empleado por DNI
                    cursor.execute("""
                        SELECT TOP 1
                            PG.NRODOCUMENTO AS DNI,
                            CONCAT(PG.NOMBRES, ' ', PG.A_PATERNO, ' ', PG.A_MATERNO) AS NOMBRE,
                            PL.DESCRIPCION AS REGIMENLABORAL,
                            CA.DESCRIPCION AS CARGO,
                            PE.FECHA_INICIOPLANILLA AS FECHA_INGRESO
                        FROM PERSONAL_GENERAL PG
                        INNER JOIN PERSONAL PE ON PE.IDCODIGOGENERAL = PG.IDCODIGOGENERAL
                        INNER JOIN CARGOS_PERSONAL CA ON CA.IDCARGO = PE.IDCARGO 
                        INNER JOIN PLANILLA PL ON PL.IDPLANILLA = PE.IDPLANILLA
                        WHERE PG.NRODOCUMENTO LIKE ?
                        ORDER BY PE.FECHA_INICIOPLANILLA DESC;
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],          # DNI
                            'nombre': data[1],       # NOMBRE
                            'regimen_laboral': data[2], # REGIMEN_LABORAL
                            'cargo': data[3],       # CARGO
                            'fecha_ingreso': data[4].strftime('%Y-%m-%d') if data[4] else None # FECHA_INGRESO
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)




class ApiSueldos_ajs(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        try:
            with connection_inversioneajs.cursor() as cursor:
                if query:
                    # Consulta SQL para obtener datos del empleado por DNI
                    cursor.execute("""
                        SELECT TOP 1
                            PG.NRODOCUMENTO AS DNI,
                            CONCAT(PG.NOMBRES, ' ', PG.A_PATERNO, ' ', PG.A_MATERNO) AS NOMBRE,
                            PL.DESCRIPCION AS REGIMENLABORAL,
                            CA.DESCRIPCION AS CARGO,
                            PE.FECHA_INICIOPLANILLA AS FECHA_INGRESO
                        FROM PERSONAL_GENERAL PG
                        INNER JOIN PERSONAL PE ON PE.IDCODIGOGENERAL = PG.IDCODIGOGENERAL
                        INNER JOIN CARGOS_PERSONAL CA ON CA.IDCARGO = PE.IDCARGO 
                        INNER JOIN PLANILLA PL ON PL.IDPLANILLA = PE.IDPLANILLA
                        WHERE PG.NRODOCUMENTO LIKE ?
                        ORDER BY PE.FECHA_INICIOPLANILLA DESC;
                    """, ['%' + query + '%'])
                
                    data_object = cursor.fetchall()
                    data_json = []
                    
                    for data in data_object:
                        data_json.append({
                            'dni': data[0],          # DNI
                            'nombre': data[1],       # NOMBRE
                            'regimen_laboral': data[2], # REGIMEN_LABORAL
                            'cargo': data[3],       # CARGO
                            'fecha_ingreso': data[4].strftime('%Y-%m-%d') if data[4] else None # FECHA_INGRESO
                        })
                    
                    return JsonResponse(data_json, safe=False)
                
                return JsonResponse([], safe=False)
                
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return JsonResponse({'error': str(e)}, status=500)




#===================================================================================
####################################################################################
#===================================================================================
# MODULO EVALUACIONES - Don Luis
#===================================================================================
####################################################################################
#===================================================================================


# SECCION OBJETIVOS DE EVALUACION




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
                # Intentar ejecutar el procedimiento almacenado con el área 4 y el periodo
                cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @periodo=?", [4, periodo])
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
                """, [4, periodo])
            
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
                VALUES (?, ?, ?,?, ?, ?, ?, ?, ?, ?)
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                cursor.execute("EXEC RRHH_EV_OBJETIVOS_MEJORA 4")
            
            # Obtener los resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                objetivo = dict(zip(columns, row))
                # Convertir fechas a formato string para JSON si existen y no son None
                if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                    objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                    objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                results.append(objetivo)
                
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
    
# SECCION COMPETENCIAS DE EVALUACION

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
                from datetime import datetime
                periodo = str(datetime.now().year)
            
            # Extraer solo el año si viene en formato CAMP2026
            if periodo.startswith('CAMP'):
                periodo = periodo.replace('CAMP', '')
            
            # Ejecutar el procedimiento almacenado con el parámetro de periodo
            cursor.execute("EXEC SP_RESUMEN_RRHH_COMPETENCIAS @id_area=?, @periodo=?", [4, periodo])
            
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
                cursor.execute("EXEC RRHH_EV_COMPETENCIAS_MEJORA 4")
            
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
            
            # Obtener pare�metros opcionales
            id_area = request.GET.get('id_area')
            id_evaluacion = request.GET.get('id_evaluacion')
            
            if id_evaluacion:
                # Si se solicita una evaluacion espece�fica, usar el procedimiento de detalles
                cursor.execute("EXEC SP_DETALLE_EVALUACION_FASE_INTERMEDIA ?", [id_evaluacion])
                
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
                    'message': 'Detalles de evaluacion obtenidos correctamente',
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
                
                # Obtener los nombres de las columnas
                columns = [column[0] for column in cursor.description]
                
                # Convertir los resultados a una lista de diccionarios
                evaluaciones = []
                for row in cursor.fetchall():
                    evaluacion = dict(zip(columns, row))
                    
                    # Convertir fecha a string para JSON si existe
                    if 'fecha_evaluacion' in evaluacion and evaluacion['fecha_evaluacion']:
                        evaluacion['fecha_evaluacion'] = evaluacion['fecha_evaluacion'].strftime('%Y-%m-%d')
                    
                    # Asegurar que los porcentajes sean ne�meros enteros
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
                    'message': 'Evaluaciones de fase intermedia obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'periodo': periodo,
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

#### lINEAS CELULARES 
@method_decorator(csrf_exempt, name='dispatch')
class LineaCelularesView(View):

    # =========================
    # CREAR REGISTRO
    # =========================
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection.cursor()

            query = """
                INSERT INTO LINEA_CELULARES 
                (TELEFONO, NOMBRES_APELLIDOS, CARGO, AREA, CORREO)
                VALUES (?, ?, ?, ?, ?)
            """

            values = [
                data['telefono'],
                data['nombres_apellidos'],
                data['cargo'],
                data['area'],
                data['correo']
            ]

            cursor.execute(query, values)
            connection.commit()
            cursor.close()

            return JsonResponse({'status': 'success', 'message': 'Registro creado correctamente'})
        
        except Exception as e:
            connection.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    # =========================
    # LISTAR / OBTENER POR ID
    # =========================
    def get(self, request, id=None, *args, **kwargs):
        try:
            cursor = connection.cursor()

            if id:
                cursor.execute("SELECT * FROM LINEA_CELULARES WHERE ID_LN = ?", [id])
                columns = [col[0] for col in cursor.description]
                row = cursor.fetchone()

                if not row:
                    return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)

                data = dict(zip(columns, row))
                cursor.close()
                return JsonResponse(data)

            else:
                cursor.execute("SELECT * FROM LINEA_CELULARES ORDER BY ID_LN DESC")
                columns = [col[0] for col in cursor.description]

                data = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

                cursor.close()
                return JsonResponse({"data": data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    # =========================
    # ACTUALIZAR
    # =========================
    def put(self, request, id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection.cursor()

            cursor.execute("SELECT ID_LN FROM LINEA_CELULARES WHERE ID_LN = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)

            query = """
                UPDATE LINEA_CELULARES
                SET TELEFONO = ?, 
                    NOMBRES_APELLIDOS = ?, 
                    CARGO = ?, 
                    AREA = ?,
                    CORREO = ?
                WHERE ID_LN = ?
            """

            values = [
                data['telefono'],
                data['nombres_apellidos'],
                data['cargo'],
                data['area'],
                data['correo'],
                id
            ]

            cursor.execute(query, values)
            connection.commit()
            cursor.close()

            return JsonResponse({'status': 'success', 'message': 'Actualizado correctamente'})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


    # =========================
    # ELIMINAR
    # =========================
    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection.cursor()

            cursor.execute("SELECT ID_LN FROM LINEA_CELULARES WHERE ID_LN = ?", [id])
            if cursor.fetchone() is None:
                return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)

            cursor.execute("DELETE FROM LINEA_CELULARES WHERE ID_LN = ?", [id])
            connection.commit()
            cursor.close()

            return JsonResponse({'status': 'success', 'message': 'Eliminado correctamente'})

        except Exception as e:
            connection.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class LineaCelularesTemplateView(TemplateView):
    template_name = 'TICS/lineas_celulares.html'


