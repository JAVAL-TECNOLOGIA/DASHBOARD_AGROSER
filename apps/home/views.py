from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from apps.connection.connect_portalaei import connection_portalaei
from django.views.decorators.csrf import csrf_exempt


class HomeView(TemplateView):
    template_name = 'home/home.html'

class Error403(TemplateView):
    template_name = 'home/error-403.html'


@method_decorator(csrf_exempt, name='dispatch')
class UsuariosPortalView(View):
    def get(self, request, *args, **kwargs):
        try:
            cursor = connection_portalaei.cursor()
            
            # Ejecutar la consulta para obtener los usuarios
            cursor.execute("""
                SELECT [id]
                      ,[password]
                      ,[last_login]
                      ,[username]
                      ,[first_name]
                      ,[last_name]
                      ,[email]
                      ,[admin]
                      ,[active]
                      ,[is_superuser]
                FROM [PORTAL_AEI].[dbo].[user_user]
            """)
            
            # Obtener los nombres de las columnas
            columns = [col[0] for col in cursor.description]
            
            # Convertir los resultados a una lista de diccionarios
            usuarios = []
            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                # Convertir fechas a formato string para JSON si es necesario
                if 'last_login' in usuario and usuario['last_login']:
                    usuario['last_login'] = usuario['last_login'].strftime('%Y-%m-%d %H:%M:%S')
                usuarios.append(usuario)

            return JsonResponse({
                'status': 'success',
                'data': usuarios
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

        finally:
            if cursor:
                cursor.close()



