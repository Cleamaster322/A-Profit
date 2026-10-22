from django.db import migrations, models


def clear_placeholder_owner_names(apps, schema_editor):
    # Раньше при создании протокола фронтенд подставлял в ФИО «Не указано».
    Protocol = apps.get_model('cars', 'Protocol')
    Protocol.objects.filter(owner_name__iexact='Не указано').update(owner_name='')


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0018_protocol_photo_type_varchar'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='owner_legal_entity',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RunPython(clear_placeholder_owner_names, migrations.RunPython.noop),
    ]
