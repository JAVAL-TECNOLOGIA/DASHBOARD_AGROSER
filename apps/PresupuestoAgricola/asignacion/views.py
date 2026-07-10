# views.py
import json
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei
from apps.utils.permissions import es_admin
from django.http import JsonResponse


class asignacion_ingenieros(TemplateView):
    permission_required = 'modulo_presupuesto_agricola'
    template_name = 'PresupuestoAgricola/rrhh_asignacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                           SELECT a.ID_ASIGNACION, u.id, u.first_name, u.last_name, l.DESCRIPCION, c.DESCRIPCION
                           FROM ASIGNACION_LOTE a
                                    INNER JOIN user_user u ON u.id = a.ID_RESPONSABLE
                                    INNER JOIN dbo.LOTE L ON a.ID_LOTE = L.ID_LOTE
                                    INNER JOIN dbo.CAMPANIA C ON a.ID_CAMPANIA = C.ID_CAMPANIA
                           """)
            asignaciones = []
            for row in cursor.fetchall():
                asignaciones.append({
                    'ID_ASIGNACION': row[0],
                    'ID_USUARIO': row[1],
                    "NOMBRE": f"{row[2]} {row[3]}",
                    "LOTE": row[4],
                    "CAMPANIA": row[5]
                })
            cursor.close()
            context['asignaciones'] = asignaciones
        except Exception as e:
            context['asignaciones'] = []
            context['error'] = str(e)

        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_LOTE, DESCRIPCION FROM LOTE")
            lotes = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            cursor.close()
            context['lotes'] = lotes
        except Exception as e:
            context['lotes'] = []
            context['error_lotes'] = str(e)

        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM CAMPANIA")
            campanias = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            cursor.close()
            context['campanias'] = campanias
        except Exception as e:
            context['campanias'] = []
            context['error_campanias'] = str(e)

        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                           SELECT id, first_name, last_name, username, email
                           FROM [PORTAL_AEI].[dbo].[user_user]
                           WHERE active=1
                           """)
            ingenieros = []
            for row in cursor.fetchall():
                ingenieros.append({
                    'ID_USUARIO': row[0],
                    'NOMBRE': f"{row[1]} {row[2]} ({row[3]})",
                    'EMAIL': row[4]
                })
            cursor.close()
            context['ingenieros'] = ingenieros
        except Exception as e:
            context['ingenieros'] = []
            context['error_ingenieros'] = str(e)
        return context


@method_decorator(csrf_exempt, name='dispatch')


class IngenierosListView(View):
    def get(self, request):
        try:
            cursor = connection_portalaei.cursor()
            # Ajusta el filtro según tu lógica de ingenieros (ejemplo: admin=1 y active=1)
            cursor.execute("""
                           SELECT id, first_name, last_name, username, email
                           FROM [PORTAL_AEI].[dbo].[user_user]
                           WHERE active=1
                           """)
            ingenieros = []
            for row in cursor.fetchall():
                ingenieros.append({
                    'ID_USUARIO': row[0],
                    'NOMBRE': f"{row[1]} {row[2]} ({row[3]})",
                    'EMAIL': row[4]
                })
            cursor.close()
            return JsonResponse({'status': 'success', 'data': ingenieros})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AsignacionLoteCRUDView(View):
    def get(self, request, id_asignacion=None):
        try:
            cursor = connection_portalaei.cursor()
            if id_asignacion:
                cursor.execute(
                    "SELECT ID_ASIGNACION, ID_RESPONSABLE, ID_LOTE, ID_CAMPANIA FROM ASIGNACION_LOTE WHERE ID_ASIGNACION = ?",
                    [id_asignacion])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Asignación no encontrada'}, status=404)
            else:
                cursor.execute("SELECT ID_ASIGNACION, ID_RESPONSABLE, ID_LOTE, ID_CAMPANIA FROM ASIGNACION_LOTE")
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            id_responsable = data.get('ID_RESPONSABLE') or data.get('id_responsable')
            id_lote = data.get('ID_LOTE') or data.get('id_lote')
            id_campania = data.get('ID_CAMPANIA') or data.get('id_campania')
            if not id_responsable or not id_lote or not id_campania:
                return JsonResponse({'status': 'error', 'message': 'Todos los campos son obligatorios.'}, status=400)
            cursor = connection_portalaei.cursor()
            try:
                cursor.execute("""
                               INSERT INTO ASIGNACION_LOTE (ID_RESPONSABLE, ID_LOTE, ID_CAMPANIA)
                               VALUES (?, ?, ?)
                               """, [id_responsable, id_lote, id_campania])
                connection_portalaei.commit()
                cursor.close()
                # Usar un nuevo cursor para el SELECT (esto evita el error ODBC)
                cursor2 = connection_portalaei.cursor()
                cursor2.execute(
                    "SELECT TOP 1 ID_ASIGNACION, ID_RESPONSABLE, ID_LOTE, ID_CAMPANIA FROM ASIGNACION_LOTE ORDER BY ID_ASIGNACION DESC")
                row = cursor2.fetchone()
                columns = [col[0] for col in cursor2.description]
                data = dict(zip(columns, row))
                cursor2.close()
                return JsonResponse({'status': 'success', 'data': data})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, id_asignacion):
        try:
            data = json.loads(request.body)
            id_responsable = data.get('ID_RESPONSABLE') or data.get('id_responsable')
            id_lote = data.get('ID_LOTE') or data.get('id_lote')
            id_campania = data.get('ID_CAMPANIA') or data.get('id_campania')
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_ASIGNACION FROM ASIGNACION_LOTE WHERE ID_ASIGNACION = ?", [id_asignacion])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Asignación no encontrada'}, status=404)
            cursor.execute("""
                           UPDATE ASIGNACION_LOTE
                           SET ID_RESPONSABLE = ?,
                               ID_LOTE        = ?,
                               ID_CAMPANIA    = ?
                           WHERE ID_ASIGNACION = ?
                           """, [id_responsable, id_lote, id_campania, id_asignacion])
            connection_portalaei.commit()
            cursor.close()
            # Nuevo cursor para el SELECT
            cursor2 = connection_portalaei.cursor()
            cursor2.execute(
                "SELECT ID_ASIGNACION, ID_RESPONSABLE, ID_LOTE, ID_CAMPANIA FROM ASIGNACION_LOTE WHERE ID_ASIGNACION = ?",
                [id_asignacion])
            row = cursor2.fetchone()
            columns = [col[0] for col in cursor2.description]
            data = dict(zip(columns, row))
            cursor2.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, id_asignacion):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_ASIGNACION FROM ASIGNACION_LOTE WHERE ID_ASIGNACION = ?", [id_asignacion])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Asignación no encontrada'}, status=404)
            cursor.execute("DELETE FROM ASIGNACION_LOTE WHERE ID_ASIGNACION = ?", [id_asignacion])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Asignación eliminada correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AsignacionListView(View):
    def get(self, request):
        try:
            cursor = connection_portalaei.cursor()
            # Ajusta el filtro según tu lógica de ingenieros (ejemplo: admin=1 y active=1)
            cursor.execute("""
                           SELECT a.ID_ASIGNACION, u.id, u.first_name, u.last_name, l.DESCRIPCION, c.DESCRIPCION
                           FROM ASIGNACION_LOTE a
                                    inner join user_user u on u.id = a.ID_RESPONSABLE
                                    inner join dbo.LOTE L on a.ID_LOTE = L.ID_LOTE
                                    inner join dbo.CAMPANIA C on a.ID_CAMPANIA = C.ID_CAMPANIA
                           """)
            asignaciones = []
            for row in cursor.fetchall():
                asignaciones.append({
                    'ID_ASIGNACION': row[0],
                    'ID_USUARIO': row[1],
                    "NOMBRE": row[2] + " " + row[3],
                    "LOTE": row[4],
                    "CAMPANIA": row[5]
                })
            cursor.close()
            return JsonResponse({'status': 'success', 'data': asignaciones})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
