
from django.urls import path
from .views import *

urlpatterns = [
    path('gerencia_evaluacion_desempeño/', evaluacion_desempeño.as_view(), name='gerencia_evaluacion_desempeño'),

     # API PARA OBTENER DATOS DE EVALUACIONES DE OBJETIVOS
    path('objetivos_evaluacion/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion'),
    path('objetivos_evaluacion/<int:id>/', ObjetivosEvaluacionView.as_view(), name='objetivos_evaluacion_detail'),
    
    path('detalles_objetivos/', DetallesObjetivosView.as_view(), name='detalles_objetivos'),
    path('detalles_objetivos/<int:id>/', DetallesObjetivosView.as_view(), name='detalles_objetivos_detail'),

    
    path('detalles_competencias/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias'),
    path('detalles_competencias/<int:id>/', CompetenciasEvaluacionDetailView.as_view(), name='detalles_competencias_detail'),

    #=====================================================================================================================
    # API PARA LOS DETALLES DE LA FASE INTERMEDIA
    #=====================================================================================================================
    path('api/fase-intermedia/', FaseIntermediaEvaluacionesView.as_view(), name='fase_intermedia_evaluaciones'),
    path('api/fase-intermedia/<int:id_evaluacion>/', FaseIntermediaEvaluacionesView.as_view(), name='fase_intermedia_evaluacion_detalle'),
    
    #api para los detalles de la fase intermedia
    
    
    # En tu archivo urls.py
    path('api/detalles-evaluacion/', DetallesEvaluacionModalView.as_view(), name='detalles_evaluacion_modal'),
    
    # ====================================================================================================================
    # API para la FASE FINAL de evaluaciones (GERENCIA)
    # ====================================================================================================================

    path('api/fase-final/', FaseFinalEvaluacionesContaView.as_view(), name='fase_final_evaluaciones_conta'),
    path('api/fase-final/<int:id_evaluacion>/', FaseFinalEvaluacionesContaView.as_view(), name='fase_final_evaluacion_conta_detalle'),

    # API para los detalles de la fase FINAL
    path('api/detalles-evaluacion-final/', DetallesEvaluacionFinalContaView.as_view(), name='detalles_evaluacion_final_conta'),

]
