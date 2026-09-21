import json
from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from apps.user.models import User

from .documents import valid_worker_document
from .badge import build_worker_badge
from .worker_forms import WorkerLoginForm


class WorkerDocumentValidationTests(SimpleTestCase):
    def test_preserves_foreign_worker_code_and_leading_zeroes(self):
        form = WorkerLoginForm(data={'document': '002598724', 'password': '002598724'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['document'], '002598724')
        self.assertTrue(valid_worker_document('12345678'))
        for value in ('1234567', '1234567890', '00259872X', '１２３４５６７８９'):
            self.assertFalse(valid_worker_document(value))

    def test_badge_qr_accepts_nine_digits(self):
        photo = BytesIO()
        Image.new('RGB', (100, 100), 'white').save(photo, format='PNG')
        photo.seek(0)
        result = build_worker_badge('002598724', 'Prueba Extranjero', 'Operario', photo)
        self.assertTrue(result.startswith(b'%PDF'))


class ForeignWorkerLoginTests(TestCase):
    identity = {
        'idcodigogeneral': 'worker-test', 'email': '',
        'given_names': 'Prueba', 'paternal_name': 'Extranjero', 'maternal_name': '',
    }

    @patch('apps.boletas.worker_portal.WorkerIdentityService.get_active_worker')
    def test_worker_portal_first_login_uses_all_nine_digits(self, lookup):
        lookup.return_value = self.identity
        response = self.client.post(reverse('boletas:worker_login'), {
            'document': '002598724', 'password': '002598724',
        })
        self.assertRedirects(response, reverse('boletas:worker_change_password'), fetch_redirect_response=False)
        self.assertTrue(User.objects.get(username='002598724').check_password('002598724'))
        lookup.assert_called_once_with('002598724')

    @patch('apps.boletas.api.WorkerIdentityService.get_active_worker')
    def test_api_first_login_uses_all_nine_digits(self, lookup):
        lookup.return_value = self.identity
        response = self.client.post(
            reverse('boletas:api_login'),
            data=json.dumps({'username': '002598724', 'password': '002598724'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['role'], 'worker')
        self.assertTrue(User.objects.filter(username='002598724').exists())
        lookup.assert_called_once_with('002598724')
