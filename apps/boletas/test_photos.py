import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.user.models import User
from .models import PayslipAcknowledgement, WorkerIdentityProfile
from .test_identity import image_bytes


class PayslipPhotoTests(TestCase):
    @patch('apps.boletas.views.PaySlipService.list', return_value=[])
    def test_erg_filter_forces_month_even_with_week_url(self, slips):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('boletas:index'), {'payroll_type':'ERG', 'mode':'week', 'week':'2026-W33', 'month':'2026-08'})
        self.assertEqual(response.context['mode'], 'month')
        self.assertEqual(slips.call_args.args[0].start.isoformat(), '2026-08-01')
        self.assertEqual(slips.call_args.args[0].end.isoformat(), '2026-08-31')

    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        override = override_settings(MEDIA_ROOT=self.media.name)
        override.enable()
        self.addCleanup(override.disable)
        self.admin = User.objects.create_user('photo-admin', 'admin@example.test', 'Admin', 'Prueba', 'test-password')
        self.admin.admin = True
        self.admin.save()
        self.worker = User.objects.create_user('01234567', 'photo@example.test', 'Trabajador', 'Prueba', 'test-password')
        self.profile = WorkerIdentityProfile.objects.create(user=self.worker, worker_document='01234567',
            photo=SimpleUploadedFile('photo.png', image_bytes(), content_type='image/png'))
        self.url = reverse('boletas:worker_photo', args=[self.profile.pk])

    def test_photo_requires_module_permission(self):
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_admin_can_view_photo_and_missing_file_returns_404(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertIn('no-store', response['Cache-Control'])
        response.close()
        self.profile.photo.delete(save=False)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    @patch('apps.boletas.views.PaySlipService.list')
    def test_column_matches_document_and_handles_missing_photo(self, slips):
        slips.return_value = [
            {'nrodocumento': '01234567 ', 'apenom': 'CON FOTO', 'idcodigogeneral': '1'},
            {'nrodocumento': '99999999', 'apenom': 'SIN FOTO', 'idcodigogeneral': '2'},
        ]
        self.client.force_login(self.admin)
        response = self.client.get(reverse('boletas:index'))
        self.assertEqual(response.status_code, 200)
        rows = list(response.context['page'])
        self.assertTrue(rows[0]['has_photo'])
        self.assertFalse(rows[1]['has_photo'])
        self.assertFalse(rows[0]['has_signature'])
        self.assertContains(response, '>Foto</th>')
        self.assertContains(response, 'SUBIDO')
        self.assertContains(response, 'PENDIENTE')
        self.assertContains(response, 'VER DETALLE')
        self.assertNotContains(response, 'Ver conceptos')

    @patch('apps.boletas.views.PaySlipService.list')
    def test_admin_confirmation_column_shows_status_and_date(self, slips):
        slips.return_value = [{
            'nrodocumento': '01234567', 'apenom': 'TRABAJADOR',
            'idcodigogeneral': '1', 'codigoplanilla': 'ERG',
        }]
        self.client.force_login(self.admin)
        url = reverse('boletas:index')
        params = {'mode': 'month', 'month': '2026-08'}

        pending = self.client.get(url, params)
        self.assertContains(pending, '>Confirmación</th>')
        self.assertNotContains(pending, 'CONFIRMADA')

        slip = list(pending.context['page'])[0]
        acknowledgement = PayslipAcknowledgement.objects.create(
            user=self.worker,
            worker_document='01234567',
            period_start=pending.context['period'].start,
            period_end=pending.context['period'].end,
            payroll_code='ERG',
            payslip_hash=slip['fingerprint'],
            signer_name='Trabajador Prueba',
        )
        confirmed = self.client.get(url, params)
        self.assertContains(confirmed, 'CONFIRMADA')
        self.assertContains(
            confirmed,
            timezone.localtime(acknowledgement.confirmed_at).strftime('%d/%m/%Y %H:%M'),
        )

    @patch('apps.boletas.worker_portal.WorkerIdentityService.get_active_worker', return_value={'email': 'worker@example.test'})
    @patch('apps.boletas.worker_portal.worker_slips')
    def test_detail_includes_all_month_documents_and_identity(self, slips, identity):
        slips.return_value = [
            {'nrodocumento': '01234567', 'apenom': 'TRABAJADOR', 'idcodigogeneral': '1', 'net_total': 100, 'document_type_label': 'Boleta de pago'},
            {'nrodocumento': '01234567', 'apenom': 'TRABAJADOR', 'idcodigogeneral': '1', 'net_total': 200, 'document_type_label': 'Boleta CTS'},
        ]
        url = reverse('boletas:worker_detail', args=['01234567'])
        self.assertEqual(self.client.get(url, {'month': '2026-08'}).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.get(url, {'month': '2026-08'})
        self.assertNotContains(response, 'Datos del trabajador')
        self.assertContains(response, 'Generar fotocheck con QR')
        self.assertContains(response, self.url)
        self.assertContains(response, 'Boleta CTS')
        self.assertContains(response, 'Abrir boleta PDF', count=2)
        rows = response.context['slips']
        self.assertNotEqual(rows[0]['attachment_url'], rows[1]['attachment_url'])
        self.assertEqual(slips.call_args.args[1].start.isoformat(), '2026-08-01')
        self.assertEqual(slips.call_args.args[1].end.isoformat(), '2026-08-31')
        self.assertEqual(self.client.get(url, {'month': 'invalid'}).status_code, 400)

    @patch('apps.boletas.views.PaySlipPdfView._build_pdf', return_value=b'%PDF-test')
    @patch('apps.boletas.worker_portal.worker_slips')
    def test_attachment_selects_exact_payslip(self, slips, build_pdf):
        from .periods import month_range
        from .worker_portal import payslip_fingerprint
        first = {'nrodocumento': '01234567', 'net_total': 100}
        second = {'nrodocumento': '01234567', 'net_total': 200}
        slips.return_value = [first, second]
        period = month_range('2026-08')
        self.profile.signature = SimpleUploadedFile('signature.png', image_bytes(), content_type='image/png')
        self.profile.save(update_fields=['signature'])
        acknowledgement = PayslipAcknowledgement.objects.create(
            user=self.worker,
            worker_document='01234567',
            period_start=period.start,
            period_end=period.end,
            payslip_hash=payslip_fingerprint(second, period),
            signer_name='Trabajador Prueba',
        )
        self.client.force_login(self.admin)
        url = reverse('boletas:worker_month_pdf', args=['01234567'])
        response = self.client.get(url, {'month': '2026-08', 'slip': payslip_fingerprint(second, period)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(build_pdf.call_args.args[0], second)
        self.assertEqual(build_pdf.call_args.kwargs['signature_path'], self.profile.signature.path)
        self.assertEqual(build_pdf.call_args.kwargs['signed_at'], acknowledgement.confirmed_at)
        self.assertEqual(self.client.get(url, {'month': '2026-08', 'slip': 'invalid'}).status_code, 404)

    @patch('apps.boletas.worker_portal.worker_slips', return_value=[{'apenom': 'TRABAJADOR PRUEBA', 'cargo_personal': 'Operario'}])
    def test_badge_requires_permission_and_photo(self, slips):
        url = reverse('boletas:worker_badge', args=['01234567'])
        self.assertEqual(self.client.get(url, {'month': '2026-08'}).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.get(url, {'month': '2026-08'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF'))
        self.profile.photo.delete()
        self.assertEqual(self.client.get(url, {'month': '2026-08'}).status_code, 409)

    def test_badge_qr_keeps_leading_zero(self):
        from .badge import build_worker_badge
        from io import BytesIO
        from reportlab.graphics.barcode import createBarcodeDrawing
        with patch('apps.boletas.badge.createBarcodeDrawing', wraps=createBarcodeDrawing) as qr:
            build_worker_badge('01234567', 'Prueba', 'Operario', BytesIO(image_bytes()))
        self.assertEqual(qr.call_args.kwargs['value'], '01234567')

    def test_employer_signature_is_default_for_other_payslip_formats(self):
        from .periods import month_range
        from .views import PaySlipPdfView

        period = month_range('2026-08')
        slip = {
            'nrodocumento': '01234567', 'apenom': 'TRABAJADOR PRUEBA',
            'basico': 100, 'income_total': 100, 'deduction_total': 10,
            'net_total': 90, 'concepts': [],
        }
        content = PaySlipPdfView._build_pdf(
            dict(slip, payroll_type='OTRO'), period,
        )
        self.assertTrue(content.startswith(b'%PDF'))
        self.assertIn(b'/Subtype /Image', content)

    def test_badge_sheet_places_six_workers_per_a4_page(self):
        from io import BytesIO
        import re
        from .badge import build_worker_badge_sheet

        workers = [
            {
                'document': f'{index:08d}',
                'name': f'TRABAJADOR {index}',
                'position': 'OPERARIO',
                'photo': BytesIO(image_bytes()),
            }
            for index in range(1, 8)
        ]
        content = build_worker_badge_sheet(workers)
        self.assertEqual(len(re.findall(rb'/Type\s*/Page\b', content)), 2)
        self.assertIn(b'/MediaBox [ 0 0 595.2756 841.8898 ]', content)

    @patch('apps.boletas.views.PaySlipService.list')
    def test_badge_sheet_includes_only_complete_registered_workers(self, slips):
        slips.return_value = [{
            'nrodocumento': '01234567',
            'apenom': 'TRABAJADOR PRUEBA',
            'cargo_personal': 'OPERARIO',
            'payroll_type': 'ERG',
        }]
        self.client.force_login(self.admin)
        url = reverse('boletas:worker_badge_sheet')
        params = {'mode': 'month', 'month': '2026-08', 'payroll_type': 'ERG'}
        self.assertEqual(self.client.get(url, params).status_code, 404)

        self.profile.signature = SimpleUploadedFile('signature.png', image_bytes(), content_type='image/png')
        self.profile.save(update_fields=['signature'])
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_admin_can_reset_worker_password_to_document(self):
        self.worker.set_password('ChangedPassword!42')
        self.worker.save(update_fields=['password'])
        self.client.force_login(self.admin)
        response = self.client.post(reverse('boletas:worker_reset_password', args=['01234567']))
        self.assertRedirects(response, reverse('boletas:index'), fetch_redirect_response=False)
        self.worker.refresh_from_db()
        self.assertTrue(self.worker.check_password('01234567'))

    def test_admin_can_delete_identity_and_files(self):
        from .periods import month_range

        period = month_range('2026-08')
        PayslipAcknowledgement.objects.create(
            user=self.worker,
            worker_document='01234567',
            period_start=period.start,
            period_end=period.end,
            payroll_code='ERG',
            payslip_hash='a' * 64,
            signer_name='Trabajador Prueba',
        )
        self.profile.signature = SimpleUploadedFile('signature.png', image_bytes(), content_type='image/png')
        self.profile.save(update_fields=['signature'])
        photo_storage, photo_name = self.profile.photo.storage, self.profile.photo.name
        signature_storage, signature_name = self.profile.signature.storage, self.profile.signature.name
        self.client.force_login(self.admin)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse('boletas:worker_reset_identity', args=['01234567']))
        self.assertRedirects(response, reverse('boletas:index'), fetch_redirect_response=False)
        self.assertFalse(WorkerIdentityProfile.objects.filter(worker_document='01234567').exists())
        self.assertFalse(PayslipAcknowledgement.objects.filter(worker_document='01234567').exists())
        self.assertFalse(photo_storage.exists(photo_name))
        self.assertFalse(signature_storage.exists(signature_name))
