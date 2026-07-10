from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.db import transaction
from django.http import JsonResponse
from apps.connection.connect_portalaei import connection_portalaei
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator


# Create your views here.

class evaluacion_desempeño(TemplateView):
    permission_required = 'modulo_gerencia' 
    template_name = 'GERENCIA/ADMINISTRACION/RRHH/pages/rrhh_evaluacion_desempeño.html'



#==============================================================================================
# EVALUACIONES DE OBJETIVOS
#==============================================================================================


class ObjetivosEvaluacionView(View):
    @transaction.atomic
    
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener el parámetro de periodo desde la URL (año)
            periodo = request.GET.get('campania', None)  # Mantener 'campania' como nombre del parámetro para compatibilidad
            
            # Si no se proporciona periodo, usar el año actual
            if not periodo:
                from datetime import date
                periodo = str(date.today().year)
            
            # Extraer solo el año si viene en formato CAMP2026
            if periodo.startswith('CAMP'):
                periodo = periodo.replace('CAMP', '')
            
            try:
            # Ejecutar el procedimiento almacenado con el área 4 hardcodeada
                cursor.execute("EXEC SP_RESUMEN_RRHH_OBJETIVOS @id_area=?, @periodo=?", [17, periodo])
            
            except Exception as sp_error:
                # Si el procedimiento falla, usar una consulta directa
                print(f"Error en procedimiento almacenado: {sp_error}")
                cursor.execute("""
                    SELECT 
                        e.id,
                        e.id_evaluador,
                        e.id_evaluado,
                        e.id_area,
                        e.periodo,
                        u1.first_name + ' ' + u1.last_name as evaluador,
                        u2.first_name + ' ' + u2.last_name as evaluado,
                        a.nombre_area
                    FROM RRHH_EVALUACIONES e
                    LEFT JOIN user_user u1 ON e.id_evaluador = u1.id
                    LEFT JOIN user_user u2 ON e.id_evaluado = u2.id
                    LEFT JOIN RRHH_AREAS a ON e.id_area = a.id_area
                    WHERE e.id_area = ? AND e.periodo = ?
                """, [17, periodo])
            
            # Obtener los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            objetivos = []
            for row in cursor.fetchall():
                objetivo = dict(zip(columns, row))
                # Convertir fechas a formato string para JSON si existen
                if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                    objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                    objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                objetivos.append(objetivo)

            return JsonResponse({
                'status': 'success',
                'data': objetivos,
                'periodo': periodo
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

        finally:
            if cursor:
                cursor.close()


@method_decorator(csrf_exempt, name='dispatch')
class DetallesObjetivosView(View):
    @transaction.atomic
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection_portalaei.cursor()

            # Verificar si es un nuevo objetivo individual (tiene id_evaluacion)
            if 'id_evaluacion' in data:
                # Insertar solo el objetivo
                obj_query = """
                INSERT INTO RRHH_OBJETIVOS 
                (id_evaluacion, descripcion, fecha_inicio, fecha_fin, 
                indicador,meta, no_cumple, cumple, excede, sobresaliente) 
                VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(obj_query, [
                    data['id_evaluacion'],
                    data['descripcion'],
                    data['fecha_inicio'],
                    data['fecha_fin'],
                    data['indicador'],
                    data['meta'],
                    data.get('no_cumple', 0),
                    data.get('cumple', 0),
                    data.get('excede', 0),
                    data.get('sobresaliente', 0)
                ])
                
                connection_portalaei.commit()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Objetivo guardado correctamente',
                    'id_evaluacion': data['id_evaluacion']
                })
                
            else:
                # Verificar si ya existe una evaluación para este evaluado
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM RRHH_EVALUACIONES 
                    WHERE id_evaluado = ? AND periodo = ?
                """, [data['id_evaluado'], data['periodo']])

                count = cursor.fetchone()[0]
                if count > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ya existe una evaluación para este colaborador'
                    }, status=400)

                # Lógica existente para crear nueva evaluación con objetivos
                eval_query = """
                INSERT INTO RRHH_EVALUACIONES 
                (id_evaluador, id_evaluado, id_area, periodo) 
                VALUES (?, ?, ?, ?);
                """
                
                cursor.execute(eval_query, [
                    data['id_evaluador'],
                    data['id_evaluado'],
                    data['id_area'],
                    data['periodo']
                ])

                cursor.execute("SELECT IDENT_CURRENT('RRHH_EVALUACIONES')")
                id_evaluacion = cursor.fetchone()[0]
                
                obj_query = """
                INSERT INTO RRHH_OBJETIVOS 
                (id_evaluacion, descripcion, fecha_inicio, fecha_fin, 
                indicador,meta, no_cumple, cumple, excede, sobresaliente) 
                VALUES (?, ?,?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                for objetivo in data['objetivos']:
                    cursor.execute(obj_query, [
                        id_evaluacion,
                        objetivo['descripcion'],
                        objetivo['fecha_inicio'],
                        objetivo['fecha_fin'],
                        objetivo['indicador'],
                        objetivo['meta'],
                        objetivo.get('no_cumple', 0),
                        objetivo.get('cumple', 0),
                        objetivo.get('excede', 0),
                        objetivo.get('sobresaliente', 0)
                    ])
                
                connection_portalaei.commit()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluación y objetivos guardados correctamente',
                    'id_evaluacion': id_evaluacion
                })
            
        except KeyError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Falta el campo requerido: {str(e)}'
            }, status=400)
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
        
        finally:
            if cursor:
                cursor.close()

    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si se proporcionó un ID específico
            objetivo_id = kwargs.get('id')
            
            if objetivo_id:
                # Si hay ID, ejecutar consulta para un objetivo específico
                cursor.execute("""
                    SELECT * FROM RRHH_OBJETIVOS WHERE id = ?
                """, [objetivo_id])
            else:
                # Si no hay ID, ejecutar el procedimiento para todos
                cursor.execute("EXEC RRHH_EV_OBJETIVOS_MEJORA 17")
            
            # Obtener los resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
                
            return JsonResponse({
                'status': 'success',
                'message': 'Datos obtenidos correctamente',
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()
    
    def delete(self, request, id, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # 1. Obtener el id_evaluacion del objetivo
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_OBJETIVOS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Objetivo no encontrado'
                }, status=404)
                
            id_evaluacion = result[0]
            
            # 2. Contar cuántos objetivos tiene la evaluación
            cursor.execute("""
                SELECT COUNT(*) 
                FROM RRHH_OBJETIVOS 
                WHERE id_evaluacion = ?
            """, [id_evaluacion])
            
            cantidad_objetivos = cursor.fetchone()[0]
            
            # 3. Si es el último objetivo, verificar si hay competencias asociadas
            if cantidad_objetivos == 1:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM RRHH_COMPETENCIAS 
                    WHERE id_evaluacion = ? AND estado = 1
                """, [id_evaluacion])
                
                cantidad_competencias = cursor.fetchone()[0]
                
                if cantidad_competencias > 0:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'No se puede eliminar el objetivo. Existen competencias asociadas a esta evaluación. Por favor, elimine primero las competencias.',
                        'data': {
                            'competencias_existentes': cantidad_competencias
                        }
                    }, status=400)
            
            # 4. Eliminar el objetivo
            cursor.execute("""
                DELETE FROM RRHH_OBJETIVOS 
                WHERE id = ?
            """, [id])
            
            # 5. Si era el último objetivo y no hay competencias, eliminar la evaluación
            if cantidad_objetivos == 1:
                cursor.execute("""
                    DELETE FROM RRHH_EVALUACIONES 
                    WHERE id = ?
                """, [id_evaluacion])
                mensaje = 'Objetivo y evaluación eliminados correctamente'
            else:
                mensaje = 'Objetivo eliminado correctamente'
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': mensaje,
                'data': {
                    'objetivo_id': id,
                    'evaluacion_id': id_evaluacion,
                    'evaluacion_eliminada': cantidad_objetivos == 1
                }
            })
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def put(self, request, id, *args, **kwargs):
        try:
            # Decodificar los datos JSON del body
            data = json.loads(request.body)
            
            # Validar que el objetivo existe
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_OBJETIVOS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Objetivo no encontrado'
                }, status=404)

            # Actualizar el objetivo
            update_query = """
                UPDATE RRHH_OBJETIVOS 
                SET descripcion = ?,
                    fecha_inicio = ?,
                    fecha_fin = ?,
                    indicador = ?,
                    meta = ?,
                    no_cumple = ?,
                    cumple = ?,
                    excede = ?,
                    sobresaliente = ?
                WHERE id = ?
            """
            
            cursor.execute(update_query, [
                data['descripcion'],
                data['fecha_inicio'],
                data['fecha_fin'],
                data['indicador'],
                data['meta'],
                data.get('no_cumple', 0),
                data.get('cumple', 0),
                data.get('excede', 0),
                data.get('sobresaliente', 0),
                id
            ])
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Objetivo actualizado correctamente',
                'data': {
                    'id': id,
                    'descripcion': data['descripcion'],
                    'fecha_inicio': data['fecha_inicio'],
                    'fecha_fin': data['fecha_fin'],
                    'indicador': data['indicador'],
                    'meta': data['meta'],
                    'no_cumple': data.get('no_cumple', 0),
                    'cumple': data.get('cumple', 0),
                    'excede': data.get('excede', 0),
                    'sobresaliente': data.get('sobresaliente', 0)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            }, status=400)
            
        except KeyError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Falta el campo requerido: {str(e)}'
            }, status=400)
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


    
    
#==============================================================================================
# EVALUACIONES DE COMPETENCIAS
#==============================================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CompetenciasEvaluacionDetailView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            id_evaluacion = data.get('id_evaluacion')
            competencias = data.get('competencias', [])
            
            # Validar que exista id_evaluacion
            if not id_evaluacion:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El ID de evaluación es requerido'
                }, status=400)
            
            # Validar que haya al menos una competencia
            if not competencias:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Debe enviar al menos una competencia'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            try:
                # Insertar cada competencia
                for competencia in competencias:
                    cursor.execute("""
                        INSERT INTO RRHH_COMPETENCIAS (
                            id_evaluacion,
                            id_tipo_competencia,
                            meta,
                            comentarios,
                            no_cumple,
                            cumple,
                            excede,
                            sobresaliente,
                            estado,
                            fecha_inicio,
                            fecha_fin
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?
                        )
                    """, [
                        id_evaluacion,
                        competencia['id_tipo_competencia'],
                        competencia['meta'],
                        competencia['comentarios'],
                        competencia['no_cumple'],
                        competencia['cumple'],
                        competencia['excede'],
                        competencia['sobresaliente'],
                        competencia['fecha_inicio'],
                        competencia['fecha_fin']
                    ])
                
                cursor.commit()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Competencias guardadas correctamente'
                })
                
            except Exception as e:
                # Si hay error, hacer rollback
                cursor.rollback()
                print(f"Error al guardar competencias: {str(e)}")
                raise e
                
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error al procesar la solicitud: {str(e)}'
            }, status=500)
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Verificar si se proporcionó un ID específico
            competencia_id = kwargs.get('id')
            
            # Obtener el parámetro id_evaluacion de la query string
            id_evaluacion = request.GET.get('id_evaluacion')
            
            if competencia_id:
                # Si hay ID, ejecutar consulta para una competencia específica
                cursor.execute("""
                    SELECT 
                        comp.id,
                        comp.id_evaluacion,
                        u.first_name as nombre_evaluado,
                        u.last_name as apellido_evaluado,
                        tc.id as id_tipo_competencia,
                        tc.nombre as nombre_competencia,
                        comp.meta,
                        comp.comentarios,
                        e.periodo,
                        a.nombre_area,
                        comp.fecha_inicio,
						comp.fecha_fin,
                        comp.no_cumple,
                        comp.cumple,
                        comp.excede,
                        comp.sobresaliente,
                        comp.estado
                    FROM RRHH_COMPETENCIAS comp
                    INNER JOIN RRHH_EVALUACIONES e ON comp.id_evaluacion = e.id
                    INNER JOIN user_user u ON e.id_evaluado = u.id
                    INNER JOIN AREA a ON e.id_area = a.id_area
                    INNER JOIN RRHH_TIPOS_COMPETENCIAS tc ON comp.id_tipo_competencia = tc.id
                    WHERE comp.id = ?
                """, [competencia_id])
            elif id_evaluacion:
                # Si hay ID de evaluación, obtener todas las competencias de esa evaluación
                cursor.execute("""
                    SELECT 
                        comp.id,
                        comp.id_evaluacion,
                        u.first_name as nombre_evaluado,
                        u.last_name as apellido_evaluado,
                        tc.id as id_tipo_competencia,
                        tc.nombre as nombre_competencia,
                        comp.meta,
                        comp.comentarios,
                        e.periodo,
                        a.nombre_area,
                        comp.fecha_inicio,
						comp.fecha_fin,
                        comp.no_cumple,
                        comp.cumple,
                        comp.excede,
                        comp.sobresaliente,
                        comp.estado
                    FROM RRHH_COMPETENCIAS comp
                    INNER JOIN RRHH_EVALUACIONES e ON comp.id_evaluacion = e.id
                    INNER JOIN user_user u ON e.id_evaluado = u.id
                    INNER JOIN AREA a ON e.id_area = a.id_area
                    INNER JOIN RRHH_TIPOS_COMPETENCIAS tc ON comp.id_tipo_competencia = tc.id
                    WHERE comp.id_evaluacion = ? AND comp.estado = 1
                    ORDER BY comp.id
                """, [id_evaluacion])
            else:
                # Si no hay ID, ejecutar el procedimiento para todos
                cursor.execute("EXEC RRHH_EV_COMPETENCIAS_MEJORA 17")
            
            # Obtener los resultados
            columns = [column[0] for column in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                
                # Convertir fechas a formato string para JSON si existen y no son None
                if 'fecha_inicio' in result and result['fecha_inicio']:
                    result['fecha_inicio'] = result['fecha_inicio'].strftime('%Y-%m-%d')
                if 'fecha_fin' in result and result['fecha_fin']:
                    result['fecha_fin'] = result['fecha_fin'].strftime('%Y-%m-%d')
                
                # Convertir el campo periodo a formato de fecha si existe y no es None
                if 'periodo' in result and result['periodo']:
                    try:
                        result['periodo'] = result['periodo'].strftime('%Y-%m-%d')
                    except AttributeError:
                        result['periodo'] = result['periodo']
                
                # Asegurar que los campos numéricos sean números
                for field in ['no_cumple', 'cumple', 'excede', 'sobresaliente']:
                    if field in result:
                        result[field] = int(result[field]) if result[field] is not None else 0
                
                # Asegurar que estado sea booleano
                if 'estado' in result:
                    result['estado'] = bool(result['estado'])
                
                results.append(result)
                
            return JsonResponse({
                'status': 'success',
                'message': 'Datos obtenidos correctamente',
                'data': results
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error', 
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()
    

    def put(self, request, id, *args, **kwargs):
        try:
            # Decodificar los datos JSON del body
            data = json.loads(request.body)
            
            # Validar que la competencia existe
            cursor = connection_portalaei.cursor()
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_COMPETENCIAS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Competencia no encontrada'
                }, status=404)

            # Actualizar la competencia
            update_query = """
                UPDATE RRHH_COMPETENCIAS 
                SET id_tipo_competencia = ?,
                    meta = ?,
                    comentarios = ?,
                    no_cumple = ?,
                    cumple = ?,
                    excede = ?,
                    sobresaliente = ?
                WHERE id = ?
            """
            
            cursor.execute(update_query, [
                data['id_tipo_competencia'],
                data['meta'],
                data['comentarios'],
                data.get('no_cumple', 0),
                data.get('cumple', 0),
                data.get('excede', 0),
                data.get('sobresaliente', 0),
                id
            ])
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Competencia actualizada correctamente',
                'data': {
                    'id': id,
                    'id_tipo_competencia': data['id_tipo_competencia'],
                    'meta': data['meta'],
                    'comentarios': data['comentarios'],
                    'no_cumple': data.get('no_cumple', 0),
                    'cumple': data.get('cumple', 0),
                    'excede': data.get('excede', 0),
                    'sobresaliente': data.get('sobresaliente', 0)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Datos JSON inválidos'
            }, status=400)
            
        except KeyError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Falta el campo requerido: {str(e)}'
            }, status=400)
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def delete(self, request, id, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # 1. Verificar si la competencia existe
            cursor.execute("""
                SELECT id_evaluacion 
                FROM RRHH_COMPETENCIAS 
                WHERE id = ?
            """, [id])
            
            result = cursor.fetchone()
            if not result:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Competencia no encontrada'
                }, status=404)
                
            id_evaluacion = result[0]
            
            # 2. Eliminar solo la competencia
            cursor.execute("""
                DELETE FROM RRHH_COMPETENCIAS 
                WHERE id = ?
            """, [id])
            
            connection_portalaei.commit()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Competencia eliminada correctamente',
                'data': {
                    'competencia_id': id,
                    'evaluacion_id': id_evaluacion,
                    'evaluacion_eliminada': False  # Siempre será False ya que no eliminamos la evaluación
                }
            })
            
        except Exception as e:
            if cursor:
                connection_portalaei.rollback()
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()




####################################################################################################################################
# FASE INTERMEDIA
####################################################################################################################################


#Api para la fase intermedia tabla principal
@method_decorator(csrf_exempt, name='dispatch')
class FaseIntermediaEvaluacionesView(View):
    """
    Vista para manejar la fase intermedia de evaluaciones de desempeño
    Permite consultar evaluaciones con porcentajes de avance de objetivos y competencias
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros opcionales
            id_area = request.GET.get('id_area')
            id_evaluacion = request.GET.get('id_evaluacion')
            campania = request.GET.get('campania', '')
            
            if id_evaluacion:
                # Si se solicita una evaluación específica, usar el procedimiento de detalles
                cursor.execute("EXEC SP_DETALLE_EVALUACION_FASE_INTERMEDIA ?", [id_evaluacion])
                
                # Obtener información general de la evaluación
                columns = [column[0] for column in cursor.description]
                evaluacion_info = cursor.fetchone()
                
                if not evaluacion_info:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Evaluación no encontrada'
                    }, status=404)
                
                evaluacion_data = dict(zip(columns, evaluacion_info))
                
                # Obtener objetivos (segundo resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    obj_columns = [column[0] for column in cursor.description]
                    objetivos = []
                    for row in cursor.fetchall():
                        objetivo = dict(zip(obj_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                            objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                        if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                            objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                        objetivos.append(objetivo)
                else:
                    objetivos = []
                
                # Obtener competencias (tercer resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    comp_columns = [column[0] for column in cursor.description]
                    competencias = []
                    for row in cursor.fetchall():
                        competencia = dict(zip(comp_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in competencia and competencia['fecha_inicio']:
                            competencia['fecha_inicio'] = competencia['fecha_inicio']
                        if 'fecha_fin' in competencia and competencia['fecha_fin']:
                            competencia['fecha_fin'] = competencia['fecha_fin']
                        competencias.append(competencia)
                else:
                    competencias = []
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Detalles de evaluación obtenidos correctamente',
                    'data': {
                        'evaluacion': evaluacion_data,
                        'objetivos': objetivos,
                        'competencias': competencias
                    }
                })
                
            else:
                # Obtener lista general de evaluaciones para la fase intermedia
                if id_area and campania:
                    try:
                        # Extraer solo el año de la campaña
                        year = campania.replace('CAMP', '') if 'CAMP' in str(campania) else campania
                        cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES ?, ?", [id_area, year])
                    except:
                        # Si falla con campaña, intentar sin ella
                        cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES ?", [id_area])
                elif id_area:
                    cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES ?", [id_area])
                else:
                    cursor.execute("EXEC SP_FASE_INTERMEDIA_EVALUACIONES")
                
                # Obtener los nombres de las columnas
                columns = [column[0] for column in cursor.description]
                
                # Convertir los resultados a una lista de diccionarios
                evaluaciones = []
                for row in cursor.fetchall():
                    evaluacion = dict(zip(columns, row))
                    
                    # Convertir fecha a string para JSON si existe
                    if 'fecha_evaluacion' in evaluacion and evaluacion['fecha_evaluacion']:
                        evaluacion['fecha_evaluacion'] = evaluacion['fecha_evaluacion'].strftime('%Y-%m-%d')
                    
                    # Asegurar que los porcentajes sean números enteros
                    for field in ['porcentaje_objetivos', 'porcentaje_competencias', 'porcentaje_general']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(float(evaluacion[field]))
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que los contadores sean números enteros
                    for field in ['total_objetivos', 'objetivos_con_avance', 'total_competencias', 'competencias_con_avance']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(evaluacion[field])
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que el estado sea booleano
                    if 'estado' in evaluacion:
                        evaluacion['estado'] = bool(evaluacion['estado'])
                    
                    evaluaciones.append(evaluacion)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluaciones de fase intermedia obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'filtros_aplicados': {
                        'id_area': id_area
                    }
                })
                
        except Exception as e:
            print(f"Error en FaseIntermediaEvaluacionesView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener datos de fase intermedia: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


#Api para los detalles de la fase intermedia


@method_decorator(csrf_exempt, name='dispatch')
class DetallesEvaluacionModalView(View):
    """
    Vista para obtener detalles de objetivos o competencias para el modal de avance rápido
    Ejecuta el procedimiento almacenado SP_OBTENER_DETALLES_EVALUACION_MODAL
    
    Parámetros:
    - id_evaluacion: ID de la evaluación (requerido)
    - tipo: Tipo de tabla (1 = Objetivos, 2 = Competencias) (requerido)
    """
    

    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros de la URL
            id_evaluacion = request.GET.get('id_evaluacion')
            tipo_tabla = request.GET.get('tipo')  # 1 = Objetivos, 2 = Competencias
            cargar_comentarios = request.GET.get('cargar_comentarios')  # Para cargar solo comentarios
            
            # Si se solicita cargar solo comentarios
            if cargar_comentarios == 'true' and id_evaluacion:
                try:
                    id_evaluacion_int = int(id_evaluacion)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El parámetro id_evaluacion debe ser un número válido'
                    }, status=400)
                
                # Consultar comentarios de la tabla RRHH_EVALUACIONES
                cursor.execute("""
                    SELECT 
                        comentarios_objetivos_general,
                        comentarios_competencias_general
                    FROM RRHH_EVALUACIONES 
                    WHERE id = ? AND estado = 1
                """, [id_evaluacion_int])
                
                resultado = cursor.fetchone()
                
                if resultado:
                    comentarios = {
                        'comentarios_objetivos_general': resultado[0] or '',
                        'comentarios_competencias_general': resultado[1] or ''
                    }
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Comentarios obtenidos correctamente',
                        'comentarios': comentarios,
                        'id_evaluacion': id_evaluacion_int
                    })
                else:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No se encontraron comentarios para esta evaluación',
                        'comentarios': {
                            'comentarios_objetivos_general': '',
                            'comentarios_competencias_general': ''
                        },
                        'id_evaluacion': id_evaluacion_int
                    })
            
            # Validar parámetros requeridos para obtener detalles
            if not id_evaluacion or not tipo_tabla:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los parámetros id_evaluacion y tipo'
                }, status=400)
            
            # Validar que sean números válidos
            try:
                id_evaluacion_int = int(id_evaluacion)
                tipo_tabla_int = int(tipo_tabla)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Los parámetros id_evaluacion y tipo deben ser números válidos'
                }, status=400)
            
            # Validar que tipo_tabla sea 1 o 2
            if tipo_tabla_int not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El parámetro tipo debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            print(f"Ejecutando procedimiento con: id_evaluacion={id_evaluacion_int}, tipo_tabla={tipo_tabla_int}")
            
            # Ejecutar el procedimiento almacenado
            cursor.execute(
                "EXEC SP_OBTENER_DETALLES_EVALUACION_MODAL @id_evaluacion = ?, @tipo_tabla = ?", 
                [id_evaluacion_int, tipo_tabla_int]
            )
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(columns, row))
                
                # Procesar fechas para objetivos
                if tipo_tabla_int == 1:  # Objetivos
                    # Convertir fechas a string si existen y no son None
                    for fecha_field in ['fecha_inicio', 'fecha_fin']:
                        if fecha_field in detalle and detalle[fecha_field]:
                            if hasattr(detalle[fecha_field], 'strftime'):
                                detalle[fecha_field] = detalle[fecha_field].strftime('%Y-%m-%d')
                    
                    # Mantener fechas formateadas como string
                    for formato_field in ['fecha_inicio_formato', 'fecha_fin_formato']:
                        if formato_field in detalle and detalle[formato_field]:
                            detalle[formato_field] = str(detalle[formato_field])
                
                # Asegurar que los porcentajes sean números enteros
                if 'porcentaje_actual' in detalle:
                    detalle['porcentaje_actual'] = int(detalle['porcentaje_actual']) if detalle['porcentaje_actual'] is not None else 0
                
                # Asegurar que las puntuaciones sean números enteros
                for field in ['puntuacion_no_cumple', 'puntuacion_cumple', 'puntuacion_excede', 'puntuacion_sobresaliente']:
                    if field in detalle:
                        detalle[field] = int(detalle[field]) if detalle[field] is not None else 0
                
                # Asegurar que campos numéricos específicos sean enteros
                for field in ['duracion_dias', 'dias_restantes']:
                    if field in detalle and detalle[field] is not None:
                        detalle[field] = int(detalle[field])
                
                detalles.append(detalle)
            
            # Determinar el nombre del tipo para la respuesta
            tipo_nombre = "objetivos" if tipo_tabla_int == 1 else "competencias"
            
            print(f"Procedimiento ejecutado correctamente. Registros encontrados: {len(detalles)}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'{tipo_nombre.title()} obtenidos correctamente',
                'data': detalles,
                'total_registros': len(detalles),
                'id_evaluacion': id_evaluacion_int,
                'tipo': tipo_nombre
            })
            
        except Exception as e:
            print(f"Error en DetallesEvaluacionModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener detalles: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    

    def put(self, request, *args, **kwargs):
        """
        Actualizar porcentajes de avance para múltiples objetivos o competencias
        Incluye actualización de comentarios generales en la tabla RRHH_EVALUACIONES
        
        Estructura esperada del JSON:
        {
            "tipo": 1 o 2 (1=Objetivos, 2=Competencias),
            "id_evaluacion": 189,
            "actualizaciones": [
                {
                    "id": 123,
                    "porcentaje_avance": 85
                    "comentarios": "Comentarios sobre el objetivo 123"
                },
                {
                    "id": 124,
                    "porcentaje_avance": 70,
                    "comentarios": "Comentarios sobre el objetivo 124"
                }
            ],
            "comentarios_objetivos_general": "Comentario general para objetivos...",
            "comentarios_competencias_general": "Comentario general para competencias..."
        }
        """
        cursor = None
        try:
            # Parsear los datos JSON del request
            data = json.loads(request.body)
            
            # Validar estructura básica de datos
            if 'tipo' not in data or 'actualizaciones' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los campos "tipo" y "actualizaciones"'
                }, status=400)
            
            tipo_tabla = data['tipo']
            actualizaciones = data['actualizaciones']
            id_evaluacion = data.get('id_evaluacion')
            
            
            # Obtener comentarios generales del request
            comentarios_objetivos_general = data.get('comentarios_objetivos_general', '')
            comentarios_competencias_general = data.get('comentarios_competencias_general', '')
            
            # Validar tipo de tabla
            if tipo_tabla not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El campo "tipo" debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            # Validar que hay actualizaciones
            if not actualizaciones or not isinstance(actualizaciones, list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requiere al menos una actualización en el array "actualizaciones"'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            # Determinar tabla y campo según el tipo
            if tipo_tabla == 1:  # Objetivos
                tabla = "RRHH_OBJETIVOS"
                id_campo = "id"
            else:  # Competencias
                tabla = "RRHH_COMPETENCIAS"
                id_campo = "id"
            
            actualizaciones_exitosas = []
            actualizaciones_fallidas = []
            
            # Procesar cada actualización de porcentajes
            for actualizacion in actualizaciones:
                try:
                    # Validar estructura de cada actualización
                    if 'id' not in actualizacion or 'porcentaje_avance' not in actualizacion:
                        actualizaciones_fallidas.append({
                            'registro': actualizacion,
                            'error': 'Faltan campos "id" o "porcentaje_avance"'
                        })
                        continue
                    
                    registro_id = actualizacion['id']
                    porcentaje_avance = actualizacion['porcentaje_avance']
                    
                    
                    # Validar que el ID sea un número válido
                    try:
                        registro_id = int(registro_id)
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'ID debe ser un número válido'
                        })
                        continue
                    
                    # Validar que el porcentaje esté en el rango válido
                    try:
                        porcentaje_avance = float(porcentaje_avance)
                        if porcentaje_avance < 0 or porcentaje_avance > 100:
                            actualizaciones_fallidas.append({
                                'id': registro_id,
                                'error': 'El porcentaje debe estar entre 0 y 100'
                            })
                            continue
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'El porcentaje debe ser un número válido'
                        })
                        continue
                    
                    # Verificar que el registro existe
                    cursor.execute(f"""
                        SELECT {id_campo} FROM {tabla} 
                        WHERE {id_campo} = ? AND estado = 1
                    """, [registro_id])
                    
                    if not cursor.fetchone():
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': f'{"Objetivo" if tipo_tabla == 1 else "Competencia"} no encontrado o inactivo'
                        })
                        continue
                    
                    # Realizar la actualización del porcentaje
                    
                    #agrego YERSON
                    if tipo_tabla == 1:  # Objetivos
                        comentarios_objetivo = actualizacion.get('comentarios_objetivos', '')
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porc_cumplimiento = ?, comentarios_objetivos = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_avance, comentarios_objetivo, registro_id])
                    else:  # Competencias
                        comentarios_competencia = actualizacion.get('comentarios_competencias', '')
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porc_cumplimiento = ?, comentarios_competencias = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_avance, comentarios_competencia, registro_id])
                        
                    #cursor.execute(f"""
                     #   UPDATE {tabla} 
                      #  SET porc_cumplimiento = ?
                       # WHERE {id_campo} = ?
                    #""", [porcentaje_avance, registro_id])
                    
                    # Verificar que se actualizó al menos una fila
                    if cursor.rowcount > 0:
                        actualizaciones_exitosas.append({
                            'id': registro_id,
                            'porcentaje_anterior': None,  # Podríamos obtenerlo antes de la actualización si es necesario
                            'porcentaje_nuevo': porcentaje_avance,
                            'comentarios_objetivos': comentarios_objetivo if tipo_tabla == 1 else None
                        })
                    else:
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'No se pudo actualizar el registro'
                        })
                    
                except Exception as e:
                    actualizaciones_fallidas.append({
                        'id': actualizacion.get('id', 'desconocido'),
                        'error': f'Error al procesar actualización: {str(e)}'
                    })
                    continue
            
            # Actualizar comentarios generales en la tabla RRHH_EVALUACIONES
            comentarios_actualizados = False
            if id_evaluacion:
                try:
                    # Verificar que la evaluación existe
                    cursor.execute("""
                        SELECT id FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion])
                    
                    if cursor.fetchone():
                        # Actualizar comentarios según el tipo
                        if tipo_tabla == 1:  # Objetivos
                            cursor.execute("""
                                UPDATE RRHH_EVALUACIONES 
                                SET comentarios_objetivos_general = ?
                                WHERE id = ?
                            """, [comentarios_objetivos_general, id_evaluacion])
                        else:  # Competencias
                            cursor.execute("""
                                UPDATE RRHH_EVALUACIONES 
                                SET comentarios_competencias_general = ?
                                WHERE id = ?
                            """, [comentarios_competencias_general, id_evaluacion])
                        
                        if cursor.rowcount > 0:
                            comentarios_actualizados = True
                            print(f"Comentarios generales actualizados para evaluación {id_evaluacion}")
                    else:
                        print(f"Evaluación {id_evaluacion} no encontrada o inactiva")
                        
                except Exception as e:
                    print(f"Error al actualizar comentarios generales: {str(e)}")
                    # No fallar toda la operación por comentarios, solo registrar el error
            
            # Confirmar todas las transacciones si hay al menos una actualización exitosa
            if actualizaciones_exitosas or comentarios_actualizados:
                connection_portalaei.commit()
            
            # Determinar el estado de la respuesta
            total_actualizaciones = len(actualizaciones)
            exitosas = len(actualizaciones_exitosas)
            fallidas = len(actualizaciones_fallidas)
            
            if exitosas == total_actualizaciones:
                status_code = 200
                message = f"Todas las actualizaciones fueron exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales actualizados"
                status = 'success'
            elif exitosas > 0:
                status_code = 207  # Multi-Status
                message = f"Actualizaciones parcialmente exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales actualizados"
                status = 'partial_success'
            else:
                if comentarios_actualizados:
                    status_code = 200
                    message = "Comentarios generales actualizados correctamente"
                    status = 'success'
                else:
                    status_code = 400
                    message = f"Ninguna actualización fue exitosa (0/{total_actualizaciones})"
                    status = 'error'
            
            tipo_nombre = "objetivos" if tipo_tabla == 1 else "competencias"
            
            print(f"Actualización de {tipo_nombre}: {exitosas} exitosas, {fallidas} fallidas, comentarios: {comentarios_actualizados}")
            
            return JsonResponse({
                'status': status,
                'message': message,
                'data': {
                    'tipo': tipo_nombre,
                    'total_procesadas': total_actualizaciones,
                    'exitosas': exitosas,
                    'fallidas': fallidas,
                    'comentarios_actualizados': comentarios_actualizados,
                    'id_evaluacion': id_evaluacion,
                    'actualizaciones_exitosas': actualizaciones_exitosas,
                    'actualizaciones_fallidas': actualizaciones_fallidas
                }
            }, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)
            
        except Exception as e:
            # En caso de error general, hacer rollback
            if cursor:
                try:
                    connection_portalaei.rollback()
                except:
                    pass
            
            print(f"Error en PUT DetallesEvaluacionModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()


# ============================================
#   FASE FINAL – LOGISTICA
# ============================================

# API para la fase final tabla principal
@method_decorator(csrf_exempt, name='dispatch')
class FaseFinalEvaluacionesContaView(View):
    """
    Vista para manejar la fase final de evaluaciones de desempeño
    Permite consultar evaluaciones con porcentajes de avance final de objetivos y competencias
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros opcionales
            id_area = request.GET.get('id_area')
            id_evaluacion = request.GET.get('id_evaluacion')
            campania = request.GET.get('campania', '')
            
            if id_evaluacion:
                # Si se solicita una evaluación específica, usar el procedimiento de detalles
                cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES ?", [id_evaluacion])
                
                # Obtener información general de la evaluación
                columns = [column[0] for column in cursor.description]
                evaluacion_info = cursor.fetchone()
                
                if not evaluacion_info:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Evaluación no encontrada'
                    }, status=404)
                
                evaluacion_data = dict(zip(columns, evaluacion_info))
                
                # Obtener objetivos (segundo resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    obj_columns = [column[0] for column in cursor.description]
                    objetivos = []
                    for row in cursor.fetchall():
                        objetivo = dict(zip(obj_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in objetivo and objetivo['fecha_inicio']:
                            objetivo['fecha_inicio'] = objetivo['fecha_inicio'].strftime('%Y-%m-%d')
                        if 'fecha_fin' in objetivo and objetivo['fecha_fin']:
                            objetivo['fecha_fin'] = objetivo['fecha_fin'].strftime('%Y-%m-%d')
                        objetivos.append(objetivo)
                else:
                    objetivos = []
                
                # Obtener competencias (tercer resultado del procedimiento)
                cursor.nextset()
                if cursor.description:
                    comp_columns = [column[0] for column in cursor.description]
                    competencias = []
                    for row in cursor.fetchall():
                        competencia = dict(zip(comp_columns, row))
                        # Convertir fechas a string si existen
                        if 'fecha_inicio' in competencia and competencia['fecha_inicio']:
                            competencia['fecha_inicio'] = competencia['fecha_inicio']
                        if 'fecha_fin' in competencia and competencia['fecha_fin']:
                            competencia['fecha_fin'] = competencia['fecha_fin']
                        competencias.append(competencia)
                else:
                    competencias = []
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Detalles de evaluación final obtenidos correctamente',
                    'data': {
                        'evaluacion': evaluacion_data,
                        'objetivos': objetivos,
                        'competencias': competencias
                    }
                })
                
            else:
                # Obtener lista general de evaluaciones para la fase final
                if id_area and campania:
                    try:
                        # Extraer solo el año de la campaña
                        year = campania.replace('CAMP', '') if 'CAMP' in str(campania) else campania
                        cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES ?, ?", [id_area, year])
                    except:
                        # Si falla con campaña, intentar sin ella
                        cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES ?", [id_area])
                elif id_area:
                    cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES ?", [id_area])
                else:
                    cursor.execute("EXEC SP_FASE_FINAL_EVALUACIONES")
                
                # Obtener los nombres de las columnas
                columns = [column[0] for column in cursor.description]
                
                # Convertir los resultados a una lista de diccionarios
                evaluaciones = []
                for row in cursor.fetchall():
                    evaluacion = dict(zip(columns, row))
                    
                    # Convertir fecha a string para JSON si existe
                    if 'fecha_evaluacion' in evaluacion and evaluacion['fecha_evaluacion']:
                        evaluacion['fecha_evaluacion'] = evaluacion['fecha_evaluacion'].strftime('%Y-%m-%d')
                    
                    # Asegurar que los porcentajes sean números enteros (usar los mismos campos que fase intermedia)
                    for field in ['porcentaje_objetivos', 'porcentaje_competencias', 'porcentaje_general']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(float(evaluacion[field]))
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que los contadores sean números enteros
                    for field in ['total_objetivos', 'objetivos_con_avance', 'total_competencias', 'competencias_con_avance']:
                        if field in evaluacion and evaluacion[field] is not None:
                            evaluacion[field] = int(evaluacion[field])
                        else:
                            evaluacion[field] = 0
                    
                    # Asegurar que el estado sea booleano
                    if 'estado' in evaluacion:
                        evaluacion['estado'] = bool(evaluacion['estado'])
                    
                    evaluaciones.append(evaluacion)
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Evaluaciones de fase final obtenidas correctamente',
                    'data': evaluaciones,
                    'total_evaluaciones': len(evaluaciones),
                    'filtros_aplicados': {
                        'id_area': id_area
                    },
                    'debug_info': {
                        'columns_found': columns,
                        'sample_data': evaluaciones[0] if evaluaciones else None
                    }
                })
                
        except Exception as e:
            print(f"Error en FaseFinalEvaluacionesView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener datos de fase final: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()




# API para los detalles de la fase final
@method_decorator(csrf_exempt, name='dispatch')
class DetallesEvaluacionFinalContaView(View):
    """
    Vista para obtener detalles finales de objetivos o competencias para el modal de avance final
    Ejecuta el procedimiento almacenado SP_OBTENER_DETALLES_EVALUACION_FINAL_MODAL
    
    Parámetros:
    - id_evaluacion: ID de la evaluación (requerido)
    - tipo: Tipo de tabla (1 = Objetivos, 2 = Competencias) (requerido)
    """
    
    def get(self, request, *args, **kwargs):
        cursor = None
        try:
            cursor = connection_portalaei.cursor()
            
            # Obtener parámetros de la URL
            id_evaluacion = request.GET.get('id_evaluacion')
            tipo_tabla = request.GET.get('tipo')  # 1 = Objetivos, 2 = Competencias
            cargar_comentarios = request.GET.get('cargar_comentarios')  # Para cargar solo comentarios finales
            
            # Si se solicita cargar solo comentarios finales
            if cargar_comentarios == 'true' and id_evaluacion:
                try:
                    id_evaluacion_int = int(id_evaluacion)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'El parámetro id_evaluacion debe ser un número válido'
                    }, status=400)
                
                # Consultar comentarios finales de la tabla RRHH_EVALUACIONES
                try:
                    cursor.execute("""
                        SELECT 
                            comentarios_objetivos_general_final,
                            comentarios_competencias_general_final
                        FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion_int])
                except Exception as query_error:
                    print(f"Error al consultar campos específicos, usando campos estándar: {query_error}")
                    # Si falla, usar campos estándar
                    cursor.execute("""
                        SELECT 
                            comentarios_objetivos_general,
                            comentarios_competencias_general
                        FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion_int])
                
                resultado = cursor.fetchone()
                
                if resultado:
                    comentarios = {
                        'comentarios_objetivos_general_final': resultado[0] or '',
                        'comentarios_competencias_general_final': resultado[1] or ''
                    }
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Comentarios finales obtenidos correctamente',
                        'comentarios': comentarios,
                        'id_evaluacion': id_evaluacion_int
                    })
                else:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'No se encontraron comentarios finales para esta evaluación',
                        'comentarios': {
                            'comentarios_objetivos_general_final': '',
                            'comentarios_competencias_general_final': ''
                        },
                        'id_evaluacion': id_evaluacion_int
                    })
            
            # Validar parámetros requeridos para obtener detalles
            if not id_evaluacion or not tipo_tabla:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los parámetros id_evaluacion y tipo'
                }, status=400)
            
            # Validar que sean números válidos
            try:
                id_evaluacion_int = int(id_evaluacion)
                tipo_tabla_int = int(tipo_tabla)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Los parámetros id_evaluacion y tipo deben ser números válidos'
                }, status=400)
            
            # Validar que tipo_tabla sea 1 o 2
            if tipo_tabla_int not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El parámetro tipo debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            print(f"Ejecutando procedimiento final con: id_evaluacion={id_evaluacion_int}, tipo_tabla={tipo_tabla_int}")
            
            # Ejecutar el mismo procedimiento almacenado que la fase intermedia
            cursor.execute(
                "EXEC SP_OBTENER_DETALLES_EVALUACION_MODAL @id_evaluacion = ?, @tipo_tabla = ?", 
                [id_evaluacion_int, tipo_tabla_int]
            )
            
            # Obtener los nombres de las columnas
            columns = [column[0] for column in cursor.description]
            # Convertir los resultados a una lista de diccionarios
            detalles = []
            for row in cursor.fetchall():
                detalle = dict(zip(columns, row))
                
                # Procesar fechas para objetivos
                if tipo_tabla_int == 1:  # Objetivos
                    # Convertir fechas a string si existen y no son None
                    for fecha_field in ['fecha_inicio', 'fecha_fin']:
                        if fecha_field in detalle and detalle[fecha_field]:
                            if hasattr(detalle[fecha_field], 'strftime'):
                                detalle[fecha_field] = detalle[fecha_field].strftime('%Y-%m-%d')
                    
                    # Mantener fechas formateadas como string
                    for formato_field in ['fecha_inicio_formato', 'fecha_fin_formato']:
                        if formato_field in detalle and detalle[formato_field]:
                            detalle[formato_field] = str(detalle[formato_field])
                
                # Asegurar que los porcentajes sean números enteros
                # Para fase final, usar el campo porc_etapa_final si existe, sino usar porcentaje_actual
                if 'porc_etapa_final' in detalle:
                    detalle['porc_etapa_final'] = int(detalle['porc_etapa_final']) if detalle['porc_etapa_final'] is not None else 0
                else:
                    # Si no existe porc_etapa_final, usar porcentaje_actual como base
                    detalle['porc_etapa_final'] = int(detalle.get('porcentaje_actual', 0)) if detalle.get('porcentaje_actual') is not None else 0
                
                if 'porcentaje_actual' in detalle:
                    detalle['porcentaje_actual'] = int(detalle['porcentaje_actual']) if detalle['porcentaje_actual'] is not None else 0
                
                # Asegurar que los campos de comentarios finales existen según el tipo
                if tipo_tabla_int == 1:  # Objetivos
                    if 'coment_objetivo_ff' not in detalle:
                        detalle['coment_objetivo_ff'] = ''  # Solo usar campo específico, sin fallback
                else:  # Competencias
                    if 'coment_competencia_ff' not in detalle:
                        detalle['coment_competencia_ff'] = ''  # Solo usar campo específico, sin fallback
                
                # Consulta adicional para obtener comentarios finales específicos de este registro
                try:
                    registro_id = detalle.get('id')
                    if registro_id:
                        tabla_consulta = "RRHH_OBJETIVOS" if tipo_tabla_int == 1 else "RRHH_COMPETENCIAS"
                        cursor_extra = connection_portalaei.cursor()
                        
                        # Usar el campo correcto según el tipo de tabla
                        if tipo_tabla_int == 1:  # Objetivos
                            cursor_extra.execute(f"""
                                SELECT coment_objetivo_ff, porc_etapa_final 
                                FROM {tabla_consulta} 
                                WHERE id = ? AND estado = 1
                            """, [registro_id])
                        else:  # Competencias
                            cursor_extra.execute(f"""
                                SELECT coment_competencia_ff, porc_etapa_final 
                                FROM {tabla_consulta} 
                                WHERE id = ? AND estado = 1
                            """, [registro_id])
                        
                        resultado_extra = cursor_extra.fetchone()
                        if resultado_extra:
                            # Sobreescribir con datos específicos de fase final (sin fallbacks)
                            if tipo_tabla_int == 1:  # Objetivos
                                detalle['coment_objetivo_ff'] = resultado_extra[0] or ''
                            else:  # Competencias
                                detalle['coment_competencia_ff'] = resultado_extra[0] or ''
                            if resultado_extra[1] is not None:
                                detalle['porc_etapa_final'] = int(resultado_extra[1])
                        cursor_extra.close()
                except Exception as e:
                    print(f"Error al consultar datos específicos de fase final: {e}")
                    # Continuar con los datos básicos
                
                # Asegurar que las puntuaciones sean números enteros
                for field in ['puntuacion_no_cumple', 'puntuacion_cumple', 'puntuacion_excede', 'puntuacion_sobresaliente']:
                    if field in detalle:
                        detalle[field] = int(detalle[field]) if detalle[field] is not None else 0
                
                # Asegurar que campos numéricos específicos sean enteros
                for field in ['duracion_dias', 'dias_restantes']:
                    if field in detalle and detalle[field] is not None:
                        detalle[field] = int(detalle[field])
                
                detalles.append(detalle)
            
            # Determinar el nombre del tipo para la respuesta
            tipo_nombre = "objetivos" if tipo_tabla_int == 1 else "competencias"
            
            print(f"Procedimiento final ejecutado correctamente. Registros encontrados: {len(detalles)}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'{tipo_nombre.title()} finales obtenidos correctamente',
                'data': detalles,
                'total_registros': len(detalles),
                'id_evaluacion': id_evaluacion_int,
                'tipo': tipo_nombre
            })
            
        except Exception as e:
            print(f"Error en DetallesEvaluacionFinalModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return JsonResponse({
                'status': 'error',
                'message': f'Error al obtener detalles finales: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()

    def put(self, request, *args, **kwargs):
        """
        Actualizar porcentajes de avance final para múltiples objetivos o competencias
        Incluye actualización de comentarios generales finales en la tabla RRHH_EVALUACIONES
        
        Estructura esperada del JSON:
        {
            "tipo": 1 o 2 (1=Objetivos, 2=Competencias),
            "id_evaluacion": 189,
            "actualizaciones": [
                {
                    "id": 123,
                    "porc_etapa_final": 85,
                    "coment_objetivo_ff": "Comentario final del objetivo"
                },
                {
                    "id": 124,
                    "porc_etapa_final": 70,
                    "coment_objetivo_ff": "Otro comentario final"
                }
            ],
            "comentarios_objetivos_general_final": "Comentario general final para objetivos...",
            "comentarios_competencias_general_final": "Comentario general final para competencias..."
        }
        """
        cursor = None
        try:
            # Parsear los datos JSON del request
            data = json.loads(request.body)
            
            # Validar estructura básica de datos
            if 'tipo' not in data or 'actualizaciones' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren los campos "tipo" y "actualizaciones"'
                }, status=400)
            
            tipo_tabla = data['tipo']
            actualizaciones = data['actualizaciones']
            id_evaluacion = data.get('id_evaluacion')
            
            # Obtener comentarios generales finales del request
            comentarios_objetivos_general_final = data.get('comentarios_objetivos_general_final', '')
            comentarios_competencias_general_final = data.get('comentarios_competencias_general_final', '')
            
            # Validar tipo de tabla
            if tipo_tabla not in [1, 2]:
                return JsonResponse({
                    'status': 'error',
                    'message': 'El campo "tipo" debe ser 1 (Objetivos) o 2 (Competencias)'
                }, status=400)
            
            # Validar que hay actualizaciones
            if not actualizaciones or not isinstance(actualizaciones, list):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requiere al menos una actualización en el array "actualizaciones"'
                }, status=400)
            
            cursor = connection_portalaei.cursor()
            
            # Determinar tabla y campo según el tipo
            if tipo_tabla == 1:  # Objetivos
                tabla = "RRHH_OBJETIVOS"
                id_campo = "id"
            else:  # Competencias
                tabla = "RRHH_COMPETENCIAS"
                id_campo = "id"
            
            actualizaciones_exitosas = []
            actualizaciones_fallidas = []
            
            # Procesar cada actualización de porcentajes finales
            for actualizacion in actualizaciones:
                try:
                    # Validar estructura de cada actualización
                    if 'id' not in actualizacion or 'porc_etapa_final' not in actualizacion:
                        actualizaciones_fallidas.append({
                            'registro': actualizacion,
                            'error': 'Faltan campos "id" o "porc_etapa_final"'
                        })
                        continue
                    
                    registro_id = actualizacion['id']
                    porcentaje_final = actualizacion['porc_etapa_final']
                    # Usar el campo correcto según el tipo de tabla
                    if tipo_tabla == 1:  # Objetivos
                        comentario_final = actualizacion.get('coment_objetivo_ff', '')
                    else:  # Competencias
                        comentario_final = actualizacion.get('coment_competencia_ff', '')
                    
                    # Validar que el ID sea un número válido
                    try:
                        registro_id = int(registro_id)
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'ID debe ser un número válido'
                        })
                        continue
                    
                    # Validar que el porcentaje esté en el rango válido
                    try:
                        porcentaje_final = float(porcentaje_final)
                        if porcentaje_final < 0 or porcentaje_final > 130:
                            actualizaciones_fallidas.append({
                                'id': registro_id,
                                'error': 'El porcentaje debe estar entre 0 y 130'
                            })
                            continue
                    except (ValueError, TypeError):
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'El porcentaje debe ser un número válido'
                        })
                        continue
                    
                    # Verificar que el registro existe
                    cursor.execute(f"""
                        SELECT {id_campo} FROM {tabla} 
                        WHERE {id_campo} = ? AND estado = 1
                    """, [registro_id])
                    
                    if not cursor.fetchone():
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': f'{"Objetivo" if tipo_tabla == 1 else "Competencia"} no encontrado o inactivo'
                        })
                        continue
                    
                    # Realizar la actualización del porcentaje final y comentario final
                    # Usar el campo correcto según el tipo de tabla
                    try:
                        if tipo_tabla == 1:  # Objetivos
                            cursor.execute(f"""
                                UPDATE {tabla} 
                                SET porc_etapa_final = ?, coment_objetivo_ff = ?
                                WHERE {id_campo} = ?
                            """, [porcentaje_final, comentario_final, registro_id])
                        else:  # Competencias
                            cursor.execute(f"""
                                UPDATE {tabla} 
                                SET porc_etapa_final = ?, coment_competencia_ff = ?
                                WHERE {id_campo} = ?
                            """, [porcentaje_final, comentario_final, registro_id])
                    except Exception as update_error:
                        print(f"Error al actualizar con campos específicos, intentando con campos estándar: {update_error}")
                        # Si falla, usar campos estándar de la fase intermedia
                        cursor.execute(f"""
                            UPDATE {tabla} 
                            SET porcentaje_actual = ?, comentarios = ?
                            WHERE {id_campo} = ?
                        """, [porcentaje_final, comentario_final, registro_id])
                    
                    # Verificar que se actualizó al menos una fila
                    if cursor.rowcount > 0:
                        # Usar el campo correcto en el log según el tipo de tabla
                        if tipo_tabla == 1:  # Objetivos
                            campo_comentario = 'coment_objetivo_ff'
                        else:  # Competencias
                            campo_comentario = 'coment_competencia_ff'
                        
                        actualizaciones_exitosas.append({
                            'id': registro_id,
                            'porc_etapa_final_anterior': None,
                            'porc_etapa_final_nuevo': porcentaje_final,
                            campo_comentario: comentario_final
                        })
                    else:
                        actualizaciones_fallidas.append({
                            'id': registro_id,
                            'error': 'No se pudo actualizar el registro'
                        })
                    
                except Exception as e:
                    actualizaciones_fallidas.append({
                        'id': actualizacion.get('id', 'desconocido'),
                        'error': f'Error al procesar actualización final: {str(e)}'
                    })
                    continue
            
            # Actualizar comentarios generales finales en la tabla RRHH_EVALUACIONES
            comentarios_actualizados = False
            if id_evaluacion:
                try:
                    # Verificar que la evaluación existe
                    cursor.execute("""
                        SELECT id FROM RRHH_EVALUACIONES 
                        WHERE id = ? AND estado = 1
                    """, [id_evaluacion])
                    
                    if cursor.fetchone():
                        # Actualizar comentarios finales según el tipo
                        try:
                            if tipo_tabla == 1:  # Objetivos
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_objetivos_general_final = ?
                                    WHERE id = ?
                                """, [comentarios_objetivos_general_final, id_evaluacion])
                            else:  # Competencias
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_competencias_general_final = ?
                                    WHERE id = ?
                                """, [comentarios_competencias_general_final, id_evaluacion])
                        except Exception as comment_error:
                            print(f"Error al actualizar comentarios específicos, usando campos estándar: {comment_error}")
                            # Si falla, usar campos estándar
                            if tipo_tabla == 1:  # Objetivos
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_objetivos_general = ?
                                    WHERE id = ?
                                """, [comentarios_objetivos_general_final, id_evaluacion])
                            else:  # Competencias
                                cursor.execute("""
                                    UPDATE RRHH_EVALUACIONES 
                                    SET comentarios_competencias_general = ?
                                    WHERE id = ?
                                """, [comentarios_competencias_general_final, id_evaluacion])
                        
                        if cursor.rowcount > 0:
                            comentarios_actualizados = True
                            print(f"Comentarios generales finales actualizados para evaluación {id_evaluacion}")
                    else:
                        print(f"Evaluación {id_evaluacion} no encontrada o inactiva")
                        
                except Exception as e:
                    print(f"Error al actualizar comentarios generales finales: {str(e)}")
                    # No fallar toda la operación por comentarios, solo registrar el error
            
            # Confirmar todas las transacciones si hay al menos una actualización exitosa
            if actualizaciones_exitosas or comentarios_actualizados:
                connection_portalaei.commit()
            
            # Determinar el estado de la respuesta
            total_actualizaciones = len(actualizaciones)
            exitosas = len(actualizaciones_exitosas)
            fallidas = len(actualizaciones_fallidas)
            
            if exitosas == total_actualizaciones:
                status_code = 200
                message = f"Todas las actualizaciones finales fueron exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales finales actualizados"
                status = 'success'
            elif exitosas > 0:
                status_code = 207  # Multi-Status
                message = f"Actualizaciones finales parcialmente exitosas ({exitosas}/{total_actualizaciones})"
                if comentarios_actualizados:
                    message += " y comentarios generales finales actualizados"
                status = 'partial_success'
            else:
                if comentarios_actualizados:
                    status_code = 200
                    message = "Comentarios generales finales actualizados correctamente"
                    status = 'success'
                else:
                    status_code = 400
                    message = f"Ninguna actualización final fue exitosa (0/{total_actualizaciones})"
                    status = 'error'
            
            tipo_nombre = "objetivos" if tipo_tabla == 1 else "competencias"
            
            print(f"Actualización final de {tipo_nombre}: {exitosas} exitosas, {fallidas} fallidas, comentarios: {comentarios_actualizados}")
            
            return JsonResponse({
                'status': status,
                'message': message,
                'data': {
                    'tipo': tipo_nombre,
                    'total_procesadas': total_actualizaciones,
                    'exitosas': exitosas,
                    'fallidas': fallidas,
                    'comentarios_actualizados': comentarios_actualizados,
                    'id_evaluacion': id_evaluacion,
                    'actualizaciones_exitosas': actualizaciones_exitosas,
                    'actualizaciones_fallidas': actualizaciones_fallidas
                }
            }, status=status_code)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Formato JSON inválido'
            }, status=400)
            
        except Exception as e:
            # En caso de error general, hacer rollback
            if cursor:
                try:
                    connection_portalaei.rollback()
                except:
                    pass
            
            print(f"Error en PUT DetallesEvaluacionFinalModalView: {str(e)}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            
            return JsonResponse({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}',
                'error_type': type(e).__name__
            }, status=500)
            
        finally:
            if cursor:
                cursor.close()



    
