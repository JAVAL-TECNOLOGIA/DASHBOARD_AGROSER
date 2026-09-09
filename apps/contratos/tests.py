from datetime import date

from django.test import SimpleTestCase

from .forms import ContractGenerationForm


class ContractGenerationFormTests(SimpleTestCase):
    choices = (("01", "CONTRATO DE PRUEBA"),)

    def test_rejects_end_before_start(self):
        form = ContractGenerationForm(
            data={
                "worker_id": "12345678",
                "contract_type": "01",
                "start_date": "2026-07-27",
                "end_date": "2026-07-26",
                "basic": "1200.00",
                "trial_days": "0",
            },
            contract_types=self.choices,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_accepts_complete_contract_information(self):
        form = ContractGenerationForm(
            data={
                "worker_id": "12345678",
                "contract_type": "01",
                "start_date": "2026-07-27",
                "end_date": "2026-09-30",
                "basic": "1200.00",
                "trial_days": "0",
            },
            contract_types=self.choices,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["start_date"], date(2026, 7, 27))
