import json
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from PIL import Image

from apps.user.models import User

from .documents import valid_worker_document
from .badge import build_worker_badge
from reportlab.graphics.barcode import createBarcodeDrawing
from .worker_forms import WorkerLoginForm
from .periods import custom_range
from .services import PaySlipService
from .worker_portal import worker_slips


class WorkerDocumentValidationTests(SimpleTestCase):
    @patch.object(PaySlipService, 'list')
    def test_combined_plant_week_sums_both_payroll_segments(self, payroll_list):
        payroll_list.return_value = [{
            'nrodocumento': '75522713',
            'payroll_type': 'OBP',
            'basico': Decimal('41.00'),
            'income_total': Decimal('200.79'),
            'deduction_total': Decimal('37.87'),
            'net_total': Decimal('162.92'),
            'concepts': [
                {'codigo_equiv': 'IN0001', 'importe': Decimal('56.46')},
                {'codigo_equiv': 'IN0001', 'importe': Decimal('82.00')},
                {'codigo_equiv': 'TOT_IN', 'importe': Decimal('124.08')},
                {'codigo_equiv': 'TOT_IN', 'importe': Decimal('200.79')},
                {'codigo_equiv': 'TOT_DE', 'importe': Decimal('16.16')},
                {'codigo_equiv': 'TOT_DE', 'importe': Decimal('37.87')},
                {'codigo_equiv': 'TO0002', 'importe': Decimal('107.92')},
                {'codigo_equiv': 'TO0002', 'importe': Decimal('162.92')},
            ],
        }]
        slip = worker_slips(
            '75522713', custom_range('2026-09-28', '2026-10-04')
        )[0]
        self.assertEqual(slip['basico'], Decimal('138.46'))
        self.assertEqual(slip['income_total'], Decimal('324.87'))
        self.assertEqual(slip['deduction_total'], Decimal('54.03'))
        self.assertEqual(slip['net_total'], Decimal('270.84'))

    def test_preserves_foreign_worker_code_and_leading_zeroes(self):
        form = WorkerLoginForm(data={'document': '002598724', 'password': '002598724'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['document'], '002598724')
        self.assertTrue(valid_worker_document('12345678'))
        for value in ('1234567', '1234567890', '00259872X', '１２３４５６７８９'):
            self.assertFalse(valid_worker_document(value))

    def test_badge_barcode_appends_one_to_nine_digit_document(self):
        photo = BytesIO()
        Image.new('RGB', (100, 100), 'white').save(photo, format='PNG')
        photo.seek(0)
        with patch('apps.boletas.badge.createBarcodeDrawing', wraps=createBarcodeDrawing) as barcode:
            result = build_worker_badge('002598724', 'Prueba Extranjero', 'Operario', photo)
        self.assertEqual(barcode.call_args.args, ('Code128',))
        self.assertEqual(barcode.call_args.kwargs['value'], '0025987241')
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
