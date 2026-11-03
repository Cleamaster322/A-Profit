from pathlib import Path

from django.conf import settings
from django.utils import timezone

from .protocol_docx import build_protocol_docx_context, render_protocol_docx
from .protocol_docx.placeholder_aliases import add_protocol_placeholder_aliases
from .protocol_storage import (
    ProtocolFileBusyError,
    legacy_protocol_docx_path,
    protocol_dir,
    protocol_document_path,
    replace_file_atomically,
    sync_protocol_folder,
)
from .protocol_word import count_word_pages
from .equipment_verification import (
    MissingVerificationError,
    build_equipment_verification_values,
    missing_verifications_message,
    protocol_sample_date,
)
from .evaluation_sheet import build_evaluation_context
from .tech_record_table import render_tech_record_table
from .xlsx_renderer import render_xlsx

TEMPLATES_DIR = Path(settings.BASE_DIR) / "cars" / "templates"

# Документы, которые кнопка «Сформировать» собирает в папку протокола.
# Количество страниц через Word считается только для протокола: в его шаблоне
# есть {{ protocol_page_count }}.
PROTOCOL_DOCUMENT = ("Протокол", "protocol_template.docx", True)
PROTOCOL_DOCUMENTS = [
    PROTOCOL_DOCUMENT,
    ("Заявка", "application_template.docx", False),
    ("Техзапись", "tech_record_template.docx", False),
]



def render_evaluation_sheet(template_path, output_path, protocol):
    return render_xlsx(template_path, output_path, build_evaluation_context(protocol))


# Excel-документы со своим контекстом: лист оценки неопределенности
# (services/evaluation_sheet.py) и бланк «Таблица для техзаписи» (services/tech_record_table.py).
EXCEL_DOCUMENTS = [
    ("Лист оценки", "evaluation_sheet_template.xlsx", render_evaluation_sheet),
    ("Таблица для техзаписи", "tech_record_table_template.xlsx", render_tech_record_table),
]


def build_document_context(protocol):
    context = build_protocol_docx_context(protocol)
    add_protocol_placeholder_aliases(context)
    return context


def render_document(template_path, output_path, context, count_pages):
    """Рендер во временный файл рядом с output_path и подмена старого файла."""
    with replace_file_atomically(output_path) as temp_path:
        if count_pages:
            render_with_stable_page_count(template_path, temp_path, context)
        else:
            render_protocol_docx(template_path=template_path, output_path=temp_path, context=context)

    return output_path


def generate_protocol_docx(protocol, output_path=None):
    """
    Собирает DOCX протокола. По умолчанию перезаписывает <папка протокола>/<номер> Протокол.docx.
    """
    title, template_name, count_pages = PROTOCOL_DOCUMENT
    template_path = TEMPLATES_DIR / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Не найден шаблон протокола: {template_path}")

    output_path = Path(output_path or protocol_document_path(protocol, title))
    return render_document(template_path, output_path, build_document_context(protocol), count_pages)


def generate_protocol_documents(protocol, allow_missing_verifications=False):
    """
    Собирает все документы протокола в его папку (каждый файл перезаписывается).

    Документ без шаблона пропускается. Если файл открыт в Word, остальные документы
    всё равно собираются, а ошибка попадает в errors.

    Без действующей поверки оборудования на дату отбора — MissingVerificationError;
    allow_missing_verifications=True (admin) — формируем с ближайшей поверкой и предупреждаем.
    Первое формирование фиксирует дату протокола (first_generated_date).
    """
    protocol_template = TEMPLATES_DIR / PROTOCOL_DOCUMENT[1]
    if not protocol_template.exists():
        raise FileNotFoundError(f"Не найден шаблон протокола: {protocol_template}")

    _, missing = build_equipment_verification_values(protocol, allow_missing=False)
    missing_message = missing_verifications_message(missing, protocol_sample_date(protocol)) if missing else None
    if missing and not allow_missing_verifications:
        raise MissingVerificationError(missing_message)

    if protocol.first_generated_date is None:
        protocol.first_generated_date = timezone.localdate()
        protocol.save(update_fields=["first_generated_date"])

    # Папка называется по VIN: если переименовать раньше не удалось, пробуем ещё раз.
    folder_warning = sync_protocol_folder(protocol)

    base_context = build_document_context(protocol)
    result = {
        "folder": protocol_dir(protocol),
        "files": [],
        "skipped": [],
        "errors": [],
        "warnings": [warning for warning in (folder_warning, missing_message) if warning],
    }

    for title, template_name, count_pages in PROTOCOL_DOCUMENTS:
        template_path = TEMPLATES_DIR / template_name

        if not template_path.exists():
            result["skipped"].append(f"{title} (нет шаблона {template_name})")
            continue

        try:
            output_path = render_document(
                template_path,
                protocol_document_path(protocol, title),
                dict(base_context),
                count_pages,
            )
        except ProtocolFileBusyError as error:
            result["errors"].append(str(error))
            continue

        result["files"].append(output_path)

    for title, template_name, render in EXCEL_DOCUMENTS:
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            result["skipped"].append(f"{title} (нет шаблона {template_name})")
            continue

        output_path = protocol_document_path(protocol, title, extension="xlsx")
        try:
            with replace_file_atomically(output_path) as temp_path:
                render(template_path, temp_path, protocol)
        except ProtocolFileBusyError as error:
            result["errors"].append(str(error))
            continue

        result["files"].append(output_path)

    # До появления нескольких документов протокол лежал в папке как <номер>.docx.
    if result["files"]:
        try:
            legacy_protocol_docx_path(protocol).unlink(missing_ok=True)
        except OSError:
            pass

    return result


def render_with_stable_page_count(template_path, output_path, context):
    page_count = ""
    for _ in range(3):
        context["protocol_page_count"] = page_count
        render_protocol_docx(
            template_path=template_path,
            output_path=output_path,
            context=context,
        )
        measured_page_count = str(count_word_pages(output_path))
        if measured_page_count == page_count:
            return
        page_count = measured_page_count

    raise RuntimeError("Не удалось стабилизировать количество страниц протокола в Word.")
