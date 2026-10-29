from django.db import migrations, models


def fuel_type_to_varchar(apps, schema_editor):
    # В MySQL fuel_type создавался вручную как ENUM('petrol','diesel','hybrid','electric'):
    # новые «Гибрид-бензин» / «Гибрид-дизель» туда не помещаются — делаем VARCHAR, как в модели.
    if schema_editor.connection.vendor != 'mysql':
        return

    schema_editor.execute(
        "ALTER TABLE protocol_measurements MODIFY COLUMN fuel_type VARCHAR(20) NULL"
    )


def hybrid_to_hybrid_petrol(apps, schema_editor):
    ProtocolMeasurement = apps.get_model('cars', 'ProtocolMeasurement')
    ProtocolMeasurement.objects.filter(fuel_type='hybrid').update(fuel_type='hybrid_petrol')


class Migration(migrations.Migration):
    # ALTER TABLE в MySQL нельзя выполнять внутри транзакции миграции.
    atomic = False

    dependencies = [
        ('cars', '0022_header_documents_other'),
    ]

    operations = [
        migrations.RunPython(fuel_type_to_varchar, migrations.RunPython.noop),
        migrations.RunPython(hybrid_to_hybrid_petrol, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='protocolmeasurement',
            name='fuel_type',
            field=models.CharField(blank=True, choices=[('petrol', 'Бензин'), ('diesel', 'Дизель'), ('hybrid_petrol', 'Гибрид-бензин'), ('hybrid_diesel', 'Гибрид-дизель'), ('electric', 'Электро')], max_length=20, null=True),
        ),
    ]
