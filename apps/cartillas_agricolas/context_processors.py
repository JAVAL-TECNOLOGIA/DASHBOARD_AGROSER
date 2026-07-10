"""
Context processors para Cartillas Agrícolas.
Inyecta cartillas_areas en el contexto para construir el menú dinámico.
"""
from .services import get_areas_cartillas_agricolas


def cartillas_areas(request):
    """Añade cartillas_areas al contexto para el sidebar."""
    try:
        areas = get_areas_cartillas_agricolas()
        return {'cartillas_areas': areas}
    except Exception:
        return {'cartillas_areas': []}
