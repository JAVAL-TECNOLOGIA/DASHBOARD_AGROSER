# views.py
import json
import threading
import pyodbc
from datetime import datetime, date, timedelta
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.http import HttpResponse

import apps.connection.connect_portalaei as portalaei_db
from apps.utils.permissions import es_admin
from django.http import JsonResponse
import traceback 


connection_portalaei = getattr(portalaei_db, 'connection_portalaei', None)
_portalaei_reconnect_lock = threading.Lock()


def _close_portalaei_connection(connection):
    if connection is None:
        return

    try:
        connection.close()
    except Exception:
        pass


def _connection_is_alive(connection):
    if connection is None:
        return False

    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        return True
    except pyodbc.Error:
        return False
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass


def _reconnect_portalaei(stale_connection=None):
    """Recrea la conexión compartida a PORTAL_AEI de forma segura."""
    global connection_portalaei

    with _portalaei_reconnect_lock:
        # Otro request pudo haber recuperado la conexión mientras esperaba el lock.
        if stale_connection is None and _connection_is_alive(connection_portalaei):
            return connection_portalaei

        if (
            stale_connection is not None
            and connection_portalaei is not stale_connection
            and _connection_is_alive(connection_portalaei)
        ):
            return connection_portalaei

        previous_connection = connection_portalaei
        _close_portalaei_connection(previous_connection)
        connection_portalaei = None
        portalaei_db.connection_portalaei = None

        new_connection = pyodbc.connect(
            portalaei_db.build_pyodbc_connection_string(
                portalaei_db.host,
                portalaei_db.name,
                portalaei_db.user,
                portalaei_db.password,
                mars=True
            )
        )

        # Mantener actualizada la referencia del módulo de conexión para los
        # consumidores que accedan a ella después de la reconexión.
        connection_portalaei = new_connection
        portalaei_db.connection_portalaei = connection_portalaei
        return connection_portalaei


def _get_portalaei_cursor(ensure_alive=True):
    """Obtiene un cursor y recupera la conexión si dejó de responder."""
    connection = connection_portalaei

    if connection is None:
        connection = _reconnect_portalaei()
    elif ensure_alive and not _connection_is_alive(connection):
        connection = _reconnect_portalaei(stale_connection=connection)

    return connection.cursor()


def _is_portalaei_connection_error(error):
    """Distingue errores de transporte/conexión de errores SQL funcionales."""
    if not isinstance(error, pyodbc.Error):
        return False

    sqlstate = str(error.args[0]).upper() if error.args else ''
    if sqlstate.startswith('08') or sqlstate in ('HYT00', 'HYT01'):
        return True

    message = str(error).lower()
    connection_messages = (
        'communication link failure',
        'connection is closed',
        'connection was closed',
        'closed connection',
        'server is not found',
        'server does not exist',
        'login timeout expired',
        'network-related',
        'transport-level error',
        'tcp provider',
    )
    return any(fragment in message for fragment in connection_messages)

# ===============================
# Vista del escáner con sede
# ===============================
from django.shortcuts import render

def marcador_escaner(request, id_sede):
    """Vista del escáner para una sede específica"""
    try:
        cursor = _get_portalaei_cursor(ensure_alive=True)
        cursor.execute("""
            SELECT ID_SEDE, NOMBRE_SEDE, IDEMPRESA
            FROM SEDES_MARCACIONES
            WHERE ID_SEDE = ?
        """, [id_sede])
        
        sede = cursor.fetchone()
        cursor.close()
        
        if not sede:
            return render(request, 'MARCADORES/error.html', {'mensaje': 'Sede no encontrada'})
        
        context = {
            'id_sede': sede[0],
            'sede_nombre': sede[1],
            'sede_ubicacion': f'Empresa: {sede[2]}' if sede[2] else 'Sin empresa'
        }
        
        return render(request, 'MARCADORES/escaner.html', context)
    except Exception as e:
        return render(request, 'MARCADORES/error.html', {'mensaje': str(e)})


# ===============================
# Procesar registro de entrada/salida
# ===============================
@csrf_exempt
def procesar_marcacion(request):
    if request.method == 'POST':
        cursor = None
        active_connection = None
        try:
            data = json.loads(request.body)
            codigo_personal = data.get('codigo_personal', '').strip()
            id_sede = data.get('id_sede', 1)
            
            if not codigo_personal:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Por favor, ingrese su número de código de barras',
                    'tipo': 'danger'
                })
            
            fecha_actual = datetime.now().date()
            hora_actual = datetime.now().strftime('%H:%M:%S')
            
            cursor = _get_portalaei_cursor(ensure_alive=True)
            active_connection = connection_portalaei
            
            cursor.execute("""
                SELECT ID_PERSONAL, CODIGO_PERSONAL, NOMBRES, APELLIDOS, IDEMPRESA
                FROM PERSONAL
                WHERE CODIGO_PERSONAL = ? AND ESTADO = 1
            """, [codigo_personal])
            
            personal = cursor.fetchone()
            
            if not personal:
                nombres = 'SIN NOMBRE'
                apellidos = 'SIN APELLIDO'
                genero = 'Masculino'

                cursor.execute("""
                    INSERT INTO PERSONAL (CODIGO_PERSONAL, NOMBRES, APELLIDOS, GENERO, ESTADO, IDEMPRESA)
                    OUTPUT INSERTED.ID_PERSONAL
                    VALUES (?, ?, ?, ?, 1, 1)
                """, [codigo_personal, nombres, apellidos, genero])
                
                id_personal = cursor.fetchone()[0]
                connection_portalaei.commit()
                
                cursor.execute("""
                    INSERT INTO ASISTENCIA (ID_PERSONAL, ID_SEDE, HORA_INGRESO, LOG_FECHA, ESTADO)
                    VALUES (?, ?, ?, CAST(? AS DATE), 1)
                """, [id_personal, id_sede, hora_actual, fecha_actual])
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({
                    'status': 'warning',
                    'message': f'DNI no encontrado pero registrado | {codigo_personal} | Ingreso: {hora_actual}',
                    'tipo': 'warning'
                })
            
            id_personal = personal[0]
            nombre_completo = f"{personal[2]} {personal[3]}"

            # 🔥 VALIDACIÓN GLOBAL ANTI-DUPLICADOS
            cursor.execute("""
                SELECT TOP 1 HORA_INGRESO, HORA_SALIDA, LOG_FECHA
                FROM ASISTENCIA
                WHERE ID_PERSONAL = ? AND ID_SEDE = ?
                ORDER BY ID_ASISTENCIA DESC
            """, [id_personal, id_sede])

            ultima = cursor.fetchone()

            if ultima:
                hora_ing = ultima[0]
                hora_sal = ultima[1]
                fecha_reg = ultima[2]

                ultima_hora = hora_sal if hora_sal else hora_ing

                if ultima_hora:
                    if isinstance(fecha_reg, datetime):
                        fecha_reg_dt = fecha_reg.date()
                    else:
                        fecha_reg_dt = fecha_reg

                    ultima_dt = datetime.combine(fecha_reg_dt, ultima_hora)
                    actual_dt = datetime.now()

                    diferencia = (actual_dt - ultima_dt).total_seconds()

                    if diferencia <= 300:
                        cursor.close()
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Ya registraste una marcación hace unos segundos.',
                            'tipo': 'danger'
                        })

            # 🔍 Buscar registro actual
            cursor.execute("""
                SELECT ID_ASISTENCIA, HORA_INGRESO, HORA_SALIDA, LOG_FECHA
                FROM ASISTENCIA
                WHERE ID_PERSONAL = ? AND ID_SEDE = ? 
                AND (
                    CAST(LOG_FECHA AS DATE) = CAST(? AS DATE) OR
                    (CAST(LOG_FECHA AS DATE) = CAST(DATEADD(day, -1, ?) AS DATE) AND HORA_SALIDA IS NULL)
                )
                ORDER BY ID_ASISTENCIA DESC
            """, [id_personal, id_sede, fecha_actual, fecha_actual])
            
            registro_hoy = cursor.fetchone()
            
            if registro_hoy:
                id_asistencia, hora_ingreso, hora_salida, fecha_registro = registro_hoy

                if hora_salida:
                    # ✅ NUEVO INGRESO
                    cursor.execute("""
                        INSERT INTO ASISTENCIA (ID_PERSONAL, ID_SEDE, HORA_INGRESO, LOG_FECHA, ESTADO)
                        VALUES (?, ?, ?, CAST(? AS DATE), 1)
                    """, [id_personal, id_sede, hora_actual, fecha_actual])

                    connection_portalaei.commit()
                    cursor.close()

                    return JsonResponse({
                        'status': 'success',
                        'message': f'{nombre_completo} | {codigo_personal} | Ingreso: {hora_actual}',
                        'tipo': 'success'
                    })

                else:
                    # 🔥 VALIDAR SI ES OTRO DÍA
                    if isinstance(fecha_registro, datetime):
                        fecha_registro_dt = fecha_registro.date()
                    else:
                        fecha_registro_dt = fecha_registro

                    if fecha_registro_dt < fecha_actual:
                        # ✅ ES OTRO DÍA → NUEVO INGRESO
                        cursor.execute("""
                            INSERT INTO ASISTENCIA (ID_PERSONAL, ID_SEDE, HORA_INGRESO, LOG_FECHA, ESTADO)
                            VALUES (?, ?, ?, CAST(? AS DATE), 1)
                        """, [id_personal, id_sede, hora_actual, fecha_actual])

                        connection_portalaei.commit()
                        cursor.close()

                        return JsonResponse({
                            'status': 'success',
                            'message': f'{nombre_completo} | {codigo_personal} | Ingreso: {hora_actual}',
                            'tipo': 'success'
                        })

                    else:
                        # ✅ MISMO DÍA → SALIDA
                        cursor.execute("""
                            UPDATE ASISTENCIA
                            SET HORA_SALIDA = ?
                            WHERE ID_ASISTENCIA = ?
                        """, [hora_actual, id_asistencia])

                        connection_portalaei.commit()
                        cursor.close()

                        return JsonResponse({
                            'status': 'success',
                            'message': f'{nombre_completo} | {codigo_personal} | Salida: {hora_actual}',
                            'tipo': 'primary'
                        })

            else:
                # ✅ PRIMER INGRESO DEL DÍA
                cursor.execute("""
                    INSERT INTO ASISTENCIA (ID_PERSONAL, ID_SEDE, HORA_INGRESO, LOG_FECHA, ESTADO)
                    VALUES (?, ?, ?, CAST(? AS DATE), 1)
                """, [id_personal, id_sede, hora_actual, fecha_actual])

                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({
                    'status': 'success',
                    'message': f'{nombre_completo} | {codigo_personal} | Ingreso: {hora_actual}',
                    'tipo': 'success'
                })
                
        except Exception as e:
            traceback.print_exc()

            if _is_portalaei_connection_error(e):
                try:
                    _reconnect_portalaei(stale_connection=active_connection)
                    return JsonResponse({
                        'status': 'warning',
                        'message': 'Se restableció la conexión. Vuelva a escanear el código.',
                        'tipo': 'warning'
                    })
                except Exception:
                    traceback.print_exc()
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No se pudo restablecer la conexión con SQL Server.',
                        'tipo': 'danger'
                    }, status=503)

            return JsonResponse({
                'status': 'error',
                'message': f'Error: {str(e)}',
                'tipo': 'danger'
            }, status=500)
        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


def marcadores_health(request):
    """Comprueba que Django y SQL Server estén disponibles."""
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Método no permitido'
        }, status=405)

    cursor = None
    try:
        cursor = _get_portalaei_cursor(ensure_alive=True)
        return JsonResponse({
            'status': 'success',
            'message': 'Servidor y SQL Server disponibles.'
        })
    except Exception:
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': 'SQL Server no está disponible.'
        }, status=503)
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass



# ===============================
# Vista principal: Mostrar sedes en cards
# ===============================
class marcadores(TemplateView):
    template_name = 'MARCADORES/marcadores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener todas las sedes con conteo de marcaciones
            cursor.execute("""
                SELECT 
                    s.ID_SEDE, 
                    s.NOMBRE_SEDE,
                    s.IDEMPRESA,
                    COUNT(DISTINCT a.ID_ASISTENCIA) AS TOTAL_MARCACIONES
                FROM SEDES_MARCACIONES s
                LEFT JOIN ASISTENCIA a ON s.ID_SEDE = a.ID_SEDE
                GROUP BY s.ID_SEDE, s.NOMBRE_SEDE, s.IDEMPRESA
                ORDER BY s.NOMBRE_SEDE
            """)
            
            sedes = []
            for row in cursor.fetchall():
                sedes.append({
                    'ID_SEDE': row[0],
                    'NOMBRE_SEDE': row[1],
                    'IDEMPRESA': row[2],
                    'TOTAL_MARCACIONES': row[3]
                })
            context['sedes'] = sedes
            
            # Obtener empresas para el filtro de exportación
            cursor.execute("SELECT IDEMPRESA, DESCRIPCION FROM EMPRESA ORDER BY DESCRIPCION")
            empresas = []
            for row in cursor.fetchall():
                empresas.append({
                    'id': row[0],
                    'descripcion': row[1]
                })
            context['empresas'] = empresas
            
            cursor.close()
        except Exception as e:
            context['sedes'] = []
            context['empresas'] = []
            context['error'] = str(e)
            
        return context


# ===============================
# Vista de marcaciones por sede
# ===============================
class marcaciones_sede(TemplateView):
    template_name = 'MARCADORES/marcaciones_sede.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_sede = self.kwargs.get('id_sede')
        
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener información de la sede
            cursor.execute("""
                SELECT ID_SEDE, NOMBRE_SEDE, IDEMPRESA
                FROM SEDES_MARCACIONES
                WHERE ID_SEDE = ?
            """, [id_sede])
            
            sede = cursor.fetchone()
            
            if sede:
                context['sede'] = {
                    'ID_SEDE': sede[0],
                    'NOMBRE_SEDE': sede[1],
                    'IDEMPRESA': sede[2] 
                }
            else:
                context['error'] = 'Sede no encontrada'
            
            # Empresas para filtros
            cursor.execute("SELECT IDEMPRESA, DESCRIPCION FROM EMPRESA ORDER BY DESCRIPCION")
            empresas = []
            for row in cursor.fetchall():
                empresas.append({
                    'id': row[0],
                    'descripcion': row[1]
                })
            context['empresas'] = empresas
            
            cursor.close()
        except Exception as e:
            context['error'] = str(e)
            
        return context


# ===============================
# API: Obtener asistencias con filtros (incluye filtro por sede)
# ===============================
@csrf_exempt
def obtener_asistencias(request):
    if request.method == 'GET':
        try:
            fecha_inicio = request.GET.get('fecha_inicio', '')
            fecha_fin = request.GET.get('fecha_fin', '')
            empresa_filtro = request.GET.get('empresa', '')
            sede_filtro = request.GET.get('sede', '')
            
            cursor = connection_portalaei.cursor()
            
            query = """
                SELECT a.ID_ASISTENCIA, a.ID_PERSONAL, a.ID_SEDE, a.HORA_INGRESO, a.HORA_SALIDA, 
                       a.LOG_FECHA, a.ESTADO,
                       p.CODIGO_PERSONAL, p.NOMBRES, p.APELLIDOS, p.IDEMPRESA,
                       e.DESCRIPCION as EMPRESA_NOMBRE,
                       s.NOMBRE_SEDE as SEDE_NOMBRE
                FROM ASISTENCIA a
                INNER JOIN PERSONAL p ON a.ID_PERSONAL = p.ID_PERSONAL
                LEFT JOIN EMPRESA e ON p.IDEMPRESA = e.IDEMPRESA
                LEFT JOIN SEDES_MARCACIONES s ON a.ID_SEDE = s.ID_SEDE
                WHERE 1=1
            """
            params = []
            
            # Aplicar filtros de fecha solo si se proporcionan
            if fecha_inicio and fecha_fin:
                query += " AND CAST(a.LOG_FECHA AS DATE) BETWEEN ? AND ?"
                params.append(fecha_inicio)
                params.append(fecha_fin)
            elif fecha_inicio:
                query += " AND CAST(a.LOG_FECHA AS DATE) >= ?"
                params.append(fecha_inicio)
            elif fecha_fin:
                query += " AND CAST(a.LOG_FECHA AS DATE) <= ?"
                params.append(fecha_fin)
            
            if empresa_filtro:
                query += " AND e.DESCRIPCION = ?"
                params.append(empresa_filtro)
            
            if sede_filtro:
                query += " AND a.ID_SEDE = ?"
                params.append(sede_filtro)
            
            # Ordenar por fecha más reciente primero
            query += " ORDER BY a.LOG_FECHA DESC, a.HORA_INGRESO DESC"
            
            cursor.execute(query, params)
            
            asistencias = []
            for row in cursor.fetchall():
               
                hora_ingreso = row[3].strftime('%H:%M:%S') if row[3] else None
                hora_salida = row[4].strftime('%H:%M:%S') if row[4] else None
                log_fecha = row[5].strftime('%Y-%m-%d') if row[5] else None
                
                # Calcular estado basado en marcaciones y horas trabajadas
                estado_numerico = row[6]  # El estado original de la BD
                
                if hora_ingreso and hora_salida:
                    try:
                        from datetime import datetime, timedelta
                        ingreso_dt = datetime.strptime(hora_ingreso, '%H:%M:%S')
                        salida_dt = datetime.strptime(hora_salida, '%H:%M:%S')
                        
                        # Si la salida es menor que el ingreso, asumimos que cruzó medianoche
                        if salida_dt < ingreso_dt:
                            salida_dt += timedelta(days=1)
                        
                        diferencia = salida_dt - ingreso_dt
                        horas = diferencia.total_seconds() / 3600
                        horas_trabajadas = f"{int(horas)}h {int((horas % 1) * 60)}m"
                        
                        # Determinar estado basado en el estado de la BD y horas trabajadas
                        if estado_numerico == 2:
                            estado_texto = 'Completado'
                        elif horas >= 6:
                            estado_texto = 'Completado'  # Debería ser actualizado por la función
                        else:
                            estado_texto = 'Completo'  # Tiene ambas marcaciones pero menos de 6 horas
                    except:
                        horas_trabajadas = "Error cálculo"
                        estado_texto = 'Completo'
                elif hora_ingreso and not hora_salida:
                    estado_texto = 'Incompleto'
                    horas_trabajadas = None
                else:
                    estado_texto = 'Sin datos'
                    horas_trabajadas = None

                asistencias.append({
                    'ID_ASISTENCIA': row[0],
                    'ID_PERSONAL': row[1],
                    'ID_SEDE': row[2],
                    'HORA_INGRESO': hora_ingreso,
                    'HORA_SALIDA': hora_salida,
                    'LOG_FECHA': log_fecha,
                    'ESTADO': estado_texto,
                    'HORAS_TRABAJADAS': horas_trabajadas,
                    'CODIGO_PERSONAL': row[7],
                    'NOMBRES': row[8],
                    'APELLIDOS': row[9],
                    'NOMBRE_COMPLETO': f"{row[8]} {row[9]}",
                    'IDEMPRESA': row[10],
                    'EMPRESA_NOMBRE': row[11],
                    'SEDE_NOMBRE': row[12]
                })
            
            # Actualizar estados en la base de datos para registros que califican como "Completado" - REMOVIDO
            # actualizar_estados_completados(cursor)  # Solo se ejecuta manualmente ahora
            
            cursor.close()
            return JsonResponse({'status': 'success', 'data': asistencias})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ===============================
# API: Listar todas las sedes
# ===============================
@csrf_exempt
def sedes_list_api(request):
    """Endpoint para obtener todas las sedes con conteo de marcaciones"""
    if request.method == 'GET':
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT 
                    s.ID_SEDE, 
                    s.NOMBRE_SEDE,
                    s.IDEMPRESA,
                    COUNT(DISTINCT a.ID_ASISTENCIA) AS TOTAL_MARCACIONES
                FROM SEDES_MARCACIONES s
                LEFT JOIN ASISTENCIA a ON s.ID_SEDE = a.ID_SEDE
                GROUP BY s.ID_SEDE, s.NOMBRE_SEDE, s.IDEMPRESA
                ORDER BY s.NOMBRE_SEDE
            """)
            
            sedes = []
            for row in cursor.fetchall():
                sedes.append({
                    'ID_SEDE': row[0],
                    'NOMBRE_SEDE': row[1],
                    'IDEMPRESA': row[2],
                    'TOTAL_MARCACIONES': row[3]
                })
            
            cursor.close()
            return JsonResponse({'status': 'success', 'data': sedes})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ===============================
# Exportar a TXT formato Nisira
# ===============================
@csrf_exempt
def exportar_txt_nisira(request):
    if request.method == 'GET':
        try:
            fecha_inicio = request.GET.get('fecha_inicio', '')
            fecha_final = request.GET.get('fecha_final', '')
            fecha_fin = request.GET.get('fecha_fin', '')  # Alternativa para compatibilidad
            empresa_filtro = request.GET.get('empresa', '')
            sede_filtro = request.GET.get('sede', '')
            
            # Usar fecha_fin si fecha_final no está presente
            if not fecha_final and fecha_fin:
                fecha_final = fecha_fin
            
            cursor = connection_portalaei.cursor()
            
            query = """
                SELECT p.CODIGO_PERSONAL, 
                       a.HORA_INGRESO AS HORA,
                       a.LOG_FECHA
                FROM ASISTENCIA a
                INNER JOIN PERSONAL p ON a.ID_PERSONAL = p.ID_PERSONAL
                LEFT JOIN EMPRESA e ON p.IDEMPRESA = e.IDEMPRESA
                WHERE a.HORA_INGRESO IS NOT NULL
            """
            params = []
            
            if fecha_inicio and fecha_final:
                query += " AND CAST(a.LOG_FECHA AS DATE) BETWEEN ? AND ?"
                params.append(fecha_inicio)
                params.append(fecha_final)
            elif fecha_inicio:
                query += " AND CAST(a.LOG_FECHA AS DATE) >= ?"
                params.append(fecha_inicio)
            elif fecha_final:
                query += " AND CAST(a.LOG_FECHA AS DATE) <= ?"
                params.append(fecha_final)
            
            if empresa_filtro:
                query += " AND e.DESCRIPCION = ?"
                params.append(empresa_filtro)
            
            if sede_filtro:
                query += " AND a.ID_SEDE = ?"
                params.append(sede_filtro)
            
            query += """
                UNION ALL
                SELECT p.CODIGO_PERSONAL, 
                       a.HORA_SALIDA AS HORA,
                       a.LOG_FECHA
                FROM ASISTENCIA a
                INNER JOIN PERSONAL p ON a.ID_PERSONAL = p.ID_PERSONAL
                LEFT JOIN EMPRESA e ON p.IDEMPRESA = e.IDEMPRESA
                WHERE a.HORA_SALIDA IS NOT NULL
            """
            
            if fecha_inicio and fecha_final:
                query += " AND CAST(a.LOG_FECHA AS DATE) BETWEEN ? AND ?"
                params.append(fecha_inicio)
                params.append(fecha_final)
            elif fecha_inicio:
                query += " AND CAST(a.LOG_FECHA AS DATE) >= ?"
                params.append(fecha_inicio)
            elif fecha_final:
                query += " AND CAST(a.LOG_FECHA AS DATE) <= ?"
                params.append(fecha_final)
            
            if empresa_filtro:
                query += " AND e.DESCRIPCION = ?"
                params.append(empresa_filtro)
            
            if sede_filtro:
                query += " AND a.ID_SEDE = ?"
                params.append(sede_filtro)
            
            query += " ORDER BY LOG_FECHA, HORA"
            
            cursor.execute(query, params)
            
            lineas = []
            for row in cursor.fetchall():
                codigo = row[0] if row[0] else ''
                
                # Manejar diferentes tipos de datos para hora
                hora = ''
                if row[1]:
                    if isinstance(row[1], str):
                        # Si ya es string, parsearlo
                        try:
                            hora_obj = datetime.strptime(row[1], '%H:%M:%S')
                            hora = hora_obj.strftime('%H%M%S')
                        except:
                            hora = row[1].replace(':', '')[:6]
                    else:
                        # Si es datetime.time o datetime
                        try:
                            hora = row[1].strftime('%H%M%S')
                        except:
                            hora = str(row[1]).replace(':', '')[:6]
                
                # Manejar fecha
                fecha = ''
                if row[2]:
                    if isinstance(row[2], str):
                        try:
                            fecha_obj = datetime.strptime(row[2], '%Y-%m-%d')
                            fecha = fecha_obj.strftime('%d%m%y')
                        except:
                            fecha = row[2].replace('-', '')[-6:]
                    else:
                        try:
                            fecha = row[2].strftime('%d%m%y')
                        except:
                            fecha = str(row[2]).replace('-', '')[-6:]
                
                linea = f"{codigo}|{fecha}|{hora}"
                lineas.append(linea)
            
            cursor.close()
            
            contenido = '\n'.join(lineas)
            response = HttpResponse(contenido, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="asistencias_nisira_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt"'
            
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)




# ===============================
# API: Estadísticas por sede
# ===============================
@csrf_exempt
def estadisticas_sede(request):
    """Obtener estadísticas detalladas de una sede específica"""
    if request.method == 'GET':
        try:
            id_sede = request.GET.get('id_sede')
            fecha_inicio = request.GET.get('fecha_inicio', '')
            fecha_fin = request.GET.get('fecha_fin', '')
            
            if not id_sede:
                return JsonResponse({'status': 'error', 'message': 'ID_SEDE requerido'}, status=400)
            
            cursor = connection_portalaei.cursor()
            
            # Query base
            query = """
                SELECT 
                    COUNT(DISTINCT a.ID_ASISTENCIA) AS TOTAL_REGISTROS,
                    COUNT(DISTINCT a.ID_PERSONAL) AS TOTAL_PERSONAL,
                    COUNT(DISTINCT CAST(a.LOG_FECHA AS DATE)) AS DIAS_ACTIVOS,
                    COUNT(CASE WHEN a.HORA_INGRESO IS NOT NULL THEN 1 END) AS TOTAL_INGRESOS,
                    COUNT(CASE WHEN a.HORA_SALIDA IS NOT NULL THEN 1 END) AS TOTAL_SALIDAS
                FROM ASISTENCIA a
                WHERE a.ID_SEDE = ?
            """
            params = [id_sede]
            
            if fecha_inicio:
                query += " AND CAST(a.LOG_FECHA AS DATE) >= ?"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND CAST(a.LOG_FECHA AS DATE) <= ?"
                params.append(fecha_fin)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            estadisticas = {
                'TOTAL_REGISTROS': row[0] if row[0] else 0,
                'TOTAL_PERSONAL': row[1] if row[1] else 0,
                'DIAS_ACTIVOS': row[2] if row[2] else 0,
                'TOTAL_INGRESOS': row[3] if row[3] else 0,
                'TOTAL_SALIDAS': row[4] if row[4] else 0
            }
            
            cursor.close()
            return JsonResponse({'status': 'success', 'data': estadisticas})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ===============================
# API: CRUD de Sedes
# ===============================
@method_decorator(csrf_exempt, name='dispatch')
class SedesCRUDView(View):
    """Vista para gestionar sedes (crear, leer, actualizar)"""
    
    def get(self, request, *args, **kwargs):
        """Obtener información de una sede específica"""
        try:
            id_sede = request.GET.get('id_sede')
            
            if not id_sede:
                return JsonResponse({'status': 'error', 'message': 'ID_SEDE requerido'}, status=400)
            
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT ID_SEDE, NOMBRE_SEDE, IDEMPRESA
                FROM SEDES_MARCACIONES
                WHERE ID_SEDE = ?
            """, [id_sede])
            
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Sede no encontrada'}, status=404)
            
            sede = {
                'ID_SEDE': row[0],
                'NOMBRE_SEDE': row[1],
                'IDEMPRESA': row[2],
            }
            
            cursor.close()
            return JsonResponse({'status': 'success', 'data': sede})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    def post(self, request, *args, **kwargs):
        """Crear o actualizar una sede"""
        try:
            data = json.loads(request.body)
            id_sede = data.get('ID_SEDE')
            descripcion = data.get('NOMBRE_SEDE', '').strip()
            ubicacion = data.get('IDEMPRESA', '').strip()
            
            if not descripcion:
                return JsonResponse({'status': 'error', 'message': 'Descripción requerida'}, status=400)
            
            cursor = connection_portalaei.cursor()
            
            if id_sede:
                # Actualizar sede existente
                cursor.execute("""
                    UPDATE SEDE
                    SET NOMBRE_SEDE = ?, IDEMPRESA = ?
                    WHERE ID_SEDE = ?
                """, [descripcion, ubicacion, id_sede])
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Sede actualizada correctamente',
                    'id_sede': id_sede
                })
            else:
                # Crear nueva sede
                cursor.execute("""
                    INSERT INTO SEDES_MARCACIONES (NOMBRE_SEDE, IDEMPRESA)
                    OUTPUT INSERTED.ID_SEDE
                    VALUES (?, ?)
                """, [descripcion, ubicacion])
                
                nuevo_id = cursor.fetchone()[0]
                connection_portalaei.commit()
                cursor.close()
                
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Sede creada correctamente',
                    'id_sede': nuevo_id
                })
                
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ===============================
# Vista de Administración de Marcadores
# ===============================
class administracion_marcadores(TemplateView):
    template_name = 'MARCADORES/administracion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) AS TOTAL_MARCACIONES,
                    COUNT(DISTINCT ID_PERSONAL) AS TOTAL_PERSONAL,
                    MIN(LOG_FECHA) AS FECHA_MAS_ANTIGUA,
                    MAX(LOG_FECHA) AS FECHA_MAS_RECIENTE
                FROM ASISTENCIA
            """)
            
            stats = cursor.fetchone()
            if stats:
                context['total_marcaciones'] = stats[0]
                context['total_personal'] = stats[1]
                context['fecha_mas_antigua'] = stats[2]
                context['fecha_mas_reciente'] = stats[3]
            
            cursor.close()
        except Exception as e:
            context['error'] = str(e)
            
        return context


# ===============================
# API: Eliminar marcaciones por rango de fechas
# ===============================
@csrf_exempt
def eliminar_marcaciones(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fecha_inicio = data.get('fecha_inicio', '').strip()
            fecha_fin = data.get('fecha_fin', '').strip()
            
            if not fecha_inicio or not fecha_fin:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Debe especificar fecha de inicio y fin'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            # Primero contar cuántos registros se eliminarán
            cursor.execute("""
                SELECT COUNT(*) 
                FROM ASISTENCIA 
                WHERE CAST(LOG_FECHA AS DATE) BETWEEN ? AND ?
            """, [fecha_inicio, fecha_fin])
            
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.close()
                return JsonResponse({
                    'status': 'warning',
                    'message': 'No se encontraron marcaciones en el rango especificado'
                })
            
            # Eliminar las marcaciones
            cursor.execute("""
                DELETE FROM ASISTENCIA 
                WHERE CAST(LOG_FECHA AS DATE) BETWEEN ? AND ?
            """, [fecha_inicio, fecha_fin])
            
            connection_portalaei.commit()
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Se eliminaron {count} marcaciones correctamente',
                'count': count
            })
            
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': f'Error al eliminar marcaciones: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# ===============================
# API: Obtener estadísticas por rango de fechas
# ===============================
@csrf_exempt
def estadisticas_rango(request):
    if request.method == 'GET':
        try:
            fecha_inicio = request.GET.get('fecha_inicio', '')
            fecha_fin = request.GET.get('fecha_fin', '')
            
            if not fecha_inicio or not fecha_fin:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Debe especificar fecha de inicio y fin'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) AS TOTAL,
                    COUNT(DISTINCT ID_PERSONAL) AS PERSONAL,
                    COUNT(DISTINCT ID_SEDE) AS SEDES
                FROM ASISTENCIA 
                WHERE CAST(LOG_FECHA AS DATE) BETWEEN ? AND ?
            """, [fecha_inicio, fecha_fin])
            
            stats = cursor.fetchone()
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'total_marcaciones': stats[0],
                    'total_personal': stats[1],
                    'total_sedes': stats[2]
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

# ===============================
# Exportar a Excel
# ===============================
@csrf_exempt
def exportar_excel(request):
    if request.method == 'GET':
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
            from django.http import HttpResponse
            
            
            fecha_inicio = request.GET.get('fecha_inicio', '')
            fecha_fin = request.GET.get('fecha_fin', '')
            empresa_filtro = request.GET.get('empresa', '')
            sede_filtro = request.GET.get('sede', '')
            
            cursor = connection_portalaei.cursor()
            
            query = """
                SELECT a.ID_ASISTENCIA, a.ID_PERSONAL, a.ID_SEDE, a.HORA_INGRESO, a.HORA_SALIDA, 
                       a.LOG_FECHA, a.ESTADO,
                       p.CODIGO_PERSONAL, p.NOMBRES, p.APELLIDOS, p.IDEMPRESA,
                       e.DESCRIPCION as EMPRESA_NOMBRE,
                       s.NOMBRE_SEDE as SEDE_NOMBRE
                FROM ASISTENCIA a
                INNER JOIN PERSONAL p ON a.ID_PERSONAL = p.ID_PERSONAL
                LEFT JOIN EMPRESA e ON p.IDEMPRESA = e.IDEMPRESA
                LEFT JOIN SEDES_MARCACIONES s ON a.ID_SEDE = s.ID_SEDE
                WHERE 1=1
            """
            params = []
            
            if fecha_inicio and fecha_fin:
                query += " AND CAST(a.LOG_FECHA AS DATE) BETWEEN ? AND ?"
                params.append(fecha_inicio)
                params.append(fecha_fin)
            elif fecha_inicio:
                query += " AND CAST(a.LOG_FECHA AS DATE) >= ?"
                params.append(fecha_inicio)
            elif fecha_fin:
                query += " AND CAST(a.LOG_FECHA AS DATE) <= ?"
                params.append(fecha_fin)
            
            if empresa_filtro:
                query += " AND e.DESCRIPCION = ?"
                params.append(empresa_filtro)
            
            if sede_filtro:
                query += " AND a.ID_SEDE = ?"
                params.append(sede_filtro)
            
            query += " ORDER BY a.LOG_FECHA DESC, a.HORA_INGRESO DESC"
            
            cursor.execute(query, params)
            
            # Crear workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Marcaciones"
            
            # Estilos
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            center_alignment = Alignment(horizontal="center")
            
            # Headers
            headers = [
                'ID', 'Código', 'Nombres', 'Apellidos', 'Empresa', 'Sede',
                'Hora Ingreso', 'Hora Salida', 'Horas Trabajadas', 'Fecha', 'Estado'
            ]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
            
            # Datos
            row_num = 2
            for row in cursor.fetchall():
                hora_ingreso = row[3].strftime('%H:%M:%S') if row[3] else None
                hora_salida = row[4].strftime('%H:%M:%S') if row[4] else None
                log_fecha = row[5].strftime('%Y-%m-%d') if row[5] else None
                
                # Calcular estado y horas
                if hora_ingreso and hora_salida:
                    estado_texto = 'Completo'
                    try:
                        from datetime import datetime, timedelta
                        ingreso_dt = datetime.strptime(hora_ingreso, '%H:%M:%S')
                        salida_dt = datetime.strptime(hora_salida, '%H:%M:%S')
                        
                        if salida_dt < ingreso_dt:
                            salida_dt += timedelta(days=1)
                        
                        diferencia = salida_dt - ingreso_dt
                        horas = diferencia.total_seconds() / 3600
                        horas_trabajadas = f"{int(horas)}h {int((horas % 1) * 60)}m"
                    except:
                        horas_trabajadas = "Error"
                elif hora_ingreso and not hora_salida:
                    estado_texto = 'Incompleto'
                    horas_trabajadas = '-'
                else:
                    estado_texto = 'Sin datos'
                    horas_trabajadas = '-'
                
                data_row = [
                    row[0], row[7], row[8], row[9], row[11] or '-', row[12] or '-',
                    hora_ingreso or '-', hora_salida or '-', horas_trabajadas,
                    log_fecha, estado_texto
                ]
                
                for col, value in enumerate(data_row, 1):
                    ws.cell(row=row_num, column=col, value=value)
                
                row_num += 1
            
            # Ajustar ancho de columnas
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            cursor.close()
            
            # Preparar respuesta
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="marcaciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
            
            wb.save(response)
            return response
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# ===============================
# Función para actualizar estados basado en horas trabajadas
# ===============================
def actualizar_estados_completados(cursor):
    """
    Actualiza el estado de los registros de asistencia basado en las horas trabajadas.
    Marca como estado 2 (Completado) los registros con 6+ horas trabajadas.
    """
    try:
        # Obtener todos los registros con ingreso y salida que no estén marcados como completados
        cursor.execute("""
            SELECT ID_ASISTENCIA, HORA_INGRESO, HORA_SALIDA, ESTADO
            FROM ASISTENCIA 
            WHERE HORA_INGRESO IS NOT NULL 
            AND HORA_SALIDA IS NOT NULL 
            AND (ESTADO != 2 OR ESTADO IS NULL OR ESTADO = 1)
        """)
        
        registros_pendientes = cursor.fetchall()
        registros_actualizados = 0
        
        for registro in registros_pendientes:
            id_asistencia = registro[0]
            hora_ingreso = registro[1]
            hora_salida = registro[2]
            estado_actual = registro[3]
            
            try:
                from datetime import datetime, timedelta
                
                # Manejar diferentes tipos de datos para hora_ingreso
                if isinstance(hora_ingreso, str):
                    ingreso_dt = datetime.strptime(hora_ingreso, '%H:%M:%S')
                elif hasattr(hora_ingreso, 'hour'):  # datetime.time object
                    ingreso_dt = datetime.combine(datetime.today(), hora_ingreso)
                else:  # datetime object
                    ingreso_dt = hora_ingreso
                
                # Manejar diferentes tipos de datos para hora_salida
                if isinstance(hora_salida, str):
                    salida_dt = datetime.strptime(hora_salida, '%H:%M:%S')
                elif hasattr(hora_salida, 'hour'):  # datetime.time object
                    salida_dt = datetime.combine(datetime.today(), hora_salida)
                else:  # datetime object
                    salida_dt = hora_salida
                
                # Si la salida es menor que el ingreso, asumimos que cruzó medianoche
                if salida_dt.time() < ingreso_dt.time():
                    salida_dt += timedelta(days=1)
                
                # Calcular diferencia en horas
                diferencia = salida_dt - ingreso_dt
                horas_trabajadas = diferencia.total_seconds() / 3600
                
                # Si trabajó 6 horas o más, marcar como completado (estado = 2)
                if horas_trabajadas >= 6:
                    cursor.execute("""
                        UPDATE ASISTENCIA 
                        SET ESTADO = 2
                        WHERE ID_ASISTENCIA = ?
                    """, [id_asistencia])
                    registros_actualizados += 1
                    print(f"Registro {id_asistencia} actualizado a estado 2 (Completado) - {horas_trabajadas:.2f} horas (estado anterior: {estado_actual})")
                else:
                    print(f"Registro {id_asistencia} no califica para Completado - {horas_trabajadas:.2f} horas")
                
            except Exception as e:
                print(f"Error calculando horas para registro {id_asistencia}: {e}")
                print(f"Tipos de datos - Ingreso: {type(hora_ingreso)}, Salida: {type(hora_salida)}")
                continue
        
        print(f"Se actualizaron {registros_actualizados} de {len(registros_pendientes)} registros a estado 'Completado'")
        
        return registros_actualizados
        
    except Exception as e:
        print(f"Error en actualizar_estados_completados: {e}")
        return 0

# ===============================
# Endpoint para actualizar estados manualmente
# ===============================
@csrf_exempt
def actualizar_estados_manual(request):
    """Endpoint para actualizar manualmente todos los estados basado en horas trabajadas"""
    if request.method == 'POST':
        try:
            cursor = connection_portalaei.cursor()
            
            # Primero verificar cuántos registros hay pendientes
            cursor.execute("""
                SELECT COUNT(*)
                FROM ASISTENCIA 
                WHERE HORA_INGRESO IS NOT NULL 
                AND HORA_SALIDA IS NOT NULL 
                AND (ESTADO != 2 OR ESTADO IS NULL OR ESTADO = 1)
            """)
            total_pendientes = cursor.fetchone()[0]
            
            print(f"DEBUG: Total registros pendientes de revisión: {total_pendientes}")
            
            registros_actualizados = actualizar_estados_completados(cursor)
            
            # Asegurar que los cambios se confirmen
            connection_portalaei.commit()
            
            # Verificar cuántos registros quedaron pendientes después de la actualización
            cursor.execute("""
                SELECT COUNT(*)
                FROM ASISTENCIA 
                WHERE HORA_INGRESO IS NOT NULL 
                AND HORA_SALIDA IS NOT NULL 
                AND (ESTADO != 2 OR ESTADO IS NULL OR ESTADO = 1)
            """)
            pendientes_restantes = cursor.fetchone()[0]
            
            cursor.close()
            
            mensaje = f'Estados actualizados correctamente. {registros_actualizados} registros marcados como Completado de {total_pendientes} revisados. {pendientes_restantes} registros siguen pendientes (menos de 6 horas).'
            
            return JsonResponse({
                'status': 'success', 
                'message': mensaje,
                'registros_actualizados': registros_actualizados,
                'total_pendientes': total_pendientes,
                'pendientes_restantes': pendientes_restantes
            })
            
        except Exception as e:
            connection_portalaei.rollback()
            print(f"ERROR en actualizar_estados_manual: {e}")
            return JsonResponse({
                'status': 'error', 
                'message': f'Error al actualizar estados: {str(e)}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# ===============================
# Endpoint de debug para verificar estados
# ===============================
@csrf_exempt
def verificar_estados_debug(request):
    """Endpoint para verificar el estado actual de los registros"""
    if request.method == 'GET':
        try:
            cursor = connection_portalaei.cursor()
            
            # Contar registros por estado
            cursor.execute("""
                SELECT 
                    ESTADO,
                    COUNT(*) as CANTIDAD
                FROM ASISTENCIA 
                WHERE HORA_INGRESO IS NOT NULL 
                AND HORA_SALIDA IS NOT NULL
                GROUP BY ESTADO
                ORDER BY ESTADO
            """)
            
            estados = []
            for row in cursor.fetchall():
                estados.append({
                    'estado': row[0],
                    'cantidad': row[1]
                })
            
            # Obtener algunos registros de ejemplo con 6+ horas
            cursor.execute("""
                SELECT TOP 5
                    ID_ASISTENCIA, 
                    HORA_INGRESO, 
                    HORA_SALIDA, 
                    ESTADO,
                    LOG_FECHA
                FROM ASISTENCIA 
                WHERE HORA_INGRESO IS NOT NULL 
                AND HORA_SALIDA IS NOT NULL
                ORDER BY LOG_FECHA DESC
            """)
            
            ejemplos = []
            for row in cursor.fetchall():
                try:
                    from datetime import datetime, timedelta
                    
                    hora_ingreso = row[1]
                    hora_salida = row[2]
                    
                    # Calcular horas trabajadas
                    if isinstance(hora_ingreso, str):
                        ingreso_dt = datetime.strptime(hora_ingreso, '%H:%M:%S')
                    elif hasattr(hora_ingreso, 'hour'):
                        ingreso_dt = datetime.combine(datetime.today(), hora_ingreso)
                    else:
                        ingreso_dt = hora_ingreso
                    
                    if isinstance(hora_salida, str):
                        salida_dt = datetime.strptime(hora_salida, '%H:%M:%S')
                    elif hasattr(hora_salida, 'hour'):
                        salida_dt = datetime.combine(datetime.today(), hora_salida)
                    else:
                        salida_dt = hora_salida
                    
                    if salida_dt.time() < ingreso_dt.time():
                        salida_dt += timedelta(days=1)
                    
                    diferencia = salida_dt - ingreso_dt
                    horas = diferencia.total_seconds() / 3600
                    
                    ejemplos.append({
                        'id': row[0],
                        'ingreso': str(hora_ingreso),
                        'salida': str(hora_salida),
                        'estado': row[3],
                        'fecha': str(row[4]),
                        'horas_calculadas': round(horas, 2),
                        'califica_completado': horas >= 6
                    })
                    
                except Exception as e:
                    ejemplos.append({
                        'id': row[0],
                        'error': str(e)
                    })
            
            cursor.close()
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'estados_resumen': estados,
                    'ejemplos_registros': ejemplos
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
