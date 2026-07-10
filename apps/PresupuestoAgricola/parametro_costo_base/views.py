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


class parametro_costo_base(TemplateView):
    permission_required = 'modulo_presupuesto_agricola'
    template_name = 'PresupuestoAgricola/parametro_costo_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_admin'] = es_admin(self.request.user)

        try:
            cursor = connection_portalaei.cursor()

            # Obtener configuraciones de tipo trabajo
            cursor.execute("""
                           SELECT c.ID_CONFIG_TTRAB,
                                  c.ID_CAMPANIA + ' - ' + cal.NOM_CORTO + ' - ' + tt.NOM_CORTO AS descripcion_completa
                           FROM CONFIG_TIPO_TRABAJO c
                                    JOIN TIPO_CALCULO cal ON cal.ID_TP_CALCULO = c.ID_TP_CALCULO
                                    JOIN TIPO_TRABAJO tt ON tt.ID_TP_TRABAJO = c.ID_TP_TRABAJO
                           ORDER BY c.ID_CONFIG_TTRAB DESC
                           """)

            tipos_costo = [
                {
                    'ID_CONFIG_TTRAB': row[0],
                    'descripcion_completa': row[1]
                }
                for row in cursor.fetchall()
            ]
            context['tipos_costo'] = tipos_costo

            # Obtener unidades de medida
            cursor.execute("SELECT ID_UNIDAD, NOMBRE, NOM_CORTO, DESCRIPCION FROM UNIDAD_MEDIDA ORDER BY NOMBRE")
            unidades = [{'ID_UNIDAD': row[0], 'NOMBRE': row[1], 'NOM_CORTO': row[2], 'DESCRIPCION': row[3]} for row in
                        cursor.fetchall()]
            context['unidades'] = unidades

            cursor.close()
        except Exception as e:
            context['tipos_costo'] = []
            context['unidades'] = []

        return context


@method_decorator(csrf_exempt, name='dispatch')
class ParametroCostoCRUDView(View):

    def get(self, request, id_parametro=None):
        try:
            cursor = connection_portalaei.cursor()
            if id_parametro:
                cursor.execute("""
                               SELECT ID_PARAMETRO,
                                      ID_CONFIG_TTRAB,
                                      ASIGNACION_FAMILIAR,
                                      COSTO_BASE,
                                      JORNAL,
                                      DOMINICAL,
                                      COMISION_SERVIS,

                                      COSTO_REND_RECLUTADOR,
                                      COSTO_SUPERVISOR,
                                      COSTO_CTRL_RENDIMIENTO,
                                      COSTO_CTRL_CALIDAD,

                                      DESCRIPCION
                               FROM PARAMETRO_COSTO
                               WHERE ID_PARAMETRO = ?
                               """, [id_parametro])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Registro no encontrado'}, status=404)
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, row))
                return JsonResponse({'status': 'success', 'data': data})
            else:
                cursor.execute("""
                               SELECT p.ID_PARAMETRO,
                                      -- Configuración de trabajo (campaña - cálculo - trabajo)
                                      ca.DESCRIPCION + ' - ' + tt.NOM_CORTO + ' - ' + cal.NOM_CORTO AS NOMBRE_COSTO,

                                      p.COSTO_BASE,
                                      p.ASIGNACION_FAMILIAR,
                                      p.JORNAL,
                                      p.DOMINICAL,
                                      p.COMISION_SERVIS,

                                      p.COSTO_REND_RECLUTADOR,
                                      p.COSTO_SUPERVISOR,
                                      p.COSTO_CTRL_RENDIMIENTO,
                                      p.COSTO_CTRL_CALIDAD,

                                      p.DESCRIPCION
                               FROM PARAMETRO_COSTO p
                                        JOIN CONFIG_TIPO_TRABAJO c ON p.ID_CONFIG_TTRAB = c.ID_CONFIG_TTRAB
                                        JOIN TIPO_CALCULO cal ON cal.ID_TP_CALCULO = c.ID_TP_CALCULO
                                        JOIN TIPO_TRABAJO tt ON tt.ID_TP_TRABAJO = c.ID_TP_TRABAJO
                                        JOIN CAMPANIA ca ON c.ID_CAMPANIA = ca.ID_CAMPANIA
                               ORDER BY p.ID_PARAMETRO DESC
                               """)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            id_config_ttrab = data.get('id_config_ttrab')
            asig_fam = data.get('asignacion_familiar', '')
            jornal = float(data.get('jornal', 1))
            dominical = float(data.get('dominical', 1))
            com_servis = float(data.get('comision_servis', 1))
            descripcion = data.get('descripcion', '')

            costo_reclutador = float(data.get('costo_reclutador', 0))
            costo_supervisor = float(data.get('costo_supervisor', 0))
            costo_ctrl_rend = float(data.get('costo_ctrl_rend', 0))
            costo_ctrl_cal = float(data.get('costo_ctrl_cal', 0))
            costo_base = float(data.get('costo_base', 0))

            cursor = connection_portalaei.cursor()
            cursor.execute("""
                           INSERT INTO PARAMETRO_COSTO
                           (ID_CONFIG_TTRAB, ASIGNACION_FAMILIAR, JORNAL, COSTO_BASE, DOMINICAL, COMISION_SERVIS,
                            COSTO_REND_RECLUTADOR, COSTO_SUPERVISOR, COSTO_CTRL_RENDIMIENTO, COSTO_CTRL_CALIDAD,
                            DESCRIPCION)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, [id_config_ttrab, asig_fam, jornal, costo_base, dominical, com_servis, costo_reclutador,
                                 costo_supervisor, costo_ctrl_rend, costo_ctrl_cal, descripcion
                                 ])
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Registro creado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def put(self, request, id_parametro):
        try:
            data = json.loads(request.body)
            # id_tipo_costo = data.get('id_tipo_costo')
            asig_fam = data.get('asignacion_familiar', '')
            jornal = float(data.get('jornal', 1))
            dominical = float(data.get('dominical', 1))
            com_servis = float(data.get('comision_servis', 1))
            descripcion = data.get('descripcion', '')

            costo_reclutador = float(data.get('costo_reclutador', 0))
            costo_supervisor = float(data.get('costo_supervisor', 0))
            costo_ctrl_rend = float(data.get('costo_ctrl_rend', 0))
            costo_ctrl_cal = float(data.get('costo_ctrl_cal', 0))
            costo_base = float(data.get('costo_base', 0))

            cursor = connection_portalaei.cursor()
            cursor.execute("""
                           UPDATE PARAMETRO_COSTO
                           SET ASIGNACION_FAMILIAR    = ?,
                               JORNAL                 = ?,
                               DOMINICAL              = ?,
                               COSTO_BASE             = ?,
                               COMISION_SERVIS        = ?,
                               COSTO_REND_RECLUTADOR  = ?,
                               COSTO_SUPERVISOR       = ?,
                               COSTO_CTRL_RENDIMIENTO = ?,
                               COSTO_CTRL_CALIDAD     = ?,
                               DESCRIPCION            = ?
                           WHERE ID_PARAMETRO = ?
                           """,
                           [asig_fam, jornal, dominical, costo_base, com_servis, costo_reclutador, costo_supervisor,
                            costo_ctrl_rend, costo_ctrl_cal, descripcion, id_parametro])
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Registro actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, id_parametro):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("DELETE FROM PARAMETRO_COSTO WHERE ID_PARAMETRO = ?", [id_parametro])
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Registro eliminado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def deleteParametroCosto(request, id_parametro):
    try:
        cursor = connection_portalaei.cursor()
        cursor.execute(
            "DELETE FROM PARAMETRO_COSTO WHERE ID_PARAMETRO = ?",
            [id_parametro]
        )
        connection_portalaei.commit()
        cursor.close()
        return JsonResponse({'status': 'success', 'message': 'Parámetro eliminado'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
