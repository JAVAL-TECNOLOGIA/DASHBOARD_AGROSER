import logging
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db import DatabaseError, transaction
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache

from apps.user.models import User

from .periods import DateRange, month_range, resolve_date_range, week_value_for_date
from .analytics import build_payroll_summary
from .models import PayrollRelease, PayslipAcknowledgement, WorkerIdentityProfile
from .services import PAYROLL_TYPES, PaySlipService


logger = logging.getLogger(__name__)
WEEKLY_PAYROLL_TYPES = ("OBP", "OBR")


def _official_payroll_period(service, payroll_type, month_value, week_number=""):
    month = month_range(month_value)
    if payroll_type not in WEEKLY_PAYROLL_TYPES:
        return month, [], ""
    weeks = service.payroll_weeks(month_value, payroll_type)
    selected = str(week_number or "").strip()
    if weeks and selected not in {item["number"] for item in weeks}:
        selected = weeks[-1]["number"]
    row = next((item for item in weeks if item["number"] == selected), None)
    if not row:
        return month, weeks, ""
    return DateRange(row["start"], row["end"], "Semana {} · {} al {}".format(
        row["number"], row["start"].strftime("%d/%m/%Y"), row["end"].strftime("%d/%m/%Y")
    )), weeks, selected


class PaySlipPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "boletas.visualizar_boletas"
    raise_exception = True

    def has_permission(self):
        user = self.request.user
        return user.is_authenticated and (
            getattr(user, "admin", False) or super().has_permission()
        )


def _confirmed_signature(slip, period):
    """Return signature metadata only after this exact payslip was confirmed."""
    from .worker_portal import payslip_fingerprint

    fingerprint = payslip_fingerprint(slip, period)
    acknowledgement = PayslipAcknowledgement.objects.filter(
        payslip_hash=fingerprint,
    ).first()
    if not acknowledgement:
        return {}
    profile = WorkerIdentityProfile.objects.filter(
        worker_document=acknowledgement.worker_document,
    ).first()
    if not profile or not profile.signature:
        return {}
    if not profile.signature.storage.exists(profile.signature.name):
        return {}
    return {
        "signature_path": profile.signature.path,
        "signer_name": acknowledgement.signer_name,
        "signed_at": acknowledgement.confirmed_at,
    }


@method_decorator(never_cache, name="dispatch")
class WorkerPhotoView(PaySlipPermissionMixin, View):
    media_field = 'photo'
    def get(self, request, pk):
        profile = get_object_or_404(WorkerIdentityProfile, pk=pk)
        media = getattr(profile, self.media_field)
        if not media:
            raise Http404('El trabajador no tiene fotografía registrada.')
        try:
            photo = media.open('rb')
        except FileNotFoundError:
            raise Http404('La fotografía no está disponible.')
        return FileResponse(photo, as_attachment=False)


class WorkerSignatureView(WorkerPhotoView):
    media_field = 'signature'


def _return_to_payslips(request):
    url = reverse('boletas:index')
    query_string = request.META.get('QUERY_STRING', '')
    return redirect('{}?{}'.format(url, query_string) if query_string else url)


class WorkerPasswordResetView(PaySlipPermissionMixin, View):
    def post(self, request, document):
        if not document.isdigit() or len(document) != 8:
            messages.error(request, 'El DNI indicado no es válido.')
            return _return_to_payslips(request)
        worker = User.objects.filter(username=document).first()
        if not worker:
            messages.error(request, 'El trabajador todavía no tiene un usuario registrado.')
            return _return_to_payslips(request)
        worker.set_password(document)
        worker.save(update_fields=['password'])
        messages.success(request, 'La clave de {} fue restablecida. Su clave temporal es su DNI.'.format(document))
        return _return_to_payslips(request)


class WorkerIdentityResetView(PaySlipPermissionMixin, View):
    def post(self, request, document):
        if not document.isdigit() or len(document) != 8:
            messages.error(request, 'El DNI indicado no es válido.')
            return _return_to_payslips(request)

        files_to_delete = []
        with transaction.atomic():
            profile = WorkerIdentityProfile.objects.select_for_update().filter(worker_document=document).first()
            if not profile:
                messages.info(request, 'El trabajador no tiene foto ni firma registradas.')
                return _return_to_payslips(request)
            for field_name in ('photo', 'signature'):
                field = getattr(profile, field_name)
                if field and field.name:
                    files_to_delete.append((field.storage, field.name))
            profile.delete()

            def delete_identity_files():
                for storage, name in files_to_delete:
                    try:
                        storage.delete(name)
                    except OSError:
                        logger.exception('No se pudo eliminar el archivo de identidad %s.', name)

            transaction.on_commit(delete_identity_files)

        messages.success(request, 'La foto y firma de {} fueron eliminadas. Deberá registrarlas nuevamente.'.format(document))
        return _return_to_payslips(request)


class PayrollReleaseWorkflowView(PaySlipPermissionMixin, View):
    """Valida y luego autoriza un periodo antes de mostrarlo a trabajadores."""

    def post(self, request):
        if not getattr(request.user, "admin", False):
            return HttpResponse("Solo un administrador puede autorizar boletas.", status=403)
        action = request.POST.get("action", "")
        payroll_type = request.POST.get("payroll_type", "").strip().upper()
        if action not in ("validate", "authorize") or payroll_type not in dict(PAYROLL_TYPES):
            messages.error(request, "La acción o planilla seleccionada no es válida.")
            return _return_to_payslips(request)
        mode = "week" if payroll_type in WEEKLY_PAYROLL_TYPES else "month" if payroll_type in ("ERG", "ERA") else request.POST.get("mode", "month")
        try:
            if payroll_type in WEEKLY_PAYROLL_TYPES:
                period, unused_weeks, unused_selected = _official_payroll_period(PaySlipService(), payroll_type, request.POST.get("month", ""), request.POST.get("payroll_week", ""))
            else:
                period = resolve_date_range(mode, month_value=request.POST.get("month", ""), week_value=request.POST.get("week", ""), start_value=request.POST.get("start", ""), end_value=request.POST.get("end", ""))
        except (TypeError, ValueError):
            messages.error(request, "El periodo seleccionado no es válido.")
            return _return_to_payslips(request)

        with transaction.atomic():
            release, unused_created = PayrollRelease.objects.select_for_update().get_or_create(
                payroll_type=payroll_type,
                period_start=period.start,
                period_end=period.end,
            )
            if action == "validate":
                if not release.validated_at:
                    release.validated_at = timezone.now()
                    release.validated_by = request.user
                    release.save(update_fields=("validated_at", "validated_by"))
                messages.success(request, "Las boletas del periodo fueron validadas.")
            elif not release.validated_at:
                messages.error(request, "Primero debes validar las boletas del periodo.")
            elif not release.released_at:
                release.released_at = timezone.now()
                release.released_by = request.user
                release.save(update_fields=("released_at", "released_by"))
                messages.success(request, "Boletas autorizadas. Los trabajadores ya pueden visualizarlas.")
            else:
                messages.info(request, "Las boletas de este periodo ya estaban autorizadas.")
        return _return_to_payslips(request)


@method_decorator(never_cache, name='dispatch')
class WorkerBadgeView(PaySlipPermissionMixin, View):
    def get(self, request, document):
        from .badge import build_worker_badge
        from .worker_portal import worker_slips
        from .periods import portal_month_range as month_range
        if not document.isdigit() or len(document) != 8:
            return HttpResponse('El DNI debe tener 8 dígitos.', status=400)
        try:
            period = month_range(request.GET.get('month', ''))
        except (ValueError, TypeError):
            return HttpResponse('Selecciona un mes válido.', status=400)
        profile = get_object_or_404(WorkerIdentityProfile, worker_document=document)
        if not profile.photo:
            return HttpResponse('Primero debe registrarse la fotografía del trabajador.', status=409)
        try:
            slips = worker_slips(document, period)
        except DatabaseError:
            return HttpResponse('No se pudo consultar al trabajador. Vuelve a intentarlo.', status=503)
        if not slips:
            raise Http404('No se encontraron datos del trabajador en el mes seleccionado.')
        try:
            with profile.photo.open('rb') as photo:
                content = build_worker_badge(document, slips[0].get('apenom'), slips[0].get('cargo_personal'), photo)
        except (OSError, ValueError):
            return HttpResponse('No se pudo generar el fotocheck. Revisa la fotografía y los datos registrados.', status=409)
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="fotocheck_{}.pdf"'.format(document)
        return response


@method_decorator(never_cache, name='dispatch')
class WorkerBadgeSheetView(PaySlipPermissionMixin, View):
    def get(self, request):
        from .badge import build_worker_badge_sheet

        mode = 'month' if request.GET.get('payroll_type', '').strip().upper() in ('ERG', 'ERA', 'OBP') else request.GET.get('mode', 'month')
        try:
            period = resolve_date_range(
                mode,
                month_value=request.GET.get('month', ''),
                week_value=request.GET.get('week', ''),
                start_value=request.GET.get('start', ''),
                end_value=request.GET.get('end', ''),
            )
        except (TypeError, ValueError):
            return HttpResponse('El periodo seleccionado no es válido.', status=400)

        try:
            slips = PaySlipService().list(period)
        except DatabaseError:
            return HttpResponse('No fue posible consultar los trabajadores.', status=503)

        payroll_type = request.GET.get('payroll_type', '').strip().upper()
        if payroll_type:
            slips = [item for item in slips if item.get('payroll_type') == payroll_type]
        query = request.GET.get('q', '').strip().casefold()
        if query:
            slips = [item for item in slips if query in ' '.join(
                str(item.get(field) or '')
                for field in ('nrodocumento', 'apenom', 'cargo_personal', 'codigoplanilla')
            ).casefold()]

        slips_by_document = {}
        for slip in slips:
            document = str(slip.get('nrodocumento') or '').strip()
            if document.isdigit() and len(document) == 8:
                slips_by_document.setdefault(document, slip)
        profiles = {
            profile.worker_document: profile
            for profile in WorkerIdentityProfile.objects.filter(
                worker_document__in=slips_by_document,
                photo__gt='',
                signature__gt='',
            ).order_by('worker_document')
        }

        workers = []
        for document, slip in slips_by_document.items():
            profile = profiles.get(document)
            if not profile:
                continue
            try:
                with profile.photo.open('rb') as photo:
                    workers.append({
                        'document': document,
                        'name': slip.get('apenom'),
                        'position': slip.get('cargo_personal'),
                        'photo': BytesIO(photo.read()),
                    })
            except (FileNotFoundError, OSError):
                logger.warning('Fotografía no disponible para el fotocheck de %s.', document)

        if not workers:
            return HttpResponse('No hay trabajadores con foto y firma registradas para los filtros seleccionados.', status=404)
        try:
            content = build_worker_badge_sheet(workers)
        except (OSError, ValueError):
            logger.exception('No se pudo generar la hoja de fotochecks.')
            return HttpResponse('No se pudo generar la hoja de fotochecks. Revisa las fotografías registradas.', status=409)
        response = HttpResponse(content, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="fotochecks_registrados_{}.pdf"'.format(period.end.strftime('%Y%m%d'))
        return response


@method_decorator(never_cache, name='dispatch')
class WorkerDetailView(PaySlipPermissionMixin, View):
    def get(self, request, document):
        from .worker_portal import worker_slips, payslip_fingerprint
        from .periods import portal_month_range as month_range
        try:
            period = month_range(request.GET.get('month', ''))
        except (ValueError, TypeError):
            return HttpResponse('Selecciona un mes válido.', status=400)
        try:
            slips = worker_slips(document, period)
        except DatabaseError:
            return HttpResponse('No se pudo consultar el detalle. Vuelve a intentarlo.', status=503)
        if not slips:
            return HttpResponse('No se encontraron boletas para este trabajador en el mes seleccionado.', status=404)
        profile = WorkerIdentityProfile.objects.filter(worker_document=document).first()
        first = slips[0]
        for slip in slips:
            slip['attachment_url'] = '{}?{}'.format(reverse('boletas:worker_month_pdf', args=[document]), urlencode({
                'month': period.start.strftime('%Y-%m'), 'slip': payslip_fingerprint(slip, period)}))
        return render(request, 'boletas/worker_detail.html', {
            'worker': first, 'slips': slips, 'period': period,
            'badge_url': '{}?{}'.format(reverse('boletas:worker_badge', args=[document]), urlencode({'month': period.start.strftime('%Y-%m')})),
            'photo_url': reverse('boletas:worker_photo', args=[profile.pk]) if profile and profile.photo else '',
            'signature_url': reverse('boletas:worker_signature', args=[profile.pk]) if profile and profile.signature else '',
        })


@method_decorator(never_cache, name='dispatch')
class WorkerMonthPdfView(PaySlipPermissionMixin, View):
    def get(self, request, document):
        from .worker_portal import worker_slips, payslip_fingerprint
        from .periods import portal_month_range as month_range
        try:
            period = month_range(request.GET.get('month', ''))
        except (ValueError, TypeError):
            return HttpResponse('Selecciona un mes válido.', status=400)
        try:
            slips = worker_slips(document, period)
        except DatabaseError:
            return HttpResponse('No se pudo consultar la boleta.', status=503)
        slip = next((item for item in slips if payslip_fingerprint(item, period) == request.GET.get('slip')), None)
        if slip is None:
            raise Http404('La boleta no existe para este trabajador y mes.')
        response = HttpResponse(
            PaySlipPdfView._build_pdf(slip, period, **_confirmed_signature(slip, period)),
            content_type='application/pdf',
        )
        response['Content-Disposition'] = 'inline; filename="boleta_{}_{}.pdf"'.format(document, period.start.strftime('%Y%m'))
        return response


@method_decorator(never_cache, name="dispatch")
class PaySlipListView(PaySlipPermissionMixin, View):
    template_name = "boletas/index.html"

    def get(self, request):
        payroll_type = request.GET.get("payroll_type", "").strip().upper()
        mode = "week" if payroll_type in WEEKLY_PAYROLL_TYPES else "month" if payroll_type in ("ERG", "ERA") else request.GET.get("mode", "month")
        month_value = request.GET.get("month", "")
        week_value = request.GET.get("week", "")
        start_value = request.GET.get("start", "")
        end_value = request.GET.get("end", "")
        query = request.GET.get("q", "").strip()
        payroll_week = request.GET.get("payroll_week", "").strip()
        service = PaySlipService()

        try:
            if payroll_type in WEEKLY_PAYROLL_TYPES:
                date_range, payroll_weeks, payroll_week = _official_payroll_period(service, payroll_type, month_value or timezone.localdate().strftime("%Y-%m"), payroll_week)
            else:
                payroll_weeks = []
                date_range = resolve_date_range(mode, month_value=month_value, week_value=week_value, start_value=start_value, end_value=end_value)
        except (TypeError, ValueError, DatabaseError):
            messages.error(request, "El periodo seleccionado no es válido.")
            mode = "month"
            date_range = resolve_date_range(mode)
            payroll_weeks, payroll_week = [], ""

        try:
            slips = service.list(date_range)
        except DatabaseError:
            logger.exception("No se pudieron consultar las boletas.")
            messages.error(request, "No fue posible consultar las boletas en este momento.")
            slips = []

        if payroll_type:
            slips = [
                slip for slip in slips if slip.get("payroll_type") == payroll_type
            ]

        if query:
            normalized = query.casefold()
            slips = [
                slip
                for slip in slips
                if normalized
                in " ".join(
                    str(slip.get(field) or "")
                    for field in ("nrodocumento", "apenom", "cargo_personal", "codigoplanilla")
                ).casefold()
            ]

        all_documents = {
            str(slip.get('nrodocumento') or '').strip()
            for slip in slips
            if str(slip.get('nrodocumento') or '').strip()
        }
        registered_documents = set(WorkerIdentityProfile.objects.filter(
            worker_document__in=all_documents,
            photo__gt='',
            signature__gt='',
        ).values_list('worker_document', flat=True))

        base_params = {
            "mode": mode,
            "month": month_value,
            "week": week_value,
            "start": start_value,
            "end": end_value,
            "payroll_type": payroll_type,
            "payroll_week": payroll_week,
        }
        for slip in slips:
            pdf_params = dict(base_params)
            pdf_params["worker"] = slip.get("idcodigogeneral")
            slip["pdf_url"] = "{}?{}".format(
                reverse("boletas:pdf"), urlencode(pdf_params)
            )
        from .worker_portal import payslip_fingerprint

        fingerprints = []
        for slip in slips:
            slip["fingerprint"] = payslip_fingerprint(slip, date_range)
            fingerprints.append(slip["fingerprint"])
        acknowledgements = {
            item.payslip_hash: item
            for item in PayslipAcknowledgement.objects.filter(
                payslip_hash__in=fingerprints
            )
        }
        for slip in slips:
            slip["acknowledgement"] = acknowledgements.get(slip["fingerprint"])

        paginator = Paginator(slips, 25)
        page = paginator.get_page(request.GET.get("page"))
        documents = {str(slip.get('nrodocumento') or '').strip() for slip in page}
        profiles = {item.worker_document: item for item in WorkerIdentityProfile.objects.filter(
            worker_document__in=documents).only('worker_document', 'photo', 'signature')}
        for slip in page:
            document = str(slip.get('nrodocumento') or '').strip()
            profile = profiles.get(document)
            slip['worker_document'] = document
            slip['has_photo'] = bool(profile and profile.photo)
            slip['has_signature'] = bool(profile and profile.signature)
            slip['detail_url'] = '{}?{}'.format(reverse('boletas:worker_detail', args=[document]),
                urlencode({'month': date_range.end.strftime('%Y-%m')})) if document else ''
        context = {
            "page": page,
            "total_slips": len(slips),
            "period": date_range,
            "mode": mode,
            "month_value": month_value or date_range.start.strftime("%Y-%m"),
            "week_value": week_value or week_value_for_date(date_range.start),
            "start_value": start_value or date_range.start.isoformat(),
            "end_value": end_value or date_range.end.isoformat(),
            "query": query,
            "payroll_type": payroll_type,
            "payroll_week": payroll_week,
            "payroll_types": PAYROLL_TYPES,
            "payroll_weeks": payroll_weeks,
            "release": PayrollRelease.objects.filter(
                payroll_type=payroll_type,
                period_start=date_range.start,
                period_end=date_range.end,
            ).first() if payroll_type else None,
            "registered_count": len(registered_documents),
            "badge_sheet_url": "{}?{}".format(
                reverse("boletas:worker_badge_sheet"),
                urlencode({**base_params, "q": query}),
            ),
            "pagination_query": urlencode(
                {
                    **base_params,
                    "q": query,
                }
            ),
        }
        return render(request, self.template_name, context)


@method_decorator(never_cache, name="dispatch")
class PaySlipConsolidatedView(PaySlipPermissionMixin, View):
    template_name = "boletas/consolidated.html"

    def get(self, request):
        mode = "month" if request.GET.get("payroll_type", "").strip().upper() in ("ERG", "ERA", "OBP") else request.GET.get("mode", "month")
        month_value = request.GET.get("month", "")
        week_value = request.GET.get("week", "")
        start_value = request.GET.get("start", "")
        end_value = request.GET.get("end", "")
        payroll_type = request.GET.get("payroll_type", "").strip().upper()
        position = request.GET.get("position", "").strip()

        try:
            period = resolve_date_range(
                mode,
                month_value=month_value,
                week_value=week_value,
                start_value=start_value,
                end_value=end_value,
            )
        except (TypeError, ValueError):
            messages.error(request, "El periodo seleccionado no es válido.")
            mode = "month"
            period = resolve_date_range(mode)

        service = PaySlipService()
        try:
            slips = service.list(period)
        except DatabaseError:
            logger.exception("No se pudo consultar el consolidado de boletas.")
            messages.error(request, "No fue posible consultar el consolidado.")
            slips = []

        position_source = [
            slip
            for slip in slips
            if not payroll_type or slip.get("payroll_type") == payroll_type
        ]
        available_positions = sorted(
            {
                str(slip.get("cargo_personal") or "SIN CARGO").strip()
                for slip in position_source
            }
        )
        positions_by_payroll = {
            code: sorted(
                {
                    str(slip.get("cargo_personal") or "SIN CARGO").strip()
                    for slip in slips
                    if slip.get("payroll_type") == code
                }
            )
            for code, unused_label in PAYROLL_TYPES
        }
        filtered_slips = [
            slip
            for slip in slips
            if (not payroll_type or slip.get("payroll_type") == payroll_type)
            and (
                not position
                or str(slip.get("cargo_personal") or "SIN CARGO").strip() == position
            )
        ]
        summary = build_payroll_summary(filtered_slips)
        comparison_year = period.end.year
        try:
            monthly_totals = service.monthly_net(
                comparison_year,
                payroll_type=payroll_type,
                position=position,
            )
        except DatabaseError:
            logger.exception("No se pudo consultar la comparación mensual.")
            monthly_totals = [
                {"month": "{}{:02d}".format(comparison_year, month), "net": Decimal("0")}
                for month in range(1, 13)
            ]
            messages.warning(request, "No fue posible cargar la comparación mensual.")

        if mode == "month" and period.start.year == comparison_year:
            monthly_totals[period.start.month - 1]["net"] = summary["total_net"]

        month_names = (
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        )
        context = {
            **summary,
            "period": period,
            "mode": mode,
            "month_value": month_value or period.start.strftime("%Y-%m"),
            "week_value": week_value or week_value_for_date(period.start),
            "start_value": start_value or period.start.isoformat(),
            "end_value": end_value or period.end.isoformat(),
            "payroll_type": payroll_type,
            "payroll_types": PAYROLL_TYPES,
            "position": position,
            "available_positions": available_positions,
            "positions_by_payroll": positions_by_payroll,
            "comparison_year": comparison_year,
            "payroll_chart": [
                {"label": row["name"], "data": float(row["net"])}
                for row in summary["payrolls"]
            ],
            "position_chart": [
                [row["name"], float(row["net"])]
                for row in summary["positions"][:12]
            ],
            "worker_chart": [
                [row["name"], float(row["net"])]
                for row in summary["workers"][:15]
            ],
            "monthly_chart": [
                [month_names[index], float(row["net"])]
                for index, row in enumerate(monthly_totals)
                if (comparison_year, index + 1) >= (2026, 8)
            ],
            "monthly_rows": [
                {"name": month_names[index], "net": row["net"]}
                for index, row in enumerate(monthly_totals)
                if (comparison_year, index + 1) >= (2026, 8)
            ],
        }
        return render(request, self.template_name, context)


@method_decorator(never_cache, name="dispatch")
class PaySlipPdfView(PaySlipPermissionMixin, View):

    def get(self, request):
        worker_id = request.GET.get("worker", "").strip()
        if not worker_id:
            raise Http404("No se indicó el trabajador.")

        try:
            service = PaySlipService()
            payroll_type = request.GET.get("payroll_type", "").strip().upper()
            if payroll_type in WEEKLY_PAYROLL_TYPES:
                period, unused_weeks, unused_selected = _official_payroll_period(service, payroll_type, request.GET.get("month", ""), request.GET.get("payroll_week", ""))
            else:
                period = resolve_date_range(request.GET.get("mode", "month"), month_value=request.GET.get("month", ""), week_value=request.GET.get("week", ""), start_value=request.GET.get("start", ""), end_value=request.GET.get("end", ""))
            slips = service.list(period)
        except (TypeError, ValueError, DatabaseError):
            logger.exception("No se pudo generar la boleta en PDF.")
            raise Http404("No fue posible consultar la boleta.")

        slip = next(
            (
                item
                for item in slips
                if str(item.get("idcodigogeneral") or "").strip() == worker_id
            ),
            None,
        )
        if slip is None:
            raise Http404("La boleta solicitada no existe para este periodo.")

        response = HttpResponse(
            self._build_pdf(slip, period, **_confirmed_signature(slip, period)),
            content_type="application/pdf",
        )
        filename = "boleta_{}_{}.pdf".format(
            slip.get("nrodocumento") or worker_id,
            period.end.strftime("%Y%m%d"),
        )
        response["Content-Disposition"] = 'inline; filename="{}"'.format(filename)
        return response

    @staticmethod
    def _build_obp_pdf(slip, period, signature_path=None, signer_name="", signed_at=None, employer_signature_path=None):
        """Render the legacy two-copy plant-worker payslip."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        page_width, page_height = landscape(A4)
        pdf = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        pdf.setTitle(slip.get("document_title") or "Boleta de remuneraciones")

        def clean(value, default="-"):
            return str(value).strip() if value not in (None, "") else default

        def decimal(value):
            try:
                return Decimal(str(value or 0))
            except Exception:
                return Decimal("0")

        def money(value):
            return "{:,.2f}".format(decimal(value))

        concepts = slip.get("concepts") or []
        groups = {
            key: [item for item in concepts if clean(item.get("idtipoconcepto"), "").upper() == key]
            for key in ("IN", "DE", "AE", "TI")
        }
        calculated_totals = {
            key: sum((decimal(item.get("importe")) for item in rows), Decimal("0"))
            for key, rows in groups.items()
        }

        def total_concept(code, fallback):
            match = next(
                (
                    item for item in concepts
                    if clean(item.get("codigo_equiv"), "").upper() == code
                ),
                None,
            )
            return decimal(match.get("importe")) if match else fallback

        # The procedure returns official total concepts. They are authoritative because
        # some visible income rows are informative/accumulated and must not be summed twice.
        totals = {
            "IN": total_concept("TOT_IN", calculated_totals["IN"]),
            "DE": total_concept("TOT_DE", calculated_totals["DE"]),
            "AE": total_concept("TOT_AE", calculated_totals["AE"]),
            "TI": calculated_totals["TI"],
        }
        net_total = total_concept("TO0002", totals["IN"] - totals["DE"])

        month_names = (
            "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
            "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
        )
        month_number = int(slip.get("mes_pago_0") or period.end.month)
        year_number = int(slip.get("anio_pago_0") or period.end.year)
        month_label = "{} {}".format(month_names[max(1, min(12, month_number)) - 1], year_number)
        week_text = clean(slip.get("nro_semanas"), "-")
        week_parts = [part.strip() for part in week_text.split("-") if part.strip()]
        week_from = week_parts[0] if week_parts else week_text
        week_to = week_parts[-1] if week_parts else week_text

        def fit(value, width, font="Helvetica", size=5.6):
            value = clean(value)
            while len(value) > 1 and pdf.stringWidth(value, font, size) > width:
                value = value[:-1]
            return value if value == clean(value) else value.rstrip() + "…"

        def label_value(x, y, label, value, label_width=23 * mm, size=6, value_width=90 * mm):
            pdf.setFont("Helvetica-Bold", size)
            pdf.drawString(x, y, label)
            pdf.setFont("Helvetica", size)
            pdf.drawString(x + label_width, y, fit(value, value_width, size=size))

        def draw_copy(left):
            width = 273 * mm
            right = left + width
            top = page_height - 6 * mm
            center = left + width / 2

            pdf.setFillColor(colors.black)
            pdf.setFont("Helvetica-Bold", 8.4)
            pdf.drawCentredString(center, top, "AGROSERVICE ICA SUR S.A.C.")
            pdf.setFont("Helvetica", 5.5)
            pdf.drawCentredString(center, top - 4 * mm, "CAR. PANAMERICANA SUR KM. 297 - ICA - ICA - SUBTANJALLA")
            pdf.setFont("Helvetica-Bold", 6.2)
            pdf.drawCentredString(center, top - 8 * mm, "R.U.C : {}".format(clean(slip.get("ruc"), "20534627077")))
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawCentredString(center, top - 14 * mm, "BOLETA DE REMUNERACIONES")
            regime = clean(slip.get("REGIMENLABORAL"), "REGIMEN AGRARIO LEY 31110").replace("N°", "")
            pdf.setFont("Helvetica-Bold", 6.2)
            pdf.drawCentredString(center, top - 18 * mm, fit("OBREROS " + regime, width - 4 * mm, "Helvetica-Bold", 6.2))
            pdf.setFont("Helvetica", 6)
            pdf.drawCentredString(center, top - 22 * mm, "Mes : {}".format(month_label))
            pdf.drawCentredString(
                center,
                top - 26 * mm,
                "De Semana : {} desde {} / A Semana : {} hasta {}".format(
                    week_from, period.start.strftime("%d/%m/%Y"), week_to, period.end.strftime("%d/%m/%Y")
                ),
            )

            info_top = top - 31 * mm
            mid = left + width / 2
            label_value(left + 2 * mm, info_top, "NOMBRES", slip.get("apenom"))
            label_value(mid + 1 * mm, info_top, "CARGO", slip.get("cargo_personal"), 18 * mm)
            affiliate = "{} - {}".format(clean(slip.get("snp_spp"), ""), clean(slip.get("CUSSP"), "")).strip(" -")
            label_value(left + 2 * mm, info_top - 4 * mm, "AFILIADO", affiliate)
            label_value(mid + 1 * mm, info_top - 4 * mm, "SEGURO SOCIAL", "ESSALUD", 24 * mm)
            label_value(left + 2 * mm, info_top - 8 * mm, "NRO. DOC.", slip.get("nrodocumento"))
            label_value(mid + 1 * mm, info_top - 8 * mm, "BCP", "", 18 * mm)
            label_value(left + 2 * mm, info_top - 12 * mm, "F. INGRESO", slip.get("fecha_ingreso"))
            label_value(mid + 1 * mm, info_top - 12 * mm, "REM. BAS.", money(slip.get("basico")), 18 * mm)

            box_top = info_top - 16 * mm
            box_bottom = 53 * mm
            box_height = box_top - box_bottom
            col_width = width / 4
            pdf.setLineWidth(0.45)
            pdf.rect(left, box_bottom, width, box_height)
            headers = (("INGRESOS", "IN"), ("DESCUENTOS", "DE"), ("APORTES EMPLEADOR", "AE"), ("TIEMPOS", "TI"))
            for index, (heading, key) in enumerate(headers):
                x = left + index * col_width
                if index:
                    pdf.line(x, box_bottom, x, box_top)
                pdf.setFont("Helvetica-Bold", 6.2)
                pdf.drawCentredString(x + col_width / 2, box_top - 3.2 * mm, heading)
                pdf.line(x, box_top - 5 * mm, x + col_width, box_top - 5 * mm)
                row_y = box_top - 8.5 * mm
                rows = groups[key]
                row_size = 5.1 if len(rows) <= 15 else 4.5
                row_step = 3.4 * mm if len(rows) <= 15 else 2.9 * mm
                max_rows = max(1, int((box_height - 10 * mm) / row_step))
                for item in rows[:max_rows]:
                    pdf.setFont("Helvetica", row_size)
                    pdf.drawString(x + 1.2 * mm, row_y, fit(item.get("descripcion"), col_width - 13 * mm, size=row_size))
                    pdf.drawRightString(x + col_width - 1.2 * mm, row_y, money(item.get("importe")))
                    row_y -= row_step

            totals_y = box_bottom - 4.5 * mm
            total_labels = (("TOTAL INGRESOS", totals["IN"]), ("TOTAL DESCUENTOS", totals["DE"]), ("TOTAL APORTES", totals["AE"]), ("Neto a Pagar S/", net_total))
            for index, (label, value) in enumerate(total_labels):
                x = left + index * col_width
                pdf.setFont("Helvetica-Bold", 5.4)
                pdf.drawString(x + 1 * mm, totals_y, label)
                pdf.drawRightString(x + col_width - 1 * mm, totals_y, money(value))

            detail_top = 45 * mm
            detail_bottom = 19 * mm
            detail_width = width * 0.55
            pdf.rect(left, detail_bottom, detail_width, detail_top - detail_bottom)
            widths = (12 * mm, 20 * mm, 18 * mm, detail_width - 50 * mm)
            cursor = left
            for item_width in widths[:-1]:
                cursor += item_width
                pdf.line(cursor, detail_bottom, cursor, detail_top)
            pdf.line(left, detail_top - 5 * mm, left + detail_width, detail_top - 5 * mm)
            for index, heading in enumerate(("DIA", "FECHA", "HORAS", "RENDIM.")):
                start = left + sum(widths[:index])
                pdf.setFont("Helvetica-Bold", 5.4)
                pdf.drawCentredString(start + widths[index] / 2, detail_top - 3.5 * mm, heading)
            day_names = ("LU", "MA", "MI", "JU", "VI", "SA", "DO")
            days = (period.end - period.start).days + 1
            for index in range(7):
                row_y = detail_top - (8 + index * 2.6) * mm
                pdf.setFont("Helvetica", 5.1)
                pdf.drawCentredString(left + widths[0] / 2, row_y, day_names[index])
                if days <= 7 and index < days:
                    current = period.start + __import__("datetime").timedelta(days=index)
                    pdf.drawCentredString(left + widths[0] + widths[1] / 2, row_y, current.strftime("%d/%m/%Y"))
            pdf.setFont("Helvetica-Bold", 5.2)
            pdf.drawString(left + 1 * mm, detail_bottom + 1.5 * mm, "TOTAL DETALLE")

            signature_left = left + detail_width + 5 * mm
            signature_right = right - 3 * mm
            signature_middle = (signature_left + signature_right) / 2
            signature_line_y = 28 * mm
            if employer_signature_path:
                pdf.drawImage(employer_signature_path, signature_left + 4 * mm, signature_line_y + 1 * mm, 35 * mm, 13 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
            if signature_path:
                try:
                    pdf.drawImage(signature_path, signature_middle + 4 * mm, signature_line_y + 1 * mm, 35 * mm, 13 * mm, preserveAspectRatio=True, anchor="c", mask="auto")
                except Exception:
                    logger.exception("No se pudo insertar la firma del trabajador en la boleta OBP.")
            pdf.line(signature_left, signature_line_y, signature_middle - 2 * mm, signature_line_y)
            pdf.line(signature_middle + 2 * mm, signature_line_y, signature_right, signature_line_y)
            pdf.setFont("Helvetica", 5.3)
            pdf.drawCentredString((signature_left + signature_middle) / 2, signature_line_y - 3 * mm, "FIRMA DEL EMPLEADOR")
            pdf.drawCentredString((signature_middle + signature_right) / 2, signature_line_y - 3 * mm, clean(signer_name or slip.get("apenom")))
            pdf.drawCentredString((signature_middle + signature_right) / 2, signature_line_y - 6 * mm, "DNI: {}".format(clean(slip.get("nrodocumento"))))
            pdf.setFont("Helvetica-Bold", 5.2)
            pdf.drawCentredString((signature_middle + signature_right) / 2, 15 * mm, "FIRMA DEL TRABAJADOR")
            if signed_at:
                pdf.setFont("Helvetica", 4.5)
                pdf.drawCentredString((signature_middle + signature_right) / 2, 12 * mm, "Conformidad: {}".format(signed_at.strftime("%d/%m/%Y %H:%M")))

        draw_copy(12 * mm)
        pdf.showPage()
        pdf.save()
        return buffer.getvalue()

    @staticmethod
    def _build_pdf(slip, period, signature_path=None, signer_name="", signed_at=None):
        employer_signature = Path(__file__).resolve().parent / "assets" / "firma_empleador.bmp"
        employer_signature_path = str(employer_signature) if employer_signature.is_file() else None
        if str(slip.get("payroll_type") or "").strip().upper() in ("ERG", "ERA", "OBP"):
            return PaySlipPdfView._build_erg_pdf(
                slip,
                period,
                signature_path=signature_path,
                employer_signature_path=employer_signature_path,
            )
        if str(slip.get("payroll_type") or "").strip().upper() == "OBP":
            return PaySlipPdfView._build_obp_pdf(
                slip,
                period,
                signature_path=signature_path,
                signer_name=signer_name,
                signed_at=signed_at,
                employer_signature_path=employer_signature_path,
            )
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            Image,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )

        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=14 * mm,
            leftMargin=14 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
            title=slip.get("document_title") or "Boleta de pago",
        )
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="PayslipTitle",
                parent=styles["Title"],
                alignment=TA_CENTER,
                fontSize=15,
                leading=18,
                textColor=colors.HexColor("#244767"),
            )
        )
        styles.add(
            ParagraphStyle(
                name="Amount",
                parent=styles["BodyText"],
                alignment=TA_RIGHT,
            )
        )

        def text(value, default="-"):
            return str(value).strip() if value not in (None, "") else default

        def amount(value):
            return "S/ {:,.2f}".format(Decimal(str(value or 0)))

        story = [
            Paragraph(slip.get("document_title") or "BOLETA DE PAGO", styles["PayslipTitle"]),
            Paragraph(text(slip.get("payroll_type_label")), styles["Heading3"]),
            Paragraph("Periodo: {}".format(period.label), styles["BodyText"]),
            Spacer(1, 5 * mm),
        ]
        employee_data = [
            ["Trabajador", text(slip.get("apenom")), "Documento", text(slip.get("nrodocumento"))],
            ["Cargo", text(slip.get("cargo_personal")), "Código", text(slip.get("idcodigogeneral"))],
            ["Régimen", text(slip.get("REGIMENLABORAL")), "Planilla", text(slip.get("codigoplanilla"))],
            ["Días trabajados", text(slip.get("dias_trabajados"), "0"), "Básico", amount(slip.get("basico"))],
        ]
        employee_table = Table(employee_data, colWidths=[31 * mm, 61 * mm, 31 * mm, 57 * mm])
        employee_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5df")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#edf3f8")),
                    ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#edf3f8")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([employee_table, Spacer(1, 6 * mm)])

        concepts = slip.get("concepts", [])
        summary_basic = slip.get("basico")
        if text(slip.get("payroll_type")).upper() == "ERG":
            import unicodedata

            def normalized(value):
                return unicodedata.normalize("NFKD", text(value)).encode("ascii", "ignore").decode().upper()

            def concept_total(predicate):
                total = Decimal("0")
                for concept in concepts:
                    searchable = normalized(
                        f'{concept.get("codigo_equiv", "")} {concept.get("descripcion", "")}'
                    )
                    if predicate(searchable):
                        total += Decimal(str(concept.get("importe") or 0))
                return total

            fondo_afp = concept_total(
                lambda value: "AFP" in value
                and any(word in value for word in ("FONDO", "APORTE", "OBLIGATORIO"))
                and "SEGURO" not in value
            )
            seguro_afp = concept_total(lambda value: "AFP" in value and "SEGURO" in value)
            renta_quinta = concept_total(
                lambda value: "QUINTA" in value or "RENTA 5" in value or "5TA CATEGORIA" in value
            )
            essalud = concept_total(lambda value: "ESSALUD" in value)

            def summary_box(title, rows, color):
                table = Table(
                    [[title, ""]] + [[label, amount(value)] for label, value in rows],
                    colWidths=[37 * mm, 23 * mm],
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("SPAN", (0, 0), (-1, 0)),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(color)),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5df")),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("PADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                return table

            earned_basic = next(
                (
                    concept.get("importe")
                    for concept in concepts
                    if str(concept.get("codigo_equiv") or "").strip().upper() == "IN0001"
                ),
                slip.get("basico"),
            )
            summary_basic = earned_basic
            income_box = summary_box("INGRESOS", [("Básico", earned_basic)], "#2e7d32")
            deduction_box = summary_box(
                "DESCUENTOS",
                [
                    ("Fondo AFP", fondo_afp),
                    ("Seguro AFP", seguro_afp),
                    ("Renta 5ta. categoría", renta_quinta),
                ],
                "#b3261e",
            )
            contribution_box = summary_box("APORTES", [("ESSALUD", essalud)], "#244767")
            boxes = Table([[income_box, deduction_box, contribution_box]], colWidths=[60 * mm] * 3)
            boxes.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            story.extend([boxes, Spacer(1, 6 * mm)])
        else:
            concept_rows = [["Código", "Concepto", "Tipo", "Importe"]]
            for concept in concepts:
                concept_rows.append(
                    [
                        text(concept.get("codigo_equiv")),
                        text(concept.get("descripcion")),
                        text(concept.get("idtipoconcepto")),
                        amount(concept.get("importe")),
                    ]
                )
            if len(concept_rows) == 1:
                concept_rows.append(["-", "Sin conceptos para el periodo", "-", amount(0)])

            concept_table = Table(
                concept_rows,
                colWidths=[25 * mm, 100 * mm, 20 * mm, 35 * mm],
                repeatRows=1,
            )
            concept_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#244767")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5df")),
                        ("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("PADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.extend(
                [Paragraph("Ingresos y conceptos", styles["Heading3"]), concept_table, Spacer(1, 6 * mm)]
            )

        totals = Table(
            [
                ["Básico", amount(summary_basic)],
                ["Total ingresos", amount(slip.get("income_total"))],
                ["Total descuentos", amount(slip.get("deduction_total"))],
                ["NETO A PAGAR", amount(slip.get("net_total"))],
            ],
            colWidths=[55 * mm, 40 * mm],
            hAlign="RIGHT",
        )
        totals.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#aebdca")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d9edf7")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(totals)
        if employer_signature_path or signature_path:
            employer_signature = Image(employer_signature_path, width=45 * mm, height=18 * mm, kind="proportional") if employer_signature_path else ""
            signature = Image(signature_path, width=45 * mm, height=18 * mm, kind="proportional") if signature_path else ""
            signature_table = Table(
                [
                    [employer_signature, signature],
                    [Paragraph("Firma del empleador", styles["BodyText"]), Paragraph("Firma digital del trabajador", styles["BodyText"]) if signature_path else ""],
                    ["", Paragraph(text(signer_name), styles["BodyText"]) if signature_path else ""],
                    ["", Paragraph(
                        "Conformidad registrada: {}".format(
                            signed_at.strftime("%d/%m/%Y %H:%M") if signed_at else "-"
                        ),
                        styles["BodyText"],
                    ) if signature_path else ""],
                ],
                colWidths=[75 * mm, 75 * mm],
                hAlign="LEFT",
            )
            signature_table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEABOVE", (0, 1), (0, 1), 0.6, colors.HexColor("#244767")),
                ("LINEABOVE", (1, 1), (1, 1), 0.6, colors.HexColor("#244767")) if signature_path else ("LINEABOVE", (1, 1), (1, 1), 0, colors.white),
            ]))
            story.extend([Spacer(1, 8 * mm), signature_table])
        document.build(story)
        return buffer.getvalue()

    @staticmethod
    def _build_erg_pdf(slip, period, signature_path=None, employer_signature_path=None):
        from django.conf import settings
        from .erg_txt import locate_payroll, read_payroll, PayrollTextError
        from .erg_pdf import build_pdf
        from pathlib import Path
        if slip.get('document_type') not in (None, '', 'payment'):
            raise Http404('Esta fuente TXT corresponde a boletas regulares; falta la exportación del documento especial solicitado.')
        if period.start.strftime('%Y%m') != period.end.strftime('%Y%m'):
            raise Http404('Selecciona un solo mes para generar la boleta ERG desde TXT.')
        month = period.end.strftime('%Y%m')
        payroll_type = str(slip.get('payroll_type') or 'ERG').strip().upper()
        document = str(slip.get('nrodocumento') or '').strip()
        setting_name = '{}_TXT_ROOT'.format(payroll_type)
        fallback_folder = '{}-source'.format(payroll_type.lower())
        root = getattr(settings, setting_name, str(Path(settings.BASE_DIR) / 'runtime_logs' / fallback_folder))
        try:
            source = locate_payroll(root, month, document)
            return build_pdf(
                read_payroll(source, month, document, payroll_type=payroll_type),
                signature_path=signature_path,
                employer_signature_path=employer_signature_path,
            )
        except (OSError, PayrollTextError) as exc:
            logger.warning('No se pudo generar ERG desde TXT: %s', exc)
            raise Http404('No se pudo generar la boleta desde el TXT validado: {}'.format(exc))

    @staticmethod
    def _build_erg_pdf_legacy(slip, period):
        """Boleta ERG en formato horizontal A4 con dos copias, según boleta.pdf."""
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        out = BytesIO(); width, height = A4; pdf = canvas.Canvas(out, pagesize=(width, height)); half = width
        concepts = slip.get("concepts") or []
        def money(v): return "{:,.2f}".format(float(v or 0))
        def total(words): return sum(float(c.get("importe") or 0) for c in concepts if any(w in str(c.get("descripcion") or "").upper() for w in words))
        def cvalue(words, default=0): return next((float(c.get("importe") or 0) for c in concepts if any(w in str(c.get("descripcion") or "").upper() for w in words)), default)
        basic = next((c.get("importe") for c in concepts if str(c.get("codigo_equiv") or "").upper() == "IN0001"), slip.get("basico")); fund=total(["FONDO AFP","APORTE AFP"]); insurance=total(["SEGURO AFP"]); fifth=total(["QUINTA","RENTA 5"]); essalud=total(["ESSALUD"]); hr_normal=cvalue(["HR.NORMALES","H.R. NORMALES"],240); hr_holiday=cvalue(["HR.FERIADO","H.R. FERIADO"]); worked=cvalue(["D.TRABAJADOS","DIAS TRABAJADOS"])
        def draw(x):
            l=x+5*mm; r=x+half-5*mm; top=height-12*mm; pdf.setFillColor(colors.black); pdf.setFont("Helvetica",6.5); pdf.drawString(l,top,"AGROSERVICE ICA SUR S.A.C."); pdf.drawString(l,top-5*mm,"R.U.C : 20534627077"); pdf.drawString(l,top-10*mm,"CAR.PANAMERICANA SUR KM. 297 - ICA - ICA - SUBTANJALLA"); pdf.setFont("Helvetica-Bold",11); pdf.drawCentredString((l+r)/2,top-17*mm,"BOLETA DE REMUNERACIONES"); pdf.setFont("Helvetica",7); name=str(slip.get("apenom") or "-"); doc=str(slip.get("nrodocumento") or "-"); pdf.drawString(l,top-24*mm,"CODIGO : "+doc+" "+name); pdf.drawString(l,top-29*mm,"CARGO : "+str(slip.get("cargo_personal") or "-")); pdf.drawString(l,top-34*mm,"AFP : "+str(slip.get("idafp") or slip.get("snp_spp") or "-")); pdf.drawString(r-75*mm,top-24*mm,"SUELDO : S/ "+money(slip.get("basico"))); pdf.drawString(r-75*mm,top-29*mm,"DNI : "+doc); pdf.drawString(r-75*mm,top-34*mm,"FEC. INGRESO : "+str(slip.get("fecha_ingreso") or "-")); y=top-47*mm; pdf.rect(l,y,r-l,8*mm); pdf.drawString(l+2*mm,y+3*mm,"PERIODO "+str(slip.get("periodo_planilla") or period.label)+"    DEL "+period.start.strftime("%d/%m/%Y")+"    AL "+period.end.strftime("%d/%m/%Y")); y-=8*mm; cols=[l,l+(r-l)*.25,l+(r-l)*.5,l+(r-l)*.75,r]; heads=["REMUNERACIONES","RETENCIONES AL TRABAJADOR","CONTRIBUCIONES DEL EMPLEADOR","TIEMPOS"]; pdf.setFont("Helvetica-Bold",6.5)
            box_bottom = y - 68*mm
            for i in range(4): pdf.rect(cols[i],box_bottom,cols[i+1]-cols[i],68*mm); pdf.drawCentredString((cols[i]+cols[i+1])/2,y-4*mm,heads[i])
            pdf.setFont("Helvetica",7)
            rows=[(0,"BASICO",basic),(1,"FONDO AFP",fund),(1,"SEGURO AFP",insurance),(1,"RENTA 5TA.",fifth),(2,"ESSALUD",essalud),(3,"HR.NORMALES",hr_normal),(3,"HR.FERIADO",hr_holiday),(3,"D.TRABAJADOS",worked)]
            positions={(0,"BASICO"):56,(1,"FONDO AFP"):56,(1,"SEGURO AFP"):49,(1,"RENTA 5TA."):42,(2,"ESSALUD"):56,(3,"HR.NORMALES"):56,(3,"HR.FERIADO"):49,(3,"D.TRABAJADOS"):42}
            for i,label,value in rows:
                yy=y-positions[(i,label)]*mm
                pdf.drawString(cols[i]+2*mm,yy,label); pdf.drawRightString(cols[i+1]-2*mm,yy,money(value))
            y=box_bottom-14*mm; values=[slip.get("income_total"),slip.get("deduction_total"),essalud,slip.get("net_total")]
            for i,(label,value) in enumerate(zip(["TOTAL INGRESOS S/.","TOTAL RETENCIONES S/.","TOTAL APORTACION S/.","NETO A PAGAR S/."],values)): pdf.rect(cols[i],y,cols[i+1]-cols[i],14*mm); pdf.setFont("Helvetica-Bold" if i==3 else "Helvetica",7); pdf.drawCentredString((cols[i]+cols[i+1])/2,y+9*mm,label); pdf.drawCentredString((cols[i]+cols[i+1])/2,y+3*mm,money(value))
        draw(0); pdf.save(); return out.getvalue()
