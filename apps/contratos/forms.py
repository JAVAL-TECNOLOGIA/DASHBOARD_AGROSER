from django import forms


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
