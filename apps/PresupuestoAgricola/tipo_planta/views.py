# views.py
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei


class PresupuestoTipoPlantaView(TemplateView):
    template_name = 'PresupuestoAgricola/tipo_planta.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# CRUD API para tipo_planta
@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoTipoPlantaCRUDView(View):
    def get(self, request, id_tipo_planta=None):
        try:
            cursor = connection_portalaei.cursor()
            
            if id_tipo_planta:
                cursor.execute("""
                    SELECT ID_TPPLANTA, NOM_CORTO, DESCRIPCION
                    FROM TIPO_PLANTA WHERE ID_TPPLANTA = ?
                """, [id_tipo_planta])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Tipo de planta no encontrado'}, status=404)
            else:
                cursor.execute("""
                    SELECT ID_TPPLANTA, NOM_CORTO, DESCRIPCION
                    FROM TIPO_PLANTA
                    ORDER BY ID_TPPLANTA
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

            nom_corto = str(data.get('NOM_CORTO') or data.get('nom_corto', '')).strip()
            descripcion = str(data.get('DESCRIPCION') or data.get('descripcion', '')).strip()

            if not nom_corto:
                return JsonResponse({'status': 'error', 'message': 'El campo Nombre Corto es obligatorio.'}, status=400)
            if not descripcion:
                return JsonResponse({'status': 'error', 'message': 'El campo Descripción es obligatorio.'}, status=400)

            cursor = connection_portalaei.cursor()
            
            # Verificar si ya existe un tipo de planta con el mismo nombre corto
            cursor.execute("SELECT ID_TPPLANTA FROM TIPO_PLANTA WHERE NOM_CORTO = ?", [nom_corto])
            if cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Ya existe un tipo de planta con ese nombre corto.'}, status=400)

            cursor.execute("""
                INSERT INTO TIPO_PLANTA (NOM_CORTO, DESCRIPCION)
                VALUES (?, ?)
            """, [nom_corto, descripcion])
            connection_portalaei.commit()

            cursor.execute("""
                SELECT TOP 1 ID_TPPLANTA, NOM_CORTO, DESCRIPCION
                FROM TIPO_PLANTA ORDER BY ID_TPPLANTA DESC
            """)
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()

            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, id_tipo_planta):
        try:
            data = json.loads(request.body)

            nom_corto = str(data.get('nom_corto', '')).strip()
            descripcion = str(data.get('descripcion', '')).strip()

            if not nom_corto:
                return JsonResponse({'status': 'error', 'message': 'El campo Nombre Corto es obligatorio.'}, status=400)
            if not descripcion:
                return JsonResponse({'status': 'error', 'message': 'El campo Descripción es obligatorio.'}, status=400)

            cursor = connection_portalaei.cursor()
            
            # Verificar si el tipo de planta existe
            cursor.execute("SELECT ID_TPPLANTA FROM TIPO_PLANTA WHERE ID_TPPLANTA = ?", [id_tipo_planta])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Tipo de planta no encontrado'}, status=404)

            # Verificar si ya existe otro tipo de planta con el mismo nombre corto
            cursor.execute("SELECT ID_TPPLANTA FROM TIPO_PLANTA WHERE NOM_CORTO = ? AND ID_TPPLANTA != ?", [nom_corto, id_tipo_planta])
            if cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Ya existe otro tipo de planta con ese nombre corto.'}, status=400)

            cursor.execute("""
                UPDATE TIPO_PLANTA
                SET NOM_CORTO=?, DESCRIPCION=?
                WHERE ID_TPPLANTA=?
            """, [nom_corto, descripcion, id_tipo_planta])
            connection_portalaei.commit()

            cursor.execute("SELECT * FROM TIPO_PLANTA WHERE ID_TPPLANTA = ?", [id_tipo_planta])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, id_tipo_planta):
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si el tipo de planta existe
            cursor.execute("SELECT ID_TPPLANTA FROM TIPO_PLANTA WHERE ID_TPPLANTA = ?", [id_tipo_planta])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Tipo de planta no encontrado'}, status=404)

            cursor.execute("DELETE FROM TIPO_PLANTA WHERE ID_TPPLANTA = ?", [id_tipo_planta])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Tipo de planta eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)