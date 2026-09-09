from django.urls import path
from .views import WorkerBadgeView

from .views import PaySlipConsolidatedView, PaySlipListView, PaySlipPdfView, WorkerPhotoView, WorkerSignatureView, WorkerDetailView, WorkerMonthPdfView, WorkerBadgeSheetView, WorkerPasswordResetView, WorkerIdentityResetView
from .api import admin_attendance_api, admin_release_api, admin_reset_password_api, admin_worker_access_api, admin_worker_badge_api, admin_worker_detail_api, admin_worker_pdf_api, admin_workers_api, change_password_api, confirm_payslip_api, login_api, portal_content_api, register_identity_api, worker_payslips_api, worker_pdf_api
from .worker_portal import (
    WorkerIdentityView,
    WorkerDashboardView,
    WorkerLoginView,
    WorkerPasswordChangeView,
    WorkerPayslipConfirmView,
    WorkerPayslipPdfView,
)


app_name = "boletas"

urlpatterns = [
    path('trabajador/fotocheck/<str:document>/', WorkerBadgeView.as_view(), name='worker_badge'),
    path('trabajadores/fotochecks/', WorkerBadgeSheetView.as_view(), name='worker_badge_sheet'),
    path('trabajador/<str:document>/restablecer-clave/', WorkerPasswordResetView.as_view(), name='worker_reset_password'),
    path('trabajador/<str:document>/eliminar-identidad/', WorkerIdentityResetView.as_view(), name='worker_reset_identity'),
    path('trabajador/firma/<int:pk>/', WorkerSignatureView.as_view(), name='worker_signature'),
    path('trabajador/detalle/<str:document>/', WorkerDetailView.as_view(), name='worker_detail'),
    path('trabajador/boleta/<str:document>/', WorkerMonthPdfView.as_view(), name='worker_month_pdf'),
    path('trabajador/foto/<int:pk>/', WorkerPhotoView.as_view(), name='worker_photo'),
    path("api/login/", login_api, name="api_login"),
    path("api/portal-content/", portal_content_api, name="api_portal_content"),
    path("api/admin/marcaciones/", admin_attendance_api, name="api_admin_attendance"),
    path("api/cambiar-clave/", change_password_api, name="api_change_password"),
    path("api/registrar-identidad/", register_identity_api, name="api_register_identity"),
    path("api/mis-boletas/", worker_payslips_api, name="api_worker_payslips"),
    path("api/mis-boletas/conformidad/", confirm_payslip_api, name="api_confirm_payslip"),
    path("api/mis-boletas/pdf/", worker_pdf_api, name="api_worker_pdf"),
    path("api/admin/trabajadores/", admin_workers_api, name="api_admin_workers"),
    path("api/admin/boletas/validar/", admin_release_api, name="api_admin_release"),
    path("api/admin/trabajador/restablecer-clave/", admin_reset_password_api, name="api_admin_reset_password"),
    path("api/admin/trabajador/", admin_worker_detail_api, name="api_admin_worker_detail"),
    path("api/admin/trabajador/pdf/", admin_worker_pdf_api, name="api_admin_worker_pdf"),
    path("api/admin/trabajador/fotocheck/", admin_worker_badge_api, name="api_admin_worker_badge"),
    path("api/admin/trabajador/acceso/", admin_worker_access_api, name="api_admin_worker_access"),
    path("", PaySlipListView.as_view(), name="index"),
    path("consolidado/", PaySlipConsolidatedView.as_view(), name="consolidated"),
    path("pdf/", PaySlipPdfView.as_view(), name="pdf"),
    path("mis-boletas/ingreso/", WorkerLoginView.as_view(), name="worker_login"),
    path("mis-boletas/registrar-identidad/", WorkerIdentityView.as_view(), name="worker_identity"),
    path(
        "mis-boletas/cambiar-clave/",
        WorkerPasswordChangeView.as_view(),
        name="worker_change_password",
    ),
    path(
        "mis-boletas/",
        WorkerDashboardView.as_view(),
        name="worker_dashboard",
    ),
    path(
        "mis-boletas/pdf/",
        WorkerPayslipPdfView.as_view(),
        name="worker_pdf",
    ),
    path(
        "mis-boletas/confirmar/",
        WorkerPayslipConfirmView.as_view(),
        name="worker_confirm",
    ),
]
