"""
API Cartillas Agrícolas - Menú dinámico y filtros por área.
"""
from django.http import JsonResponse
from django.views import View

from .services import get_areas_cartillas_agricolas, get_plantillas_por_area


class AreasCartillasAPIView(View):
    """
    GET /cartillas-agricolas/api/areas/
    Retorna áreas con mostrar_en_cartillas_agricolas = 1.
    DTO: [{ idArea, nombreArea }, ...]
    """

    def get(self, request):
        try:
            areas = get_areas_cartillas_agricolas()
            return JsonResponse({'areas': areas})
        except Exception as e:
            return JsonResponse({'error': str(e), 'areas': []}, status=500)


class PlantillasPorAreaAPIView(View):
    """
    GET /cartillas-agricolas/api/plantillas/?id_area=X
    Retorna plantillas del área vía area_plantilla.
    DTO: [{ idPlantilla, nombrePlantilla }, ...]
    """

    def get(self, request):
        id_area_raw = request.GET.get('id_area')
        if not id_area_raw:
            return JsonResponse({'error': 'id_area es requerido', 'plantillas': []}, status=400)
        try:
            id_area = int(id_area_raw)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'id_area debe ser numérico', 'plantillas': []}, status=400)
        try:
            plantillas = get_plantillas_por_area(id_area)
            return JsonResponse({'plantillas': plantillas})
        except Exception as e:
            return JsonResponse({'error': str(e), 'plantillas': []}, status=500)
