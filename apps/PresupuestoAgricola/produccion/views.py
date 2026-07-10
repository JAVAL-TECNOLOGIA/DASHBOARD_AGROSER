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

class produccion_uva(TemplateView):
    permission_required = 'modulo_presupuesto_agricola'
    template_name = 'PresupuestoAgricola/produccion_uva.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_usuario = self.request.user.id
        from datetime import date
        import re
        try:
            cursor = connection_portalaei.cursor()
            # Campañas
            cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM CAMPANIA")
            campanias = []
            for row in cursor.fetchall():
                match = re.search(r'(\d{4})', row[1])
                anio = int(match.group(1)) if match else None
                campanias.append({
                    'id': row[0],
                    'descripcion': row[1],
                    'anio': anio
                })
            context['campanias'] = campanias

            # Campaña actual
            anio_actual = date.today().year
            campania_actual = next((c for c in campanias if c['anio'] == anio_actual), None)
            context['campania_actual'] = campania_actual
            context['anio_actual'] = anio_actual

            # Fundos
            cursor.execute(
                """
                SELECT f.ID_FUNDO, f.DESCRIPCION, f.ID_EMPRESA, COUNT(a.ID_ASIGNACION) AS TOTAL_LOTES
                FROM FUNDO f
                         LEFT JOIN LOTE l ON f.ID_FUNDO = l.ID_FUNDO
                         LEFT JOIN ASIGNACION_LOTE a
                                   ON l.ID_LOTE = a.ID_LOTE
                                    AND a.ID_RESPONSABLE = ?
                                       AND a.ID_CAMPANIA = ? 
                GROUP BY f.ID_FUNDO, f.DESCRIPCION, f.ID_EMPRESA
                ORDER BY f.DESCRIPCION;
                """,
                [id_usuario, 'CAMP' + str(anio_actual)]
            )
            fundos = [
                {
                    'ID_FUNDO': row[0],
                    'DESCRIPCION': row[1],
                    'ID_EMPRESA': row[2],
                    'TOTAL_LOTES': row[3]
                }
                for row in cursor.fetchall()
            ]
            context['fundos'] = fundos
            cursor.close()
        except Exception as e:
            context['fundos'] = []
            context['campanias'] = []
            context['campania_actual'] = None
            context['error'] = str(e)
        return context
  
# ===============================
# ENDPOINT: Obtener todos los datos de la tabla PRODUVA
# ===============================
@csrf_exempt
def list_produva(request):
    if request.method == 'GET':
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT 
                    p.ID_PRODUVA,
                    p.RENDIMIENTO,
                    p.RAC_PLANTA,
                    p.RAC_LOTE,
                    p.RAC_PACKING,
                    p.RAC_NACIONAL,
                    p.PESO_RAC,
                    p.KG_PROYEC_LOTE,
                    p.KG_EXPOR_LOTE,
                    p.KG_DESC_CAMP_LOTE,
                    p.KG_DESC_PROC_LOTE,
                    p.KG_PROYEC_HA,
                    p.KG_EXPOR_HA,
                    p.KG_DESC_CAMP_HA,
                    p.KG_DESC_PROC_HA,
                    p.CAJ_LOTE,
                    p.CAJ_HA,
                    p.CANT,
                    p.PORC,
                    p.ENV_FRU_PACK,
                    p.TOTAL_KG_ENV,
                    p.CAJAS,
                    p.ID_DETALLE
                FROM PROD_UVA p
                ORDER BY p.ID_PRODUVA DESC;
            """)

            rows = cursor.fetchall()

            data = [{
                    'ID_PRODUVA': row[0],
                    'RENDIMIENTO': row[1],
                    'RAC_PLANTA': row[2],
                    'RAC_LOTE': row[3],
                    'RAC_PACKING': row[4],
                    'RAC_NACIONAL': row[5],
                    'PESO_RAC': row[6],
                    'KG_PROYEC_LOTE': row[7],
                    'KG_EXPOR_LOTE': row[8],
                    'KG_DESC_CAMP_LOTE': row[9],
                    'KG_DESC_PROC_LOTE': row[10],
                    'KG_PROYEC_HA': row[11],
                    'KG_EXPOR_HA': row[12],
                    'KG_DESC_CAMP_HA': row[13],
                    'KG_DESC_PROC_HA': row[14],
                    'CAJ_LOTE': row[15],
                    'CAJ_HA': row[16],
                    'CANT': row[17],
                    'PORC': row[18],
                    'ENV_FRU_PACK': row[19],
                    'TOTAL_KG_ENV': row[20],
                    'CAJAS': row[21],
                    'ID_DETALLE': row[22]
                }
                for row in rows
            ]
            cursor.close()

            return JsonResponse({'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

class presupuesto_dl(TemplateView):
    permission_required = 'modulo_produccion_uva_1'
    template_name = 'PRODUCCION_UVA1/pages/produccionuva1_presupuesto_dl.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meses'] = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

        id_usuario = self.request.user.id
        try:
            cursor = connection_portalaei.cursor()
            # 🔹 CAMPAÑAS
            cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM CAMPANIA")
            campanias = []
            for row in cursor.fetchall():
                # tratar de extraer un año de la descripción, ej: "CAMPAÑA 2024"
                match = re.search(r'(\d{4})', row[1])
                anio = int(match.group(1)) if match else None
                campanias.append({
                    'id': row[0],
                    'descripcion': row[1],
                    'anio': anio
                })
            context['campanias'] = campanias

            # 🔹 Campaña actual según el año del sistema
            anio_actual = date.today().year
            campania_actual = next(
                (c for c in campanias if c['anio'] == anio_actual),
                None
            )
            context['campania_actual'] = campania_actual
            context['anio_actual'] = anio_actual
            cursor.execute(
                """
                SELECT f.ID_FUNDO,
                       f.DESCRIPCION,
                       f.ID_EMPRESA,
                       COUNT(a.ID_ASIGNACION) AS TOTAL_LOTES
                FROM FUNDO f
                         LEFT JOIN LOTE l ON f.ID_FUNDO = l.ID_FUNDO
                         LEFT JOIN ASIGNACION_LOTE a
                                   ON l.ID_LOTE = a.ID_LOTE
                                       AND a.ID_RESPONSABLE = ?
                                       AND a.ID_CAMPANIA = ?
                GROUP BY f.ID_FUNDO, f.DESCRIPCION, f.ID_EMPRESA
                ORDER BY f.DESCRIPCION;
                """, [id_usuario, 'CAMP'+str(campania_actual)]
            )
            fundos = [
                {
                    'id': row[0],
                    'nombre': row[1],
                    'ID_EMPRESA': row[2],
                    'TOTAL_LOTES': row[3]
                }
                for row in cursor.fetchall()
            ]
            context['fundos'] = fundos
            cursor.close()
        except Exception as e:
            context['fundos'] = []
            context['campanias'] = []
            context['campania_actual'] = None
            context['error'] = str(e)

        return context

class ProdFundosPorUsuarioCampaniaAPI(View):
    def get(self, request):
        try:
            id_usuario = request.user.id
            id_campania = request.GET.get("campania")

            # Si no mandan campaña, usar la actual
            if not id_campania:
                from datetime import date
                id_campania = f"CAMP{date.today().year}"

            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT 
                    f.ID_FUNDO,
                       f.DESCRIPCION,
                       f.ID_EMPRESA,
                       COUNT(a.ID_ASIGNACION) AS TOTAL_LOTES
                FROM FUNDO f
                LEFT JOIN LOTE l ON f.ID_FUNDO = l.ID_FUNDO
                LEFT JOIN ASIGNACION_LOTE a
                       ON l.ID_LOTE = a.ID_LOTE
                      AND a.ID_RESPONSABLE = ?
                      AND a.ID_CAMPANIA = ?
                GROUP BY f.ID_FUNDO, f.DESCRIPCION, f.ID_EMPRESA
                ORDER BY f.DESCRIPCION;
            """, [id_usuario, id_campania])

            fundos = [
                {
                    'ID_FUNDO': row[0],
                    'DESCRIPCION': row[1],
                    'ID_EMPRESA': row[2],
                    'TOTAL_LOTES': row[3]
                }
                for row in cursor.fetchall()
            ]
            cursor.close()

            return JsonResponse({'status': 'success', 'data': fundos})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


#Nuevo guardar produccion
@method_decorator(csrf_exempt, name='dispatch')
class GuardarProduccionNuevo(View):
    def post(self, request, *args, **kwargs):
        try:
            # === Parsear JSON ===
            data = json.loads(request.body)

            lote_data = data.get("lote", {})
            mapeo_data = data.get("mapeo", {})
            prod_data = data.get("prod_uva", {})

            area_lote = float(lote_data.get("area_lote") or 0)

            # === Variables de entrada ===
            hilera = float(mapeo_data.get("hilera") or 0)
            planta = float(mapeo_data.get("planta") or 0)
            id_asignacion = float(mapeo_data.get("id_asignacion") or 0)


            rac_planta = int(prod_data.get("rac_planta") or 0)
            rac_packing = int(prod_data.get("rac_packing") or 0)
            peso_rac = float(prod_data.get("peso_rac") or 0)
            rendimiento_pct = float(prod_data.get("rendimiento") or 0)
            rendimiento = rendimiento_pct / 100  # convertir a decimal
            rac_nacional = rac_planta - rac_packing
            cajas_por_lote_config = int(prod_data.get("caj_lote") or 1700)

            # === Cálculos base ===
            densidad = float(mapeo_data.get("densidad") or 0)
            total_plantas = float(mapeo_data.get("totalPlantas") or 0)
            area_productiva = float(mapeo_data.get("areaProductiva") or 0)

            # === Proyecciones ===
            rac_lote = round(area_productiva * densidad * rac_planta, 2)
            kg_proy_lote = round(densidad * rac_packing * peso_rac * area_productiva,0)
            kg_expor_lote = round(kg_proy_lote * rendimiento,0)
            kg_desc_campo_lote = round(area_productiva * rac_nacional * peso_rac * densidad,0)
            kg_desc_proc_lote = round((1 - rendimiento) * kg_proy_lote, 0)

            # === Por hectárea ===
            kg_proy_ha =  round(kg_proy_lote / area_productiva if area_productiva > 0 else 0,2)
            kg_expor_ha =  round(kg_expor_lote / area_productiva if area_productiva > 0 else 0,2)
            kg_desc_campo_ha =  round(kg_desc_campo_lote / area_productiva if area_productiva > 0 else 0, 2)
            kg_desc_proc_ha =  round(kg_desc_proc_lote / area_productiva if area_productiva > 0 else 0, 2)

            # === Cajas y cantidad ===
            caj_lote =  round(kg_expor_lote / 8.2 if kg_expor_lote > 0 else 0, 2)
            caj_ha =  round(caj_lote / area_productiva if area_productiva > 0 else 0, 2)
            cantidad =  round(caj_lote / cajas_por_lote_config if cajas_por_lote_config > 0 else 0, 2)

            env_fru_pack =  round(kg_proy_ha * 0.99, 2)
            total_kg_env =  round(env_fru_pack * area_productiva,2)

            # === Guardar en BD con transacción ===
            with transaction.atomic():
                with connection_portalaei.cursor() as cursor:
                    # Verificar si ya existe un mapeo
                    cursor.execute("SELECT TOP 1 ID_ASIGNACION FROM PROD_UVA WHERE ID_ASIGNACION = ?", [id_asignacion])
                    row = cursor.fetchone()

                    if row:
                        # === Ya existe → UPDATE ===
                        id_mapeo = row[0]
                        cursor.execute("""
                                       UPDATE PROD_UVA
                                       SET RENDIMIENTO       = ?,
                                           RAC_PLANTA        = ?,
                                           RAC_PACKING       = ?,
                                           RAC_NACIONAL      = ?,
                                           PESO_RAC          = ?,
                                           RAC_LOTE          = ?,
                                           KG_PROYEC_LOTE    = ?,
                                           KG_EXPOR_LOTE     = ?,
                                           KG_DESC_CAMP_LOTE = ?,
                                           KG_DESC_PROC_LOTE = ?,
                                           KG_PROYEC_HA      = ?,
                                           KG_EXPOR_HA       = ?,
                                           KG_DESC_CAMP_HA   = ?,
                                           KG_DESC_PROC_HA   = ?,
                                           CAJ_LOTE          = ?,
                                           CAJ_HA            = ?,
                                           CANT              = ?,
                                           porc              = ?,
                                           ENV_FRU_PACK      = ?,
                                           TOTAL_KG_ENV      = ?,
                                           CAJAS             = ?,
                                           ID_ASIGNACION     = ?
                                       WHERE ID_ASIGNACION = ?
                                       """, [
                                           rendimiento_pct,
                                           rac_planta, rac_packing, rac_nacional,
                                           peso_rac, rac_lote,
                                           kg_proy_lote, kg_expor_lote, kg_desc_campo_lote, kg_desc_proc_lote,
                                           kg_proy_ha, kg_expor_ha, kg_desc_campo_ha, kg_desc_proc_ha,
                                           caj_lote, caj_ha, cantidad, 0 , env_fru_pack, total_kg_env ,cajas_por_lote_config, id_asignacion, id_asignacion
                                       ])
                    else:
                         # Insert en PROD_UVA (usa el ID_MAPEO recién creado)
                        cursor.execute("""
                                       INSERT INTO prod_uva (rendimiento, rac_planta, rac_packing, rac_nacional,
                                                             peso_rac, rac_lote,
                                                             kg_proyec_lote, kg_expor_lote, kg_desc_camp_lote,
                                                             kg_desc_proc_lote,
                                                             kg_proyec_ha, kg_expor_ha, kg_desc_camp_ha, kg_desc_proc_ha,
                                                             caj_lote, caj_ha, cant, porc, ENV_FRU_PACK, TOTAL_KG_ENV, CAJAS, ID_ASIGNACION)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                                       """, [
                                           rendimiento_pct,
                                           rac_planta,
                                           rac_packing,
                                           rac_nacional,
                                           peso_rac,
                                           rac_lote,
                                           kg_proy_lote,
                                           kg_expor_lote,
                                           kg_desc_campo_lote,
                                           kg_desc_proc_lote,
                                           kg_proy_ha,
                                           kg_expor_ha,
                                           kg_desc_campo_ha,
                                           kg_desc_proc_ha,
                                           caj_lote,
                                           caj_ha,
                                           cantidad, 0, env_fru_pack, total_kg_env,
                                            cajas_por_lote_config, id_asignacion
                                       ])

            return JsonResponse({"ok": True, "id_asignacion": id_asignacion})

        except Exception as e:
            # rollback automático por transaction.atomic
            return JsonResponse({"ok": False, "error": str(e)}, status=400)

    def get(self, request, *args, **kwargs):
        try:
            id_asignacion = request.GET.get("id_asignacion")
            if not id_asignacion:
                return JsonResponse({"ok": False, "error": "id_asignacion es requerido"}, status=400)

            data = {}



            # 🔹 1. VALIDAR SI EXISTE MAPEO
            with connection_portalaei.cursor() as cursor:
                cursor.execute("""
                               select
                                     m.ID_MAPEO, m.FECHA,
                                                                      m.ID_ASIGNACION,
                                                                      m.HILERA,
                                                                      m.PLANTA,
                                                                      m.DENSIDAD,
                                                                      m.AREA_PRODUCTIVA,
                                                                      m.TOTAL_PLANTAS,
                                                                      m.OBSERVACION,
                                                                      md.CANTIDAD as PLANTAS_PRODUCTIVAS
                                from MAPEO m
                                join MAPEO_DETALLE md on m.ID_MAPEO = md.ID_MAPEO AND md.ID_TPPLANTA = 2
                                where m.ID_ASIGNACION = ?
                               """, [id_asignacion])

                row = cursor.fetchone()
                if not row:
                    # Si no hay mapeo, no se permite continuar
                    return JsonResponse({
                        "ok": False,
                        "found": False,
                        "message": "No existe registro de Mapeo para esta asignación. Debe completarse antes de ingresar Producción."
                    }, status=404)

                # Convertir resultado de mapeo en dict
                columns = [col[0] for col in cursor.description]
                data["mapeo"] = dict(zip(columns, row))

            # 🔹 2. SI EXISTE MAPEO, BUSCAMOS PRODUCCIÓN
            with connection_portalaei.cursor() as cursor:
                cursor.execute("""
                               SELECT TOP 1
                                ID_PRODUVA, RENDIMIENTO,
                                      RAC_PLANTA,
                                      RAC_LOTE,
                                      RAC_PACKING,
                                      RAC_NACIONAL,
                                      PESO_RAC,
                                      KG_PROYEC_LOTE,
                                      KG_EXPOR_LOTE,
                                      KG_DESC_CAMP_LOTE,
                                      KG_DESC_PROC_LOTE,
                                      KG_PROYEC_HA,
                                      KG_EXPOR_HA,
                                      KG_DESC_CAMP_HA,
                                      KG_DESC_PROC_HA,
                                      CAJ_LOTE,
                                      CAJ_HA,
                                      CANT,
                                      PORC,
                                      ENV_FRU_PACK,
                                      TOTAL_KG_ENV,
                                      CAJAS,
                                      ID_DETALLE,
                                      ID_ASIGNACION
                               FROM PROD_UVA
                               WHERE ID_ASIGNACION = ?
                               """, [id_asignacion])

                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data["produccion"] = dict(zip(columns, row))
                else:
                    data["produccion"] = None

            # 🔹 3. RESPUESTA FINAL
            return JsonResponse({"ok": True, "found": True, "data": data}, status=200)

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)

def get_produccion_campania(request):
    id_campania = request.GET.get("id_campania")
    # id_usuario = request.GET.get("id_usuario")
    id_usuario = request.user.id

    if not id_campania:
        return JsonResponse({"error": "Debe indicar id_campania"}, status=400)

    query = """
            SELECT *
            FROM dbo.VW_PRODUCCION_CAMPANIA
            WHERE ID_CAMPANIA = ? \
            """
    params = [id_campania]

    if id_usuario:
        query += " AND ID_USUARIO = ?"
        params.append(id_usuario)

    try:
        with connection_portalaei.cursor() as cursor:
            cursor.execute(query, params)
            if not cursor.description:
                return JsonResponse({"data": []})
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse({"data": data}, status=200)

    except Exception as e:
        import traceback
        return JsonResponse({
            "error": str(e),
            "trace": traceback.format_exc().splitlines()[-5:]
        }, status=500)
