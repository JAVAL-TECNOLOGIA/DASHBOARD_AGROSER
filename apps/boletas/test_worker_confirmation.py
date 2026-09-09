from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.user.models import User
from .models import PayrollRelease, PayslipAcknowledgement, WorkerIdentityProfile
from .periods import custom_range
from .worker_portal import payslip_fingerprint


class WorkerConfirmationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            '01234567', 'worker@example.test', 'Trabajador', 'Prueba',
            'ClaveSegura!42',
        )
        WorkerIdentityProfile.objects.create(
            user=self.user,
            worker_document='01234567',
            signature='boletas/identidad/firmas/prueba.png',
            photo='boletas/identidad/fotos/prueba.jpg',
            consent_accepted=True,
        )
        self.client.force_login(self.user)
        self.period = custom_range('2026-08-01', '2026-08-31')
        PayrollRelease.objects.create(
            payroll_type='ERG',
            period_start=self.period.start,
            period_end=self.period.end,
            validated_at=timezone.now(),
            validated_by=self.user,
            released_at=timezone.now(),
            released_by=self.user,
        )
        self.slip = {
            'nrodocumento': '01234567',
            'idcodigogeneral': '1',
            'apenom': 'TRABAJADOR PRUEBA',
            'payroll_type': 'ERG',
            'codigoplanilla': 'ERG',
            'document_type': 'payment',
            'document_type_label': 'Boleta de pago',
            'income_total': 100,
            'deduction_total': 10,
            'net_total': 90,
            'concepts': [],
        }
        self.fingerprint = payslip_fingerprint(self.slip, self.period)
        self.params = {
            'mode': 'custom', 'start': '2026-08-01', 'end': '2026-08-31',
            'hash': self.fingerprint,
        }
        self.worker = patch(
            'apps.boletas.worker_portal.WorkerIdentityService.get_active_worker',
            return_value={'document': '01234567'},
        )
        self.slips = patch(
            'apps.boletas.worker_portal.worker_slips', return_value=[self.slip]
        )
        self.worker.start()
        self.slips.start()
        self.addCleanup(self.worker.stop)
        self.addCleanup(self.slips.stop)

    def test_confirmation_page_has_one_action_and_no_password(self):
        response = self.client.get(reverse('boletas:worker_confirm'), self.params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirmar para visualizar')
        self.assertNotContains(response, 'Contraseña actual')
        self.assertNotContains(response, 'type="password"')
        self.assertNotContains(response, 'type="checkbox"')

    def test_one_click_records_confirmation_and_opens_pdf(self):
        response = self.client.post(reverse('boletas:worker_confirm'), self.params)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('boletas:worker_pdf') + '?'))
        self.assertIn('hash=' + self.fingerprint, response.url)
        acknowledgement = PayslipAcknowledgement.objects.get(
            user=self.user, payslip_hash=self.fingerprint
        )
        self.assertEqual(acknowledgement.worker_document, '01234567')

    def test_invalid_hash_is_never_confirmed(self):
        params = dict(self.params, hash='invalid')
        response = self.client.post(reverse('boletas:worker_confirm'), params)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(PayslipAcknowledgement.objects.exists())

    def test_worker_cannot_open_unreleased_slip_by_direct_url(self):
        PayrollRelease.objects.all().delete()
        response = self.client.get(reverse('boletas:worker_confirm'), self.params)
        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_cannot_confirm(self):
        self.client.logout()
        response = self.client.post(reverse('boletas:worker_confirm'), self.params)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('boletas:worker_login'), response.url)
