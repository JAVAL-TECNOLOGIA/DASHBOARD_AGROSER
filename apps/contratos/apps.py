import os
import sys

from django.apps import AppConfig


class ContratosConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "apps.contratos"
    verbose_name = "Generación de contratos"

    def ready(self):
        # Preload Word in the actual runserver process, never in the autoreload parent.
        is_runserver = "runserver" in sys.argv
        is_worker = os.environ.get("RUN_MAIN") == "true" or "--noreload" in sys.argv
        if is_runserver and is_worker:
            from .pdf import warm_contract_pdf_converter

            warm_contract_pdf_converter()
