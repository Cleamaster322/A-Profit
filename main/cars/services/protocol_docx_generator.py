from pathlib import Path

from django.conf import settings

from .protocol_docx import build_protocol_docx_context, render_protocol_docx
from .protocol_docx.placeholder_aliases import add_protocol_placeholder_aliases
from .protocol_word import count_word_pages


def generate_protocol_docx(protocol):
    template_path = Path(settings.BASE_DIR) / "cars" / "templates" / "protocol_template.docx"

    if not template_path.exists():
        raise FileNotFoundError(f"Не найден шаблон протокола: {template_path}")

    output_dir = Path(settings.MEDIA_ROOT) / "generated_protocols"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"protocol_{protocol.id}.docx"

    context = build_protocol_docx_context(protocol)
    add_protocol_placeholder_aliases(context)

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
            return output_path
        page_count = measured_page_count

    raise RuntimeError("Не удалось стабилизировать количество страниц протокола в Word.")