from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import *

urlpatterns = [
    path('', login_required(HomeView.as_view()), name='home'),
    path('error-403/', login_required(Error403.as_view()), name='error-403'),
    # API PARA OBTENER USUARIOS DEL PORTAL
    path('usuarios_portal/', UsuariosPortalView.as_view(), name='usuarios_portal'),
] 
