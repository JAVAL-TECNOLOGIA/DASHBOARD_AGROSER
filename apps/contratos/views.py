import logging
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import DatabaseError
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import ContractGenerationForm
from .services import ContractService


logger = logging.getLogger(__name__)


class ContractPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "contratos.gestionar_contratos"
    raise_exception = True

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            getattr(user, "admin", False) or super().has_permission()
        )


class ContractListView(ContractPermissionMixin, View):
    template_name = "contratos/index.html"

    def get(self, request):
        today = date.today()
        start_value = request.GET.get("start") or (today - timedelta(days=60)).isoformat()
        end_value = request.GET.get("end") or today.isoformat()
        status = request.GET.get("status", "")
        query = request.GET.get("q", "").strip().casefold()
        try:
            start_date = date.fromisoformat(start_value)
            end_date = date.fromisoformat(end_value)
            if end_date < start_date or (end_date - start_date).days > 366:
                raise ValueError
        except ValueError:
            messages.error(request, "El rango de fechas no es válido.")
            start_date, end_date = today - timedelta(days=60), today
            start_value, end_value = start_date.isoformat(), end_date.isoformat()

        try:
            personnel = ContractService().list_personnel(start_date, end_date)
        except DatabaseError:
            logger.exception("No se pudo consultar el personal para contratos.")
            messages.error(request, "No fue posible consultar los contratos.")
            personnel = []

        for person in personnel:
            if not person.get("contract_id"):
                person["contract_status"] = "pending"
                person["contract_status_label"] = "Pendiente de generar"
            elif person.get("physical_signature"):
                person["contract_status"] = "signed"
                person["contract_status_label"] = "Firmado"
            else:
                person["contract_status"] = "signature"
                person["contract_status_label"] = "Pendiente de firma"

        counts = {
            "pending": sum(p["contract_status"] == "pending" for p in personnel),
            "signature": sum(p["contract_status"] == "signature" for p in personnel),
            "signed": sum(p["contract_status"] == "signed" for p in personnel),
        }
        if status:
            personnel = [p for p in personnel if p["contract_status"] == status]
        if query:
            personnel = [
                p
                for p in personnel
                if query
                in "{} {} {} {}".format(
                    p.get("full_name", ""),
                    p.get("document", ""),
                    p.get("position", ""),
                    p.get("payroll", ""),
                ).casefold()
            ]

        return render(
            request,
            self.template_name,
            {
                "personnel": personnel,
                "counts": counts,
                "start_value": start_value,
                "end_value": end_value,
                "status": status,
                "query": request.GET.get("q", ""),
            },
        )


class ContractGenerateView(ContractPermissionMixin, View):
    template_name = "contratos/generate.html"

    def get_service_data(self, worker_id):
        service = ContractService()
        person = service.get_person(worker_id)
        if not person:
            raise Http404("El trabajador no existe.")
        types = service.contract_types()
        choices = [(item["idtipocontrato"], item["descripcion"]) for item in types]
        return service, person, choices

    def get(self, request, worker_id):
        unused_service, person, choices = self.get_service_data(worker_id)
        form = ContractGenerationForm(
            contract_types=choices,
            initial={
                "worker_id": worker_id,
                "start_date": person.get("fecha_ingreso"),
                "trial_days": 0,
            },
        )
        return render(request, self.template_name, {"person": person, "form": form})

    def post(self, request, worker_id):
        service, person, choices = self.get_service_data(worker_id)
        form = ContractGenerationForm(request.POST, contract_types=choices)
        if form.is_valid() and form.cleaned_data["worker_id"] != worker_id:
            form.add_error(None, "El trabajador indicado no coincide.")
        if not form.is_valid():
            return render(request, self.template_name, {"person": person, "form": form})
        try:
            contract_id = service.generate(form.cleaned_data)
        except (ValueError, DatabaseError) as exc:
            logger.exception("No se pudo generar el contrato del trabajador %s.", worker_id)
            form.add_error(None, str(exc))
            return render(request, self.template_name, {"person": person, "form": form})
        messages.success(
            request,
            "Contrato {} registrado. Descarga la plantilla para impresión y firma.".format(
                contract_id
            ),
        )
        return redirect("contratos:index")


class ContractTemplateView(ContractPermissionMixin, View):
    def get(self, request, contract_type):
        try:
            path = ContractService().template_path(contract_type)
        except FileNotFoundError as exc:
            raise Http404(str(exc))
        return FileResponse(
            path.open("rb"),
            as_attachment=True,
            filename=path.name,
        )


class ContractSignView(ContractPermissionMixin, View):
    def post(self, request, worker_id, contract_id):
        try:
            ContractService().mark_signed(worker_id, contract_id)
        except (ValueError, DatabaseError) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "La firma física del contrato fue registrada.")
        return redirect("contratos:index")
