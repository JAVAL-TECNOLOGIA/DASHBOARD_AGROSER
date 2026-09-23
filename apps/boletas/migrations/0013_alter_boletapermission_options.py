from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("boletas", "0012_alter_attendancemark_source"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="boletapermission",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": [
                    ("visualizar_boletas", "Puede visualizar boletas"),
                    ("gestionar_publicacion_boletas", "Puede validar y autorizar boletas"),
                    ("ver_marcaciones", "Puede ver marcaciones"),
                ],
                "verbose_name": "Permiso de boletas",
                "verbose_name_plural": "Permisos de boletas",
            },
        ),
    ]
