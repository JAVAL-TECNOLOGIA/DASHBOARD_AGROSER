# views.py
import json
from datetime import datetime
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei
from apps.utils.permissions import es_admin
from django.http import JsonResponse

class mapeo(TemplateView):
    template_name = 'PresupuestoAgricola/mapeo.html'

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
                                   ON l.ID_LOTE = a.ID_LOTE  AND a.ID_CAMPANIA = ?
                GROUP BY f.ID_FUNDO, f.DESCRIPCION, f.ID_EMPRESA
                ORDER BY f.DESCRIPCION;
                """,
                ['CAMP' + str(anio_actual)]
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
# ENDPOINT: Listar tipos de planta para mapeo
# ===============================
@csrf_exempt
def tipo_planta_list(request):
    if request.method == 'GET':
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_PLANTA, DESCRIPCION FROM TIPO_PLANTA")
            data = [
                {'ID_PLANTA': row[0], 'DESCRIPCION': row[1]}
                for row in cursor.fetchall()
            ]
            cursor.close()
            return JsonResponse({'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ===============================
# MAPEO DE PLANTAS POR LOTE (CRUD masivo)
# ===============================
@method_decorator(csrf_exempt, name='dispatch')
class MapeoCRUDView2(View):
    def get(self, request, *args, **kwargs):
        import traceback
        try:
            lote_id = request.GET.get('ID_LOTE')
            if not lote_id:
                return JsonResponse({'status': 'error', 'message': 'ID_LOTE requerido'}, status=400)
            cursor = connection_portalaei.cursor()
            try:
                cursor.execute("""
                    SELECT ID_MAPEO, FECHA, ID_ASIGNACION, HILERA, PLANTA, DENSIDAD, AREA_PRODUCTIVA, TOTAL_PLANTAS, OBSERVACION
                    FROM MAPEO
                    WHERE ID_ASIGNACION IN (
                        SELECT ID_ASIGNACION FROM ASIGNACION_LOTE WHERE ID_LOTE = ?
                    )
                """, [lote_id])
                data = [
                    {
                        'ID_MAPEO': row[0],
                        'FECHA': row[1],
                        'ID_ASIGNACION': row[2],
                        'HILERA': row[3],
                        'PLANTA': row[4],
                        'DENSIDAD': row[5],
                        'PLANTA_PRODUCTIVA': row[6],
                        'PLANTA_FORMACION': row[7],
                        'PLANTA_ENFERMA': row[8],
                        'PLANTA_CORDON': row[9],
                        'PLANTA_MUERTAS': row[10],
                        'PLANTA_AUSENTE': row[11],
                        'PLANTA_OTRA_VARIEDAD': row[12],
                        'PLANTA_NO_PRODUCTIVAS': row[13],
                        'AREA_PRODUCTIVA': row[14],
                        'TOTAL_PLANTAS': row[15],
                        'CANTIDAD': row[16],
                        'PORCENTAJE': row[17]
                    }
                    for row in cursor.fetchall()
                ]
                cursor.close()
                return JsonResponse({'data': data})
            except Exception as db_exc:
                tb = traceback.format_exc()
                cursor.close()
                return JsonResponse({'status': 'error', 'message': str(db_exc), 'traceback': tb}, status=500)
        except Exception as e:
            tb = traceback.format_exc()
            return JsonResponse({'status': 'error', 'message': str(e), 'traceback': tb}, status=500)
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            lote_id = data.get('lote')
            mapeos = data.get('mapeos', [])
            if not lote_id:
                return JsonResponse({'status': 'error', 'message': 'ID_LOTE requerido'}, status=400)
            cursor = connection_portalaei.cursor()
            cursor.execute("DELETE FROM MAPEO WHERE ID_LOTE = ?", [lote_id])
            for m in mapeos:
                cursor.execute(
                    """
                    INSERT INTO MAPEO (
                        FECHA, ID_ASIGNACION, HILERA, PLANTA, DENSIDAD, PLANTA_PRODUCTIVA, PLANTA_FORMACION, PLANTA_ENFERMA, PLANTA_CORDON, PLANTA_MUERTAS, PLANTA_AUSENTE, PLANTA_OTRA_VARIEDAD, PLANTA_NO_PRODUCTIVAS, AREA_PRODUCTIVA, TOTAL_PLANTAS, CANTIDAD, PORCENTAJE, ID_LOTE
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        m.get('FECHA'),
                        m.get('ID_ASIGNACION'),
                        m.get('HILERA'),
                        m.get('PLANTA'),
                        m.get('DENSIDAD'),
                        m.get('PLANTA_PRODUCTIVA'),
                        m.get('PLANTA_FORMACION'),
                        m.get('PLANTA_ENFERMA'),
                        m.get('PLANTA_CORDON'),
                        m.get('PLANTA_MUERTAS'),
                        m.get('PLANTA_AUSENTE'),
                        m.get('PLANTA_OTRA_VARIEDAD'),
                        m.get('PLANTA_NO_PRODUCTIVAS'),
                        m.get('AREA_PRODUCTIVA'),
                        m.get('TOTAL_PLANTAS'),
                        m.get('CANTIDAD'),
                        m.get('PORCENTAJE'),
                        lote_id
                    ]
                )
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Mapeo guardado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ===============================
# ENDPOINT: Obtener todos los datos de la tabla MAPEO
# ===============================
@csrf_exempt
def mapeo_todo_api(request):
    if request.method == 'GET':
        try:
            id_campania = request.GET.get("campania")

            if not id_campania:
                from datetime import date
                id_campania = f"CAMP{date.today().year}"

            anio_campania = id_campania.replace("CAMP", "")

            try:
                anio_campania = int(anio_campania)
            except:
                anio_campania = date.today().year



            cursor = connection_portalaei.cursor()

            cursor.execute("""
                SELECT 
                    ID_MAPEO,
                    FECHA,
                    ID_ASIGNACION,
                    HILERA,
                    PLANTA,
                    DENSIDAD,
                    AREA_PRODUCTIVA,
                    TOTAL_PLANTAS,
                    OBSERVACION
                FROM MAPEO
                WHERE YEAR(FECHA) = ?
                ORDER BY FECHA DESC;
            """, [anio_campania])

            rows = cursor.fetchall()
            print(f"Registros encontrados: {len(rows)}")

            data = []
            for row in rows:
                fecha = row[1]
                if hasattr(fecha, 'strftime'):
                    fecha = fecha.strftime('%Y-%m-%d')
                elif fecha:
                    fecha = str(fecha)

                data.append({
                    'ID_MAPEO': row[0],
                    'FECHA': fecha,
                    'ID_ASIGNACION': row[2],
                    'HILERA': row[3],
                    'PLANTA': row[4],
                    'DENSIDAD': row[5],
                    'AREA_PRODUCTIVA': row[6],
                    'TOTAL_PLANTAS': row[7],
                    'OBSERVACION': row[8] or ''
                })
            cursor.close()

            print(f"Total registros devueltos al frontend: {len(data)}")

            return JsonResponse({
                'data': data,
                'debug': {
                    'campania': id_campania,
                    'anio_filtrado': anio_campania,
                    'total_registros': len(data)
                }
            })
        except Exception as e:
            print(f"ERROR en mapeo_todo_api: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#Nuevo guardar mapeo
@method_decorator(csrf_exempt, name='dispatch')
class GuardarMapeoNuevo(View):
    def post(self, request, *args, **kwargs):
        try:
            # === Parsear JSON ===
            data = json.loads(request.body)

            lote_data = data.get("lote", {})
            id_lote = lote_data.get("id_lote")
            area_lote = float(lote_data.get("area_lote") or 0)

            mapeo_data = data.get("mapeo", {})
            prod_data = data.get("prod_uva", {})
            plantas = mapeo_data.get("plantas", {})

            # === Variables de entrada ===
            hilera = float(mapeo_data.get("hilera") or 0)
            planta = float(mapeo_data.get("planta") or 0)
            id_asignacion = float(mapeo_data.get("id_asignacion") or 0)

            fecha_str = mapeo_data.get("fecha")  # viene del JSON, tipo string
            fecha = None
            if fecha_str:
                try:
                    # si viene como "2025-10-05"
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                except ValueError:
                    # si viene con hora: "2025-10-05 14:30:00"
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")

            rac_planta = int(prod_data.get("rac_planta") or 0)
            rac_packing = int(prod_data.get("rac_packing") or 0)
            peso_rac = round(float(prod_data.get("peso_rac") or 0),2)
            rendimiento_pct = round(float(prod_data.get("rendimiento") or 0),2)
            rendimiento = round(rendimiento_pct / 100,2)  # convertir a decimal
            rac_nacional = rac_planta - rac_packing
            cajas_por_lote_config = int(prod_data.get("caj_lote") or 1700)

            # === Cálculos base ===
            densidad = round(10000 / (hilera * planta) if hilera > 0 and planta > 0 else 0,2)
            total_plantas = sum(plantas.values())
            area_productiva = round(plantas.get("productiva", 0) / densidad if densidad > 0 else 0,2)

            # === Proyecciones ===
            rac_lote = round(area_lote * densidad * rac_planta,2)
            kg_proy_lote = round(densidad * rac_packing * peso_rac * area_lote,2)
            kg_expor_lote = round(kg_proy_lote * rendimiento,2)
            kg_desc_campo_lote = round(area_lote * rac_nacional * peso_rac * densidad,2)
            kg_desc_proc_lote = round((1 - rendimiento) * kg_proy_lote,2)

            # === Por hectárea ===
            kg_proy_ha = round(kg_proy_lote / area_lote if area_lote > 0 else 0,2)
            kg_expor_ha = round(kg_expor_lote / area_lote if area_lote > 0 else 0,2)
            kg_desc_campo_ha = round(kg_desc_campo_lote / area_lote if area_lote > 0 else 0,2)
            kg_desc_proc_ha = round(kg_desc_proc_lote / area_lote if area_lote > 0 else 0,2)

            # === Cajas y cantidad ===
            caj_lote = round(kg_expor_lote / 8.2 if kg_expor_lote > 0 else 0,2)
            caj_ha = round(caj_lote / area_lote if area_lote > 0 else 0,2)
            cantidad = round(caj_lote / cajas_por_lote_config if cajas_por_lote_config > 0 else 0,2)

            # === Guardar en BD con transacción ===
            with transaction.atomic():
                with connection_portalaei.cursor() as cursor:
                    # Verificar si ya existe un mapeo
                    cursor.execute("SELECT TOP 1 ID_MAPEO FROM MAPEO WHERE ID_ASIGNACION = ?", [id_asignacion])
                    row = cursor.fetchone()

                    if row:
                        # === Ya existe → UPDATE ===
                        id_mapeo = row[0]

                        cursor.execute("""
                                       UPDATE MAPEO
                                       SET FECHA                 = ?,
                                           HILERA                = ?,
                                           PLANTA                = ?,
                                           DENSIDAD              = ?,
                                           PLANTA_PRODUCTIVA     = ?,
                                           PLANTA_FORMACION      = ?,
                                           PLANTA_MUERTAS        = ?,
                                           PLANTA_AUSENTE        = ?,
                                           PLANTA_ENFERMA        = ?,
                                           PLANTA_CORDON         = ?,
                                           PLANTA_OTRA_VARIEDAD  = ?,
                                           PLANTA_NO_PRODUCTIVAS = ?,
                                           TOTAL_PLANTAS         = ?,
                                           AREA_PRODUCTIVA       = ?
                                       WHERE ID_MAPEO = ?
                                       """, [
                                           fecha, hilera, planta, densidad,
                                           plantas.get("productiva", 0),
                                           plantas.get("formacion", 0),
                                           plantas.get("muertas", 0),
                                           plantas.get("ausentes", 0),
                                           plantas.get("enferma", 0),
                                           plantas.get("cordon", 0),
                                           plantas.get("moscatel_roja", 0),
                                           plantas.get("moscatel_negra", 0),
                                           total_plantas, area_productiva,
                                           id_mapeo
                                       ])
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
                                           CAJAS             = ?
                                       WHERE ID_MAPEO = ?
                                       """, [
                                           int(rendimiento_pct),
                                           rac_planta, rac_packing, rac_nacional,
                                           peso_rac, rac_lote,
                                           kg_proy_lote, kg_expor_lote, kg_desc_campo_lote, kg_desc_proc_lote,
                                           kg_proy_ha, kg_expor_ha, kg_desc_campo_ha, kg_desc_proc_ha,
                                           caj_lote, caj_ha, cantidad, 0 , 0, 0 ,cajas_por_lote_config, id_mapeo
                                       ])
                    else:
                        # === No existe → INSERT ===
                        cursor.execute("""
                                       INSERT INTO mapeo (id_asignacion, fecha, hilera, planta, densidad,
                                                          planta_productiva, planta_formacion, planta_muertas,
                                                          planta_ausente, planta_enferma,
                                                          planta_cordon, planta_otra_variedad, planta_no_productivas,
                                                          total_plantas, area_productiva)
                                            OUTPUT INSERTED.ID_MAPEO
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                                       """, [
                                                id_asignacion, fecha, hilera, planta, densidad,
                                                plantas.get("productiva", 0),
                                                plantas.get("formacion", 0),
                                                plantas.get("muertas", 0),
                                                plantas.get("ausentes", 0),
                                                plantas.get("enferma", 0),
                                                plantas.get("cordon", 0),
                                                plantas.get("moscatel_roja", 0),
                                                plantas.get("moscatel_negra", 0),
                                                total_plantas, area_productiva
                                        ])

                        # Ahora recuperamos el último ID_MAPEO
                        # cursor.execute("SELECT SCOPE_IDENTITY();")
                        id_mapeo = cursor.fetchone()[0]

                        # Insert en PROD_UVA (usa el ID_MAPEO recién creado)
                        cursor.execute("""
                                       INSERT INTO prod_uva (id_mapeo, rendimiento, rac_planta, rac_packing, rac_nacional,
                                                             peso_rac, rac_lote,
                                                             kg_proyec_lote, kg_expor_lote, kg_desc_camp_lote,
                                                             kg_desc_proc_lote,
                                                             kg_proyec_ha, kg_expor_ha, kg_desc_camp_ha, kg_desc_proc_ha,
                                                             caj_lote, caj_ha, cant, porc, ENV_FRU_PACK, TOTAL_KG_ENV, CAJAS)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                                       """, [
                                           id_mapeo,
                                           int(rendimiento_pct),
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
                                           cantidad, 0, 0, 0,
                                            cajas_por_lote_config
                                       ])

            return JsonResponse({"ok": True, "id_mapeo": id_mapeo})

        except Exception as e:
            # rollback automático por transaction.atomic
            return JsonResponse({"ok": False, "error": str(e)}, status=400)

    def get(self, request, *args, **kwargs):
        try:
            id_asignacion = request.GET.get("id_asignacion")
            if not id_asignacion:
                return JsonResponse({"ok": False, "error": "id_asignacion es requerido"}, status=400)

            with connection_portalaei.cursor() as cursor:
                # Buscamos si ya existe un registro de MAPEO con esa asignación
                cursor.execute("""
                               SELECT TOP 1
                        m.ID_MAPEO, m.FECHA,
                                      m.HILERA,
                                      m.PLANTA,
                                      m.DENSIDAD,
                                      m.PLANTA_PRODUCTIVA,
                                      m.PLANTA_FORMACION,
                                      m.PLANTA_MUERTAS,
                                      m.PLANTA_AUSENTE,
                                      m.PLANTA_ENFERMA,
                                      m.PLANTA_CORDON,
                                      m.PLANTA_OTRA_VARIEDAD,
                                      m.PLANTA_NO_PRODUCTIVAS,
                                      m.TOTAL_PLANTAS,
                                      m.AREA_PRODUCTIVA,
                                      p.RENDIMIENTO,
                                      p.RAC_PLANTA,
                                      p.RAC_PACKING,
                                      p.RAC_NACIONAL,
                                      p.PESO_RAC,
                                      p.RAC_LOTE,
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
                                        p.CAJAS
                               FROM MAPEO m
                                        INNER JOIN PROD_UVA p ON m.ID_MAPEO = p.ID_MAPEO
                               WHERE m.ID_ASIGNACION = ?
                               ORDER BY m.ID_MAPEO DESC
                               """, [id_asignacion])

                row = cursor.fetchone()
                if not row:
                    return JsonResponse({"ok": False, "found": False, "message": "No existe mapeo registrado."})

                # Convertir resultado en dict
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, row))

            return JsonResponse({"ok": True, "found": True, "data": data}, status=200)

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class CampaniasListView(View):
    def get(self, request):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_CAMPANIA, DESCRIPCION FROM [PORTAL_AEI].[dbo].[CAMPANIA]")
            campanias = []
            for row in cursor.fetchall():
                campanias.append({
                    'ID_CAMPANIA': row[0],
                    'DESCRIPCION': row[1]
                })
            cursor.close()
            return JsonResponse({'status': 'success', 'data': campanias})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class FundosPorUsuarioCampaniaAPI(View):
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
                      AND a.ID_CAMPANIA = ?
                GROUP BY f.ID_FUNDO, f.DESCRIPCION, f.ID_EMPRESA
                ORDER BY f.DESCRIPCION;
            """, [id_campania])

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

@csrf_exempt
def tipo_planta_list(request):
    if request.method == 'GET':
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_TPPLANTA, NOM_CORTO, DESCRIPCION FROM TIPO_PLANTA")
            data = [
                {'ID_TPPLANTA': row[0], 'NOM_CORTO': row[1], 'DESCRIPCION': row[2]}
                for row in cursor.fetchall()
            ]
            cursor.close()
            return JsonResponse({'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MapeoCRUDView(View):
    def get(self, request, *args, **kwargs):
        try:
            asignacion_id = request.GET.get('ID_ASIGNACION')
            if not asignacion_id:
                return JsonResponse({'status': 'error', 'message': 'ID_ASIGNACION requerido'}, status=400)

            with connection_portalaei.cursor() as cursor:
                # 🔹 Buscar el mapeo principal
                cursor.execute("""
                               SELECT ID_MAPEO,
                                      FECHA,
                                      ID_ASIGNACION,
                                      HILERA,
                                      PLANTA,
                                      DENSIDAD,
                                      AREA_PRODUCTIVA,
                                      TOTAL_PLANTAS,
                                      OBSERVACION
                               FROM MAPEO
                               WHERE ID_ASIGNACION = ?
                               """, [asignacion_id])
                mapeo_row = cursor.fetchone()

                if mapeo_row:
                    # 🔸 Si existe, convertir a dict
                    mapeo = {
                        'ID_MAPEO': mapeo_row[0],
                        'FECHA': mapeo_row[1],
                        'ID_ASIGNACION': mapeo_row[2],
                        'HILERA': float(mapeo_row[3]) if mapeo_row[3] else None,
                        'PLANTA': float(mapeo_row[4]) if mapeo_row[4] else None,
                        'DENSIDAD': float(mapeo_row[5]) if mapeo_row[5] else None,
                        'AREA_PRODUCTIVA': float(mapeo_row[6]) if mapeo_row[6] else None,
                        'TOTAL_PLANTAS': int(mapeo_row[7]) if mapeo_row[7] else None,
                        'OBSERVACION': mapeo_row[8],
                    }

                    # 🔹 Buscar detalles del mapeo
                    cursor.execute("""
                                   SELECT D.ID_DETALLE,
                                          D.ID_TPPLANTA,
                                          T.DESCRIPCION AS TIPO_PLANTA,
                                          D.CANTIDAD,
                                          D.PORCENTAJE
                                   FROM MAPEO_DETALLE AS D
                                            LEFT JOIN TIPO_PLANTA AS T ON D.ID_TPPLANTA = T.ID_TPPLANTA
                                   WHERE D.ID_MAPEO = ?
                                   ORDER BY D.ID_DETALLE
                                   """, [mapeo['ID_MAPEO']])

                    detalles_rows = cursor.fetchall()
                    detalles = [
                        {
                            'ID_DETALLE': row[0],
                            'ID_TPPLANTA': row[1],
                            'TIPO_PLANTA': row[2],
                            'CANTIDAD': int(row[3]) if row[3] else 0,
                            'PORCENTAJE': float(row[4]) if row[4] else 0.0
                        }
                        for row in detalles_rows
                    ]

                else:
                    # 🔸 No existe mapeo → permitir creación (estructura vacía)
                    mapeo = {
                        'ID_MAPEO': None,
                        'FECHA': None,
                        'ID_ASIGNACION': int(asignacion_id),
                        'HILERA': None,
                        'PLANTA': None,
                        'DENSIDAD': None,
                        'AREA_PRODUCTIVA': None,
                        'TOTAL_PLANTAS': None,
                        'OBSERVACION': None
                    }
                    detalles = []

            # 🔹 Respuesta final (sea nuevo o existente)
            return JsonResponse({
                'status': 'success',
                'found': bool(mapeo_row),
                'mapeo': mapeo,
                'detalles': detalles
            }, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            mapeo_data = data.get("mapeo", {})
            detalles = data.get("detalles", [])

            id_asignacion = int(mapeo_data.get("ID_ASIGNACION"))
            hilera = float(mapeo_data.get("HILERA") or 0)
            planta = float(mapeo_data.get("PLANTA") or 0)
            densidad = float(mapeo_data.get("DENSIDAD") or 0)
            area_productiva = float(mapeo_data.get("AREA_PRODUCTIVA") or 0)
            total_plantas = int(mapeo_data.get("TOTAL_PLANTAS") or 0)
            observacion = mapeo_data.get("OBSERVACION") or None
            # total_cantidad = sum(float(item.get("CANTIDAD", 0)) for item in detalles)

            with transaction.atomic():
                with connection_portalaei.cursor() as cursor:
                    # 🔹 Verificar si ya existe un mapeo
                    cursor.execute("SELECT TOP 1 ID_MAPEO FROM MAPEO WHERE ID_ASIGNACION = ?", [id_asignacion])
                    row = cursor.fetchone()

                    if row:
                        id_mapeo = row[0]
                        # 🔸 Actualizar mapeo
                        cursor.execute("""
                                       UPDATE MAPEO
                                       SET HILERA          = ?,
                                           PLANTA          = ?,
                                           DENSIDAD        = ?,
                                           AREA_PRODUCTIVA = ?,
                                           TOTAL_PLANTAS   = ?,
                                           OBSERVACION     = ?
                                       WHERE ID_MAPEO = ?
                                       """, [hilera, planta, densidad, area_productiva, total_plantas, observacion,
                                             id_mapeo])

                        # 🔸 Limpiar detalles anteriores
                        cursor.execute("DELETE FROM MAPEO_DETALLE WHERE ID_MAPEO = ?", [id_mapeo])
                    else:
                        # 🔸 Insertar nuevo mapeo
                        cursor.execute("""
                                       INSERT INTO MAPEO (FECHA, ID_ASIGNACION, HILERA, PLANTA, DENSIDAD,
                                                          AREA_PRODUCTIVA, TOTAL_PLANTAS, OBSERVACION)
                                           OUTPUT INSERTED.ID_MAPEO
                                       VALUES (GETDATE(), ?, ?, ?, ?, ?, ?, ?)
                                       """, [id_asignacion, hilera, planta, densidad, area_productiva, total_plantas,
                                             observacion])
                        id_mapeo = cursor.fetchone()[0]

                    # 🔹 Insertar detalles
                    for det in detalles:
                        id_tpplanta = float(det.get("ID_TPPLANTA"))
                        cantidad = float(det.get("CANTIDAD") or 0)
                        porcentaje = float(det.get("PORCENTAJE") or 0)

                        cursor.execute("""
                                       INSERT INTO MAPEO_DETALLE (ID_MAPEO, ID_TPPLANTA, CANTIDAD, PORCENTAJE)
                                       VALUES (?, ?, ?, ?)
                                       """, [id_mapeo, id_tpplanta, cantidad, porcentaje])

            return JsonResponse({"ok": True, "id_mapeo": id_mapeo}, status=200)
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def get_mapeo_resumen_campania(request):
    id_campania = request.GET.get("id_campania")
    if not id_campania:
        return JsonResponse({"error": "Debe enviar id_campania"}, status=400)

    try:
        with connection_portalaei.cursor() as cursor:
            cursor.execute(f"EXEC SP_MAPEO_RESUMEN_CAMPANIA '{id_campania}'")
            # cursor.execute("EXEC SP_MAPEO_RESUMEN_CAMPANIA %s", [id_campania])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in rows]
        return JsonResponse({"data": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)