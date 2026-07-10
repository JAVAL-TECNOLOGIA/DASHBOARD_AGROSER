# views.py
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei


class PresupuestoTipoTrabajoView(TemplateView):
    template_name = 'PresupuestoAgricola/tipo_trabajo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# CRUD API para tipo_trabajo
@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoTipoTrabajoCRUDView(View):
    def get(self, request, id_tipo_trabajo=None):
        try:
            cursor = connection_portalaei.cursor()
            
            if id_tipo_trabajo:
                cursor.execute("""
                    SELECT ID_TP_TRABAJO, NOM_CORTO, DESCRIPCION
                    FROM TIPO_TRABAJO WHERE ID_TP_TRABAJO = ?
                """, [id_tipo_trabajo])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Tipo de trabajo no encontrado'}, status=404)
            else:
                cursor.execute("""
                    SELECT ID_TP_TRABAJO, NOM_CORTO, DESCRIPCION
                    FROM TIPO_TRABAJO
                    ORDER BY ID_TP_TRABAJO
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
            
            # Verificar si ya existe un tipo de trabajo con el mismo nombre corto
            cursor.execute("SELECT ID_TP_TRABAJO FROM TIPO_TRABAJO WHERE NOM_CORTO = ?", [nom_corto])
            if cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Ya existe un tipo de trabajo con ese nombre corto.'}, status=400)

            cursor.execute("""
                INSERT INTO TIPO_TRABAJO (NOM_CORTO, DESCRIPCION)
                VALUES (?, ?)
            """, [nom_corto, descripcion])
            connection_portalaei.commit()

            cursor.execute("""
                SELECT TOP 1 ID_TP_TRABAJO, NOM_CORTO, DESCRIPCION
                FROM TIPO_TRABAJO ORDER BY ID_TP_TRABAJO DESC
            """)
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()

            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, id_tipo_trabajo):
        try:
            data = json.loads(request.body)

            nom_corto = str(data.get('nom_corto', '')).strip()
            descripcion = str(data.get('descripcion', '')).strip()

            if not nom_corto:
                return JsonResponse({'status': 'error', 'message': 'El campo Nombre Corto es obligatorio.'}, status=400)
            if not descripcion:
                return JsonResponse({'status': 'error', 'message': 'El campo Descripción es obligatorio.'}, status=400)

            cursor = connection_portalaei.cursor()
            
            # Verificar si el tipo de trabajo existe
            cursor.execute("SELECT ID_TP_TRABAJO FROM TIPO_TRABAJO WHERE ID_TP_TRABAJO = ?", [id_tipo_trabajo])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Tipo de trabajo no encontrado'}, status=404)

            # Verificar si ya existe otro tipo de trabajo con el mismo nombre corto
            cursor.execute("SELECT ID_TP_TRABAJO FROM TIPO_TRABAJO WHERE NOM_CORTO = ? AND ID_TP_TRABAJO != ?", [nom_corto, id_tipo_trabajo])
            if cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Ya existe otro tipo de trabajo con ese nombre corto.'}, status=400)

            cursor.execute("""
                UPDATE TIPO_TRABAJO
                SET NOM_CORTO=?, DESCRIPCION=?
                WHERE ID_TP_TRABAJO=?
            """, [nom_corto, descripcion, id_tipo_trabajo])
            connection_portalaei.commit()

            cursor.execute("SELECT * FROM TIPO_TRABAJO WHERE ID_TP_TRABAJO = ?", [id_tipo_trabajo])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, id_tipo_trabajo):
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si el tipo de trabajo existe
            cursor.execute("SELECT ID_TP_TRABAJO FROM TIPO_TRABAJO WHERE ID_TP_TRABAJO = ?", [id_tipo_trabajo])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Tipo de trabajo no encontrado'}, status=404)

            cursor.execute("DELETE FROM TIPO_TRABAJO WHERE ID_TP_TRABAJO = ?", [id_tipo_trabajo])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Tipo de trabajo eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)