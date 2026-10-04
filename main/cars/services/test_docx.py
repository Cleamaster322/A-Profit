from pathlib import Path

from django.conf import settings

from .protocol_docx import build_protocol_docx_context, render_protocol_docx
from .protocol_docx.v6_placeholder_migration import add_v6_context_aliases


PROTOCOL_TEMPLATES = {
    "old": "protocol_template.docx",
    "v5": "protocol_template_v5_source.docx",
    "v6": "protocol_template_v6_source.docx",
}


def generate_protocol_docx(protocol, template_variant="old"):
    template_filename = PROTOCOL_TEMPLATES.get(template_variant)
    if template_filename is None:
        raise ValueError(f"Неизвестный вариант шаблона: {template_variant}")

    template_path = Path(settings.BASE_DIR) / "cars" / "templates" / template_filename

    if not template_path.exists():
        raise FileNotFoundError(f"Не найден шаблон протокола: {template_path}")

    output_dir = Path(settings.MEDIA_ROOT) / "generated_protocols"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"protocol_{protocol.id}_{template_variant}.docx"

    context = build_protocol_docx_context(protocol)
    if template_variant == "v6":
        add_v6_context_aliases(context)

    return render_protocol_docx(
        template_path=template_path,
        output_path=output_path,
        context=context,
    )