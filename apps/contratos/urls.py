from django.urls import path

from .views import (
    ContractGenerateView,
    ContractListView,
    ContractSignView,
    ContractTemplateView,
)


app_name = "contratos"

urlpatterns = [
    path("", ContractListView.as_view(), name="index"),
    path("generar/<str:worker_id>/", ContractGenerateView.as_view(), name="generate"),
    path("plantilla/<str:contract_type>/", ContractTemplateView.as_view(), name="template"),
    path(
        "firmar/<str:worker_id>/<str:contract_id>/",
        ContractSignView.as_view(),
        name="sign",
    ),
]
