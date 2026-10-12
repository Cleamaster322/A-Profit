import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0009_protocol_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='generation',
            field=models.ForeignKey(
                blank=True,
                db_column='generation_id',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='protocols',
                to='cars.generation',
            ),
        ),
        migrations.AddField(
            model_name='protocol',
            name='configuration',
            field=models.ForeignKey(
                blank=True,
                db_column='configuration_id',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='protocols',
                to='cars.configuration',
            ),
        ),
    ]