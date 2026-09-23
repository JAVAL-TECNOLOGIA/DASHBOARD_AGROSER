import csv
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase, override_settings
from django.http import Http404
from .erg_txt import read_payroll, locate_payroll, PayrollTextError
from .views import PaySlipPdfView
from .periods import DateRange, month_range


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
            writer.writerows([
                list(self.header), list(self.header.values()),
                list(self.detail), list(self.detail.values()), [],
                ['codigo', 'nombres', 'dia1', 'fecha1', 'normales1', 'extras1251'],
                [self.header['codigo'], 'PRUEBA', 'LUNES', self.header['desde1'], '8.00', '1.50'], [],
                ['codigo', 'dia1', 'rdia1', 'total_rendimiento'],
                [self.header['codigo'], '0.00', '11.82', '11.82'],
            ])

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

    def test_locates_official_ns_suffix(self):
        target = self.path.with_name('01234567_NS.txt')
        self.path.rename(target)
        self.assertEqual(locate_payroll(self.root, '202608', '01234567'), target)

    def test_employee_txt_accepts_nine_digit_foreign_code(self):
        self.path = self.path.with_name('002598724_N.txt')
        self.header['codigo'] = '002598724'
        self.header['documento'] = '002598724'
        self.detail['codigo'] = '002598724'
        self.write()
        data = read_payroll(self.path, '202608', '002598724')
        self.assertEqual(data['header']['documento'], '002598724')

    def test_week_number_selects_the_matching_folder_when_worker_has_multiple_weeks(self):
        second = self.root / '20260842-20260842' / 'normal'
        second.mkdir(parents=True)
        target = second / self.path.name
        target.write_bytes(self.path.read_bytes())
        self.assertEqual(locate_payroll(self.root, '202608', '01234567', week_number='42'), target)

    @patch('apps.boletas.views.PaySlipService.payroll_weeks')
    def test_plant_pdf_infers_missing_week_from_confirmed_period(self, payroll_weeks):
        self.header['descripcion_planilla'] = 'OBREROS PLANTA'
        self.header['periodo'] = '202609'
        self.header['desde1'], self.header['hasta1'] = '20260907', '20260913'
        week_43 = self.root / '20260943-20260943' / 'normal'
        week_43.mkdir(parents=True)
        self.path = week_43 / '01234567_NS.txt'
        self.write()
        week_44 = self.root / '20260944-20260944' / 'normal'
        week_44.mkdir(parents=True)
        (week_44 / self.path.name).write_bytes(self.path.read_bytes())
        payroll_weeks.return_value = [{
            'number': '43', 'start': date(2026, 9, 7),
            'end': date(2026, 9, 13), 'equivalent': '',
        }]
        period = DateRange(date(2026, 9, 7), date(2026, 9, 13), 'Semana 43')

        with override_settings(OBP_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf(
                {'nrodocumento': '01234567', 'payroll_type': 'OBP'}, period
            )

        self.assertTrue(result.startswith(b'%PDF'))
        payroll_weeks.assert_called_once_with('2026-09', 'OBP')

    def test_source_missing_never_falls_back_to_estimates(self):
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            with self.assertRaises(Http404):PaySlipPdfView._build_erg_pdf({'nrodocumento':'99999999'},month_range('2026-08'))

    def test_pdf_integration_and_special_document_block(self):
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            result=PaySlipPdfView._build_erg_pdf({'nrodocumento':'01234567'},month_range('2026-08'))
            self.assertTrue(result.startswith(b'%PDF'))
            self.assertIn(b'/MediaBox [ 0 0 595.2756 841.8898 ]', result)
            with self.assertRaises(Http404):PaySlipPdfView._build_erg_pdf({'nrodocumento':'01234567','document_type':'cts'},month_range('2026-08'))

    def test_monthly_pdf_ignores_week_value_from_worker_form(self):
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf(
                {'nrodocumento': '01234567', 'payroll_type': 'ERG', '_payroll_week': '2026-W31'},
                month_range('2026-08'),
            )
        self.assertTrue(result.startswith(b'%PDF'))

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

    def test_erg_pdf_always_embeds_employer_signature(self):
        with override_settings(ERG_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf(
                {'nrodocumento': '01234567', 'payroll_type': 'ERG'},
                month_range('2026-08'),
            )
        self.assertIn(b'/Subtype /Image', result)

    def test_era_uses_agrarian_source_with_the_same_validation_and_pdf(self):
        self.header['descripcion_planilla'] = 'EMPLEADOS REGIMEN AGRARIO'
        self.write()
        with self.assertRaises(PayrollTextError):
            read_payroll(self.path, '202608', '01234567', payroll_type='ERG')
        with override_settings(ERA_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf(
                {'nrodocumento': '01234567', 'payroll_type': 'ERA'},
                month_range('2026-08'),
            )
        self.assertTrue(result.startswith(b'%PDF'))
        self.assertIn(b'/Subtype /Image', result)

    def test_obp_uses_plant_worker_source_with_the_same_validation_and_pdf(self):
        self.path.unlink()
        self.path = self.path.with_name('012345678.txt')
        self.header['codigo'] = '012345678'
        self.header['documento'] = '012345678'
        self.header['descripcion_planilla'] = 'OBREROS PLANTA'
        self.detail['codigo'] = '012345678'
        self.write()
        with self.assertRaises(PayrollTextError):
            read_payroll(self.path, '202608', '012345678', payroll_type='ERA')
        with override_settings(OBP_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf(
                {'nrodocumento': '012345678', 'payroll_type': 'OBP'},
                month_range('2026-08'),
            )
        self.assertTrue(result.startswith(b'%PDF'))
        self.assertIn(b'/Subtype /Image', result)

    def test_obp_reads_daily_hours_and_performance(self):
        self.header['descripcion_planilla'] = 'OBREROS PLANTA'
        self.write()
        data = read_payroll(self.path, '202608', '01234567', payroll_type='OBP')
        self.assertEqual(data['daily_details'], [{
            'day': 'LUNES',
            'date': '20260801',
            'hours': Decimal('9.50'),
            'performance': Decimal('11.82'),
        }])

    @patch('apps.boletas.plant_pdf.build_pdf', return_value=b'%PDF-plant')
    def test_obr_uses_general_plant_source_and_weekly_format(self, build_pdf):
        self.header['descripcion_planilla'] = 'OBREROS PLANTA GENERAL'
        self.write()
        with override_settings(OBR_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf(
                {'nrodocumento': '01234567', 'payroll_type': 'OBR'},
                month_range('2026-08'),
            )
        self.assertEqual(result, b'%PDF-plant')
        self.assertEqual(build_pdf.call_args.args[0]['header']['payroll_type'], 'OBR')
        self.assertEqual(build_pdf.call_args.args[0]['daily_details'][0]['performance'], Decimal('11.82'))

    def test_obp_pdf_joins_txt_files_when_week_crosses_month(self):
        self.header['descripcion_planilla'] = 'OBREROS PLANTA'
        self.header['desde1'] = self.header['hasta1'] = '20260831'
        self.write()
        september = self.root / '20260943-20260943' / 'normal'
        september.mkdir(parents=True)
        self.path = september / '01234567_NS.txt'
        self.header['periodo'] = '202609'
        self.header['desde1'], self.header['hasta1'] = '20260901', '20260906'
        self.write()
        period = DateRange(date(2026,8,31), date(2026,9,6), 'Semana 42 + 43')
        with override_settings(OBP_TXT_ROOT=str(self.root)):
            result = PaySlipPdfView._build_pdf({'nrodocumento':'01234567','payroll_type':'OBP','_payroll_week':'42+43'}, period)
        self.assertTrue(result.startswith(b'%PDF'))
