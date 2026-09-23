from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from unittest.mock import patch

from apps.user.models import User

from .models import PayrollRelease


class PayrollReleaseWorkflowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin-release",
            email="admin-release@example.test",
            first_name="Admin",
            last_name="Boletas",
            password="test-password",
        )
        self.admin.admin = True
        self.admin.save(update_fields=("admin",))
        self.client.force_login(self.admin)
        self.url = reverse("boletas:release_workflow") + "?mode=month&month=2026-08&payroll_type=ERG"
        self.data = {
            "payroll_type": "ERG",
            "mode": "month",
            "month": "2026-08",
            "week": "",
            "start": "2026-08-01",
            "end": "2026-08-31",
        }

    def test_period_must_be_validated_before_authorization(self):
        response = self.client.post(self.url, {**self.data, "action": "authorize"})
        self.assertEqual(response.status_code, 302)
        release = PayrollRelease.objects.get(payroll_type="ERG")
        self.assertIsNone(release.validated_at)
        self.assertIsNone(release.released_at)

    def test_validation_then_authorization_releases_period(self):
        self.client.post(self.url, {**self.data, "action": "validate"})
        release = PayrollRelease.objects.get(payroll_type="ERG")
        self.assertEqual(release.status, "validated")
        self.assertEqual(release.validated_by, self.admin)

        self.client.post(self.url, {**self.data, "action": "authorize"})
        release.refresh_from_db()
        self.assertEqual(release.status, "authorized")
        self.assertEqual(release.released_by, self.admin)

    def test_non_admin_cannot_change_release(self):
        worker = User.objects.create_user(
            username="12345678",
            email="worker-release@example.test",
            first_name="Worker",
            last_name="Test",
            password="test-password",
        )
        self.client.force_login(worker)
        response = self.client.post(self.url, {**self.data, "action": "validate"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(PayrollRelease.objects.exists())

    def test_user_with_release_permission_can_validate_and_authorize(self):
        operator = User.objects.create_user(
            username="LNEYRA",
            email="lneyra@example.test",
            first_name="Luis",
            last_name="Neyra",
            password="test-password",
        )
        operator.user_permissions.add(
            Permission.objects.get(content_type__app_label="boletas", codename="visualizar_boletas"),
            Permission.objects.get(content_type__app_label="boletas", codename="gestionar_publicacion_boletas"),
        )
        self.client.force_login(operator)
        response = self.client.post(self.url, {**self.data, "action": "validate"})
        self.assertEqual(response.status_code, 302)
        release = PayrollRelease.objects.get(payroll_type="ERG")
        self.assertEqual(release.validated_by, operator)
        response = self.client.post(self.url, {**self.data, "action": "authorize"})
        self.assertEqual(response.status_code, 302)
        release.refresh_from_db()
        self.assertEqual(release.released_by, operator)

    @patch("apps.boletas.views.PaySlipService.list", return_value=[])
    def test_release_controls_are_visible_with_specific_permission(self, unused_slips):
        operator = User.objects.create_user(
            username="release-operator",
            email="operator@example.test",
            first_name="Operador",
            last_name="Boletas",
            password="test-password",
        )
        operator.user_permissions.add(
            Permission.objects.get(content_type__app_label="boletas", codename="visualizar_boletas"),
            Permission.objects.get(content_type__app_label="boletas", codename="gestionar_publicacion_boletas"),
        )
        self.client.force_login(operator)
        response = self.client.get(reverse("boletas:index"), {"mode": "month", "month": "2026-08", "payroll_type": "ERG"})
        self.assertTrue(operator.has_perm("boletas.gestionar_publicacion_boletas"))
        self.assertTrue(response.context["can_manage_release"])
        self.assertContains(response, "Validar boletas")
