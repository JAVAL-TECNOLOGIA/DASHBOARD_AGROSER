from django.shortcuts import redirect
from django.urls import path, include, reverse

from .api_views import AreasCartillasAPIView, PlantillasPorAreaAPIView
from .evaluaciones_cartillas.api_views import EvaluacionesAPIView
from .evaluaciones_cartillas.filtros_api import CartillasInitAPIView, CartillasFiltrosAPIView
from .evaluaciones_cartillas.views import EvaluacionesCartillasView
from .services import get_areas_cartillas_agricolas


def redirect_cartillas_root(request):
    """Redirige /cartillas-agricolas/ al primer área disponible o a id_area=1."""
    areas = get_areas_cartillas_agricolas()
    id_area = areas[0]['idArea'] if areas else 1
    return redirect(reverse('cartillas_por_area', kwargs={'id_area': id_area}))


urlpatterns = [
    path('', redirect_cartillas_root),
    path('<int:id_area>/', EvaluacionesCartillasView.as_view(), name='cartillas_por_area'),
    path('evaluaciones/', include('apps.cartillas_agricolas.evaluaciones_cartillas.urls')),
    path('api/areas/', AreasCartillasAPIView.as_view(), name='cartillas_api_areas'),
    path('api/plantillas/', PlantillasPorAreaAPIView.as_view(), name='cartillas_api_plantillas'),
    path('api/init/', CartillasInitAPIView.as_view(), name='cartillas_api_init'),
    path('api/filtros/', CartillasFiltrosAPIView.as_view(), name='cartillas_api_filtros'),
    path('api/evaluaciones/', EvaluacionesAPIView.as_view(), name='cartillas_evaluaciones_api'),
]
