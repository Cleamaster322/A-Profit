from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0011_backfill_protocol_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='manufacture_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]