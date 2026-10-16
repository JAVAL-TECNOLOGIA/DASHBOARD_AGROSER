from django import forms
from django.utils import timezone

class ContractTemplateUploadForm(forms.Form):
    contract_type = forms.ChoiceField(widget=forms.Select(attrs={"class": "form-control"}))
    file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control-file", "accept": ".doc,.docx"}
        )
    )

    def __init__(self, *args, contract_types=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.contract_types = tuple(contract_types)
        self.fields["contract_type"].choices = self.contract_types

    def clean_contract_type(self):
        value = self.cleaned_data["contract_type"]
        allowed = {str(code) for code, unused_label in self.contract_types}
        if value not in allowed:
            raise forms.ValidationError("Selecciona un tipo de contrato válido.")
        return value

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        if not uploaded.name.lower().endswith((".doc", ".docx")):
            raise forms.ValidationError("La plantilla debe estar en formato DOC o DOCX.")
        if uploaded.size > 15 * 1024 * 1024:
            raise forms.ValidationError("La plantilla no puede superar 15 MB.")
        return uploaded


class ContractGenerationForm(forms.Form):
    worker_id = forms.CharField(widget=forms.HiddenInput)
    contract_type = forms.ChoiceField(label="Tipo de contrato")
    start_date = forms.DateField(
        label="Fecha de inicio",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
    )
    end_date = forms.DateField(
        label="Fecha final",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    basic = forms.DecimalField(
        label="Básico",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )
    trial_days = forms.IntegerField(
        label="Días de prueba",
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    signature_date = forms.DateField(
        label="Fecha de firma del contrato",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date", "class": "form-control"},
        ),
    )

    def __init__(self, *args, contract_types=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contract_type"].choices = contract_types
        self.fields["contract_type"].widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end < start:
            self.add_error("end_date", "La fecha final no puede ser anterior al inicio.")
        if start and end:
            cleaned["duration_days"] = (end - start).days + 1
        return cleaned


class NewEmployeeContractForm(ContractGenerationForm):
    worker_id = forms.CharField(required=False, widget=forms.HiddenInput)
    document = forms.RegexField(
        label="DNI", regex=r"^\d{8}$", max_length=8,
        widget=forms.TextInput(attrs={"class": "form-control", "inputmode": "numeric"}),
    )
    paternal_surname = forms.CharField(label="Apellido paterno", max_length=50)
    maternal_surname = forms.CharField(label="Apellido materno", max_length=50)
    first_names = forms.CharField(label="Nombres", max_length=50)
    birth_date = forms.DateField(label="Fecha de nacimiento", widget=forms.DateInput(attrs={"type": "date"}))
    sex = forms.ChoiceField(
        label="Sexo",
        choices=(("", "Seleccione..."), ("M", "Masculino"), ("F", "Femenino")),
    )
    marital_status = forms.ChoiceField(label="Estado civil")
    phone = forms.CharField(label="Teléfono", max_length=12, required=False)
    phone2 = forms.CharField(label="Teléfono 2", max_length=12, required=False)
    mobile = forms.CharField(label="Celular", max_length=15, required=False)
    email = forms.EmailField(label="Correo", max_length=100, required=False)
    nationality = forms.ChoiceField(label="Nacionalidad")
    issuing_country = forms.ChoiceField(label="País emisor")
    birth_place = forms.ChoiceField(label="Lugar de nacimiento", required=False)
    payroll = forms.ChoiceField(label="Planilla")
    position = forms.ChoiceField(label="Cargo")
    employment_start = forms.DateField(
        label="Fecha de ingreso",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    employment_regime_type = forms.ChoiceField(
        label="T. régimen",
        choices=(("P", "Privado"), ("U", "Público")),
    )
    labor_regime = forms.ChoiceField(label="Régimen laboral")
    pension_regime = forms.ChoiceField(label="Régimen pensionario")
    worker_category = forms.ChoiceField(
        label="Categoría trabajador",
        choices=(("1", "TRABAJADOR"),),
    )
    maximum_workday = forms.BooleanField(
        label="Jornada de trabajo máxima",
        required=False,
        initial=True,
    )
    medical_service = forms.ChoiceField(
        label="Servicio médico",
        choices=(("1", "EsSalud"), ("0", "Seguro privado")),
    )
    income_periodicity = forms.ChoiceField(label="Periodicidad del ingreso")
    payment_type = forms.ChoiceField(label="Tipo de pago")
    occupational_category = forms.ChoiceField(label="Categoría ocupacional")
    special_situation = forms.ChoiceField(
        label="Situación especial",
        choices=(("0", "NINGUNO"),),
    )
    educational_level = forms.ChoiceField(label="Nivel educativo")

    def __init__(self, *args, catalogs=None, **kwargs):
        catalogs = catalogs or {}
        kwargs.setdefault("initial", {})
        kwargs["initial"].setdefault("employment_start", timezone.localdate())
        kwargs["initial"].setdefault("start_date", timezone.localdate())
        kwargs["initial"].setdefault("signature_date", timezone.localdate())
        kwargs["initial"].setdefault("nationality", "PER")
        kwargs["initial"].setdefault("issuing_country", "604")
        kwargs["initial"].setdefault("employment_regime_type", "P")
        kwargs["initial"].setdefault("labor_regime", "26")
        kwargs["initial"].setdefault("pension_regime", "02")
        kwargs["initial"].setdefault("worker_category", "1")
        kwargs["initial"].setdefault("maximum_workday", True)
        kwargs["initial"].setdefault("medical_service", "1")
        kwargs["initial"].setdefault("income_periodicity", "3")
        kwargs["initial"].setdefault("payment_type", "2")
        kwargs["initial"].setdefault("occupational_category", "02")
        kwargs["initial"].setdefault("special_situation", "0")
        kwargs["initial"].setdefault("educational_level", "007")
        super().__init__(*args, **kwargs)
        for name in self.fields:
            if not isinstance(self.fields[name].widget, forms.HiddenInput):
                css_class = "form-check-input" if isinstance(
                    self.fields[name].widget, forms.CheckboxInput
                ) else "form-control"
                self.fields[name].widget.attrs.setdefault("class", css_class)
        for name in (
            "contract_type", "marital_status", "nationality", "issuing_country",
            "birth_place", "payroll", "position", "labor_regime", "pension_regime",
            "income_periodicity", "payment_type", "occupational_category",
            "educational_level",
        ):
            self.fields[name].choices = catalogs.get(name, ())
        for name in ("contract_type", "marital_status", "payroll", "position"):
            self.fields[name].choices = [("", "Seleccione...")] + list(
                self.fields[name].choices
            )
        locked_defaults = (
            "employment_start", "start_date", "signature_date", "nationality",
            "issuing_country", "employment_regime_type", "labor_regime",
            "pension_regime", "worker_category", "maximum_workday",
            "medical_service", "income_periodicity", "payment_type",
            "occupational_category", "special_situation", "educational_level",
        )
        for name in locked_defaults:
            field = self.fields[name]
            field.disabled = True
            field.widget.attrs["class"] = (
                field.widget.attrs.get("class", "") + " default-locked"
            ).strip()
            field.widget.attrs["title"] = "Valor definido por defecto"

    def clean(self):
        cleaned = super().clean()
        cleaned["worker_id"] = cleaned.get("document")
        return cleaned
