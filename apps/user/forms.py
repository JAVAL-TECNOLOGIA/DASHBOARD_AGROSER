from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User


class BootstrapFormMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class FormUser(BootstrapFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name")
        labels = {
            "email": "Correo",
            "username": "Usuario",
            "first_name": "Nombres",
            "last_name": "Apellidos",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class FormUserUpdate(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name")
        labels = {
            "email": "Correo",
            "username": "Usuario",
            "first_name": "Nombres",
            "last_name": "Apellidos",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class FormUpdatePassword(BootstrapFormMixin, forms.Form):
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        validators=[validate_password],
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput,
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save(update_fields=["password"])
        return self.user
