import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0008_protocol_workflow_and_supercharger'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='model',
            field=models.ForeignKey(
                blank=True,
                db_column='model_id',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='protocols',
                to='cars.model',
            ),
        ),
    ]