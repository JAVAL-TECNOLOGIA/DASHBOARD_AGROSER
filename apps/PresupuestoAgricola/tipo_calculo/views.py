# views.py
import json

from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei
from apps.utils.permissions import es_admin
from django.http import JsonResponse

class tipo_calculo(TemplateView):
    permission_required = 'modulo_presupuesto_agricola'
    template_name = 'PresupuestoAgricola/tipo_calculo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        return context



@method_decorator(csrf_exempt, name='dispatch')
class TipoCalculoCRUDView(View):
    def get(self, request, id_tipo_calculo=None):
        try:
            cursor = connection_portalaei.cursor()
            if id_tipo_calculo:
                cursor.execute("SELECT ID_TP_CALCULO, NOM_CORTO, DESCRIPCION FROM TIPO_CALCULO WHERE ID_TP_CALCULO = ?", [id_tipo_calculo])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Tipo de cálculo no encontrado'}, status=404)
            else:
                cursor.execute("SELECT ID_TP_CALCULO, NOM_CORTO, DESCRIPCION FROM TIPO_CALCULO")
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    def post(self, request):
        try:
            data = json.loads(request.body)
            nombre = data.get('NOM_CORTO') or data.get('nom_corto')
            descripcion = data.get('DESCRIPCION') or data.get('descripcion')

            cursor = connection_portalaei.cursor()
            cursor.execute(
                "INSERT INTO TIPO_CALCULO (NOM_CORTO, DESCRIPCION) VALUES (?, ?)",
                [nombre, descripcion]
            )
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Tipo de cálculo creado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    def put(self, request, id_tipo_calculo):
        try:
            data = json.loads(request.body)
            nombre = data.get('NOM_CORTO') or data.get('nom_corto')
            descripcion = data.get('DESCRIPCION') or data.get('descripcion')

            cursor = connection_portalaei.cursor()
            cursor.execute(
                "UPDATE TIPO_CALCULO SET NOM_CORTO = ?, DESCRIPCION = ? WHERE ID_TP_CALCULO = ?",
                [nombre, descripcion, id_tipo_calculo]
            )
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Tipo de cálculo actualizado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def deleteTipoCalculo(request, id_tipo_calculo):
    try:
        cursor = connection_portalaei.cursor()
        cursor.execute(
            "DELETE FROM TIPO_CALCULO WHERE ID_TP_CALCULO = ?",
            [id_tipo_calculo]
        )
        connection_portalaei.commit()
        cursor.close()
        return JsonResponse({'status': 'success', 'message': 'Tipo de cálculo eliminado'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)