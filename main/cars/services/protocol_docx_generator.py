from pathlib import Path

from django.conf import settings

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
from .evaluation_sheet import build_evaluation_context
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

# Лист оценки неопределенности — Excel, свой контекст (services/evaluation_sheet.py).
EVALUATION_DOCUMENT = ("Лист оценки", "evaluation_sheet_template.xlsx")


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


def generate_protocol_documents(protocol):
    """
    Собирает все документы протокола в его папку (каждый файл перезаписывается).

    Документ без шаблона пропускается. Если файл открыт в Word, остальные документы
    всё равно собираются, а ошибка попадает в errors.
    """
    protocol_template = TEMPLATES_DIR / PROTOCOL_DOCUMENT[1]
    if not protocol_template.exists():
        raise FileNotFoundError(f"Не найден шаблон протокола: {protocol_template}")

    # Папка называется по VIN: если переименовать раньше не удалось, пробуем ещё раз.
    folder_warning = sync_protocol_folder(protocol)

    base_context = build_document_context(protocol)
    result = {
        "folder": protocol_dir(protocol),
        "files": [],
        "skipped": [],
        "errors": [],
        "warnings": [folder_warning] if folder_warning else [],
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

    title, template_name = EVALUATION_DOCUMENT
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        result["skipped"].append(f"{title} (нет шаблона {template_name})")
    else:
        output_path = protocol_document_path(protocol, title, extension="xlsx")
        try:
            with replace_file_atomically(output_path) as temp_path:
                render_xlsx(template_path, temp_path, build_evaluation_context(protocol))
        except ProtocolFileBusyError as error:
            result["errors"].append(str(error))
        else:
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
