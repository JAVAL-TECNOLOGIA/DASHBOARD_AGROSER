from django.urls import path
from .views import AssetDashboardView, AssetManageView, AssetStatusView, AssetSummaryApi, AvailableAssetsApi, AssignmentApi

app_name = "tic_assets"

urlpatterns = [
    path("tic/asignaciones/", AssetDashboardView.as_view(), name="dashboard"),
    path("tic/asignaciones/equipo/", AssetManageView.as_view(), name="asset_manage"),
    path("tic/asignaciones/equipo/<int:pk>/estado/", AssetStatusView.as_view(), name="asset_status"),
    path("api/tic/asignaciones/resumen/", AssetSummaryApi.as_view(), name="api_summary"),
    path("api/tic/asignaciones/equipos-disponibles/", AvailableAssetsApi.as_view(), name="api_available"),
    path("api/tic/asignaciones/registrar/", AssignmentApi.as_view(), name="api_assign"),
]
