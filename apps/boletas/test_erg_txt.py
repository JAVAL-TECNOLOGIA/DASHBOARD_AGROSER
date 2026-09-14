import csv
import tempfile
from pathlib import Path
from django.test import SimpleTestCase, override_settings
from django.http import Http404
from .erg_txt import read_payroll, locate_payroll, PayrollTextError
from .views import PaySlipPdfView
from .periods import month_range


class ErgTxtTests(SimpleTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        folder = self.root / '20260808-20260808' / 'normal'
        folder.mkdir(parents=True)
        self.path = folder / '01234567_N.txt'
        self.header = {'codigo':'01234567','documento':'01234567','apenom':'PRUEBA LOCAL',
            'periodo':'202608','descripcion_planilla':'EMPLEADOS REGIMEN GENERAL',
            'desde1':'20260801','hasta1':'20260831','tot_ingresos':'100.00','tot_descuentos':'10.00','tot_aportes':'9.00'}
        self.detail = {'codigo':'01234567','copia':'1','item':'1','ingr_valor':'100.00','ingr_descri':'BASICO',
            'desc_valor':'10.00','desc_descri':'AFP','apor_valor':'9.00','apor_descri':'ESSALUD','tiem_valor':'240.00','tiem_descri':'HORAS'}
        self.write()

    def write(self):
        with self.path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f,delimiter='|')
            writer.writerows([list(self.header),list(self.header.values()),list(self.detail),list(self.detail.values()),[],['codigo','dia1'],['01234567','0.00']])

    def test_sections_totals_and_leading_zero(self):
        data = read_payroll(self.path,'202608','01234567')
        self.assertEqual(data['totals']['net'],90)
        self.assertEqual(len(data['details']),1)
        self.assertEqual(locate_payroll(self.root,'202608','01234567'),self.path)

    def test_dni_period_and_totals_must_match(self):
        for period,dni in [('202609','01234567'),('202608','99999999')]:
            with self.assertRaises(PayrollTextError):read_payroll(self.path,period,dni)
        self.header['tot_ingresos']='999.00'; self.write()
        with self.assertRaises(PayrollTextError):read_payroll(self.path,'202608')

    def test_duplicate_sources_rejected(self):
        duplicate=self.root/'202608';duplicate.mkdir()
        (duplicate/self.path.name).write_bytes(self.path.read_bytes())
        with self.assertRaises(PayrollTextError):locate_payroll(self.root,'202608','01234567')

    def test_source_missing_never_falls_back_to_estimates(self):
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            with self.assertRaises(Http404):PaySlipPdfView._build_erg_pdf({'nrodocumento':'99999999'},month_range('2026-08'))

    def test_pdf_integration_and_special_document_block(self):
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            result=PaySlipPdfView._build_erg_pdf({'nrodocumento':'01234567'},month_range('2026-08'))
            self.assertTrue(result.startswith(b'%PDF'))
            with self.assertRaises(Http404):PaySlipPdfView._build_erg_pdf({'nrodocumento':'01234567','document_type':'cts'},month_range('2026-08'))

    def test_confirmed_erg_pdf_embeds_worker_signature(self):
        from .test_identity import image_bytes

        signature = self.root / 'signature.png'
        signature.write_bytes(image_bytes())
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_erg_pdf(
                {'nrodocumento': '01234567'},
                month_range('2026-08'),
                signature_path=str(signature),
            )
        self.assertIn(b'/Subtype /Image', result)
