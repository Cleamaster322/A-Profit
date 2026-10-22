from django.db import migrations


def photo_type_to_varchar(apps, schema_editor):
    # В MySQL таблица создавалась вручную, и photo_type там ENUM со старым списком типов.
    # Новые слоты фотофиксации в ENUM не помещаются — делаем обычный VARCHAR, как в модели.
    if schema_editor.connection.vendor != 'mysql':
        return

    schema_editor.execute(
        "ALTER TABLE protocol_photos MODIFY COLUMN photo_type VARCHAR(50) NOT NULL"
    )


class Migration(migrations.Migration):
    # ALTER TABLE в MySQL нельзя выполнять внутри транзакции миграции.
    atomic = False

    dependencies = [
        ('cars', '0017_protocol_photo_slots'),
    ]

    operations = [
        migrations.RunPython(photo_type_to_varchar, migrations.RunPython.noop),
    ]
