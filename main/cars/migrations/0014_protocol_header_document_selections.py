from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0013_protocolmeasurement_pneumatic_suspension_present'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='header_document_selections',
            field=models.JSONField(blank=True, default=list),
        ),
    ]