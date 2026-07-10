# views.py
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei


class PresupuestoLotesView(TemplateView):
    template_name = 'PresupuestoAgricola/rrhh_lotes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fundos
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_FUNDO, DESCRIPCION FROM FUNDO")
            fundos = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            cursor.close()
        except Exception:
            fundos = []
        context['fundos'] = fundos

        # Variedades
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID, DESCRIPCION FROM VARIEDAD")
            variedades = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            cursor.close()
        except Exception:
            variedades = []
        context['variedades'] = variedades

        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM CAMPANIA")
            campanias = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
            cursor.close()
        except Exception:
            campanias = []

        context['campanias'] = campanias
        
        return context

# CRUD API para lotes
@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoLoteCRUDView(View):
    def get(self, request, id_lote=None):
        try:
            cursor = connection_portalaei.cursor()
            id_fundo = request.GET.get('id_fundo')
            id_campania = request.GET.get('id_campania')
            if id_lote:
                cursor.execute("""
                    SELECT 
                    L.ID_LOTE,
                    L.DESCRIPCION,
                    L.AREA_TOTAL,
                    L.ID_FUNDO,
                    L.CECO,
                    L.ID_VARIEDAD,
                    L.ID_CAMPANIA,
                    C.DESCRIPCION AS CAMPANIA
                FROM LOTE L
                LEFT JOIN CAMPANIA C 
                ON L.ID_CAMPANIA = C.ID_CAMPANIA
                WHERE L.ID_LOTE = ?
                """, [id_lote])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Lote no encontrado'}, status=404)
            elif id_fundo:
                cursor.execute("""
                    SELECT 
                        L.ID_LOTE,
                        L.DESCRIPCION,
                        L.AREA_TOTAL,
                        L.ID_FUNDO,
                        L.CECO,
                        L.ID_VARIEDAD,
                        L.ID_CAMPANIA,
                        C.DESCRIPCION AS CAMPANIA
                    FROM LOTE L
                    LEFT JOIN CAMPANIA C 
                    ON L.ID_CAMPANIA = C.ID_CAMPANIA
                    WHERE L.ID_FUNDO = ?
                """, [id_fundo])
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
            elif id_campania:
                cursor.execute("""
                    SELECT 
                        L.ID_LOTE,
                        L.DESCRIPCION,
                        L.AREA_TOTAL,
                        L.ID_FUNDO,
                        L.CECO,
                        L.ID_VARIEDAD,
                        L.ID_CAMPANIA,
                        C.DESCRIPCION AS CAMPANIA
                    FROM LOTE L
                    LEFT JOIN CAMPANIA C 
                    ON L.ID_CAMPANIA = C.ID_CAMPANIA
                    WHERE L.ID_CAMPANIA = ?
                """, [id_campania])

                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
            else:
                cursor.execute("""
                    SELECT 
                        L.ID_LOTE,
                        L.DESCRIPCION,
                        L.AREA_TOTAL,
                        L.ID_FUNDO,
                        L.CECO,
                        L.ID_VARIEDAD,
                        L.ID_CAMPANIA,
                        C.DESCRIPCION AS CAMPANIA
                    FROM LOTE L
                    LEFT JOIN CAMPANIA C 
                    ON L.ID_CAMPANIA = C.ID_CAMPANIA
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

            descripcion = str(data.get('DESCRIPCION') or data.get('descripcion', '')).strip()
            area_total = float(data.get('AREA_TOTAL') or data.get('area_total') or 0)
            id_fundo = str(data.get('ID_FUNDO') or data.get('id_fundo') or 0)
            ceco = str(data.get('CECO') or data.get('ceco', '')).strip()
            id_variedad = int(data.get('ID_VARIEDAD') or data.get('id_variedad') or 0)
            id_campania = str(data.get('ID_CAMPANIA') or data.get('id_campania') or 0)

            if not descripcion:
                return JsonResponse({'status': 'error', 'message': 'El campo DESCRIPCION es obligatorio.'}, status=400)
            if not id_fundo:
                return JsonResponse({'status': 'error', 'message': 'El campo ID_FUNDO es obligatorio.'}, status=400)
            if not id_variedad:
                return JsonResponse({'status': 'error', 'message': 'El campo ID_VARIEDAD es obligatorio.'}, status=400)

            cursor = connection_portalaei.cursor()
            cursor.execute("""
                INSERT INTO LOTE (DESCRIPCION, AREA_TOTAL, ID_FUNDO, CECO, ID_VARIEDAD, ID_CAMPANIA)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [descripcion, area_total, id_fundo, ceco, id_variedad, id_campania])
            connection_portalaei.commit()

            cursor.execute("""
                SELECT TOP 1 ID_LOTE, DESCRIPCION, AREA_TOTAL, ID_FUNDO, CECO, ID_VARIEDAD, ID_CAMPANIA
                FROM LOTE ORDER BY ID_LOTE DESC
            """)
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()

            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, id_lote):
        try:
            data = json.loads(request.body)

            descripcion = str(data.get('descripcion', '')).strip()
            area_total = float(data.get('area_total') or 0)
            id_fundo = str(data.get('id_fundo') or 0)
            ceco = str(data.get('ceco', '')).strip()
            id_variedad = int(data.get('id_variedad') or 0)
            id_campania = str(data.get('id_campania') or 0)

            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_LOTE FROM LOTE WHERE ID_LOTE = ?", [id_lote])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Lote no encontrado'}, status=404)

            cursor.execute("""
                UPDATE LOTE
                SET DESCRIPCION=?, AREA_TOTAL=?, ID_FUNDO=?, CECO=?, ID_VARIEDAD=?, ID_CAMPANIA=?
                WHERE ID_LOTE=?
            """, [descripcion, area_total, id_fundo, ceco, id_variedad, id_campania, id_lote])
            connection_portalaei.commit()

            cursor.execute("SELECT * FROM LOTE WHERE ID_LOTE = ?", [id_lote])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, id_lote):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_LOTE FROM LOTE WHERE ID_LOTE = ?", [id_lote])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Lote no encontrado'}, status=404)

            cursor.execute("DELETE FROM LOTE WHERE ID_LOTE = ?", [id_lote])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Lote eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)