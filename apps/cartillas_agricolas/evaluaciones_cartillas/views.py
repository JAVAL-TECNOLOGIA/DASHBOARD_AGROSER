from django.views.generic import TemplateView

from apps.cartillas_agricolas.services import get_areas_cartillas_agricolas


class EvaluacionesCartillasView(TemplateView):
    """Vista principal del dashboard de Cartillas Agrícolas por área."""
    template_name = 'cartillas_agricolas/evaluaciones_cartillas/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_area = self.kwargs.get('id_area')
        context['id_area'] = id_area
        context['page_title'] = 'Cartillas Agrícolas'
        # Nombre del área para breadcrumb
        areas = get_areas_cartillas_agricolas()
        area_nombre = next((a['nombreArea'] for a in areas if a['idArea'] == id_area), 'Cartillas')
        context['area_nombre'] = area_nombre
        return context
