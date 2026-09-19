from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("boletas", "0009_payrollrelease_validation_workflow")]

    operations = [
        migrations.AddField(
            model_name="attendancemark",
            name="client_event_id",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
