from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.user.models import User

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


class ContractExpirationDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "contract-admin", "contracts@example.test", "Admin", "Contratos", "test-password"
        )
        self.admin.admin = True
        self.admin.save(update_fields=["admin"])
        self.client.force_login(self.admin)

    @patch("apps.contratos.views.ContractService.list_expiring_contracts")
    @patch("apps.contratos.views.ContractService.list_personnel", return_value=[])
    def test_selected_month_card_and_expiration_list(self, unused_personnel, expiring):
        expiring.return_value = [{
            "idcodigogeneral": "W001",
            "document": "12345678",
            "full_name": "TRABAJADOR PRUEBA",
            "payroll": "REGIMEN GENERAL", "payroll_id": "ERG",
            "position": "OPERARIO",
            "contract_id": "002",
            "contract_type": "SUJETO A MODALIDAD",
            "final_contrato": date(2026, 10, 31),
        }]

        response = self.client.get(reverse("contratos:index"), {
            "expiry_month": "2026-10", "show_expiring": "1",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["expiring_count"], 1)
        self.assertEqual(expiring.call_args.args, (date(2026, 10, 1), date(2026, 10, 31)))
        self.assertContains(response, "Vencen en el mes")
        self.assertContains(response, "TRABAJADOR PRUEBA")
        self.assertContains(response, "Renovar")

    @patch("apps.contratos.views.ContractService.get_contract")
    @patch("apps.contratos.views.ContractService.contract_types")
    @patch("apps.contratos.views.ContractService.get_person")
    def test_renewal_prefills_day_after_current_contract(self, person, types, contract):
        person.return_value = {
            "idcodigogeneral": "W001", "document": "12345678",
            "full_name": "TRABAJADOR PRUEBA", "fecha_ingreso": date(2025, 1, 1),
            "payroll": "REGIMEN GENERAL", "payroll_id": "ERG", "position": "OPERARIO",
        }
        types.return_value = [{"idtipocontrato": "01", "descripcion": "PLAZO FIJO"}]
        contract.return_value = {
            "idcontrato": "002", "idtipocontrato": "01",
            "final_contrato": date(2026, 10, 31), "basico": 1500,
        }

        response = self.client.get(
            reverse("contratos:generate", args=["W001"]), {"renew": "002"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial["start_date"], date(2026, 11, 1))
        self.assertEqual(response.context["form"].initial["contract_type"], "01")
        self.assertContains(response, "Renovación del contrato")
