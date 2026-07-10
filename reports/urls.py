"""reports URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from apps.contabilidad.views import *
from django.conf import settings



urlpatterns = [
	path('admin/', admin.site.urls),
    path('', include('apps.login.urls')),
    path('', include('apps.home.urls')),
    path('', include('apps.script.urls')),
    path('', include('apps.powerbi.urls')),
    path('', include('apps.user.urls')),
    path('rrhh/', include('apps.rrhh.urls')),
    path('contabilidad/', include('apps.contabilidad.urls')),
    path('', include('apps.TIC.urls')),
    path('', include('apps.FITOSANIDAD.urls')),
    path('costos/', include('apps.COSTOS.urls')),
    path('logistica/', include('apps.LOGISTICA.urls')),
    path('almacen/', include('apps.ALMACEN.urls')),
    path('legal/', include('apps.LEGAL.urls')),
    path('seguridad/', include('apps.SEGURIDAD.urls')),
    path('calidad/', include('apps.CALIDAD.urls')),
    path('evaluaciones/', include('apps.EVALUACIONES.urls')),
    path('aplicaciones/', include('apps.APLICACIONES.urls')),
    path('riego/', include('apps.RIEGO.urls')),
    path('produccionuva1/', include('apps.PRODUCCIONUVA1.urls')),
    path('produccionuva2/', include('apps.PRODUCCIONUVA2.urls')),
    path('produccionpalta/', include('apps.PRODUCCIONPALTA.urls')), 
    path('gerencia/', include('apps.GERENCIA.urls')),
    path('gerencia_produccion/', include('apps.GERENCIA_PRODUCCION.urls')),
    path('presupuesto-agricola/', include('apps.PresupuestoAgricola.urls')),
    path('cartillas-agricolas/', include('apps.cartillas_agricolas.urls')),
    path('riegopalta/', include('apps.RIEGO_PALTA.urls')),
    path('riegouva/', include('apps.RIEGO_UVA.urls')),
    path('marcadores/', include('apps.MARCADORES.urls')),
    path('controller_prod/', include('apps.CONTROLLER_PROD.urls')),
    path('salud/', include('apps.SALUD.urls')),
    path('sst/', include('apps.SST.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)