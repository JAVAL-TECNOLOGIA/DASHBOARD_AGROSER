# views.py
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei


class PresupuestoUnidadMedidaView(TemplateView):
    template_name = 'PresupuestoAgricola/unidad_medida.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# CRUD API para unidad_medida
@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoUnidadMedidaCRUDView(View):
    def get(self, request, id_unidad=None):
        try:
            cursor = connection_portalaei.cursor()
            
            if id_unidad:
                cursor.execute("""
                    SELECT ID_UNIDAD, NOMBRE, NOM_CORTO, DESCRIPCION, ESTADO
                    FROM UNIDAD_MEDIDA WHERE ID_UNIDAD = ?
                """, [id_unidad])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Unidad de medida no encontrada'}, status=404)
            else:
                cursor.execute("""
                    SELECT ID_UNIDAD, NOMBRE, NOM_CORTO, DESCRIPCION, ESTADO
                    FROM UNIDAD_MEDIDA
                    ORDER BY ID_UNIDAD
                """)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)

            nombre = str(data.get('NOMBRE') or data.get('nombre', '')).strip()
            nom_corto = str(data.get('NOM_CORTO') or data.get('nom_corto', '')).strip()
            descripcion = str(data.get('DESCRIPCION') or data.get('descripcion', '')).strip()
            estado = int(data.get('ESTADO') or data.get('estado', 1))

            if not nombre:
                return JsonResponse({'status': 'error', 'message': 'El campo Nombre es obligatorio.'}, status=400)
            if not nom_corto:
                return JsonResponse({'status': 'error', 'message': 'El campo Abreviatura es obligatorio.'}, status=400)

            cursor = connection_portalaei.cursor()
            
            # Verificar si ya existe una unidad de medida con el mismo nombre o abreviatura
            cursor.execute("SELECT ID_UNIDAD FROM UNIDAD_MEDIDA WHERE NOMBRE = ? OR NOM_CORTO = ?", [nombre, nom_corto])
            if cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Ya existe una unidad de medida con ese nombre o abreviatura.'}, status=400)

            cursor.execute("""
                INSERT INTO UNIDAD_MEDIDA (NOMBRE, NOM_CORTO, DESCRIPCION, ESTADO)
                VALUES (?, ?, ?, ?)
            """, [nombre, nom_corto, descripcion, estado])
            connection_portalaei.commit()

            cursor.execute("""
                SELECT TOP 1 ID_UNIDAD, NOMBRE, NOM_CORTO, DESCRIPCION, ESTADO
                FROM UNIDAD_MEDIDA ORDER BY ID_UNIDAD DESC
            """)
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()

            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, id_unidad):
        try:
            data = json.loads(request.body)

            nombre = str(data.get('nombre', '')).strip()
            nom_corto = str(data.get('nom_corto', '')).strip()
            descripcion = str(data.get('descripcion', '')).strip()
            estado = int(data.get('estado', 1))

            if not nombre:
                return JsonResponse({'status': 'error', 'message': 'El campo Nombre es obligatorio.'}, status=400)
            if not nom_corto:
                return JsonResponse({'status': 'error', 'message': 'El campo Abreviatura es obligatorio.'}, status=400)

            cursor = connection_portalaei.cursor()
            
            # Verificar si la unidad de medida existe
            cursor.execute("SELECT ID_UNIDAD FROM UNIDAD_MEDIDA WHERE ID_UNIDAD = ?", [id_unidad])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Unidad de medida no encontrada'}, status=404)

            # Verificar si ya existe otra unidad de medida con el mismo nombre o abreviatura
            cursor.execute("SELECT ID_UNIDAD FROM UNIDAD_MEDIDA WHERE (NOMBRE = ? OR NOM_CORTO = ?) AND ID_UNIDAD != ?", [nombre, nom_corto, id_unidad])
            if cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Ya existe otra unidad de medida con ese nombre o abreviatura.'}, status=400)

            cursor.execute("""
                UPDATE UNIDAD_MEDIDA
                SET NOMBRE=?, NOM_CORTO=?, DESCRIPCION=?, ESTADO=?
                WHERE ID_UNIDAD=?
            """, [nombre, nom_corto, descripcion, estado, id_unidad])
            connection_portalaei.commit()

            cursor.execute("SELECT * FROM UNIDAD_MEDIDA WHERE ID_UNIDAD = ?", [id_unidad])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, id_unidad):
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si la unidad de medida existe
            cursor.execute("SELECT ID_UNIDAD FROM UNIDAD_MEDIDA WHERE ID_UNIDAD = ?", [id_unidad])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Unidad de medida no encontrada'}, status=404)

            cursor.execute("DELETE FROM UNIDAD_MEDIDA WHERE ID_UNIDAD = ?", [id_unidad])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Unidad de medida eliminada correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)