# views.py
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei


class PresupuestoTipoTrabajoView(TemplateView):
    template_name = 'PresupuestoAgricola/tipo_costo_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoTipoCostoCRUDView(View):
    def get(self, request, id_tipo_costo=None):
        try:
            cursor = connection_portalaei.cursor()

            if id_tipo_costo    :
                cursor.execute("""
                    SELECT 
                        C.ID_TP_COSTO,
                        TC.NOM_CORTO AS TIPO_CALCULO,
                        C.NOMBRE,
                        C.DESCRIPCION
                    FROM TIPO_COSTO_BASE C
                    INNER JOIN TIPO_CALCULO TC ON TC.ID_TP_CALCULO = C.ID_TP_CALCULO
                    WHERE C.ID_TP_COSTO = ?
                """, [id_tipo_costo])
                row = cursor.fetchone()
                if not row:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'No encontrado'}, status=404)

                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, row))
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
            else:
                cursor.execute("""
                    SELECT 
                        C.ID_TP_COSTO,
                        TC.NOM_CORTO AS TIPO_CALCULO,
                        C.NOMBRE,
                        C.DESCRIPCION
                    FROM TIPO_COSTO_BASE C
                    INNER JOIN TIPO_CALCULO TC ON TC.ID_TP_CALCULO = C.ID_TP_CALCULO
                    ORDER BY C.ID_TP_COSTO DESC
                """)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        try:
            body = json.loads(request.body)
            id_tipo_calculo = body.get('id_tp_calculo')
            nombre = body.get('nombre')
            descripcion = body.get('descripcion', '')

            cursor = connection_portalaei.cursor()
            cursor.execute("""
                INSERT INTO TIPO_COSTO_BASE (ID_TP_CALCULO, NOMBRE, DESCRIPCION)
                VALUES (?, ?, ?)
            """, [id_tipo_calculo, nombre, descripcion])
            connection_portalaei.commit()
            cursor.close()

            return JsonResponse({'status': 'success', 'message': 'Tipo de costo creado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id_tipo_costo):
        try:
            body = json.loads(request.body)
            nombre = body.get('nombre')
            descripcion = body.get('descripcion', '')
            id_tipo_calculo = body.get('id_tipo_calculo')
            id_tipo_costo = body.get('id_tipo_costo')

            cursor = connection_portalaei.cursor()
            cursor.execute("""
                UPDATE TIPO_COSTO_BASE
                SET ID_TP_CALCULO = ?,
                    NOMBRE = ?,
                    DESCRIPCION = ?
                WHERE ID_TP_COSTO = ?
            """, [id_tipo_calculo, nombre, descripcion, id_tipo_costo])
            connection_portalaei.commit()
            cursor.close()

            return JsonResponse({'status': 'success', 'message': 'Tipo de costo actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, id_tipo_costo):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                DELETE FROM TIPO_COSTO_BASE WHERE ID_TP_COSTO = ?
            """, [id_tipo_costo])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Tipo de costo eliminado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoTipoCalculoListView(View):
    def get(self, request):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT ID_TP_CALCULO, NOM_CORTO, DESCRIPCION
                FROM TIPO_CALCULO
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)