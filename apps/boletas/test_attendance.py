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

    def post_mark(self, document='01234567', source='QR'):
        return self.client.post(
            self.url,
            data=json.dumps({'document': document, 'source': source}),
            content_type='application/json',
        )

    def test_only_admin_can_open_attendance_kiosk(self):
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertContains(self.client.get(self.url), 'Abrir pantalla de marcación')

    def test_independent_reader_screen_requires_admin_and_renders(self):
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(self.screen_url).status_code, 403)
        self.client.force_login(self.admin)
        response = self.client.get(self.screen_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ACERQUE SU FOTOCHECK AL LECTOR')

    def test_qr_toggles_entry_and_exit_and_blocks_duplicate_scan(self):
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
        second = self.post_mark(source='MANUAL')
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()['action'], 'OUT')
        self.assertEqual(AttendanceMark.objects.count(), 2)
        self.assertEqual(AttendanceMark.objects.first().source, 'MANUAL')

    def test_worker_without_enabled_badge_cannot_mark(self):
        PayslipAcknowledgement.objects.all().delete()
        self.client.force_login(self.admin)
        response = self.post_mark()
        self.assertEqual(response.status_code, 409)
        self.assertFalse(AttendanceMark.objects.exists())

    def test_invalid_qr_is_rejected(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.post_mark('123').status_code, 400)
