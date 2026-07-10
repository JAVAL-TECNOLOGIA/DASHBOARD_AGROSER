from django.shortcuts import redirect
from django.urls import path, reverse

from .views import EvaluacionesCartillasView
from apps.cartillas_agricolas.services import get_areas_cartillas_agricolas


def redirect_evaluaciones(request):
    """Redirige /cartillas-agricolas/evaluaciones/ al primer área (compatibilidad)."""
    areas = get_areas_cartillas_agricolas()
    id_area = areas[0]['idArea'] if areas else 1
    return redirect(reverse('cartillas_por_area', kwargs={'id_area': id_area}))


urlpatterns = [
    path('', redirect_evaluaciones, name='evaluaciones_cartillas'),
]
