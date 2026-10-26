import re

from django.db import migrations, models

INVALID_FOLDER_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def number_label(protocol):
    # Копия protocol_storage.protocol_number_label на момент миграции.
    number = (protocol.protocol_number or '').strip()
    if (
        number
        and not number.startswith('TEMP-')
        and not INVALID_FOLDER_CHARS.search(number)
        and number.strip('. ') == number
    ):
        return number
    return str(protocol.id).zfill(5)


def fill_folders_and_photo_paths(apps, schema_editor):
    """
    Существующие папки назывались просто номером — записываем это имя, чтобы их найти
    (под «<номер> <VIN> <дата>» их переименует relocate_protocol_files или следующее
    сохранение протокола). Пути фото «00012/photos/x.jpg» становятся «photos/x.jpg».
    """
    Protocol = apps.get_model('cars', 'Protocol')
    ProtocolPhoto = apps.get_model('cars', 'ProtocolPhoto')

    for protocol in Protocol.objects.all():
        protocol.files_folder = number_label(protocol)
        protocol.save(update_fields=['files_folder'])

    for photo in ProtocolPhoto.objects.exclude(file_path__isnull=True).exclude(file_path=''):
        path = photo.file_path.replace('\\', '/')
        if path.startswith('protocol_photos/') or path.startswith('photos/') or '/' not in path:
            continue
        photo.file_path = path.split('/', 1)[1]
        photo.save(update_fields=['file_path'])


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0020_owner_requisites'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocol',
            name='files_folder',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.RunPython(fill_folders_and_photo_paths, migrations.RunPython.noop),
    ]
