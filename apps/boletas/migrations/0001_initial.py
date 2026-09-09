from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BoletaPermission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Permiso de boletas",
                "verbose_name_plural": "Permisos de boletas",
                "managed": False,
                "default_permissions": (),
                "permissions": [
                    ("visualizar_boletas", "Puede visualizar boletas"),
                ],
            },
        ),
    ]
