from datetime import date
from pathlib import Path
import tempfile
from unittest.mock import patch
from io import BytesIO

from django.test import SimpleTestCase, TestCase
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.user.models import User

from .forms import ContractGenerationForm
from .identity import IdentityLookupError, _api_token, lookup_dni


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
                "signature_date": "2026-07-27",
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
                "signature_date": "2026-07-27",
            },
            contract_types=self.choices,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["start_date"], date(2026, 7, 27))
        self.assertEqual(form.cleaned_data["duration_days"], 66)


class IdentityLookupTests(SimpleTestCase):
    def test_reads_token_from_runtime_file(self):
        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "apiperu.token"
            token_file.write_text("file-secret\n", encoding="utf-8")
            with patch.dict("os.environ", {"APIPERU_TOKEN": ""}), override_settings(
                APIPERU_TOKEN_FILE=str(token_file)
            ):
                self.assertEqual(_api_token(), "file-secret")

    @patch("apps.contratos.identity._api_token", return_value="secret")
    @patch("apps.contratos.identity.requests.post")
    def test_maps_api_peru_dni_response(self, post, unused_token):
        post.return_value.status_code = 200
        post.return_value.json.return_value = {
            "success": True,
            "data": {
                "numero": "00932970", "nombres": "BELTRAN",
                "apellido_paterno": "PASHANACE", "apellido_materno": "TAPULLIMA",
            },
        }
        self.assertEqual(lookup_dni("00932970")["first_names"], "BELTRAN")

    @patch("apps.contratos.identity._api_token", return_value="secret")
    @patch("apps.contratos.identity.requests.post")
    def test_reports_document_not_found(self, post, unused_token):
        post.return_value.status_code = 404
        post.return_value.json.return_value = {
            "success": False, "message": "El DNI no existe",
        }
        with self.assertRaises(IdentityLookupError):
            lookup_dni("00000000")


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
    @patch("apps.contratos.views.ContractService.contract_types", return_value=[])
    def test_selected_month_card_and_expiration_list(self, unused_types, unused_personnel, expiring):
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

    @patch("apps.contratos.views.ContractService.contract_types")
    def test_template_can_be_uploaded_and_reused_from_dashboard(self, contract_types):
        from .services import ContractService, dashboard_template_path

        contract_types.return_value = [{"idtipocontrato": "01", "descripcion": "PLAZO FIJO"}]
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            response = self.client.post(
                reverse("contratos:template_upload"),
                {
                    "contract_type": "01",
                    "file": SimpleUploadedFile(
                        "plantilla.docx",
                        b"plantilla-local",
                        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    ),
                },
            )
            self.assertRedirects(
                response, reverse("contratos:index") + "?tab=templates",
                fetch_redirect_response=False,
            )
            template = dashboard_template_path("01")
            self.assertTrue(template.is_file())
            service = ContractService()
            with patch.object(service, "_rows") as rows:
                self.assertEqual(service.template_path("01"), template)
                rows.assert_not_called()

    @patch("apps.contratos.views.build_contract_pdf", return_value=BytesIO(b"%PDF-1.4\n"))
    @patch("apps.contratos.views.ContractService.template_path")
    @patch("apps.contratos.views.ContractService.contract_document_data")
    def test_contract_pdf_download_uses_worker_and_contract_data(self, document_data, template_path, build_pdf):
        document_data.return_value = {
            "full_name": "TRABAJADOR PRUEBA",
            "idtipocontrato": "01",
        }
        template_path.return_value = "template.docx"

        with tempfile.TemporaryDirectory() as directory, patch(
            "apps.contratos.views._contract_pdf_path",
            return_value=Path(directory) / "W001_002.pdf",
        ):
            response = self.client.get(reverse("contratos:pdf", args=["W001", "002"]))
            second = self.client.get(reverse("contratos:pdf", args=["W001", "002"]))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "application/pdf")
            self.assertTrue(response["Content-Disposition"].startswith("inline;"))
            self.assertIn("CONTRATO_TRABAJADOR_PRUEBA_002.pdf", response["Content-Disposition"])
            response.close()
            second.close()
        document_data.assert_called_once_with("W001", "002")
        build_pdf.assert_called_once_with("template.docx", document_data.return_value)
