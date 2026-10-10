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
        super().__init__(
            *args, contract_types=catalogs.get("contract_type", ()), **kwargs
        )
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
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
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
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
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
    sex = forms.ChoiceField(label="Sexo", choices=(("M", "Masculino"), ("F", "Femenino")))
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
    employment_start = forms.DateField(label="Fecha de ingreso", widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, catalogs=None, **kwargs):
        catalogs = catalogs or {}
        kwargs.setdefault("initial", {})
        kwargs["initial"].setdefault("employment_start", timezone.localdate())
        kwargs["initial"].setdefault("signature_date", timezone.localdate())
        kwargs["initial"].setdefault("nationality", "PER")
        kwargs["initial"].setdefault("issuing_country", "604")
        super().__init__(*args, **kwargs)
        for name in self.fields:
            if not isinstance(self.fields[name].widget, forms.HiddenInput):
                self.fields[name].widget.attrs.setdefault("class", "form-control")
        for name in (
            "contract_type", "marital_status", "nationality", "issuing_country",
            "birth_place", "payroll", "position",
        ):
            self.fields[name].choices = catalogs.get(name, ())

    def clean(self):
        cleaned = super().clean()
        cleaned["worker_id"] = cleaned.get("document")
        return cleaned
