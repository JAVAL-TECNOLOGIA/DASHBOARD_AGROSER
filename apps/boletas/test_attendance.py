import json
import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.user.models import User
from .models import AttendanceMark, PayslipAcknowledgement, WorkerIdentityProfile
from .test_identity import image_bytes


class AttendanceKioskTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        override = override_settings(MEDIA_ROOT=self.media.name)
        override.enable()
        self.addCleanup(override.disable)
        self.admin = User.objects.create_user(
            'attendance-admin', 'attendance-admin@example.test',
            'Operador', 'Marcaciones', 'test-password',
        )
        self.admin.admin = True
        self.admin.save(update_fields=['admin'])
        self.worker = User.objects.create_user(
            '01234567', 'attendance-worker@example.test',
            'Ana', 'Trabajadora', 'test-password',
        )
        self.profile = WorkerIdentityProfile.objects.create(
            user=self.worker,
            worker_document='01234567',
            photo=SimpleUploadedFile('photo.png', image_bytes(), content_type='image/png'),
            signature=SimpleUploadedFile('signature.png', image_bytes(), content_type='image/png'),
        )
        PayslipAcknowledgement.objects.create(
            user=self.worker,
            worker_document='01234567',
            period_start=timezone.localdate().replace(day=1),
            period_end=timezone.localdate(),
            payslip_hash='c' * 64,
            signer_name='Ana Trabajadora',
        )
        self.url = reverse('boletas:attendance')
        self.screen_url = reverse('boletas:attendance_screen')

    def post_mark(self, document='01234567', source='BARCODE', **extra):
        payload = {'document': document, 'source': source}
        if source in ('BARCODE', 'BARCODE_OFFLINE') and 'barcode' not in extra:
            payload['barcode'] = document + '1'
        payload.update(extra)
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_only_admin_can_open_attendance_kiosk(self):
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Abrir estación por red local')
        self.assertContains(response, 'http://192.168.100.3:7000/boletas/marcaciones/pantalla/')
        self.assertContains(response, 'App.init();')

    def test_independent_reader_screen_requires_admin_and_renders(self):
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(self.screen_url).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.get(self.screen_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ACERQUE SU FOTOCHECK AL LECTOR')

    def test_barcode_toggles_entry_and_exit_and_blocks_duplicate_scan(self):
        self.client.force_login(self.admin)
        first = self.post_mark()
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()['action'], 'IN')
        self.assertEqual(first.json()['photoUrl'], reverse('boletas:worker_photo', kwargs={'pk': self.profile.pk}))
        duplicate = self.post_mark()
        self.assertEqual(duplicate.status_code, 409)
        self.assertTrue(duplicate.json()['duplicate'])
        AttendanceMark.objects.filter(worker_document='01234567').update(
            marked_at=timezone.now() - timedelta(seconds=31),
        )
        second = self.post_mark()
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()['action'], 'OUT')
        self.assertEqual(AttendanceMark.objects.count(), 2)
        self.assertEqual(AttendanceMark.objects.first().source, 'BARCODE')

    def test_worker_without_enabled_badge_cannot_mark(self):
        PayslipAcknowledgement.objects.all().delete()
        self.client.force_login(self.admin)
        response = self.post_mark()
        self.assertEqual(response.status_code, 409)
        self.assertFalse(AttendanceMark.objects.exists())

    def test_invalid_barcode_and_old_qr_source_are_rejected(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.post_mark('123').status_code, 400)
        self.assertEqual(self.post_mark(source='QR').status_code, 400)
        self.assertEqual(self.post_mark(source='QR_OFFLINE').status_code, 503)

    def test_barcode_suffix_is_removed_before_recording(self):
        self.client.force_login(self.admin)
        response = self.post_mark(source='BARCODE', barcode='012345671')
        self.assertEqual(response.status_code, 200)
        mark = AttendanceMark.objects.get()
        self.assertEqual(mark.worker_document, '01234567')
        self.assertEqual(mark.source, 'BARCODE')
        self.assertEqual(self.post_mark(source='BARCODE', barcode='012345672').status_code, 400)
        self.assertEqual(self.post_mark(source='BARCODE', barcode='0025987241').status_code, 400)

    def test_nine_digit_worker_barcode_preserves_leading_zeroes(self):
        foreign_worker = User.objects.create_user(
            '002598724', 'foreign-worker@example.test', 'Ana', 'Extranjera', 'test-password',
        )
        WorkerIdentityProfile.objects.create(
            user=foreign_worker, worker_document='002598724',
            photo=SimpleUploadedFile('foreign-photo.png', image_bytes(), content_type='image/png'),
            signature=SimpleUploadedFile('foreign-signature.png', image_bytes(), content_type='image/png'),
        )
        PayslipAcknowledgement.objects.create(
            user=foreign_worker, worker_document='002598724',
            period_start=timezone.localdate().replace(day=1), period_end=timezone.localdate(),
            payslip_hash='d' * 64, signer_name='Ana Extranjera',
        )
        self.client.force_login(self.admin)
        response = self.post_mark(document='002598724', source='BARCODE', barcode='0025987241')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AttendanceMark.objects.get().worker_document, '002598724')

    def test_barcode_offline_records_synchronized_source(self):
        self.client.force_login(self.admin)
        response = self.post_mark(source='BARCODE_OFFLINE', barcode='012345671')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['synchronized'])

    def test_offline_mark_keeps_capture_time_and_is_idempotent(self):
        self.client.force_login(self.admin)
        captured = timezone.now() - timedelta(hours=1)
        event_id = 'offline-event-12345678'
        first = self.post_mark(
            source='LEGACY_OFFLINE', clientEventId=event_id,
            capturedAt=captured.isoformat(),
        )
        self.assertEqual(first.status_code, 200)
        self.assertTrue(first.json()['synchronized'])
        mark = AttendanceMark.objects.get(client_event_id=event_id)
        self.assertAlmostEqual(mark.marked_at.timestamp(), captured.timestamp(), delta=1)
        repeated = self.post_mark(
            source='LEGACY_OFFLINE', clientEventId=event_id,
            capturedAt=captured.isoformat(),
        )
        self.assertEqual(repeated.status_code, 200)
        self.assertEqual(AttendanceMark.objects.filter(client_event_id=event_id).count(), 1)

    def test_service_worker_is_available_to_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('boletas:attendance_service_worker'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/javascript')
        self.assertContains(response, 'agroservice-attendance-v3')
