from django.db import migrations


def backfill_protocol_models(apps, schema_editor):
    Protocol = apps.get_model('cars', 'Protocol')
    Model = apps.get_model('cars', 'Model')

    for protocol in Protocol.objects.filter(model__isnull=True):
        if not protocol.brand_name or not protocol.commercial_name:
            continue

        model = (
            Model.objects
            .filter(
                brand__name__iexact=protocol.brand_name.strip(),
                name__iexact=protocol.commercial_name.strip(),
            )
            .first()
        )

        if model:
            protocol.model_id = model.id
            protocol.save(update_fields=['model'])


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0010_protocol_generation_protocol_configuration'),
    ]

    operations = [
        migrations.RunPython(
            backfill_protocol_models,
            migrations.RunPython.noop,
        ),
    ]