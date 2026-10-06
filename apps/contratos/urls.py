from django.urls import path

from .views import (
    ContractBulkPdfView,
    ContractGenerateView,
    ContractListView,
    ContractPdfView,
    ContractSignView,
    ContractTemplateView,
)


app_name = "contratos"

urlpatterns = [
    path("", ContractListView.as_view(), name="index"),
    path("pdf/generar-lote/", ContractBulkPdfView.as_view(), name="bulk_pdf"),
    path("generar/<str:worker_id>/", ContractGenerateView.as_view(), name="generate"),
    path("plantilla/<str:contract_type>/", ContractTemplateView.as_view(), name="template"),
    path("pdf/<str:worker_id>/<str:contract_id>/", ContractPdfView.as_view(), name="pdf"),
    path(
        "firmar/<str:worker_id>/<str:contract_id>/",
        ContractSignView.as_view(),
        name="sign",
    ),
]
