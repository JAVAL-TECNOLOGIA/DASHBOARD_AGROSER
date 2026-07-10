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

class config_tipo_trabajo(TemplateView):
    permission_required = 'modulo_presupuesto_agricola'
    template_name = 'PresupuestoAgricola/config_tipo_trabajo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)
        
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener tipos de trabajo
            cursor.execute("SELECT ID_TP_TRABAJO, NOM_CORTO, DESCRIPCION FROM TIPO_TRABAJO ORDER BY NOM_CORTO")
            tipos_trabajo = [{'ID_TP_TRABAJO': row[0], 'NOM_CORTO': row[1], 'DESCRIPCION': row[2]} for row in cursor.fetchall()]
            context['tipos_trabajo'] = tipos_trabajo
            
            # Obtener tipos de cálculo
            cursor.execute("SELECT ID_TP_CALCULO, NOM_CORTO, DESCRIPCION FROM TIPO_CALCULO ORDER BY NOM_CORTO")
            tipos_calculo = [{'ID_TP_CALCULO': row[0], 'NOM_CORTO': row[1], 'DESCRIPCION': row[2]} for row in cursor.fetchall()]
            context['tipos_calculo'] = tipos_calculo
            
            # Obtener campañas
            cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM CAMPANIA ORDER BY DESCRIPCION")
            campanias = [{'ID_CAMPANIA': row[0], 'DESCRIPCION': row[1]} for row in cursor.fetchall()]
            context['campanias'] = campanias
            
            cursor.close()
        except Exception as e:
            context['tipos_trabajo'] = []
            context['tipos_calculo'] = []
            context['campanias'] = []
            
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ConfigTipoTrabajoCRUDView(View):
    def get(self, request, id_config_ttrab=None):
        try:
            cursor = connection_portalaei.cursor()
            if id_config_ttrab:
                cursor.execute("""
                    SELECT ct.ID_CONFIG_TTRAB, ct.ID_TP_TRABAJO, ct.ID_TP_CALCULO, ct.ID_CAMPANIA, ct.OBSERVACION,
                           tt.NOM_CORTO as nombre_tipo_trabajo, tc.NOM_CORTO as nombre_tipo_calculo, c.DESCRIPCION as descripcion_campania
                    FROM CONFIG_TIPO_TRABAJO ct
                    LEFT JOIN TIPO_TRABAJO tt ON ct.ID_TP_TRABAJO = tt.ID_TP_TRABAJO
                    LEFT JOIN TIPO_CALCULO tc ON ct.ID_TP_CALCULO = tc.ID_TP_CALCULO
                    LEFT JOIN CAMPANIA c ON ct.ID_CAMPANIA = c.ID_CAMPANIA
                    WHERE ct.ID_CONFIG_TTRAB = ?
                """, [id_config_ttrab])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Configuración no encontrada'}, status=404)
            else:
                cursor.execute("""
                    SELECT ct.ID_CONFIG_TTRAB, ct.ID_TP_TRABAJO, ct.ID_TP_CALCULO, ct.ID_CAMPANIA, ct.OBSERVACION,
                           tt.NOM_CORTO as nombre_tipo_trabajo, tc.NOM_CORTO as nombre_tipo_calculo, c.DESCRIPCION as descripcion_campania
                    FROM CONFIG_TIPO_TRABAJO ct
                    LEFT JOIN TIPO_TRABAJO tt ON ct.ID_TP_TRABAJO = tt.ID_TP_TRABAJO
                    LEFT JOIN TIPO_CALCULO tc ON ct.ID_TP_CALCULO = tc.ID_TP_CALCULO
                    LEFT JOIN CAMPANIA c ON ct.ID_CAMPANIA = c.ID_CAMPANIA
                    ORDER BY ct.ID_CONFIG_TTRAB DESC
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
            id_tipo_trabajo = data.get('id_tipo_trabajo')
            id_tipo_calculo = data.get('id_tipo_calculo')
            id_campania = data.get('id_campania')
            observacion = data.get('observacion', '')

            cursor = connection_portalaei.cursor()
            cursor.execute(
                "INSERT INTO CONFIG_TIPO_TRABAJO (ID_TP_TRABAJO, ID_TP_CALCULO, ID_CAMPANIA, OBSERVACION) VALUES (?, ?, ?, ?)",
                [id_tipo_trabajo, id_tipo_calculo, id_campania, observacion]
            )
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Configuración creada'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
    def put(self, request, id_config_ttrab):
        try:
            data = json.loads(request.body)
            id_tipo_trabajo = data.get('id_tipo_trabajo')
            id_tipo_calculo = data.get('id_tipo_calculo')
            id_campania = data.get('id_campania')
            observacion = data.get('observacion', '')

            cursor = connection_portalaei.cursor()
            cursor.execute(
                "UPDATE CONFIG_TIPO_TRABAJO SET ID_TP_TRABAJO = ?, ID_TP_CALCULO = ?, ID_CAMPANIA = ?, OBSERVACION = ? WHERE ID_CONFIG_TTRAB = ?",
                [id_tipo_trabajo, id_tipo_calculo, id_campania, observacion, id_config_ttrab]
            )
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Configuración actualizada'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
@csrf_exempt
def deleteConfigTipoTrabajo(request, id_config_ttrab):
    try:
        cursor = connection_portalaei.cursor()
        cursor.execute(
            "DELETE FROM CONFIG_TIPO_TRABAJO WHERE ID_CONFIG_TTRAB = ?",
            [id_config_ttrab]
        )
        connection_portalaei.commit()
        cursor.close()
        return JsonResponse({'status': 'success', 'message': 'Configuración eliminada'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)