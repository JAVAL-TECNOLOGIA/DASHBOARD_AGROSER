from django.urls import path
from . import views

urlpatterns = [
    path('', views.evaluacion_fertilidad, name='test_template_evaluacion_fertilidad'),
]
