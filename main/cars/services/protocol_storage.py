"""
Файлы протоколов на диске.

Структура: <корень>/<номер>/<номер>.docx и <корень>/<номер>/photos/<тип>_<uuid>.<расширение>.
Корней два — «В работе» и «Завершённые» (ProtocolStorageSettings). В какой из них
сейчас лежит папка протокола, хранит Protocol.files_location. У фото в БД путь
относительно корня (00001/photos/...), поэтому при переносе папки меняется только
files_location.
"""
import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage

IN_PROGRESS = 'in_progress'
COMPLETED = 'completed'

DEFAULT_DIRS = {
    IN_PROGRESS: Path('protocols') / 'in_progress',
    COMPLETED: Path('protocols') / 'completed',
}

# Старое расположение фото: MEDIA_ROOT/protocol_photos/<id>/<файл>.
LEGACY_PHOTO_PREFIX = 'protocol_photos/'

PHOTOS_DIR = 'photos'

# Символы, недопустимые в имени папки Windows.
INVALID_FOLDER_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class ProtocolStorageError(Exception):
    """Ошибка работы с папкой протокола; текст показывается пользователю."""


class ProtocolFileBusyError(ProtocolStorageError):
    pass


# =========================
# Корневые папки
# =========================

def default_root(location):
    return Path(settings.MEDIA_ROOT) / DEFAULT_DIRS[location]


def _configured_dirs():
    from ..models import ProtocolStorageSettings

    storage_settings = ProtocolStorageSettings.load()
    return {
        IN_PROGRESS: storage_settings.in_progress_dir,
        COMPLETED: storage_settings.completed_dir,
    }


def get_root(location):
    configured = (_configured_dirs()[location] or '').strip()
    return Path(configured) if configured else default_root(location)


def _normalized(path):
    return Path(os.path.normcase(os.path.abspath(path)))


def validate_storage_dirs(in_progress_dir, completed_dir):
    """Проверка путей из админки. Пустой путь заменяется папкой по умолчанию."""
    errors = {}
    roots = {}

    for field, location, value in (
        ('in_progress_dir', IN_PROGRESS, in_progress_dir),
        ('completed_dir', COMPLETED, completed_dir),
    ):
        value = (value or '').strip()
        if value and not Path(value).is_absolute():
            errors[field] = 'Укажите абсолютный путь (например, D:\\Протоколы или \\\\сервер\\Протоколы).'
            continue
        roots[field] = Path(value) if value else default_root(location)

    if errors:
        raise ValidationError(errors)

    in_progress = _normalized(roots['in_progress_dir'])
    completed = _normalized(roots['completed_dir'])

    if in_progress == completed:
        raise ValidationError('Папки «В работе» и «Завершённые» должны быть разными.')
    if in_progress in completed.parents or completed in in_progress.parents:
        raise ValidationError('Одна папка не может лежать внутри другой.')

    for field, root in roots.items():
        try:
            root.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=root):
                pass
        except OSError as error:
            errors[field] = f'Нет доступа на запись в папку: {error}'

    if errors:
        raise ValidationError(errors)


# =========================
# Папка протокола
# =========================

def protocol_folder_name(protocol):
    number = (protocol.protocol_number or '').strip()

    if (
        number
        and not number.startswith('TEMP-')
        and not INVALID_FOLDER_CHARS.search(number)
        and number.strip('. ') == number
    ):
        return number

    return str(protocol.id).zfill(5)


def protocol_dir(protocol, location=None):
    return get_root(location or protocol.files_location) / protocol_folder_name(protocol)


def create_protocol_dir(protocol):
    protocol_dir(protocol).mkdir(parents=True, exist_ok=True)


def protocol_document_path(protocol, title):
    """Документ протокола: <папка>/<номер> <название>.docx, например «00012 Заявка.docx»."""
    folder_name = protocol_folder_name(protocol)
    return protocol_dir(protocol) / f'{folder_name} {title}.docx'


def legacy_protocol_docx_path(protocol):
    """Старое имя DOCX протокола (<номер>.docx) — удаляется после нового формирования."""
    folder_name = protocol_folder_name(protocol)
    return protocol_dir(protocol) / f'{folder_name}.docx'


def _move_dir(protocol, source_location, target_location):
    source = protocol_dir(protocol, source_location)
    target = protocol_dir(protocol, target_location)

    if not source.exists():
        return

    if target.exists():
        raise ProtocolStorageError(
            f'Папка протокола уже существует: {target}. Разберите её вручную и повторите.'
        )

    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(source), str(target))
    except OSError as error:
        raise ProtocolStorageError(
            f'Не удалось перенести папку протокола {source} → {target}: {error}'
        ) from error


@contextmanager
def protocol_files_moved_to(protocol, location):
    """
    Переносит папку протокола в другой корень и меняет files_location.

    Если код внутри блока (сохранение статуса) упал — папка возвращается назад.
    Поле files_location сохраняет вызывающий код.
    """
    previous = protocol.files_location

    if previous == location:
        yield
        return

    _move_dir(protocol, previous, location)
    protocol.files_location = location

    try:
        yield
    except BaseException:
        _move_dir(protocol, location, previous)
        protocol.files_location = previous
        raise


def protocol_file_dirs(protocol):
    """
    Папки с файлами протокола: текущая и старая media/protocol_photos/<id>.

    Собирать до protocol.delete() — после удаления у объекта нет id.
    """
    return [
        protocol_dir(protocol),
        Path(settings.MEDIA_ROOT) / LEGACY_PHOTO_PREFIX / str(protocol.id),
    ]


def remove_dirs(paths):
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)


# =========================
# Фото
# =========================

def _protocol_file_storage(protocol):
    return FileSystemStorage(location=str(get_root(protocol.files_location)))


def photo_file_stem(title):
    """Имя файла фото = название на сайте; недопустимые для Windows символы заменяем."""
    stem = INVALID_FOLDER_CHARS.sub('_', title).strip(' .')
    return stem or 'Фото'


def save_photo_file(protocol, title, uploaded_file):
    """
    Сохраняет фото в папку протокола под именем «<название>.<расширение>»
    и возвращает путь относительно корня. Файл с таким именем перезаписывается.
    """
    extension = Path(uploaded_file.name).suffix.lower()
    relative_path = str(
        PurePosixPath(protocol_folder_name(protocol))
        / PHOTOS_DIR
        / f'{photo_file_stem(title)}{extension}'
    )

    storage = _protocol_file_storage(protocol)
    if storage.exists(relative_path):
        storage.delete(relative_path)

    return storage.save(relative_path, uploaded_file)


def is_legacy_photo_path(file_path):
    return str(file_path or '').replace('\\', '/').startswith(LEGACY_PHOTO_PREFIX)


def photo_absolute_path(photo, protocol=None):
    """Полный путь к файлу фото (без проверки, что файл есть)."""
    if not photo.file_path:
        return None

    file_path = str(photo.file_path)

    if is_legacy_photo_path(file_path):
        return Path(settings.MEDIA_ROOT) / file_path

    protocol = protocol or photo.protocol
    return get_root(protocol.files_location) / file_path


def delete_photo_file(photo, protocol=None):
    path = photo_absolute_path(photo, protocol)

    if path is None:
        return

    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


# =========================
# DOCX
# =========================

@contextmanager
def replace_file_atomically(target_path):
    """
    Даёт временный путь рядом с target_path; после успешного блока подменяет им target_path.

    Так старый файл не портится, если сборка упала. Если target_path открыт
    в Word, подмена не удастся — ProtocolFileBusyError.
    """
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.with_name(f'~tmp_{uuid4().hex}{target_path.suffix}')

    try:
        yield temp_path
        try:
            os.replace(temp_path, target_path)
        except PermissionError as error:
            raise ProtocolFileBusyError(
                f'Файл {target_path.name} занят (возможно, открыт в Word). '
                'Закройте его и повторите.'
            ) from error
    finally:
        temp_path.unlink(missing_ok=True)
