from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from django.contrib import messages

class UtilidadesSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si estamos en la página de utilidades
        if 'rrhh_consulta_utilidades' in request.path:
            # Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                return redirect('login')

            # Almacenar la URL original en la sesión
            request.session['utilidades_url'] = request.path

        # Si hay una URL de utilidades almacenada y se intenta acceder a otra ruta
        elif request.session.get('utilidades_url'):
            # Solo permitir logout y la URL original de utilidades
            if 'logout' not in request.path:
                return redirect(request.session.get('utilidades_url'))

        return self.get_response(request)
