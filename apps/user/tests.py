from django.contrib.auth.backends import ModelBackend
from django.test import SimpleTestCase

from .forms import FormUpdatePassword
from .models import User


class UserAccessTests(SimpleTestCase):
    def test_restricted_user_is_rejected_by_authentication_backend(self):
        user = User(
            username="restricted",
            email="restricted@example.com",
            first_name="Usuario",
            last_name="Restringido",
            active=False,
        )
        self.assertFalse(user.is_active)
        self.assertFalse(ModelBackend().user_can_authenticate(user))

    def test_active_user_is_accepted_by_authentication_backend(self):
        user = User(
            username="active",
            email="active@example.com",
            first_name="Usuario",
            last_name="Activo",
            active=True,
        )
        self.assertTrue(ModelBackend().user_can_authenticate(user))

    def test_password_form_rejects_different_passwords(self):
        form = FormUpdatePassword(
            data={
                "password1": "UnaClaveSegura-2026",
                "password2": "OtraClaveSegura-2026",
            },
            user=User(),
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
