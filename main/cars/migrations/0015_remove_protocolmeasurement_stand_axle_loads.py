from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0014_protocol_header_document_selections'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='protocolmeasurement',
            name='stand_axle1_load_kg',
        ),
        migrations.RemoveField(
            model_name='protocolmeasurement',
            name='stand_axle2_load_kg',
        ),
    ]