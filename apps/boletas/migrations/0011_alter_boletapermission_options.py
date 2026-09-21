from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boletas", "0010_attendancemark_client_event_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="boletapermission",
            options={
                "managed": False,
                "default_permissions": (),
                "verbose_name": "Permiso de boletas",
                "verbose_name_plural": "Permisos de boletas",
                "permissions": [
                    ("visualizar_boletas", "Puede visualizar boletas"),
                    ("ver_marcaciones", "Puede ver marcaciones"),
                ],
            },
        ),
    ]
