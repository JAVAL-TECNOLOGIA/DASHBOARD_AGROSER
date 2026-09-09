from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .forms import FormUpdatePassword, FormUser, FormUserUpdate
from .models import User


class UserAdministrationMixin:
    """Allow portal administrators and holders of the legacy user permission."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not (
            getattr(request.user, "admin", False)
            or request.user.has_perm("user.aei_user")
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def permission_groups():
        permissions = (
            Permission.objects.select_related("content_type")
            .exclude(content_type__app_label__in=("admin", "contenttypes", "sessions"))
            .order_by("content_type__app_label", "name", "codename")
        )
        groups = OrderedDict()
        for permission in permissions:
            app_label = permission.content_type.app_label
            groups.setdefault(app_label, []).append(permission)
        return groups.items()

    @staticmethod
    def selected_permission_ids(request):
        values = request.POST.getlist("permissions")
        return list(
            Permission.objects.filter(pk__in=values).values_list("pk", flat=True)
        )


class HomeUser(UserAdministrationMixin, View):
    template_name = "user/list_user.html"

    def get(self, request):
        query = request.GET.get("q", "").strip()
        status = request.GET.get("status", "").strip()
        users = User.objects.prefetch_related("user_permissions").order_by(
            "-active", "last_name", "first_name"
        )
        if query:
            users = users.filter(
                Q(username__icontains=query)
                | Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        if status == "active":
            users = users.filter(active=True)
        elif status == "restricted":
            users = users.filter(active=False)
        return render(
            request,
            self.template_name,
            {
                "users": users,
                "query": query,
                "status": status,
                "total_users": users.count(),
            },
        )


class ListUser(UserAdministrationMixin, View):
    """Compatibility JSON endpoint used by older clients."""

    def get(self, request):
        data = [
            {
                "pk": user.pk,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "active": user.active,
                "permissions": user.user_permissions.count(),
            }
            for user in User.objects.prefetch_related("user_permissions").order_by("-id")
        ]
        from django.http import JsonResponse

        return JsonResponse(data, safe=False)


class CreateUser(UserAdministrationMixin, View):
    template_name = "user/user_form.html"

    def get(self, request):
        return self.render(request, FormUser())

    def post(self, request):
        form = FormUser(request.POST)
        if not form.is_valid():
            return self.render(request, form)
        with transaction.atomic():
            user = form.save()
            user.user_permissions.set(self.selected_permission_ids(request))
        messages.success(request, "Usuario creado correctamente.")
        return redirect("home_user")

    def render(self, request, form):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "permission_groups": self.permission_groups(),
                "selected_permissions": set(
                    int(value)
                    for value in request.POST.getlist("permissions")
                    if value.isdigit()
                ),
                "title": "Nuevo usuario",
                "submit_label": "Crear usuario",
            },
        )


class UpdateUser(UserAdministrationMixin, View):
    template_name = "user/user_form.html"

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        return self.render(
            request,
            user,
            FormUserUpdate(instance=user),
            set(user.user_permissions.values_list("pk", flat=True)),
        )

    def post(self, request, pk):
        user = self.get_object(pk)
        form = FormUserUpdate(request.POST, instance=user)
        selected = set(self.selected_permission_ids(request))
        if not form.is_valid():
            return self.render(request, user, form, selected)
        with transaction.atomic():
            form.save()
            user.user_permissions.set(selected)
        messages.success(request, "Usuario y accesos actualizados correctamente.")
        return redirect("home_user")

    def render(self, request, user, form, selected):
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "managed_user": user,
                "permission_groups": self.permission_groups(),
                "selected_permissions": selected,
                "title": "Editar usuario",
                "submit_label": "Guardar cambios",
            },
        )


class UpdatePassword(UserAdministrationMixin, View):
    template_name = "user/update_password.html"

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        return render(
            request,
            self.template_name,
            {"form": FormUpdatePassword(user=user), "managed_user": user},
        )

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = FormUpdatePassword(request.POST, user=user)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "managed_user": user},
            )
        form.save()
        if user.pk == request.user.pk:
            update_session_auth_hash(request, user)
        messages.success(request, "Contraseña actualizada correctamente.")
        return redirect("home_user")


class ToggleUserAccess(UserAdministrationMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk == request.user.pk:
            messages.error(request, "No puedes restringir tu propia cuenta.")
            return redirect("home_user")
        user.active = not user.active
        user.save(update_fields=["active"])
        action = "restablecido" if user.active else "restringido temporalmente"
        messages.success(request, "El acceso de {} fue {}.".format(user.username, action))
        return redirect("home_user")


class DeleteUser(UserAdministrationMixin, View):
    template_name = "user/delete_user.html"

    def get_object(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.pk == request.user.pk:
            raise Http404("No puedes eliminar tu propia cuenta.")
        if user.admin:
            raise PermissionDenied("Las cuentas administradoras no se eliminan desde este módulo.")
        return user

    def get(self, request, pk):
        return render(
            request,
            self.template_name,
            {"managed_user": self.get_object(request, pk)},
        )

    def post(self, request, pk):
        user = self.get_object(request, pk)
        username = user.username
        try:
            user.delete()
        except DatabaseError:
            messages.error(
                request,
                "No se puede eliminar esta cuenta porque tiene información relacionada. "
                "Puedes restringir temporalmente su acceso.",
            )
        else:
            messages.success(request, "El usuario {} fue eliminado.".format(username))
        return redirect("home_user")
