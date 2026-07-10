from django.urls import path
from . import views
from .views import sync_evaluaciones

urlpatterns = [
    path("api/sync/evaluaciones/", sync_evaluaciones, name="sync_evaluaciones"),
    path("test/offline/", views.test_plantilla_offline, name="test_plantilla_offline"),
]