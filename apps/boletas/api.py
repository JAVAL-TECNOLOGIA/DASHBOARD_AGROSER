import json
import base64
import binascii
import uuid
import mimetypes
from io import BytesIO
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import DatabaseError, transaction
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.user.models import User

from .models import AttendanceMark, PayrollRelease, PayslipAcknowledgement, PayslipView, PortalContent, WorkerAccessRestriction, WorkerIdentityProfile
from .periods import DateRange, portal_month_range as month_range
from .services import PaySlipService
from .views import PaySlipPdfView, _official_payroll_period
from .worker_portal import WorkerIdentityService, payslip_fingerprint, worker_slips


TOKEN_SALT = "agroservice-rrhh-api"
TOKEN_MAX_AGE = 60 * 60 * 12


@csrf_exempt
@require_http_methods(["GET", "POST"])
def portal_content_api(request):
    user, role = _auth(request, ("admin", "worker"))
    if not user:
        return _json({"error": "SesiÃ³n no vÃ¡lida."}, 401)
    if request.method == "GET":
        items = PortalContent.objects.filter(active=True)
        return _json({"rit": next((_content_json(x) for x in items if x.kind == PortalContent.KIND_RIT), None), "notice": next((_content_json(x) for x in items if x.kind == PortalContent.KIND_NOTICE), None)})
    if role != "admin":
        return _json({"error": "Solo el administrador puede actualizar contenidos."}, 403)
    kind = str(request.POST.get("kind") or "").upper()
    if kind not in (PortalContent.KIND_RIT, PortalContent.KIND_NOTICE):
        return _json({"error": "Tipo de contenido invÃ¡lido."}, 400)
    item, _ = PortalContent.objects.get_or_create(kind=kind, defaults={"updated_by": user})
    item.title = str(request.POST.get("title") or "").strip()
    item.body = str(request.POST.get("body") or "").strip()
    item.active = True; item.updated_by = user
    if request.FILES.get("file"):
        item.file = request.FILES["file"]
    item.save()
    return _json({"ok": True, "content": _content_json(item)})


def _content_json(item):
    return {"kind": item.kind, "title": item.title, "body": item.body, "file": item.file.url if item.file else "", "updatedAt": item.updated_at.isoformat()}


@csrf_exempt
@require_http_methods(["GET", "POST"])
def admin_attendance_api(request):
    user, role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "SesiÃ³n administrativa no vÃ¡lida."}, 401)
    if request.method == "POST":
        data = _body(request); document = str(data.get("document") or "").strip(); action = str(data.get("action") or "IN").upper()
        if not document.isdigit() or len(document) != 8 or action not in ("IN", "OUT"):
            return _json({"error": "DNI o tipo de marcaciÃ³n invÃ¡lido."}, 400)
        mark = AttendanceMark.objects.create(worker_document=document, action=action, marked_by=user)
        return _json({"ok": True, "document": document, "action": action, "markedAt": mark.marked_at.isoformat()})
    rows = AttendanceMark.objects.all()[:100]
    return _json({"marks": [{"document": x.worker_document, "action": x.action, "markedAt": x.marked_at.isoformat()} for x in rows]})


def _cors(response):
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def _json(data, status=200):
    return _cors(JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False}))


def _body(request):
    try:
        return json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return {}


def _token(user, role):
    return signing.dumps({"user_id": user.pk, "role": role}, salt=TOKEN_SALT, compress=True)


def _auth(request, roles=("worker", "admin")):
    value = request.headers.get("Authorization", "")
    if not value.startswith("Bearer "):
        return None, None
    try:
        payload = signing.loads(value[7:], salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
        if payload.get("role") not in roles:
            return None, None
        user = User.objects.get(pk=payload["user_id"], active=True)
        if payload.get("role") == "worker" and WorkerAccessRestriction.objects.filter(
            worker_document=user.username, disabled=True
        ).exists():
            return None, None
        return user, payload["role"]
    except (signing.BadSignature, signing.SignatureExpired, User.DoesNotExist, KeyError):
        return None, None


def _amount(value):
    return float(Decimal(str(value or 0)))


def _full_name(user):
    return "{} {}".format(user.first_name, user.last_name).strip() or user.username


def _identity_complete(user):
    from .identity import identity_complete
    return identity_complete(user)


def _is_released(payroll_type, period):
    return PayrollRelease.objects.filter(
        payroll_type=str(payroll_type or "").strip().upper(),
        period_start=period.start,
        period_end=period.end,
        released_at__isnull=False,
    ).exists()


def _decode_image(value, label):
    if not isinstance(value, str) or "," not in value:
        raise ValueError("{} no válida.".format(label))
    header, encoded = value.split(",", 1)
    allowed = {"data:image/png;base64": "png", "data:image/jpeg;base64": "jpg", "data:image/webp;base64": "webp"}
    extension = allowed.get(header.lower())
    if not extension:
        raise ValueError("El formato de {} no está permitido.".format(label))
    try:
        content = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error):
        raise ValueError("{} no válida.".format(label))
    if not 200 <= len(content) <= 5 * 1024 * 1024:
        raise ValueError("{} debe pesar menos de 5 MB.".format(label))
    return ContentFile(content, name="{}.{}".format(uuid.uuid4().hex, extension))


def _slip_json(slip, period, week_number=""):
    fingerprint = payslip_fingerprint(slip, period)
    return {
        "hash": fingerprint,
        "type": slip.get("document_type", "payment"),
        "title": slip.get("document_type_label") or "Boleta de Pago",
        "payroll": slip.get("payroll_type_label") or "",
        "period": period.label,
        "week": week_number,
        "basic": _amount(slip.get("basico")),
        "income": _amount(slip.get("income_total")),
        "deductions": _amount(slip.get("deduction_total")),
        "net": _amount(slip.get("net_total")),
        "confirmed": PayslipAcknowledgement.objects.filter(payslip_hash=fingerprint).exists(),
    }


WEEKLY_PAYROLL_TYPES = ("OBP", "OBR")


def _official_week_period(month_value, week_number, payroll_type="OBP"):
    weeks = PaySlipService().payroll_weeks(month_value, payroll_type)
    row = next((item for item in weeks if item["number"] == str(week_number).strip()), None)
    if not row:
        raise ValueError("La semana no pertenece al periodo seleccionado.")
    return DateRange(
        start=row["start"],
        end=row["end"],
        label="Semana {} · {} al {}".format(
            row["number"], row["start"].strftime("%d/%m/%Y"), row["end"].strftime("%d/%m/%Y")
        ),
    )


def _worker_month_slips(document, month_value, selected_week=""):
    """Use weekly periods for plant workers and monthly periods for employees."""
    month = month_range(month_value)
    monthly_slips = worker_slips(document, month)
    results = [
        (slip, month, "")
        for slip in monthly_slips
        if str(slip.get("payroll_type") or "").strip().upper() not in WEEKLY_PAYROLL_TYPES
    ]
    weekly_payroll = next(
        (
            str(slip.get("payroll_type") or "").strip().upper()
            for slip in monthly_slips
            if str(slip.get("payroll_type") or "").strip().upper() in WEEKLY_PAYROLL_TYPES
        ),
        "",
    )
    weeks = []
    selected = ""
    if weekly_payroll:
        period, weeks, selected = _official_payroll_period(PaySlipService(), weekly_payroll, month_value, selected_week)
    if selected:
        results.extend(
            (slip, period, selected)
            for slip in worker_slips(document, period)
            if str(slip.get("payroll_type") or "").strip().upper() == weekly_payroll
        )
    results = [
        item for item in results
        if _is_released(item[0].get("payroll_type"), item[1])
    ]
    return month, results, weeks, selected


def _requested_worker_slip(document, month_value, requested_hash, week_value=""):
    period = month_range(month_value)
    if week_value:
        monthly_slips = worker_slips(document, period)
        weekly_payroll = next(
            (
                str(item.get("payroll_type") or "").strip().upper()
                for item in monthly_slips
                if str(item.get("payroll_type") or "").strip().upper() in WEEKLY_PAYROLL_TYPES
            ),
            "",
        )
        if not weekly_payroll:
            raise ValueError("El trabajador no pertenece a una planilla semanal.")
        period, unused_weeks, selected = _official_payroll_period(PaySlipService(), weekly_payroll, month_value, week_value)
        if not selected:
            raise ValueError("La semana no pertenece al periodo seleccionado.")
    slip = next(
        (
            item for item in worker_slips(document, period)
            if payslip_fingerprint(item, period) == requested_hash
        ),
        None,
    )
    if slip and not _is_released(slip.get("payroll_type"), period):
        slip = None
    if slip:
        slip['_payroll_week'] = str(week_value or '').strip()
    return period, slip


def _admin_period(month_value, payroll_type, week_number=""):
    if payroll_type not in WEEKLY_PAYROLL_TYPES:
        return month_range(month_value), [], ""
    return _official_payroll_period(PaySlipService(), payroll_type, month_value, week_number)


def _file_data_url(field):
    if not field:
        return ""
    try:
        with field.open("rb") as source:
            encoded = base64.b64encode(source.read()).decode("ascii")
        mime = mimetypes.guess_type(field.name)[0] or "image/png"
        return "data:{};base64,{}".format(mime, encoded)
    except (FileNotFoundError, OSError):
        return ""


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login_api(request):
    if request.method == "OPTIONS":
        return _json({})
    data = _body(request)
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "")

    admin = authenticate(request, username=username, password=password)
    if admin and (admin.is_superuser or admin.is_staff or getattr(admin, "admin", False)):
        return _json({"token": _token(admin, "admin"), "role": "admin", "mustChangePassword": False,
                      "name": _full_name(admin)})

    if not username.isdigit() or len(username) != 8:
        return _json({"error": "DNI o contraseña incorrectos."}, 401)
    if WorkerAccessRestriction.objects.filter(worker_document=username, disabled=True).exists():
        return _json({"error": "Tu acceso al portal fue deshabilitado. Comunícate con Recursos Humanos."}, 403)
    try:
        identity = WorkerIdentityService().get_active_worker(username)
    except DatabaseError:
        return _json({"error": "No se pudo consultar la información laboral."}, 503)
    if not identity:
        return _json({"error": "DNI o contraseña incorrectos."}, 401)

    user = User.objects.filter(username=username).first()
    if user is None:
        if password != username:
            return _json({"error": "DNI o contraseña incorrectos."}, 401)
        with transaction.atomic():
            email = identity.get("email") or "{}@boletas.local".format(username)
            if User.objects.filter(email=email).exists():
                email = "{}.{}@boletas.local".format(username, identity.get("idcodigogeneral"))
            user = User.objects.create_user(
                username=username, email=email,
                first_name=(identity.get("given_names") or "TRABAJADOR")[:50],
                last_name="{} {}".format(identity.get("paternal_name") or "", identity.get("maternal_name") or "").strip()[:50],
                password=username,
            )
    authenticated = authenticate(request, username=username, password=password)
    if authenticated is None:
        return _json({"error": "DNI o contraseña incorrectos."}, 401)
    return _json({
        "token": _token(authenticated, "worker"), "role": "worker",
        "mustChangePassword": authenticated.check_password(username),
        "needsIdentity": not _identity_complete(authenticated),
        "name": _full_name(authenticated),
    })


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def change_password_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, role = _auth(request, ("worker",))
    if not user:
        return _json({"error": "Sesión no válida."}, 401)
    password = str(_body(request).get("password") or "")
    if password == user.username:
        return _json({"error": "La nueva contraseña no puede ser igual al DNI."}, 400)
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        return _json({"error": " ".join(exc.messages)}, 400)
    user.set_password(password)
    user.save(update_fields=["password"])
    return _json({"token": _token(user, role), "ok": True, "needsIdentity": not _identity_complete(user)})


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register_identity_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("worker",))
    if not user:
        return _json({"error": "Sesión no válida."}, 401)
    if user.check_password(user.username):
        return _json({"error": "Primero debes cambiar tu contraseña."}, 403)
    data = _body(request)
    if data.get("consent") is not True:
        return _json({"error": "Debes aceptar el consentimiento de identidad."}, 400)
    try:
        signature = _decode_image(data.get("signature"), "La firma")
        photo = _decode_image(data.get("photo"), "La fotografía")
    except ValueError as exc:
        return _json({"error": str(exc)}, 400)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    profile, unused_created = WorkerIdentityProfile.objects.get_or_create(
        user=user, defaults={"worker_document": user.username}
    )
    if profile.signature:
        profile.signature.delete(save=False)
    if profile.photo:
        profile.photo.delete(save=False)
    profile.worker_document = user.username
    profile.signature = signature
    profile.photo = photo
    profile.consent_accepted = True
    profile.consent_at = timezone.now()
    profile.ip_address = ip_address
    profile.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
    profile.save()
    return _json({"ok": True})


@require_http_methods(["GET", "OPTIONS"])
def worker_payslips_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("worker",))
    if not user:
        return _json({"error": "Sesión no válida."}, 401)
    if not _identity_complete(user):
        return _json({"error": "Debes registrar tu firma y fotografía antes de ingresar.", "needsIdentity": True}, 403)
    try:
        month_value = request.GET.get("month") or "2026-08"
        if len(month_value) != 7 or month_value[4:5] != "-":
            return _json({"error": "Selecciona un periodo válido."}, 400)
        available_periods = PaySlipService().worker_payroll_periods(user.username, "202608")
        requested_period = month_value.replace("-", "")
        if available_periods and requested_period not in available_periods:
            requested_period = available_periods[0]
            month_value = "{}-{}".format(requested_period[:4], requested_period[4:])
        period, slips_with_period, weeks, selected_week = _worker_month_slips(
            user.username,
            month_value,
            request.GET.get("week", ""),
        )
        identity = WorkerIdentityService().get_active_worker(user.username)
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible consultar las boletas."}, 503)
    return _json({
        "worker": {"document": user.username, "name": _full_name(user), "email": identity.get("email") if identity else ""},
        "period": period.label,
        "selectedPeriod": month_value,
        "periods": [
            {
                "value": "{}-{}".format(value[:4], value[4:]),
                "label": month_range("{}-{}".format(value[:4], value[4:])).label,
            }
            for value in available_periods
        ],
        "selectedWeek": selected_week,
        "weeks": [
            {
                "number": item["number"],
                "start": item["start"].isoformat(),
                "end": item["end"].isoformat(),
                "label": "Semana {} · {} al {}".format(
                    item["number"], item["start"].strftime("%d/%m/%Y"), item["end"].strftime("%d/%m/%Y")
                ),
            }
            for item in weeks
        ],
        "slips": [
            _slip_json(slip, slip_period, week_number)
            for slip, slip_period, week_number in slips_with_period
        ],
    })


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def confirm_payslip_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("worker",))
    if not user:
        return _json({"error": "Sesión no válida."}, 401)
    if not _identity_complete(user):
        return _json({"error": "Debes registrar tu firma y fotografía antes de continuar."}, 403)
    data = _body(request)
    if data.get("accept") is not True:
        return _json({"error": "Debes confirmar la conformidad de la boleta."}, 400)
    try:
        requested_hash = str(data.get("hash") or "")
        period, slip = _requested_worker_slip(
            user.username,
            data.get("month") or "2026-08",
            requested_hash,
            str(data.get("week") or ""),
        )
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible validar la boleta."}, 503)
    if not slip:
        return _json({"error": "Boleta no encontrada."}, 404)
    slip['_payroll_week'] = request.GET.get('week', '').strip()
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    acknowledgement, unused_created = PayslipAcknowledgement.objects.get_or_create(
        payslip_hash=requested_hash,
        defaults={
            "user": user,
            "worker_document": user.username,
            "period_start": period.start,
            "period_end": period.end,
            "payroll_code": str(slip.get("codigoplanilla") or "")[:20],
            "signer_name": _full_name(user)[:160],
            "ip_address": ip_address,
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
        },
    )
    return _json({"ok": True, "confirmedAt": acknowledgement.confirmed_at.isoformat()})


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def admin_release_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "SesiÃ³n administrativa no vÃ¡lida."}, 401)
    data = _body(request)
    payroll_type = str(data.get("payroll") or "").strip().upper()
    month_value = str(data.get("month") or "")
    if payroll_type not in ("ERG", "ERA", "OBP", "OBR"):
        return _json({"error": "Selecciona un rÃ©gimen vÃ¡lido."}, 400)
    try:
        period, unused_weeks, selected_week = _admin_period(
            month_value, payroll_type, str(data.get("week") or "")
        )
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "El periodo o semana no es vÃ¡lido."}, 400)
    action = str(data.get("action") or "validate").strip().lower()
    if action not in ("validate", "authorize"):
        return _json({"error": "La acción no es válida."}, 400)
    release, created = PayrollRelease.objects.get_or_create(
        payroll_type=payroll_type,
        period_start=period.start,
        period_end=period.end,
    )
    if action == "validate" and not release.validated_at:
        release.validated_at = timezone.now()
        release.validated_by = user
        release.save(update_fields=("validated_at", "validated_by"))
    elif action == "authorize":
        if not release.validated_at:
            return _json({"error": "Primero debes validar las boletas del periodo."}, 409)
        if not release.released_at:
            release.released_at = timezone.now()
            release.released_by = user
            release.save(update_fields=("released_at", "released_by"))
    return _json({"ok": True, "created": created, "status": release.status, "period": period.label, "week": selected_week})


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def admin_reset_password_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "SesiÃ³n administrativa no vÃ¡lida."}, 401)
    document = str(_body(request).get("document") or "").strip()
    if not document.isdigit() or len(document) != 8:
        return _json({"error": "DNI no vÃ¡lido."}, 400)
    worker = User.objects.filter(username=document).first()
    if not worker:
        return _json({"error": "El trabajador todavÃ­a no tiene usuario creado."}, 404)
    worker.set_password(document)
    worker.save(update_fields=["password"])
    return _json({"ok": True})


@require_http_methods(["GET"])
def admin_worker_pdf_api(request):
    token = request.GET.get("token", "")
    if token and not request.headers.get("Authorization"):
        request.META["HTTP_AUTHORIZATION"] = "Bearer {}".format(token)
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "SesiÃ³n administrativa no vÃ¡lida."}, 401)
    document = str(request.GET.get("document") or "").strip()
    month_value = request.GET.get("month") or "2026-08"
    payroll_type = str(request.GET.get("payroll") or "").strip().upper()
    try:
        period, unused_weeks, unused_selected = _admin_period(month_value, payroll_type, request.GET.get("week", ""))
        slip = next(
            (item for item in PaySlipService().list(period)
             if str(item.get("nrodocumento") or "").strip() == document
             and (not payroll_type or item.get("payroll_type") == payroll_type)),
            None,
        )
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible consultar la boleta."}, 503)
    if not slip:
        return _json({"error": "Boleta no encontrada."}, 404)
    requested_hash = request.GET.get("hash", "")
    if requested_hash and payslip_fingerprint(slip, period) != requested_hash:
        return _json({"error": "La boleta no corresponde al periodo seleccionado."}, 404)
    slip['_payroll_week'] = request.GET.get('week', '').strip()
    return _cors(HttpResponse(PaySlipPdfView._build_pdf(slip, period), content_type="application/pdf"))


@require_http_methods(["GET", "OPTIONS"])
def admin_workers_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "Sesión administrativa no válida."}, 401)
    month_value = request.GET.get("month") or "2026-08"
    payroll_filter = str(request.GET.get("payroll") or "").strip().upper()
    try:
        period, weeks, selected_week = _admin_period(
            month_value, payroll_filter, request.GET.get("week", "")
        )
        slips = PaySlipService().list(period)
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible consultar las boletas."}, 503)
    if payroll_filter:
        slips = [slip for slip in slips if slip.get("payroll_type") == payroll_filter]
    documents = {
        value for value in (str(slip.get("nrodocumento") or "").strip() for slip in slips)
        if value.isdigit() and len(value) == 8
    }
    identity_documents = set(
        WorkerIdentityProfile.objects.filter(
            worker_document__in=documents, consent_accepted=True,
            signature__gt="", photo__gt="",
        ).values_list("worker_document", flat=True)
    )
    signature_documents = set(
        WorkerIdentityProfile.objects.filter(worker_document__in=documents, signature__gt="")
        .values_list("worker_document", flat=True)
    )
    photo_documents = set(
        WorkerIdentityProfile.objects.filter(worker_document__in=documents, photo__gt="")
        .values_list("worker_document", flat=True)
    )
    downloaded_documents = set(
        PayslipAcknowledgement.objects.filter(
            worker_document__in=documents,
            period_start=period.start,
            period_end=period.end,
        ).values_list("worker_document", flat=True)
    )
    disabled_documents = set(
        WorkerAccessRestriction.objects.filter(
            worker_document__in=documents, disabled=True
        ).values_list("worker_document", flat=True)
    )
    workers = {}
    for slip in slips:
        document = str(slip.get("nrodocumento") or "").strip()
        if document not in documents:
            continue
        item = workers.setdefault(document, {
            "document": document, "name": str(slip.get("apenom") or "").strip(),
            "position": str(slip.get("cargo_personal") or "").strip(),
            "payroll": slip.get("payroll_type_label") or "", "net": 0.0,
            "payslips": 0, "confirmed": 0,
            "hasIdentity": document in identity_documents,
            "hasSignature": document in signature_documents,
            "hasPhoto": document in photo_documents,
            "downloaded": document in downloaded_documents,
            "disabled": document in disabled_documents,
        })
        item["net"] += _amount(slip.get("net_total"))
        item["payslips"] += 1
        if PayslipAcknowledgement.objects.filter(worker_document=document, period_start=period.start, period_end=period.end).exists():
            item["confirmed"] = item["payslips"]
    return _json({
        "period": period.label,
        "released": _is_released(payroll_filter, period) if payroll_filter else False,
        "total": len(workers),
        "workers": list(workers.values()),
        "selectedWeek": selected_week,
        "weekly": payroll_filter in WEEKLY_PAYROLL_TYPES,
        "weeks": [
            {
                "number": item["number"],
                "label": "Semana {} · {} al {}".format(
                    item["number"], item["start"].strftime("%d/%m/%Y"), item["end"].strftime("%d/%m/%Y")
                ),
            }
            for item in weeks
        ],
        "periods": [
            {
                "value": "{}-{}".format(value[:4], value[4:]),
                "label": month_range("{}-{}".format(value[:4], value[4:])).label,
            }
            for value in PaySlipService().payroll_periods()
        ],
    })


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def admin_worker_access_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "Sesión administrativa no válida."}, 401)
    data = _body(request)
    document = str(data.get("document") or "").strip()
    if not document.isdigit() or len(document) != 8:
        return _json({"error": "DNI no válido."}, 400)
    disabled = data.get("disabled") is True
    restriction, unused_created = WorkerAccessRestriction.objects.update_or_create(
        worker_document=document,
        defaults={
            "disabled": disabled,
            "reason": "Trabajador retirado" if disabled else "Acceso habilitado por RRHH",
            "disabled_at": timezone.now() if disabled else None,
            "updated_by": user,
        },
    )
    return _json({"ok": True, "disabled": restriction.disabled})


@require_http_methods(["GET", "OPTIONS"])
def admin_worker_detail_api(request):
    if request.method == "OPTIONS":
        return _json({})
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "Sesión administrativa no válida."}, 401)
    document = str(request.GET.get("document") or "").strip()
    if not document.isdigit() or len(document) != 8:
        return _json({"error": "DNI no válido."}, 400)
    try:
        payroll_type = str(request.GET.get("payroll") or "").strip().upper()
        period, unused_weeks, unused_selected = _admin_period(
            request.GET.get("month") or "2026-08",
            payroll_type,
            request.GET.get("week", ""),
        )
        slips = worker_slips(document, period)
        if payroll_type:
            slips = [item for item in slips if item.get("payroll_type") == payroll_type]
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible consultar al trabajador."}, 503)
    if not slips:
        return _json({"error": "No se encontraron boletas para el trabajador."}, 404)
    profile = WorkerIdentityProfile.objects.filter(worker_document=document).first()
    first = slips[0]
    return _json({
        "worker": {
            "document": document,
            "name": str(first.get("apenom") or "").strip(),
            "position": str(first.get("cargo_personal") or "").strip(),
            "payroll": first.get("payroll_type_label") or "",
            "photo": _file_data_url(profile.photo) if profile else "",
            "signature": _file_data_url(profile.signature) if profile else "",
            "identityVerifiedAt": profile.verified_at.isoformat() if profile else None,
        },
        "period": period.label,
        "slips": [_slip_json(slip, period) for slip in slips],
    })


@require_http_methods(["GET"])
def admin_worker_badge_api(request):
    user, unused_role = _auth(request, ("admin",))
    if not user:
        return _json({"error": "Sesión administrativa no válida."}, 401)
    document = str(request.GET.get("document") or "").strip()
    if not document.isdigit() or len(document) != 8:
        return _json({"error": "DNI no válido."}, 400)
    profile = WorkerIdentityProfile.objects.filter(worker_document=document).first()
    if not profile or not profile.photo or not profile.signature:
        return _json({"error": "El trabajador debe tener fotografía y firma registradas."}, 409)
    try:
        identity = WorkerIdentityService().get_active_worker(document)
        period = month_range(request.GET.get("month") or "2026-08")
        slips = worker_slips(document, period)
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible generar el fotocheck."}, 503)
    if not identity or not slips:
        return _json({"error": "No se encontró información activa del trabajador."}, 404)
    if not PayslipAcknowledgement.objects.filter(
        worker_document=document,
        payslip_hash__in=[payslip_fingerprint(slip, period) for slip in slips],
    ).exists():
        return _json({"error": "El trabajador debe confirmar una boleta del periodo antes de generar su fotocheck."}, 409)

    from .badge import build_worker_badge
    try:
        with profile.photo.open('rb') as photo:
            content = build_worker_badge(document, slips[0].get('apenom'), slips[0].get('cargo_personal'), photo)
    except (OSError, ValueError):
        return _json({'error': 'No se pudo generar el fotocheck. Revisa la fotografía y los datos del trabajador.'}, 409)
    response = HttpResponse(content, content_type='application/pdf')
    response["Content-Disposition"] = 'attachment; filename="fotocheck_{}.pdf"'.format(document)
    return _cors(response)


@require_http_methods(["GET"])
def worker_pdf_api(request):
    token = request.GET.get("token", "")
    if token and not request.headers.get("Authorization"):
        request.META["HTTP_AUTHORIZATION"] = "Bearer {}".format(token)
    user, unused_role = _auth(request, ("worker",))
    if not user:
        return _json({"error": "Sesión no válida."}, 401)
    if not _identity_complete(user):
        return _json({"error": "Debes registrar tu firma y fotografía antes de ingresar."}, 403)
    requested_hash = request.GET.get("hash", "")
    try:
        period, slip = _requested_worker_slip(
            user.username,
            request.GET.get("month") or "2026-08",
            requested_hash,
            request.GET.get("week", ""),
        )
    except (DatabaseError, TypeError, ValueError):
        return _json({"error": "No fue posible consultar la boleta."}, 503)
    if not slip:
        return _json({"error": "Boleta no encontrada."}, 404)
    acknowledgement = PayslipAcknowledgement.objects.filter(
        user=user, payslip_hash=requested_hash
    ).first()
    if not acknowledgement:
        return _json({"error": "Debes dar conformidad antes de descargar el PDF."}, 403)
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")
    PayslipView.objects.update_or_create(
        payslip_hash=requested_hash,
        defaults={
            "user": user,
            "worker_document": user.username,
            "period_start": period.start,
            "period_end": period.end,
            "ip_address": ip_address,
            "user_agent": request.META.get("HTTP_USER_AGENT", "")[:300],
        },
    )
    profile = WorkerIdentityProfile.objects.get(user=user)
    response = HttpResponse(
        PaySlipPdfView._build_pdf(
            slip, period,
            signature_path=profile.signature.path,
            signer_name=acknowledgement.signer_name,
            signed_at=acknowledgement.confirmed_at,
        ),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = 'inline; filename="boleta.pdf"'
    return _cors(response)
