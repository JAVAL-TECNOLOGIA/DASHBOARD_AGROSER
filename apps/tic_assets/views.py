from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
try:
    from rest_framework_simplejwt.authentication import JWTAuthentication
    API_AUTHENTICATION = (JWTAuthentication, SessionAuthentication)
except ImportError:
    API_AUTHENTICATION = (SessionAuthentication,)

from .models import Asset, Assignment


CATEGORY_META = {
    Asset.Category.PHONE: {"label": "Celulares", "icon": "bi-phone", "color": "#008b87"},
    Asset.Category.LAPTOP: {"label": "Laptops", "icon": "bi-laptop", "color": "#2878c8"},
    Asset.Category.PC: {"label": "PC", "icon": "bi-display", "color": "#7c55c7"},
    Asset.Category.OTHER: {"label": "Otros", "icon": "bi-boxes", "color": "#b8730b"},
}


def summary_rows():
    counts = {
        row["category"]: row
        for row in Asset.objects.values("category").annotate(
            total=Count("id"),
            available=Count("id", filter=Q(status__in=[Asset.Status.NEW, Asset.Status.AVAILABLE])),
            assigned=Count("id", filter=Q(status=Asset.Status.ASSIGNED)),
            maintenance=Count("id", filter=Q(status=Asset.Status.MAINTENANCE)),
        )
    }
    return [{"category": key, **meta, **counts.get(key, {"total": 0, "available": 0, "assigned": 0, "maintenance": 0})} for key, meta in CATEGORY_META.items()]


class AssetDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "TICS/asignaciones/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.request.GET.get("categoria", "")
        status = self.request.GET.get("estado", "")
        query = self.request.GET.get("q", "").strip()
        assets = Asset.objects.all()
        if category in CATEGORY_META:
            assets = assets.filter(category=category)
        if status:
            assets = assets.filter(status=status)
        if query:
            assets = assets.filter(Q(code__icontains=query) | Q(serial_number__icontains=query) | Q(brand__icontains=query) | Q(model__icontains=query) | Q(current_holder_name__icontains=query))
        context.update({"cards": summary_rows(), "assets": assets[:250], "category": category, "status": status, "query": query, "category_choices": Asset.Category.choices, "status_choices": Asset.Status.choices, "recent_movements": Assignment.objects.select_related("asset")[:12]})
        return context


@method_decorator(csrf_exempt, name="dispatch")
class AssetManageView(LoginRequiredMixin, View):
    def post(self, request):
        asset_id = request.POST.get("id")
        asset = get_object_or_404(Asset, pk=asset_id) if asset_id else Asset(created_by=request.user)
        for field in ("code", "category", "brand", "model", "serial_number", "imei", "phone_number", "condition", "accessories", "notes"):
            if field in request.POST:
                setattr(asset, field, request.POST.get(field, "").strip())
        if request.POST.get("status") in dict(Asset.Status.choices):
            asset.status = request.POST["status"]
        asset.save()
        return redirect("tic_assets:dashboard")


@method_decorator(csrf_exempt, name="dispatch")
class AssetStatusView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, pk):
        asset = get_object_or_404(Asset.objects.select_for_update(), pk=pk)
        target = request.POST.get("status")
        movement_map = {
            Asset.Status.AVAILABLE: Assignment.Type.RETURN,
            Asset.Status.MAINTENANCE: Assignment.Type.MAINTENANCE_IN,
            Asset.Status.RETIRED: Assignment.Type.RETIRE,
        }
        if target not in movement_map:
            return JsonResponse({"detail": "Estado no permitido"}, status=400)
        Assignment.objects.create(
            asset=asset, movement_type=movement_map[target],
            worker_document=asset.current_holder_document,
            worker_name=asset.current_holder_name,
            observations=request.POST.get("observations", "").strip(),
            registered_by=request.user,
        )
        asset.status = target
        if target in (Asset.Status.AVAILABLE, Asset.Status.RETIRED):
            asset.current_holder_document = ""
            asset.current_holder_name = ""
        asset.save()
        return redirect("tic_assets:dashboard")


class AssetSummaryApi(APIView):
    authentication_classes = API_AUTHENTICATION
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(summary_rows())


class AvailableAssetsApi(APIView):
    authentication_classes = API_AUTHENTICATION
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        category = request.GET.get("category", "")
        assets = Asset.objects.filter(status__in=[Asset.Status.NEW, Asset.Status.AVAILABLE])
        if category in CATEGORY_META:
            assets = assets.filter(category=category)
        return Response([{"id": item.id, "code": item.code, "category": item.category, "category_label": item.get_category_display(), "brand": item.brand, "model": item.model, "serial_number": item.serial_number, "description": str(item)} for item in assets[:300]])


class AssignmentApi(APIView):
    authentication_classes = API_AUTHENTICATION
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        asset = get_object_or_404(Asset.objects.select_for_update(), pk=request.data.get("asset_id"))
        if asset.status not in (Asset.Status.NEW, Asset.Status.AVAILABLE):
            return Response({"detail": "El equipo ya no está disponible."}, status=409)
        name = str(request.data.get("worker_name", "")).strip()
        document = str(request.data.get("worker_document", "")).strip()
        if not name or not document or "signature" not in request.FILES:
            return Response({"detail": "Trabajador, documento y firma son obligatorios."}, status=400)
        movement = Assignment.objects.create(
            asset=asset, worker_name=name, worker_document=document,
            worker_email=str(request.data.get("worker_email", "")).strip(),
            worker_phone=str(request.data.get("worker_phone", "")).strip(),
            observations=str(request.data.get("observations", "")).strip(),
            signature=request.FILES["signature"], evidence=request.FILES.get("evidence"),
            registered_by=request.user,
        )
        asset.status = Asset.Status.ASSIGNED
        asset.current_holder_name = name
        asset.current_holder_document = document
        asset.save(update_fields=("status", "current_holder_name", "current_holder_document", "updated_at"))
        if movement.worker_email:
            try:
                send_mail(
                    f"Constancia de asignación TIC {asset.code}",
                    f"Hola {name}, se registró la entrega de {asset.get_category_display()} {asset.brand} {asset.model} (código {asset.code}). Conserva este mensaje como constancia.",
                    None, [movement.worker_email], fail_silently=True,
                )
            except Exception:
                pass
        whatsapp_text = f"Constancia de asignación TIC: {name} recibió {asset.get_category_display()} {asset.brand} {asset.model}, código {asset.code}."
        return Response({"ok": True, "assignment_id": movement.id, "whatsapp_text": whatsapp_text}, status=201)
