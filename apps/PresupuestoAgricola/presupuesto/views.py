# views.py
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.db import transaction

from apps.connection.connect_portalaei import connection_portalaei


class PresupuestoAgricolaView(TemplateView):
    template_name = 'PresupuestoAgricola/presupuesto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cursor = connection_portalaei.cursor()

        # Cargar campañas
        cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM CAMPANIA ORDER BY DESCRIPCION DESC")
        context['campanias'] = [
            {"ID_CAMPANIA": r[0], "DESCRIPCION": r[1]}
            for r in cursor.fetchall()
        ]

        # Cargar configuraciones
        cursor.execute("""
            select CTT.ID_CONFIG_TTRAB, p.ID_PARAMETRO, p.DESCRIPCION,
                CTT.ID_CAMPANIA,
                ca.DESCRIPCION AS CAMPANIA,
                tt.NOM_CORTO AS TIPO_TRABAJO,
                tc.NOM_CORTO AS TIPO_CALCULO
from dbo.PARAMETRO_COSTO p
join dbo.CONFIG_TIPO_TRABAJO CTT on p.ID_CONFIG_TTRAB = CTT.ID_CONFIG_TTRAB
JOIN CAMPANIA ca ON ca.ID_CAMPANIA = CTT.ID_CAMPANIA
JOIN TIPO_TRABAJO tt ON tt.ID_TP_TRABAJO = CTT.ID_TP_TRABAJO
JOIN TIPO_CALCULO tc ON tc.ID_TP_CALCULO = CTT.ID_TP_CALCULO
        """)

        configs = [
            {
                'ID_CONFIG_TTRAB': r[0],
                'ID_PARAMETRO': r[1],
                'DESCRIPCION': r[2],
                'ID_CAMPANIA': r[3],
                'CAMPANIA': r[4],
                'TIPO_TRABAJO': r[5],
                'TIPO_CALCULO': r[6],
            }
            for r in cursor.fetchall()
        ]

        context['configs'] = configs
        context['configs_json'] = json.dumps(configs)

        return context

@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoCRUDView(View):

    def get(self, request, id_presupuesto=None):
        try:
            cursor = connection_portalaei.cursor()
            id_usuario = self.request.user.id

            es_admin = request.user.is_superuser

            # Si viene ?idIng=...
            id_ing_filter = request.GET.get("idIng", None)

            # ---------- 1) Consulta de un solo presupuesto ----------
            if id_presupuesto:

                query = """
                        SELECT p.ID_PRESUPUESTO, \
                               p.ID_CONFIG_TTRAB, \

                               -- SNAPSHOT \
                               p.ANIO_CAMPANIA, \
                               p.CAMPANIA_DESCRIPCION, \
                               p.TIPO_TRABAJO_DESC, \
                               p.TIPO_CALCULO_DESC, \

                               -- COSTOS Y CHECKBOX \
                               p.TIENE_RECLUTADOR, \
                               p.COSTO_REND_RECLUTADOR, \
                               p.CANT_RECLUTADOR, \

                               p.TIENE_SUPERVISOR, \
                               p.COSTO_SUPERVISOR, \
                               p.CANT_SUPERVISOR, \

                               p.TIENE_CTRL_RENDIMIENTO, \
                               p.COSTO_CTRL_RENDIMIENTO, \
                               p.CANT_CTRL_RENDIMIENTO, \

                               p.TIENE_CTRL_CALIDAD, \
                               p.COSTO_CTRL_CALIDAD, \
                               p.CANT_CTRL_CALIDAD, \

                               p.ESTADO, \
                               p.FECHA_CREACION, \

                               -- INFO CONFIG PRINCIPAL \
                               ctt.ID_CAMPANIA, \
                               cam.DESCRIPCION AS CAMPANIA, \
                               tt.NOM_CORTO    AS TIPO_TRABAJO, \
                               tc.NOM_CORTO    AS TIPO_CALCULO
                        FROM PRESUPUESTO_CAB p
                                 LEFT JOIN CONFIG_TIPO_TRABAJO ctt ON p.ID_CONFIG_TTRAB = ctt.ID_CONFIG_TTRAB
                                 LEFT JOIN CAMPANIA cam ON ctt.ID_CAMPANIA = cam.ID_CAMPANIA
                                 LEFT JOIN TIPO_TRABAJO tt ON ctt.ID_TP_TRABAJO = tt.ID_TP_TRABAJO
                                 LEFT JOIN TIPO_CALCULO tc ON ctt.ID_TP_CALCULO = tc.ID_TP_CALCULO
                        WHERE p.ID_PRESUPUESTO = ? \
                        """

                cursor.execute(query, [id_presupuesto])
                row = cursor.fetchone()

                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Presupuesto no encontrado'}, status=404)

                cols = [col[0] for col in cursor.description]
                data = dict(zip(cols, row))

                return JsonResponse({'status': 'success', 'data': data})

            # ---------- 2) Listado general ----------
            if es_admin and id_ing_filter:
                list_query = """
                             SELECT 
                                p.ID_PRESUPUESTO,
                                p.ID_CONFIG_TTRAB,
                        
                                -- SNAPSHOT
                                p.CAMPANIA_DESCRIPCION,
                                p.TIPO_TRABAJO_DESC,
                                p.TIPO_CALCULO_DESC,
                        
                                -- COSTOS Y CHECKBOX
                                p.TIENE_RECLUTADOR,
                                p.COSTO_REND_RECLUTADOR,
                                p.CANT_RECLUTADOR,
                        
                                p.TIENE_SUPERVISOR,
                                p.COSTO_SUPERVISOR,
                                p.CANT_SUPERVISOR,
                        
                                p.TIENE_CTRL_RENDIMIENTO,
                                p.COSTO_CTRL_RENDIMIENTO,
                                p.CANT_CTRL_RENDIMIENTO,
                        
                                p.TIENE_CTRL_CALIDAD,
                                p.COSTO_CTRL_CALIDAD,
                                p.CANT_CTRL_CALIDAD,
                        
                                p.ESTADO,
                                p.FECHA_CREACION,
                        
                                -- INFO CONFIG PRINCIPAL
                                ctt.ID_CAMPANIA,
                                cam.DESCRIPCION AS CAMPANIA,
                                tt.NOM_CORTO AS TIPO_TRABAJO,
                                tc.NOM_CORTO AS TIPO_CALCULO
                            FROM PRESUPUESTO_CAB p
                                LEFT JOIN CONFIG_TIPO_TRABAJO ctt ON p.ID_CONFIG_TTRAB = ctt.ID_CONFIG_TTRAB
                                LEFT JOIN CAMPANIA cam ON ctt.ID_CAMPANIA = cam.ID_CAMPANIA
                                LEFT JOIN TIPO_TRABAJO tt ON ctt.ID_TP_TRABAJO = tt.ID_TP_TRABAJO
                                LEFT JOIN TIPO_CALCULO tc ON ctt.ID_TP_CALCULO = tc.ID_TP_CALCULO
                            WHERE p.ID_INGENIERO = ?
                            ORDER BY p.ID_PRESUPUESTO DESC;
                             """

                cursor.execute(list_query, [id_ing_filter])

            else:
                list_query = """
                             SELECT p.ID_PRESUPUESTO,
                                    p.ID_CONFIG_TTRAB,

                                    p.CAMPANIA_DESCRIPCION,
                                    p.TIPO_TRABAJO_DESC,
                                    p.TIPO_CALCULO_DESC,

                                    p.TIENE_RECLUTADOR,
                                    p.COSTO_REND_RECLUTADOR,
                                    p.CANT_RECLUTADOR,

                                    p.TIENE_SUPERVISOR,
                                    p.COSTO_SUPERVISOR,
                                    p.CANT_SUPERVISOR,

                                    p.TIENE_CTRL_RENDIMIENTO,
                                    p.COSTO_CTRL_RENDIMIENTO,
                                    p.CANT_CTRL_RENDIMIENTO,

                                    p.TIENE_CTRL_CALIDAD,
                                    p.COSTO_CTRL_CALIDAD,
                                    p.CANT_CTRL_CALIDAD,

                                    p.ESTADO,
                                    p.FECHA_CREACION,

                                    ctt.ID_CAMPANIA,
                                    cam.DESCRIPCION AS CAMPANIA,
                                    tt.NOM_CORTO    AS TIPO_TRABAJO,
                                    tc.NOM_CORTO    AS TIPO_CALCULO
                             FROM PRESUPUESTO_CAB p
                                      LEFT JOIN CONFIG_TIPO_TRABAJO ctt ON p.ID_CONFIG_TTRAB = ctt.ID_CONFIG_TTRAB
                                      LEFT JOIN CAMPANIA cam ON ctt.ID_CAMPANIA = cam.ID_CAMPANIA
                                      LEFT JOIN TIPO_TRABAJO tt ON ctt.ID_TP_TRABAJO = tt.ID_TP_TRABAJO
                                      LEFT JOIN TIPO_CALCULO tc ON ctt.ID_TP_CALCULO = tc.ID_TP_CALCULO

                             WHERE p.ID_INGENIERO = ?
                             ORDER BY p.ID_PRESUPUESTO DESC \
                             """
                cursor.execute(list_query, [id_usuario])

            # CONVERTIR A DICCIONARIO
            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            data = [dict(zip(cols, r)) for r in rows]

            return JsonResponse({'status': 'success', 'data': data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        finally:
            cursor.close()

    def post(self, request):
        """Crear nuevo presupuesto"""
        try:
            data = json.loads(request.body)
            cab = data.get("cabecera", {})
            detalles = data.get("detalles", [])
            id_usuario = self.request.user.id
            es_admin = request.user.is_superuser


            if es_admin:
                id_usuario = cab.get("id_ingeniero")


            # cursor = connection_portalaei.cursor()
            with transaction.atomic():
                with connection_portalaei.cursor() as cursor:
                    # ------------------------------
                    # INSERT CABECERA
                    # ------------------------------
                    cursor.execute("""
                        INSERT INTO PRESUPUESTO_CAB (
                            ID_INGENIERO,
                            ID_CAMPANIA,
                            COSTO_REND_RECLUTADOR,
                            TIENE_RECLUTADOR,
                            CANT_RECLUTADOR,
                            TIENE_SUPERVISOR,
                            COSTO_SUPERVISOR,
                            CANT_SUPERVISOR,
                            TIENE_CTRL_RENDIMIENTO,
                            COSTO_CTRL_RENDIMIENTO,
                            CANT_CTRL_RENDIMIENTO,
                            TIENE_CTRL_CALIDAD,
                            COSTO_CTRL_CALIDAD,
                            CANT_CTRL_CALIDAD,
                            ID_CONFIG_TTRAB,
                            CAMPANIA_DESCRIPCION,
                            TIPO_TRABAJO_DESC,
                            TIPO_CALCULO_DESC,
                            FECHA_CREACION,
                            ESTADO
                        )
                        OUTPUT INSERTED.ID_PRESUPUESTO
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), 'EN PROCESO')
                    """, [
                        id_usuario,            # int
                        cab.get("id_campania"),            # int
                        cab.get("costo_reclutador"),        # decimal
                        cab.get("tiene_reclutador"),        # bit
                        cab.get("cant_reclutador"),         # decimal

                        cab.get("tiene_supervisor"),
                        cab.get("costo_supervisor"),
                        cab.get("cant_supervisor"),

                        cab.get("tiene_ctrl_rendimiento"),
                        cab.get("costo_ctrl_rendimiento"),
                        cab.get("cant_ctrl_rendimiento"),

                        cab.get("tiene_ctrl_calidad"),
                        cab.get("costo_ctrl_calidad"),
                        cab.get("cant_ctrl_calidad"),

                        cab.get("id_config_ttrab"),         # FK CONFIG_TIPO_TRABAJO
                        cab.get("campania_desc"),           # varchar
                        cab.get("tipo_trabajo_desc"),       # varchar
                        cab.get("tipo_calculo_desc"),       # varchar
                    ])

                    id_presupuesto = cursor.fetchone()[0]

                    # ------------------------------
                    # INSERT DETALLE
                    # ------------------------------
                    for d in detalles:
                        cursor.execute("""
                            INSERT INTO PRESUPUESTO_DET (
                             ID_PRESUPUESTO,
                            ID_LOTE,
                            ID_MAPEO,
                            HECTAREAS,
                            PLANTAS_POR_LOTE,
                                PLANTAS_POR_HA,
                            RENDIMIENTO_ESPERADO,
                            PAGO_POR_PLANTA,
                            JORNALES_X_LOTE,
                            JORNALES_X_HA,
                            
                            -- COSTO MANO DE OBRA
                            JORNAL_BASICO,
                            ASIG_FAM,
                            DOMINICAL,
                            ESSALUD_VAC,
                            TOTAL_MANO_OBRA,
                            
                            -- RECLUTADOR
                            COMISION,
                            JORNAL_BASICO_REC,
                            ASIG_FAM_REC,
                            DOMINICAL_REC,
                            ESSALUD_VAC_REC,
                            TOTAL_RECLUTADOR,
                            
                            -- SUPERVISOR
                            N_SUPERVISOR,
                            JORNAL_BASICO_SUP,
                            ASIG_FAM_SUP,
                            DOMINICAL_SUP,
                            ESSALUD_VAC_SUP,
                            TOTAL_SUP,
                            
                            -- CONTROL RENDIMIENTO
                            N_CTRL_REND,
                            JORNAL_BASICO_CTRL,
                            ASIG_FAM_CTRL,
                            DOMINICAL_CTRL,
                            ESSALUD_VAC_CTRL,
                            TOTAL_CTRL,
                            
                            -- CONTROL CALIDAD
                            N_CTRL_CAL,
                            JORNAL_BASICO_CAL,
                            ASIG_FAM_CAL,
                            DOMINICAL_CAL,
                            ESSALUD_VAC_CAL,
                            TOTAL_CAL,
                            
                            -- OTROS
                            MOVILIDAD,
                            TOTAL,
                            COSTO_HA
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, [
                            id_presupuesto,
                            d.get("id_lote"),
                            d.get("id_mapeo"),
                            d.get("hectareas"),
                            d.get("plantas_lote"),
                            d.get("plantas_ha"),
                            d.get("rdto"),
                            d.get("pago_planta"),
                            d.get("jorl"),
                            d.get("jorha"),
                            d.get("jornal_basico"),
                            d.get("asig_fam"),
                            d.get("dominical"),
                            d.get("essalud_vac"),
                            d.get("total_mo"),
                            d.get("comision"),
                            d.get("jornal_rec"),
                            d.get("asig_fam_rec"),
                            d.get("dominical_rec"),
                            d.get("essalud_rec"),
                            d.get("total_rec"),
                            d.get("n_sup"),
                            d.get("jornal_sup"),
                            d.get("asig_fam_sup"),
                            d.get("dominical_sup"),
                            d.get("essalud_sup"),
                            d.get("total_sup"),
                            d.get("n_ctrl_rend"),
                            d.get("jornal_ctrl"),
                            d.get("asig_fam_ctrl"),
                            d.get("dominical_ctrl"),
                            d.get("essalud_ctrl"),
                            d.get("total_ctrl"),
                            d.get("n_ctrl_cal"),
                            d.get("jornal_cal"),
                            d.get("asig_fam_cal"),
                            d.get("dominical_cal"),
                            d.get("essalud_cal"),
                            d.get("total_cal"),
                            d.get("movilidad"),
                            d.get("total"),
                            d.get("costo_ha")
                        ])

                # connection_portalaei.commit()
                # cursor.close()

            return JsonResponse({
                "status": "success",
                "id_presupuesto": id_presupuesto
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def put(self, request, id_presupuesto):
        """Editar presupuesto existente"""
        try:
            data = json.loads(request.body)
            cab = data.get('cabecera')
            detalles = data.get('detalles', [])
            id_usuario = self.request.user.id
            es_admin = request.user.is_superuser

            if es_admin:
                id_usuario = cab.get("id_ingeniero"),

            with transaction.atomic():  # ← ← ← TRANSACCIÓN REAL
                with connection_portalaei.cursor() as cursor:


                    # 1️⃣ Actualizar cabecera
                    cursor.execute("""
                                   UPDATE PRESUPUESTO_CAB
                                        SET 
                                            ID_INGENIERO            = ?,
                                            
                                            COSTO_REND_RECLUTADOR  = ?,
                                            TIENE_RECLUTADOR       = ?,
                                            CANT_RECLUTADOR        = ?,
                                        
                                            TIENE_SUPERVISOR       = ?,
                                            COSTO_SUPERVISOR       = ?,
                                            CANT_SUPERVISOR        = ?,
                                        
                                            TIENE_CTRL_RENDIMIENTO = ?,
                                            COSTO_CTRL_RENDIMIENTO = ?,
                                            CANT_CTRL_RENDIMIENTO  = ?,
                                        
                                            TIENE_CTRL_CALIDAD     = ?,
                                            COSTO_CTRL_CALIDAD     = ?,
                                            CANT_CTRL_CALIDAD      = ?,
                                        
                                            ID_CONFIG_TTRAB        = ?,
                                            CAMPANIA_DESCRIPCION   = ?,
                                            TIPO_TRABAJO_DESC      = ?,
                                            TIPO_CALCULO_DESC      = ?
                                        WHERE ID_PRESUPUESTO = ?
                                   """, [
                                        #cab.get("id_ingeniero"),
                                        id_usuario,
                                        cab.get("costo_reclutador"),
                                        cab.get("tiene_reclutador"),
                                        cab.get("cant_reclutador"),

                                        cab.get("tiene_supervisor"),
                                        cab.get("costo_supervisor"),
                                        cab.get("cant_supervisor"),

                                        cab.get("tiene_ctrl_rendimiento"),
                                        cab.get("costo_ctrl_rendimiento"),
                                        cab.get("cant_ctrl_rendimiento"),

                                        cab.get("tiene_ctrl_calidad"),
                                        cab.get("costo_ctrl_calidad"),
                                        cab.get("cant_ctrl_calidad"),

                                        cab.get("id_config_ttrab"),
                                        cab.get("campania_desc"),
                                        cab.get("tipo_trabajo_desc"),
                                        cab.get("tipo_calculo_desc"),

                                        id_presupuesto

                                   ])

                    # 2️⃣ Borrar detalle anterior y reinsertar
                    cursor.execute("DELETE FROM PRESUPUESTO_DET WHERE ID_PRESUPUESTO = ?", [id_presupuesto])
                    for d in detalles:
                        cursor.execute("""
                                     INSERT INTO PRESUPUESTO_DET (
                                            ID_PRESUPUESTO,
                                            ID_LOTE,
                                            ID_MAPEO,
                                            HECTAREAS,
                                            PLANTAS_POR_LOTE,
                                            PLANTAS_POR_HA,
                                            RENDIMIENTO_ESPERADO,
                                            PAGO_POR_PLANTA,
                                            JORNALES_X_LOTE,
                                            JORNALES_X_HA,
                                        
                                            JORNAL_BASICO,
                                            ASIG_FAM,
                                            DOMINICAL,
                                            ESSALUD_VAC,
                                            TOTAL_MANO_OBRA,
                                        
                                            COMISION,
                                            JORNAL_BASICO_REC,
                                            ASIG_FAM_REC,
                                            DOMINICAL_REC,
                                            ESSALUD_VAC_REC,
                                            TOTAL_RECLUTADOR,
                                        
                                            N_SUPERVISOR,
                                            JORNAL_BASICO_SUP,
                                            ASIG_FAM_SUP,
                                            DOMINICAL_SUP,
                                            ESSALUD_VAC_SUP,
                                            TOTAL_SUP,
                                        
                                            N_CTRL_REND,
                                            JORNAL_BASICO_CTRL,
                                            ASIG_FAM_CTRL,
                                            DOMINICAL_CTRL,
                                            ESSALUD_VAC_CTRL,
                                            TOTAL_CTRL,
                                        
                                            N_CTRL_CAL,
                                            JORNAL_BASICO_CAL,
                                            ASIG_FAM_CAL,
                                            DOMINICAL_CAL,
                                            ESSALUD_VAC_CAL,
                                            TOTAL_CAL,
                                        
                                            MOVILIDAD,
                                            TOTAL,
                                            COSTO_HA
                                        )
                                        VALUES (
                                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                            ?, ?
                                        )
                                       """, [
                                            id_presupuesto,
                                            d.get('id_lote'),
                                            d.get('id_mapeo'),
                                            d.get('hectareas'),
                                            d.get('plantas_lote'),
                                            d.get('plantas_ha'),            # ← ahora sí se guarda
                                            d.get('rdto'),
                                            d.get('pago_planta'),
                                            d.get('jorl'),
                                            d.get('jorha'),

                                            d.get('jornal_basico'),
                                            d.get('asig_fam'),
                                            d.get('dominical'),
                                            d.get('essalud_vac'),
                                            d.get('total_mo'),

                                            d.get('comision'),
                                            d.get('jornal_rec'),
                                            d.get('asig_fam_rec'),
                                            d.get('dominical_rec'),
                                            d.get('essalud_rec'),
                                            d.get('total_rec'),

                                            d.get('n_sup'),
                                            d.get('jornal_sup'),
                                            d.get('asig_fam_sup'),
                                            d.get('dominical_sup'),
                                            d.get('essalud_sup'),
                                            d.get('total_sup'),

                                            d.get('n_ctrl_rend'),
                                            d.get('jornal_ctrl'),
                                            d.get('asig_fam_ctrl'),
                                            d.get('dominical_ctrl'),
                                            d.get('essalud_ctrl'),
                                            d.get('total_ctrl'),

                                            d.get('n_ctrl_cal'),
                                            d.get('jornal_cal'),
                                            d.get('asig_fam_cal'),
                                            d.get('dominical_cal'),
                                            d.get('essalud_cal'),
                                            d.get('total_cal'),

                                            d.get('movilidad'),
                                            d.get('total'),
                                            d.get('costo_ha')
                                        ])

            # connection_portalaei.commit()
            # cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Presupuesto actualizado correctamente'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def delete(self, request, id_presupuesto):
        try:
            cursor = connection_portalaei.cursor()
            # 🔹 1. Eliminar primero los detalles
            cursor.execute("""
                           DELETE
                           FROM PRESUPUESTO_DET
                           WHERE ID_PRESUPUESTO = ?
                           """, [id_presupuesto])

            # 🔹 2. Luego eliminar la cabecera
            cursor.execute("""
                           DELETE
                           FROM PRESUPUESTO_CAB
                           WHERE ID_PRESUPUESTO = ?
                           """, [id_presupuesto])

            # 🔹 3. Confirmar los cambios
            connection_portalaei.commit()
            return JsonResponse({'status': 'success', 'message': 'Presupuesto eliminado correctamente.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        finally:
            cursor.close()

@method_decorator(csrf_exempt, name='dispatch')
class LotesAsignadosAPI(View):
    def get(self, request):
        try:
            # ID del usuario logueado (usa 1 como valor por defecto en desarrollo)
            id_responsable = request.user.id if request.user.is_authenticated else 1
            id_campania = request.GET.get('campania')

            if not id_campania:
                return JsonResponse({'status': 'error', 'message': 'Debe enviar el parámetro campania'}, status=400)

            cursor = connection_portalaei.cursor()
            query = """
                SELECT 
                    al.ID_LOTE,
                    l.DESCRIPCION,
                    m.AREA_PRODUCTIVA AS HECTAREAS,
                    md.CANTIDAD AS PLANTAS_POR_LOTE,
                    m.DENSIDAD,
                    al.ID_CAMPANIA,
                    c.DESCRIPCION AS DESCRIPCION_CAMPANIA,
                    md.ID_MAPEO
                FROM ASIGNACION_LOTE al
                INNER JOIN LOTE l ON al.ID_LOTE = l.ID_LOTE
                LEFT JOIN MAPEO m ON m.ID_ASIGNACION = al.ID_ASIGNACION
                LEFT JOIN MAPEO_DETALLE md ON md.ID_MAPEO = m.ID_MAPEO AND md.ID_TPPLANTA = 2
                LEFT JOIN CAMPANIA c ON al.ID_CAMPANIA = c.ID_CAMPANIA
                WHERE al.ID_RESPONSABLE = ?
                  AND al.ID_CAMPANIA = ?
            """
            cursor.execute(query, [id_responsable, id_campania])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            cursor.close()

            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ParametroCostoAPI(View):
    def get(self, request):
        try:
            id_tipo_costo = request.GET.get('id_tipo_costo')

            cursor = connection_portalaei.cursor()

            # Si viene id_tipo_costo, filtra por ese valor
            if id_tipo_costo:
                cursor.execute("""
                    SELECT TOP 1 
                        pc.ID_PARAMETRO,
                        pc.ID_TIPO_COSTO,
                        tc.NOMBRE AS NOM_COSTO_BASE,
                        pc.ASIGNACION_FAMILIAR,
                        pc.VALOR_DIARIO,
                        pc.VALOR_SEMANAL,
                        pc.VALOR_DIA_EFECTIVO,
                        pc.JORNAL,
                        pc.DOMINICAL,
                        pc.COMISION_SERVIS,
                        pc.DESCRIPCION
                    FROM PARAMETRO_COSTO pc
                    INNER JOIN tipo_costo_base tc ON pc.ID_TIPO_COSTO = tc.ID_TP_COSTO
                    WHERE pc.ID_TIPO_COSTO = ?
                    ORDER BY pc.ID_PARAMETRO DESC
                """, [id_tipo_costo])
            else:
                # Si no viene parámetro, devuelve el último (por defecto)
                cursor.execute("""
                    SELECT TOP 1 
                        pc.ID_PARAMETRO,
                        pc.ID_TIPO_COSTO,
                        tc.NOMBRE AS NOM_COSTO_BASE,
                        pc.ASIGNACION_FAMILIAR,
                        pc.VALOR_DIARIO,
                        pc.VALOR_SEMANAL,
                        pc.VALOR_DIA_EFECTIVO,
                        pc.JORNAL,
                        pc.DOMINICAL,
                        pc.COMISION_SERVIS,
                        pc.DESCRIPCION
                    FROM PARAMETRO_COSTO pc
                    INNER JOIN tipo_costo_base tc ON pc.ID_TIPO_COSTO = tc.ID_TP_COSTO
                    ORDER BY pc.ID_PARAMETRO DESC
                """)

            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            cursor.close()

            if row:
                data = dict(zip(columns, row))
                return JsonResponse({'status': 'success', 'data': data})
            else:
                return JsonResponse({'status': 'error', 'message': 'No hay parámetros configurados para ese costo base'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoDetalleAPI(View):
    def get(self, request, id_presupuesto):
        try:
            with connection_portalaei.cursor() as cursor:
                # --- CABECERA ---
                cursor.execute("""
                    SELECT ID_PRESUPUESTO, ID_INGENIERO, ID_CAMPANIA, COSTO_REND_RECLUTADOR, TIENE_SUPERVISOR, COSTO_SUPERVISOR,
                           CANT_SUPERVISOR, TIENE_CTRL_RENDIMIENTO, COSTO_CTRL_RENDIMIENTO, CANT_CTRL_RENDIMIENTO,
                           TIENE_CTRL_CALIDAD, COSTO_CTRL_CALIDAD, CANT_CTRL_CALIDAD,
                           FECHA_CREACION, ESTADO, ID_CONFIG_TTRAB, CAMPANIA_DESCRIPCION, TIPO_TRABAJO_DESC, 
                           TIPO_CALCULO_DESC,TIENE_RECLUTADOR, CANT_RECLUTADOR
                    FROM PRESUPUESTO_CAB
                    WHERE ID_PRESUPUESTO = ?
                """, [id_presupuesto])
                row = cursor.fetchone()
                if not row:
                    return JsonResponse({'status': 'error', 'message': 'Presupuesto no encontrado'}, status=404)

                columns = [col[0] for col in cursor.description]
                cabecera = dict(zip(columns, row))

                # --- DETALLES ---
                cursor.execute("""
                    SELECT ID_DETALLE, ID_PRESUPUESTO, ID_LOTE, ID_MAPEO,
                                                            HECTAREAS, PLANTAS_POR_LOTE, PLANTAS_POR_HA,
                           RENDIMIENTO_ESPERADO,
                                                            PAGO_POR_PLANTA,
                                                            JORNALES_X_LOTE, JORNALES_X_HA,
                                                            JORNAL_BASICO, ASIG_FAM, DOMINICAL, ESSALUD_VAC,
                                                            TOTAL_MANO_OBRA,
                                                            COMISION, JORNAL_BASICO_REC, ASIG_FAM_REC, DOMINICAL_REC,
                                                            ESSALUD_VAC_REC, TOTAL_RECLUTADOR,
                                                            N_SUPERVISOR, JORNAL_BASICO_SUP, ASIG_FAM_SUP,
                                                            DOMINICAL_SUP, ESSALUD_VAC_SUP, TOTAL_SUP,
                                                            N_CTRL_REND, JORNAL_BASICO_CTRL, ASIG_FAM_CTRL,
                                                            DOMINICAL_CTRL, ESSALUD_VAC_CTRL, TOTAL_CTRL,
                                                            N_CTRL_CAL, JORNAL_BASICO_CAL, ASIG_FAM_CAL, DOMINICAL_CAL,
                                                            ESSALUD_VAC_CAL, TOTAL_CAL,
                                                            MOVILIDAD, TOTAL, COSTO_HA
                    FROM PRESUPUESTO_DET
                    WHERE ID_PRESUPUESTO = ?
                """, [id_presupuesto])
                cols = [c[0] for c in cursor.description]
                detalles = [dict(zip(cols, r)) for r in cursor.fetchall()]

            return JsonResponse({'status': 'success', 'cabecera': cabecera, 'detalles': detalles})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class ConfigTipoTrabajoAPI(View):
    def get(self, request, id_config):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT 
                    c.ID_CONFIG_TTRAB,
                    c.ID_CAMPANIA,
                    ca.DESCRIPCION AS CAMPANIA,
                    tt.NOM_CORTO AS TIPO_TRABAJO,
                    tc.NOM_CORTO AS TIPO_CALCULO,

                    -- PARAMETROS BASE
                    pc.COSTO_BASE,
                    pc.COSTO_REND_RECLUTADOR,
                    pc.COSTO_SUPERVISOR,
                    pc.COSTO_CTRL_RENDIMIENTO,
                    pc.COSTO_CTRL_CALIDAD,

                    pc.ASIGNACION_FAMILIAR,
                    pc.VALOR_DIARIO,       
                    pc.VALOR_SEMANAL,    
                    pc.VALOR_DIA_EFECTIVO,
                    pc.JORNAL,
                    pc.DOMINICAL,
                    pc.COMISION_SERVIS

                FROM CONFIG_TIPO_TRABAJO c
                JOIN CAMPANIA ca ON ca.ID_CAMPANIA = c.ID_CAMPANIA
                JOIN TIPO_TRABAJO tt ON tt.ID_TP_TRABAJO = c.ID_TP_TRABAJO
                JOIN TIPO_CALCULO tc ON tc.ID_TP_CALCULO = c.ID_TP_CALCULO
                JOIN PARAMETRO_COSTO pc ON pc.ID_CONFIG_TTRAB = c.ID_CONFIG_TTRAB

                WHERE pc.ID_PARAMETRO = ?
            """, [id_config])

            row = cursor.fetchone()

            if not row:
                return JsonResponse({'status': 'error', 'message': 'Configuración no encontrada'}, status=404)

            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))

            return JsonResponse({'status': 'success', 'data': data})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def listar_ingenieros(request):
    try:
        cursor = connection_portalaei.cursor()
        cursor.execute("""
        SP_LISTAR_INGENIEROS""")
        rows = cursor.fetchall()

        ingenieros = []
        for r in rows:
            ingenieros.append({
                "id": r[0],
                "nombre": f"{r[4]} {r[5]}".strip(),
                "username": r[3]
            })

        return JsonResponse({"status": "ok", "data": ingenieros})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})