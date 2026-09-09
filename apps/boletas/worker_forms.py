from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO
import base64
import binascii
import uuid


class WorkerIdentityForm(forms.Form):
    signature = forms.CharField(widget=forms.HiddenInput(), max_length=7 * 1024 * 1024)
    photo = forms.ImageField(label="Fotografía", widget=forms.FileInput(attrs={
        "accept": "image/*", "capture": "user", "class": "sr-only",
    }))
    consent = forms.BooleanField(label="Confirmo que la fotografía y la firma son mías y autorizo su registro para identificarme en el portal de boletas.")

    def clean_signature(self):
        value = self.cleaned_data['signature']
        try:
            header, data = value.split(',', 1)
            if header != 'data:image/png;base64':
                raise ValueError()
            raw = base64.b64decode(data, validate=True)
            if len(raw) > 5 * 1024 * 1024:
                raise ValueError()
            with Image.open(BytesIO(raw)) as image:
                if image.width * image.height > 4000000:
                    raise ValueError()
                rgba = image.convert('RGBA')
                background = Image.new('RGBA', rgba.size, 'white')
                background.alpha_composite(rgba)
                rgb = background.convert('RGB')
                ink = rgb.convert('L').point(lambda pixel: 255 if pixel < 200 else 0)
                bounds = ink.getbbox()
                if not bounds or bounds[2] - bounds[0] < 15 or bounds[3] - bounds[1] < 5:
                    raise ValueError()
                output = BytesIO()
                rgb.save(output, format='PNG')
            return ContentFile(output.getvalue(), name=uuid.uuid4().hex + '.png')
        except (ValueError, binascii.Error, OSError, UnidentifiedImageError, Image.DecompressionBombError):
            raise forms.ValidationError('Dibuja tu firma en el recuadro antes de continuar.')

    def clean_photo(self):
        photo = self.cleaned_data['photo']
        if photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError('La foto debe pesar menos de 5 MB. Vuelve a tomarla con menor resolución.')
        try:
            photo.seek(0)
            with Image.open(photo) as image:
                if image.width * image.height > 25000000:
                    raise ValueError()
                normalized = ImageOps.exif_transpose(image).convert('RGB')
                normalized.thumbnail((1600, 1600))
                output = BytesIO()
                normalized.save(output, format='JPEG', quality=88)
            return ContentFile(output.getvalue(), name=uuid.uuid4().hex + '.jpg')
        except (ValueError, OSError, Image.DecompressionBombError):
            raise forms.ValidationError('No se pudo leer la fotografía. Vuelve a tomarla.')


class WorkerLoginForm(forms.Form):
    document = forms.CharField(
        label="DNI",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "inputmode": "numeric",
                "autocomplete": "username",
                "placeholder": "Número de DNI",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "autocomplete": "current-password",
                "placeholder": "Contraseña",
            }
        ),
    )

    def clean_document(self):
        value = self.cleaned_data["document"].strip()
        if not value.isdigit() or len(value) != 8:
            raise forms.ValidationError("Ingresa un DNI válido de 8 dígitos.")
        return value


class WorkerPasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        validators=[validate_password],
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        first = cleaned.get("new_password1")
        second = cleaned.get("new_password2")
        if first and second and first != second:
            self.add_error("new_password2", "Las contraseñas no coinciden.")
        if first and self.user and first == self.user.username:
            self.add_error("new_password1", "La nueva contraseña no puede ser tu DNI.")
        return cleaned


class PayslipConfirmationForm(forms.Form):
    """El acceso autenticado y la identidad registrada autorizan la confirmación."""
    pass
