from django import forms

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
        return cleaned
