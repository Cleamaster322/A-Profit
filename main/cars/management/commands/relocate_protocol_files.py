import os
import shutil
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.management.base import BaseCommand

from cars.models import Protocol, ProtocolPhoto
from cars.services.protocol_storage import (
    COMPLETED,
    IN_PROGRESS,
    PHOTOS_DIR,
    default_root,
    get_root,
    is_legacy_photo_path,
    protocol_dir,
    protocol_folder_name,
)


def same_path(first, second):
    return os.path.normcase(os.path.abspath(first)) == os.path.normcase(os.path.abspath(second))


class Command(BaseCommand):
    help = (
        "Переносит файлы протоколов в папки из настроек: старые фото из media/protocol_photos "
        "и папки протоколов из прежних корневых папок (--source, папки по умолчанию)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать, что будет перенесено.",
        )
        parser.add_argument(
            "--source",
            action="append",
            default=[],
            help="Прежняя корневая папка («В работе» или «Завершённые»). Можно указать несколько раз.",
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        current_roots = [get_root(IN_PROGRESS), get_root(COMPLETED)]
        source_roots = [
            root
            for root in [Path(source) for source in options["source"]]
            + [default_root(IN_PROGRESS), default_root(COMPLETED)]
            if not any(same_path(root, current) for current in current_roots)
        ]

        moved_dirs = self.move_protocol_dirs(source_roots)
        moved_photos, missing = self.move_photos(source_roots + current_roots)
        created_dirs = self.create_missing_dirs()

        prefix = "[dry-run] " if self.dry_run else ""
        self.stdout.write(f"{prefix}Перенесено папок протоколов: {moved_dirs}")
        self.stdout.write(f"{prefix}Перенесено фото: {moved_photos}")
        self.stdout.write(f"{prefix}Создано пустых папок протоколов: {created_dirs}")

        if missing:
            self.stdout.write(self.style.WARNING(f"Фото нет на диске: {len(missing)}"))
            for photo in missing:
                self.stdout.write(
                    f"  протокол {photo.protocol.protocol_number or photo.protocol_id}, "
                    f"фото id={photo.id}: {photo.file_path}"
                )
        else:
            self.stdout.write(self.style.SUCCESS("Все фото на месте."))

    def move(self, source, target):
        self.stdout.write(f"  {source} -> {target}")
        if self.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))

    def move_protocol_dirs(self, source_roots):
        moved = 0

        for protocol in Protocol.objects.all():
            target = protocol_dir(protocol)
            for root in source_roots:
                source = root / protocol_folder_name(protocol)
                if not source.is_dir():
                    continue
                if target.exists():
                    self.stdout.write(self.style.WARNING(
                        f"  Пропущено, папка уже есть: {source} -> {target}"
                    ))
                    continue
                self.move(source, target)
                moved += 1

        return moved

    def create_missing_dirs(self):
        # Папка нужна каждому протоколу, даже без фото и DOCX (например, у замерщика).
        created = 0

        for protocol in Protocol.objects.all():
            target = protocol_dir(protocol)
            if target.is_dir():
                continue
            self.stdout.write(f"  создать {target}")
            if not self.dry_run:
                target.mkdir(parents=True, exist_ok=True)
            created += 1

        return created

    def move_photos(self, search_roots):
        moved = 0
        missing = []

        photos = ProtocolPhoto.objects.select_related("protocol").exclude(file_path__isnull=True).exclude(file_path="")
        for photo in photos:
            protocol = photo.protocol
            root = get_root(protocol.files_location)
            file_path = str(photo.file_path).replace("\\", "/")

            if is_legacy_photo_path(file_path):
                sources = [Path(settings.MEDIA_ROOT) / file_path]
                new_path = str(
                    PurePosixPath(protocol_folder_name(protocol)) / PHOTOS_DIR / PurePosixPath(file_path).name
                )
            else:
                sources = [search_root / file_path for search_root in search_roots]
                new_path = file_path

            target = root / new_path
            if new_path == file_path and target.is_file():
                continue

            source = next((path for path in sources if path.is_file()), None)
            if source is None:
                missing.append(photo)
                continue

            if not target.exists():
                self.move(source, target)
            moved += 1

            if not self.dry_run and new_path != file_path:
                photo.file_path = new_path
                photo.save(update_fields=["file_path"])

        return moved, missing
