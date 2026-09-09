from django.test import TestCase
from django.urls import reverse

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
