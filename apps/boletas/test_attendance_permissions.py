from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.user.models import User
from apps.user.views import UserAdministrationMixin


class AttendancePermissionTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(
            'attendance_operator', 'attendance@example.test', 'Operador', 'Prueba', 'SafePassword42!'
        )
        self.attendance_permission = Permission.objects.get(
            content_type__app_label='boletas', codename='ver_marcaciones'
        )

    def test_permission_appears_in_user_administration(self):
        groups = dict(UserAdministrationMixin.permission_groups())
        self.assertIn(self.attendance_permission, groups['boletas'])

    def test_operator_can_open_attendance_without_payslip_access(self):
        self.worker.user_permissions.add(self.attendance_permission)
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(reverse('boletas:attendance')).status_code, 200)
        self.assertEqual(self.client.get(reverse('boletas:attendance_screen')).status_code, 200)
        self.assertEqual(self.client.get(reverse('boletas:attendance_service_worker')).status_code, 200)
        self.assertEqual(self.client.get(reverse('boletas:index')).status_code, 403)

    def test_payslip_permission_does_not_grant_attendance(self):
        payslip_permission = Permission.objects.get(
            content_type__app_label='boletas', codename='visualizar_boletas'
        )
        self.worker.user_permissions.add(payslip_permission)
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(reverse('boletas:attendance')).status_code, 403)
        self.assertEqual(self.client.get(reverse('boletas:attendance_screen')).status_code, 403)

    def test_admin_keeps_attendance_access(self):
        self.worker.admin = True
        self.worker.save(update_fields=['admin'])
        self.client.force_login(self.worker)
        self.assertEqual(self.client.get(reverse('boletas:attendance')).status_code, 200)
