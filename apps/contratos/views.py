import logging
import calendar
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import DatabaseError
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import ContractGenerationForm
from .pdf import build_contract_pdf, build_contract_pdfs_batch
from .services import ContractService


logger = logging.getLogger(__name__)


def _contract_pdf_path(worker_id, contract_id):
    worker = re.sub(r"[^A-Za-z0-9_-]+", "_", str(worker_id)).strip("_")
    contract = re.sub(r"[^A-Za-z0-9_-]+", "_", str(contract_id)).strip("_")
    return Path(settings.MEDIA_ROOT) / "contratos" / "generados" / "{}_{}.pdf".format(
        worker, contract
    )


def _ensure_contract_pdf(service, worker_id, contract_id):
    path = _contract_pdf_path(worker_id, contract_id)
    if path.is_file():
        return path, "CONTRATO_{}_{}.pdf".format(worker_id, contract_id)
    data = service.contract_document_data(worker_id, contract_id)
    if not data:
        raise FileNotFoundError("No se encontró el contrato del trabajador.")
    template = service.template_path(data["idtipocontrato"])
    pdf = build_contract_pdf(template, data)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb", suffix=".pdf", prefix="contract_", dir=str(path.parent), delete=False
    ) as temporary:
        temporary.write(pdf.getvalue())
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)
    safe_name = re.sub(r"[^A-Z0-9]+", "_", data["full_name"].upper()).strip("_")
    return path, "CONTRATO_{}_{}.pdf".format(safe_name, contract_id)


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
        expiry_month = request.GET.get("expiry_month") or today.strftime("%Y-%m")
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
            expiry_year, expiry_month_number = map(int, expiry_month.split("-"))
            expiry_start = date(expiry_year, expiry_month_number, 1)
            expiry_end = date(
                expiry_year,
                expiry_month_number,
                calendar.monthrange(expiry_year, expiry_month_number)[1],
            )
        except (TypeError, ValueError):
            messages.error(request, "El mes de vencimiento no es válido.")
            expiry_month = today.strftime("%Y-%m")
            expiry_start = today.replace(day=1)
            expiry_end = date(
                today.year, today.month, calendar.monthrange(today.year, today.month)[1]
            )

        try:
            service = ContractService()
            personnel = service.list_personnel(start_date, end_date)
            expiring_contracts = service.list_expiring_contracts(expiry_start, expiry_end)
        except DatabaseError:
            logger.exception("No se pudo consultar el personal para contratos.")
            messages.error(request, "No fue posible consultar los contratos.")
            personnel = []
            expiring_contracts = []

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
            person["contract_pdf_ready"] = bool(
                person.get("contract_id")
                and _contract_pdf_path(person["idcodigogeneral"], person["contract_id"]).is_file()
            )
        for contract in expiring_contracts:
            contract["contract_pdf_ready"] = _contract_pdf_path(
                contract["idcodigogeneral"], contract["contract_id"]
            ).is_file()

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
                "expiry_month": expiry_month,
                "expiry_start": expiry_start,
                "expiry_end": expiry_end,
                "expiring_contracts": expiring_contracts,
                "expiring_count": len(expiring_contracts),
                "show_expiring": request.GET.get("show_expiring") == "1",
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
        service, person, choices = self.get_service_data(worker_id)
        renewal = None
        initial = {
            "worker_id": worker_id,
            "start_date": person.get("fecha_ingreso"),
            "trial_days": 0,
        }
        renewal_id = request.GET.get("renew", "").strip()
        if renewal_id:
            renewal = service.get_contract(worker_id, renewal_id)
            if renewal:
                initial.update({
                    "contract_type": renewal.get("idtipocontrato"),
                    "start_date": renewal["final_contrato"] + timedelta(days=1),
                    "basic": renewal.get("basico"),
                })
        form = ContractGenerationForm(
            contract_types=choices,
            initial=initial,
        )
        return render(request, self.template_name, {
            "person": person, "form": form, "renewal": renewal,
        })

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
        try:
            _ensure_contract_pdf(service, worker_id, contract_id)
        except (FileNotFoundError, RuntimeError, OSError):
            logger.exception("El contrato %s fue registrado pero su PDF no pudo generarse.", contract_id)
            messages.warning(
                request,
                "Contrato {} registrado. Usa Generar contrato para crear el PDF.".format(contract_id),
            )
            return redirect("contratos:index")
        messages.success(request, "Contrato {} registrado y PDF generado.".format(contract_id))
        return redirect("contratos:pdf", worker_id=worker_id, contract_id=contract_id)


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


class ContractPdfView(ContractPermissionMixin, View):
    def get(self, request, worker_id, contract_id):
        service = ContractService()
        try:
            path, filename = _ensure_contract_pdf(service, worker_id, contract_id)
        except (FileNotFoundError, RuntimeError, OSError) as exc:
            logger.exception("No se pudo generar el PDF del contrato %s/%s.", worker_id, contract_id)
            raise Http404("No se pudo generar el contrato PDF: {}".format(exc))
        return FileResponse(
            path.open("rb"),
            as_attachment=False,
            filename=filename,
            content_type="application/pdf",
        )


class ContractBulkPdfView(ContractPermissionMixin, View):
    max_contracts = 100

    def post(self, request):
        selected = request.POST.getlist("contracts")
        if not selected:
            messages.warning(request, "Selecciona al menos un contrato.")
            return redirect("contratos:index")
        if len(selected) > self.max_contracts:
            messages.error(
                request,
                "Solo se pueden procesar hasta {} contratos por lote.".format(self.max_contracts),
            )
            return redirect("contratos:index")

        service = ContractService()
        jobs = []
        ready = 0
        invalid = 0
        seen = set()
        for value in selected:
            try:
                worker_id, contract_id = value.split("::", 1)
            except ValueError:
                invalid += 1
                continue
            key = (worker_id.strip(), contract_id.strip())
            if not all(key) or key in seen:
                invalid += 1
                continue
            seen.add(key)
            output_path = _contract_pdf_path(*key)
            if output_path.is_file():
                ready += 1
                continue
            data = service.contract_document_data(*key)
            if not data or not data.get("is_active"):
                invalid += 1
                continue
            try:
                template = service.template_path(data["idtipocontrato"])
            except FileNotFoundError:
                invalid += 1
                continue
            jobs.append({
                "template_path": template,
                "data": data,
                "output_path": output_path,
            })

        generated = 0
        if jobs:
            try:
                generated = build_contract_pdfs_batch(jobs)
            except (RuntimeError, OSError):
                logger.exception("No se pudo generar el lote de contratos.")
                messages.error(request, "No se pudo completar la generación masiva.")
                return redirect("contratos:index")

        messages.success(
            request,
            "Proceso masivo completado: {} generados y {} ya disponibles.".format(
                generated, ready
            ),
        )
        if invalid:
            messages.warning(
                request,
                "{} contrato(s) no se procesaron porque el trabajador no está activo o faltan datos de la plantilla.".format(invalid),
            )
        return redirect("contratos:index")


class ContractSignView(ContractPermissionMixin, View):
    def post(self, request, worker_id, contract_id):
        try:
            ContractService().mark_signed(worker_id, contract_id)
        except (ValueError, DatabaseError) as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, "La firma física del contrato fue registrada.")
        return redirect("contratos:index")
