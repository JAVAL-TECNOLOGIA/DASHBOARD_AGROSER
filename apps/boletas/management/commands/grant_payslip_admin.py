from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from apps.boletas.models import BoletaPermission


class Command(BaseCommand):
    help = "Otorga administración completa del módulo de boletas a un usuario."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        username = options["username"].strip()
        user = get_user_model().objects.filter(username__iexact=username).first()
        if user is None:
            raise CommandError("No existe el usuario {}.".format(username))

        content_type = ContentType.objects.get_for_model(BoletaPermission)
        permission, unused_created = Permission.objects.get_or_create(
            content_type=content_type,
            codename="administrar_boletas",
            defaults={"name": "Puede administrar completamente las boletas"},
        )
        user.user_permissions.add(permission)
        self.stdout.write(self.style.SUCCESS(
            "{} ahora administra completamente el módulo de boletas.".format(user.username)
        ))
