# views.py
import json
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.connection.connect_portalaei import connection_portalaei
from apps.utils.permissions import es_admin
from django.http import JsonResponse

class PresupuestoFundosView(TemplateView):
	template_name = 'PresupuestoAgricola/rrhh_fundos.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['es_admin'] = es_admin(self.request.user)
		try:
			cursor = connection_portalaei.cursor()
			cursor.execute("SELECT IDEMPRESA, DESCRIPCION FROM EMPRESA")
			empresas = [{'id': row[0], 'descripcion': row[1]} for row in cursor.fetchall()]
			cursor.close()
		except Exception:
			empresas = []
		context['empresas'] = empresas
		return context


@method_decorator(csrf_exempt, name='dispatch')
class PresupuestoFundoCRUDView(View):
    def get(self, request, id_fundo=None):
        try:
            cursor = connection_portalaei.cursor()
            if id_fundo:
                cursor.execute("SELECT ID_FUNDO, DESCRIPCION, ID_EMPRESA FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, row))
                    cursor.close()
                    return JsonResponse({'status': 'success', 'data': data})
                else:
                    cursor.close()
                    return JsonResponse({'status': 'error', 'message': 'Fundo no encontrado'}, status=404)
            else:
                cursor.execute("SELECT ID_FUNDO, DESCRIPCION, ID_EMPRESA FROM FUNDO")
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            id_fundo = data.get('ID_FUNDO') or data.get('id_fundo')
            descripcion = data.get('DESCRIPCION') or data.get('descripcion')
            id_empresa = data.get('ID_EMPRESA') or data.get('id_empresa')
            if id_fundo is None or str(id_fundo).strip() == '':
                return JsonResponse({'status': 'error', 'message': 'El campo ID_FUNDO es obligatorio.'}, status=400)
            if descripcion is None or str(descripcion).strip() == '':
                return JsonResponse({'status': 'error', 'message': 'El campo DESCRIPCION es obligatorio.'}, status=400)
            if id_empresa is None or str(id_empresa).strip() == '':
                return JsonResponse({'status': 'error', 'message': 'El campo ID_EMPRESA es obligatorio.'}, status=400)
            descripcion = str(descripcion).strip()
            id_fundo = str(id_fundo).strip()
            cursor = connection_portalaei.cursor()
            try:
                # Verificar si el ID_FUNDO ya existe
                cursor.execute("SELECT ID_FUNDO FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
                existing_fundo = cursor.fetchone()
                if existing_fundo:
                    cursor.close()
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Ya existe un fundo con el ID "{id_fundo}". Por favor, use un ID diferente.'
                    }, status=400)
                
                cursor.execute("""
                               INSERT INTO FUNDO (ID_FUNDO, DESCRIPCION, ID_EMPRESA)
                               VALUES (?, ?, ?)
                               """, [id_fundo, descripcion, id_empresa])
                connection_portalaei.commit()
                cursor.execute("SELECT ID_FUNDO, DESCRIPCION, ID_EMPRESA FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
                row = cursor.fetchone()
                columns = [col[0] for col in cursor.description]
                data = dict(zip(columns, row))
                cursor.close()
                return JsonResponse({'status': 'success', 'data': data})
            except Exception as e:
                connection_portalaei.rollback()
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def put(self, request, id_fundo):
        try:
            data = json.loads(request.body)
            descripcion = data.get('descripcion', '').strip()
            id_empresa = data.get('id_empresa')
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_FUNDO FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Fundo no encontrado'}, status=404)
            cursor.execute("""
                           UPDATE FUNDO
                           SET DESCRIPCION = ?,
                               ID_EMPRESA  = ?
                           WHERE ID_FUNDO = ?
                           """, [descripcion, id_empresa, id_fundo])
            connection_portalaei.commit()
            cursor.execute("SELECT ID_FUNDO, DESCRIPCION, ID_EMPRESA FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
            row = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            data = dict(zip(columns, row))
            cursor.close()
            return JsonResponse({'status': 'success', 'data': data})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    def delete(self, request, id_fundo):
        try:
            cursor = connection_portalaei.cursor()
            cursor.execute("SELECT ID_FUNDO FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
            if not cursor.fetchone():
                cursor.close()
                return JsonResponse({'status': 'error', 'message': 'Fundo no encontrado'}, status=404)
            cursor.execute("DELETE FROM FUNDO WHERE ID_FUNDO = ?", [id_fundo])
            connection_portalaei.commit()
            cursor.close()
            return JsonResponse({'status': 'success', 'message': 'Fundo eliminado correctamente'})
        except Exception as e:
            connection_portalaei.rollback()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)