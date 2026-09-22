import hashlib
import json
import logging
import unicodedata
from urllib.parse import urlencode
from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.core.cache import cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError, connections, transaction
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.utils import timezone
from .identity import identity_complete
from .worker_forms import WorkerIdentityForm

from apps.user.models import User

from .models import PayslipAcknowledgement, PayslipView, PayrollRelease, WorkerIdentityProfile
from .periods import month_range, resolve_date_range, week_value_for_date
from .services import PaySlipService
from .views import PaySlipPdfView, WEEKLY_PAYROLL_TYPES, _confirmed_signature, _official_payroll_period
from .worker_forms import (
    PayslipConfirmationForm,
    WorkerLoginForm,
    WorkerPasswordChangeForm,
)


logger = logging.getLogger(__name__)

DOCUMENT_TYPES = OrderedDict((
    ("payment", "Boletas de Pago"),
    ("cts", "Boleta CTS"),
    ("utilities", "Boleta de Utilidades"),
    ("gratification", "Boleta de Gratificación"),
))
DOCUMENT_TITLES = {
    "payment": "BOLETA DE PAGO",
    "cts": "BOLETA CTS",
    "utilities": "BOLETA DE UTILIDADES",
    "gratification": "BOLETA DE GRATIFICACIÓN",
}


def concept_document_type(concept):
    value = "{} {}".format(
        concept.get("descripcion") or "", concept.get("codigo_equiv") or ""
    )
    normalized = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode().upper()
    if "UTILIDAD" in normalized:
        return "utilities"
    if "GRATIFIC" in normalized:
        return "gratification"
    if "CTS" in normalized or "COMPENSACION POR TIEMPO" in normalized:
        return "cts"
    return "payment"


def split_worker_documents(slips):
    documents = []
    for slip in slips:
        if slip.get("movement_id"):
            detected = {concept_document_type(item) for item in slip.get("concepts", [])}
            document_type = next(
                (code for code in ("utilities", "cts", "gratification") if code in detected),
                "payment",
            )
            document = dict(slip)
            document["document_type"] = document_type
            document["document_type_label"] = DOCUMENT_TYPES[document_type]
            document["document_title"] = DOCUMENT_TITLES[document_type]
            documents.append(document)
            continue
        groups = {code: [] for code in DOCUMENT_TYPES}
        for concept in slip.get("concepts", []):
            groups[concept_document_type(concept)].append(concept)
        for document_type, concepts in groups.items():
            if not concepts:
                continue
            document = dict(slip)
            document["concepts"] = concepts
            document["document_type"] = document_type
            document["document_type_label"] = DOCUMENT_TYPES[document_type]
            document["document_title"] = DOCUMENT_TITLES[document_type]
            document["income_total"] = sum(
                (PaySlipService._amount(item) for item in concepts if PaySlipService._is_income(item)), 0
            )
            document["deduction_total"] = sum(
                (PaySlipService._amount(item) for item in concepts if PaySlipService._is_deduction(item)), 0
            )
            document["net_total"] = document["income_total"] - document["deduction_total"]
            documents.append(document)
    return documents


class WorkerIdentityService:
    def get_active_worker(self, document):
        sql = """
            SELECT TOP 1
                pg.idcodigogeneral,
                RTRIM(pg.nrodocumento) AS document,
                RTRIM(pg.a_paterno) AS paternal_name,
                RTRIM(pg.a_materno) AS maternal_name,
                RTRIM(pg.nombres) AS given_names,
                RTRIM(ISNULL(pg.email, '')) AS email
            FROM personal_general pg WITH (NOLOCK)
            INNER JOIN personal_empresa pe WITH (NOLOCK)
                ON pe.idcodigogeneral = pg.idcodigogeneral
                AND pe.idempresa = %s
            WHERE RTRIM(pg.nrodocumento) = %s
                AND pe.fecha_cese IS NULL
            ORDER BY pe.fecha_ingreso DESC
        """
        with connections["payroll"].cursor() as cursor:
            cursor.execute(sql, [PaySlipService().company_id, document])
            if not cursor.description:
                return None
            row = cursor.fetchone()
            if not row:
                return None
            columns = [column[0] for column in cursor.description]
            return {
                key: value.strip() if isinstance(value, str) else value
                for key, value in zip(columns, row)
            }


def payslip_fingerprint(slip, period):
    concepts = [
        {
            "code": str(item.get("codigo_equiv") or ""),
            "type": str(item.get("idtipoconcepto") or ""),
            "description": str(item.get("descripcion") or ""),
            "amount": str(item.get("importe") or 0),
        }
        for item in slip.get("concepts", [])
    ]
    concepts.sort(key=lambda item: (item["type"], item["code"], item["description"]))
    payload = {
        "document": str(slip.get("nrodocumento") or ""),
        "worker": str(slip.get("idcodigogeneral") or ""),
        "payroll": str(slip.get("codigoplanilla") or ""),
        "period_start": period.start.isoformat(),
        "period_end": period.end.isoformat(),
        "basic": str(slip.get("basico") or 0),
        "income": str(slip.get("income_total") or 0),
        "deductions": str(slip.get("deduction_total") or 0),
        "net": str(slip.get("net_total") or 0),
        "concepts": concepts,
    }
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def record_worker_pdf_access(request, user, period, fingerprint):
    """Conserva el primer acceso al PDF y actualiza la última visita."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    view, created = PayslipView.objects.get_or_create(
        payslip_hash=fingerprint,
        defaults={
            "user": user,
            "worker_document": user.username,
            "period_start": period.start,
            "period_end": period.end,
            "ip_address": ip_address,
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
        },
    )
    if not created:
        view.ip_address = ip_address
        view.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
        view.save(update_fields=("ip_address", "user_agent", "last_viewed_at"))
    return view


def worker_slips(document, period):
    from .periods import visible_period
    period = visible_period(period)
    if period is None:
        return []
    cache_key = "boletas:worker:{}:{}:{}".format(document, period.start.isoformat(), period.end.isoformat())
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    slips = [
        slip
        for slip in PaySlipService().list(period)
        if str(slip.get("nrodocumento") or "").strip() == document
    ]
    documents = []
    for slip in slips:
        if str(slip.get("payroll_type") or "").strip().upper() in ("OBP", "OBR"):
            # Plant-worker concepts form one weekly payslip; CTS and agrarian
            # gratification lines belong inside the same legacy document.
            slip["document_type"] = "payment"
            slip["document_type_label"] = DOCUMENT_TYPES["payment"]
            slip["document_title"] = "BOLETA DE REMUNERACIONES"
            totals = {
                str(item.get("codigo_equiv") or "").strip().upper(): PaySlipService._amount(item)
                for item in slip.get("concepts", [])
            }
            slip["income_total"] = totals.get("TOT_IN", slip.get("income_total", 0))
            slip["deduction_total"] = totals.get("TOT_DE", slip.get("deduction_total", 0))
            slip["net_total"] = totals.get(
                "TO0002", slip["income_total"] - slip["deduction_total"]
            )
            documents.append(slip)
        else:
            documents.extend(split_worker_documents([slip]))
    cache.set(cache_key, documents, 300)
    return documents


def resolve_worker_period(document, mode, **values):
    week_value = str(values.get('week_value') or '')
    period = month_range(values.get('month_value') or timezone.localdate().strftime('%Y-%m')) if mode == 'week' and '-W' not in week_value else resolve_date_range(mode, **values)
    month = month_range(period.end.strftime('%Y-%m'))
    monthly = worker_slips(document, month)
    if not monthly:
        periods = PaySlipService().worker_payroll_periods(document, '202608')
        if periods:
            latest = periods[0]
            monthly = worker_slips(document, month_range(latest[:4] + '-' + latest[4:6]))
    weekly_type = next((str(item.get('payroll_type', '')).upper() for item in monthly if str(item.get('payroll_type', '')).upper() in WEEKLY_PAYROLL_TYPES), '')
    if weekly_type:
        official, unused_weeks, unused_selected = _official_payroll_period(
            PaySlipService(), weekly_type, month.start.strftime('%Y-%m'), values.get('week_value', '')
        )
        return 'week', official, False
    monthly_only = any(str(item.get('payroll_type', '')).upper() in ('ERG', 'ERA') for item in monthly)
    return ('month', month, True) if monthly_only else (mode, period, False)


class WorkerLoginView(View):
    template_name = "boletas/worker/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("boletas:worker_dashboard")
        return render(request, self.template_name, {"form": WorkerLoginForm()})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("boletas:worker_dashboard")
        form = WorkerLoginForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        document = form.cleaned_data["document"]
        password = form.cleaned_data["password"]
        try:
            identity = WorkerIdentityService().get_active_worker(document)
        except DatabaseError:
            logger.exception("No se pudo validar la identidad laboral.")
            form.add_error(None, "No fue posible validar tus datos en este momento.")
            return render(request, self.template_name, {"form": form})
        if not identity:
            form.add_error(None, "Documento o contraseña incorrectos.")
            return render(request, self.template_name, {"form": form})

        user = User.objects.filter(username=document).first()
        if user is None:
            if password != document:
                form.add_error(None, "Documento o contraseña incorrectos.")
                return render(request, self.template_name, {"form": form})
            email = identity.get("email") or "{}@boletas.local".format(document)
            if User.objects.filter(email=email).exists():
                email = "{}.{}@boletas.local".format(
                    document, identity.get("idcodigogeneral")
                )
            with transaction.atomic():
                user = User.objects.create_user(
                    username=document,
                    email=email,
                    first_name=(identity.get("given_names") or "TRABAJADOR")[:50],
                    last_name="{} {}".format(
                        identity.get("paternal_name") or "",
                        identity.get("maternal_name") or "",
                    ).strip()[:50],
                    password=document,
                )

        authenticated = authenticate(request, username=document, password=password)
        if authenticated is None:
            form.add_error(None, "Documento o contraseña incorrectos.")
            return render(request, self.template_name, {"form": form})
        login(request, authenticated)
        if authenticated.check_password(document):
            return redirect("boletas:worker_change_password")
        return redirect("boletas:worker_dashboard")


class WorkerPortalMixin(LoginRequiredMixin):
    login_url = "boletas:worker_login"
    require_identity = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            self.worker_identity = WorkerIdentityService().get_active_worker(
                request.user.username
            )
        except DatabaseError:
            self.worker_identity = None
        if not self.worker_identity:
            raise Http404("No existe un vínculo laboral activo para esta cuenta.")
        if request.user.check_password(request.user.username):
            return redirect("boletas:worker_change_password")
        if self.require_identity and not identity_complete(request.user):
            return redirect("boletas:worker_identity")
        return super().dispatch(request, *args, **kwargs)


class WorkerIdentityView(WorkerPortalMixin, View):
    require_identity = False
    template_name = 'boletas/worker/identity.html'

    def get(self, request):
        if identity_complete(request.user):
            return redirect('boletas:worker_dashboard')
        return render(request, self.template_name, {'form': WorkerIdentityForm()})

    def post(self, request):
        if identity_complete(request.user):
            return redirect('boletas:worker_dashboard')
        form = WorkerIdentityForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        saved_files = []
        try:
            with transaction.atomic():
                # Serializa registros simultáneos de una misma cuenta.
                User.objects.select_for_update().get(pk=request.user.pk)
                if identity_complete(request.user):
                    return redirect('boletas:worker_dashboard')
                profile, _ = WorkerIdentityProfile.objects.get_or_create(
                    user=request.user, defaults={'worker_document': request.user.username})
                for field_name in ('signature', 'photo'):
                    field = getattr(profile, field_name)
                    content = form.cleaned_data[field_name]
                    field.save(content.name, content, save=False)
                    saved_files.append((field.storage, field.name))
                profile.worker_document = request.user.username
                profile.consent_accepted = True
                profile.consent_at = timezone.now()
                profile.ip_address = request.META.get('REMOTE_ADDR')
                profile.user_agent = request.META.get('HTTP_USER_AGENT', '')[:300]
                profile.save()
        except (DatabaseError, OSError):
            for storage, name in saved_files:
                try:
                    storage.delete(name)
                except OSError:
                    logger.exception('No se pudo limpiar un archivo de identidad incompleto.')
            logger.exception('No se pudo guardar la identidad del trabajador.')
            form.add_error(None, 'No se pudo guardar el registro. Vuelve a intentarlo; todavía no se habilitó el acceso al portal.')
            return render(request, self.template_name, {'form': form})
        return redirect('boletas:worker_dashboard')


class WorkerPasswordChangeView(LoginRequiredMixin, View):
    login_url = "boletas:worker_login"
    template_name = "boletas/worker/change_password.html"

    def get(self, request):
        identity = WorkerIdentityService().get_active_worker(request.user.username)
        if not identity:
            raise Http404("No existe un vínculo laboral activo.")
        if not request.user.check_password(request.user.username):
            return redirect("boletas:worker_dashboard")
        return render(
            request,
            self.template_name,
            {"form": WorkerPasswordChangeForm(user=request.user)},
        )

    def post(self, request):
        identity = WorkerIdentityService().get_active_worker(request.user.username)
        if not identity:
            raise Http404("No existe un vínculo laboral activo.")
        form = WorkerPasswordChangeForm(request.POST, user=request.user)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        request.user.set_password(form.cleaned_data["new_password1"])
        request.user.save(update_fields=["password"])
        update_session_auth_hash(request, request.user)
        messages.success(request, "Tu contraseña fue actualizada correctamente.")
        return redirect("boletas:worker_dashboard")


class WorkerDashboardView(WorkerPortalMixin, View):
    template_name = "boletas/worker/dashboard.html"

    def get(self, request):
        mode = request.GET.get("mode", "month")
        monthly_only = False
        try:
            mode, period, monthly_only = resolve_worker_period(
                request.user.username, mode,
                month_value=request.GET.get("month", ""),
                week_value=request.GET.get("week", ""),
                start_value=request.GET.get("start", ""),
                end_value=request.GET.get("end", ""),
            )
            selected_month = request.GET.get("month", "") or period.start.strftime("%Y-%m")
            monthly_slips = worker_slips(request.user.username, month_range(selected_month))
            weekly_payroll = next((str(item.get('payroll_type') or '').strip().upper() for item in monthly_slips if str(item.get('payroll_type') or '').strip().upper() in WEEKLY_PAYROLL_TYPES), '')
            if weekly_payroll:
                period, payroll_weeks, payroll_week = _official_payroll_period(PaySlipService(), weekly_payroll, selected_month, request.GET.get("week", ""))
                mode = 'week'
            else:
                payroll_weeks, payroll_week = [], ''
        except (TypeError, ValueError, DatabaseError):
            mode = "month"
            period = resolve_date_range(mode)
            messages.error(request, "El periodo seleccionado no es válido.")
            weekly_payroll, payroll_weeks, payroll_week = '', [], ''
        try:
            slips = worker_slips(request.user.username, period)
            slips = [
                slip for slip in slips
                if PayrollRelease.objects.filter(
                    payroll_type=str(slip.get("payroll_type") or "").strip().upper(),
                    period_start=period.start,
                    period_end=period.end,
                    released_at__isnull=False,
                ).exists()
            ]
        except DatabaseError:
            logger.exception("No se pudieron consultar las boletas del trabajador.")
            slips = []
            messages.error(request, "No fue posible consultar tus boletas.")

        document_type = request.GET.get("type", "payment")
        if document_type not in DOCUMENT_TYPES:
            document_type = "payment"
        document_counts = {
            code: sum(slip.get("document_type") == code for slip in slips)
            for code in DOCUMENT_TYPES
        }
        slips = [slip for slip in slips if slip.get("document_type") == document_type]

        fingerprints = []
        for slip in slips:
            fingerprint = payslip_fingerprint(slip, period)
            slip["fingerprint"] = fingerprint
            fingerprints.append(fingerprint)
        acknowledgements = {
            item.payslip_hash: item
            for item in PayslipAcknowledgement.objects.filter(
                user=request.user, payslip_hash__in=fingerprints
            )
        }
        for slip in slips:
            slip["acknowledgement"] = acknowledgements.get(slip["fingerprint"])

        params = {
            "mode": mode,
            "month": period.start.strftime("%Y-%m") if monthly_only else request.GET.get("month", ""),
            "week": request.GET.get("week", ""),
            "start": request.GET.get("start", ""),
            "end": request.GET.get("end", ""),
        }
        return render(
            request,
            self.template_name,
            {
                "identity": self.worker_identity,
                "slips": slips,
                "period": period,
                "mode": mode,
                "monthly_only": monthly_only,
                "weekly_payroll": bool(weekly_payroll),
                "payroll_weeks": payroll_weeks,
                "payroll_week": payroll_week,
                "document_type": document_type,
                "document_tabs": [
                    {"code": code, "label": label, "count": document_counts[code]}
                    for code, label in DOCUMENT_TYPES.items()
                ],
                "month_value": params["month"] or period.start.strftime("%Y-%m"),
                "week_value": payroll_week if weekly_payroll else params["week"] or week_value_for_date(period.start),
                "start_value": params["start"] or period.start.isoformat(),
                "end_value": params["end"] or period.end.isoformat(),
            },
        )


class WorkerPayslipPdfView(WorkerPortalMixin, View):
    def get(self, request):
        unused_mode, period, unused_monthly = resolve_worker_period(
            request.user.username, request.GET.get("mode", "month"),
            month_value=request.GET.get("month", ""),
            week_value=request.GET.get("week", ""),
            start_value=request.GET.get("start", ""),
            end_value=request.GET.get("end", ""),
        )
        requested_hash = request.GET.get("hash", "")
        slip = next(
            (
                item
                for item in worker_slips(request.user.username, period)
                if payslip_fingerprint(item, period) == requested_hash
            ),
            None,
        )
        if slip is None:
            raise Http404("La boleta solicitada no existe.")
        slip['_payroll_week'] = request.GET.get('week', '').strip()
        if not PayrollRelease.objects.filter(
            payroll_type=str(slip.get("payroll_type") or "").strip().upper(),
            period_start=period.start,
            period_end=period.end,
            released_at__isnull=False,
        ).exists():
            raise Http404("La boleta todavía no fue autorizada.")
        acknowledgement = PayslipAcknowledgement.objects.filter(
            user=request.user, payslip_hash=requested_hash
        ).first()
        if not acknowledgement:
            messages.error(request, "Debes dar tu conformidad antes de visualizar la boleta.")
            return redirect("boletas:worker_dashboard")
        with transaction.atomic():
            record_worker_pdf_access(request, request.user, period, requested_hash)
            data = PaySlipPdfView._build_pdf(
                slip,
                period,
                delivery=PaySlipPdfView._delivery_data(slip, period),
                **_confirmed_signature(slip, period),
            )
        response = HttpResponse(data, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="mi_boleta_{}_{}.pdf"'.format(
            slip.get("document_type", "pago"), period.end.strftime("%Y%m%d")
        )
        return response


class WorkerPayslipConfirmView(WorkerPortalMixin, View):
    template_name = "boletas/worker/confirm.html"

    def get_slip(self, request):
        unused_mode, period, unused_monthly = resolve_worker_period(
            request.user.username, request.GET.get("mode", request.POST.get("mode", "month")),
            month_value=request.GET.get("month", request.POST.get("month", "")),
            week_value=request.GET.get("week", request.POST.get("week", "")),
            start_value=request.GET.get("start", request.POST.get("start", "")),
            end_value=request.GET.get("end", request.POST.get("end", "")),
        )
        requested_hash = request.GET.get("hash", request.POST.get("hash", ""))
        slip = next(
            (
                item
                for item in worker_slips(request.user.username, period)
                if payslip_fingerprint(item, period) == requested_hash
            ),
            None,
        )
        if not slip:
            raise Http404("La boleta solicitada no existe.")
        if not PayrollRelease.objects.filter(
            payroll_type=str(slip.get("payroll_type") or "").strip().upper(),
            period_start=period.start,
            period_end=period.end,
            released_at__isnull=False,
        ).exists():
            raise Http404("La boleta todavía no fue autorizada.")
        return period, slip, requested_hash

    def get(self, request):
        period, slip, fingerprint = self.get_slip(request)
        if PayslipAcknowledgement.objects.filter(payslip_hash=fingerprint).exists():
            messages.info(request, "Esta boleta ya fue confirmada.")
            return redirect("boletas:worker_dashboard")
        return render(
            request,
            self.template_name,
            {
                "period": period,
                "slip": slip,
                "fingerprint": fingerprint,
                "mode": request.GET.get('mode', 'month'),
                "month_value": request.GET.get('month', ''),
                "week_value": request.GET.get('week', ''),
                "form": PayslipConfirmationForm(),
            },
        )

    def post(self, request):
        period, slip, fingerprint = self.get_slip(request)
        form = PayslipConfirmationForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "period": period,
                    "slip": slip,
                    "fingerprint": fingerprint,
                    "mode": request.POST.get('mode', 'month'),
                    "month_value": request.POST.get('month', ''),
                    "week_value": request.POST.get('week', ''),
                    "form": form,
                },
            )
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
        PayslipAcknowledgement.objects.get_or_create(
            payslip_hash=fingerprint,
            defaults={
                "user": request.user,
                "worker_document": request.user.username,
                "period_start": period.start,
                "period_end": period.end,
                "payroll_code": str(slip.get("codigoplanilla") or "")[:20],
                "signer_name": "{} {}".format(
                    request.user.first_name, request.user.last_name
                ).strip(),
                "ip_address": ip_address,
                "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
            },
        )
        messages.success(request, "Tu conformidad electrónica fue registrada.")
        pdf_query = urlencode({
            "mode": "custom",
            "start": period.start.isoformat(),
            "end": period.end.isoformat(),
            "hash": fingerprint,
        })
        return redirect("{}?{}".format(reverse("boletas:worker_pdf"), pdf_query))
