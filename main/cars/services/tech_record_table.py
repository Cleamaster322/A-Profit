"""
«Таблица для техзаписи» (Excel): бланк для записи от руки, в колонке D — значения из протокола.

Шаблон — templates/tech_record_table_template.xlsx (копия «Таблица для техзаписи.xlsx»):
в колонке C подписи с местом для ручки («___ кН»), в D — {{ tt_... }}.
Строки дымности удаляются, если п. А.21.8 не применяется (как в листе оценки).
"""
from openpyxl import load_workbook

from .evaluation_sheet import evaluation_conditions
from .protocol_docx.calculations import get_related_safe, get_value
from .protocol_docx.formatters import round_half_up
from .xlsx_renderer import fill_placeholders

BRAKE_FIELDS = (
    "service_brake_front_left_kn",
    "service_brake_rear_left_kn",
    "service_brake_front_right_kn",
    "service_brake_rear_right_kn",
    "parking_brake_left_kn",
    "parking_brake_right_kn",
)
SMOKE_FIELDS = tuple(f"light_absorption_{index}" for index in range(1, 7))
SMOKE_PLACEHOLDER = "tt_light_absorption_"


def number_or_dash(value):
    rounded = round_half_up(value, 2)
    return float(rounded) if rounded is not None else "-"


def build_tech_record_table_context(protocol):
    measurement = get_related_safe(protocol, "measurement")
    brake = get_related_safe(protocol, "brake")
    light = get_related_safe(protocol, "light")

    context = {f"tt_{field}": number_or_dash(get_value(brake, field)) for field in BRAKE_FIELDS}
    context.update({f"tt_{field}": number_or_dash(get_value(measurement, field)) for field in SMOKE_FIELDS})
    context["tt_smoke_applicable"] = evaluation_conditions(protocol, measurement, brake, light)["ev_diesel_like"]
    return context


def remove_smoke_rows(worksheet):
    """Удаляет строки дымности вместе с их объединенными ячейками (A7:A12, B7:C7 …)."""
    rows = sorted({
        cell.row
        for row in worksheet.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and SMOKE_PLACEHOLDER in cell.value
    })
    if not rows:
        return

    first, last = rows[0], rows[-1]
    for merged in list(worksheet.merged_cells.ranges):
        if merged.min_row <= last and merged.max_row >= first:
            worksheet.unmerge_cells(str(merged))
    worksheet.delete_rows(first, last - first + 1)


def render_tech_record_table(template_path, output_path, protocol):
    context = build_tech_record_table_context(protocol)
    workbook = load_workbook(template_path)
    worksheet = workbook.active

    if not context["tt_smoke_applicable"]:
        remove_smoke_rows(worksheet)

    fill_placeholders(worksheet, context)
    workbook.save(output_path)
    return output_path
