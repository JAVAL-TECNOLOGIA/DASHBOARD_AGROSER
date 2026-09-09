import base64
import tempfile
from io import BytesIO
from unittest.mock import patch

from PIL import Image, ImageDraw
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.user.models import User
from .models import WorkerIdentityProfile


def image_bytes(signature=False, blank=False):
    image = Image.new('RGB', (400, 180), 'white')
    if not blank:
        ImageDraw.Draw(image).line([(20, 140), (120, 30), (180, 120), (360, 40)], fill='black', width=5)
    output = BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


class WorkerIdentityFlowTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.addCleanup(self.media.cleanup)
        self.settings_override = override_settings(MEDIA_ROOT=self.media.name)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.worker = User.objects.create_user('12345678', 'worker@example.test', 'Prueba', 'Local', 'ChangedPassword!42')
        self.client.force_login(self.worker)
        self.worker_lookup = patch('apps.boletas.worker_portal.WorkerIdentityService.get_active_worker', return_value={'idcodigogeneral': 'test'})
        self.worker_lookup.start()
        self.addCleanup(self.worker_lookup.stop)
        self.url = reverse('boletas:worker_identity')

    def payload(self, blank=False):
        return {'signature': 'data:image/png;base64,' + base64.b64encode(image_bytes(blank=blank)).decode(),
                'photo': SimpleUploadedFile('camera.png', image_bytes(), content_type='image/png'), 'consent': 'on'}

    def test_incomplete_identity_blocks_portal_and_direct_document_routes(self):
        for name in ('worker_dashboard', 'worker_pdf', 'worker_confirm'):
            response = self.client.get(reverse('boletas:' + name))
            self.assertRedirects(response, self.url, fetch_redirect_response=False)

    def test_initial_password_must_still_be_changed(self):
        self.worker.set_password(self.worker.username)
        self.worker.save()
        self.client.force_login(self.worker)
        self.assertRedirects(self.client.get(self.url), reverse('boletas:worker_change_password'), fetch_redirect_response=False)

    def test_camera_capture_and_signature_page(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'capture="user"')
        self.assertContains(response, 'signature-pad')

    def test_blank_signature_rejected(self):
        response = self.client.post(self.url, self.payload(blank=True))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(WorkerIdentityProfile.objects.exists())

    def test_missing_photo_or_consent_rejected(self):
        for missing in ('photo', 'consent'):
            data = self.payload()
            del data[missing]
            self.assertEqual(self.client.post(self.url, data).status_code, 200)
            self.assertFalse(WorkerIdentityProfile.objects.exists())

    def test_invalid_image_rejected(self):
        data = self.payload()
        data['photo'] = SimpleUploadedFile('fake.png', b'not an image', content_type='image/png')
        self.assertEqual(self.client.post(self.url, data).status_code, 200)
        self.assertFalse(WorkerIdentityProfile.objects.exists())

    def test_success_saves_both_files_and_skips_next_time(self):
        self.assertRedirects(self.client.post(self.url, self.payload()), reverse('boletas:worker_dashboard'), fetch_redirect_response=False)
        profile = WorkerIdentityProfile.objects.get(user=self.worker)
        self.assertTrue(profile.signature.storage.exists(profile.signature.name))
        self.assertTrue(profile.photo.storage.exists(profile.photo.name))
        self.assertTrue(profile.consent_accepted)
        self.assertRedirects(self.client.get(self.url), reverse('boletas:worker_dashboard'), fetch_redirect_response=False)
        old_signature = profile.signature.name
        self.client.post(self.url, self.payload())
        profile.refresh_from_db()
        self.assertEqual(profile.signature.name, old_signature)

    def test_storage_failure_does_not_unlock_portal(self):
        with patch('django.db.models.fields.files.FieldFile.save', side_effect=OSError('storage unavailable')):
            self.assertEqual(self.client.post(self.url, self.payload()).status_code, 200)
        self.assertFalse(WorkerIdentityProfile.objects.exists())

    def test_anonymous_must_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('boletas:worker_login'), response.url)
