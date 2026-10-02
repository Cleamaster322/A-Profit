from pathlib import Path

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .applicability import build_applicability_values
from .calculations import (
    build_calculated_values,
    build_uncertainty_values,
    calc_light_absorption_average,
)
from .formatters import decimal_value, fmt_bool, fmt_date, fmt_int, fmt_num, fmt_text
from .labels import (
    CYLINDER_LAYOUT_LABELS,
    ENGINE_LAYOUT_LABELS,
    FUEL_TYPE_LABELS,
    PARKING_BRAKE_LABELS,
    SERVICE_BRAKE_LABELS,
    STEERING_BOOSTER_LABELS,
    TIRE_SEASON_LABELS,
    TRANSMISSION_LABELS,
    WHEEL_FORMULA_LABELS,
    label,
)

DEFAULT_INSPECTION_PLACE = "690074, Россия, Приморский край, г. Владивосток, ул. Снеговая, д. 64"


# =========================
# Базовые helpers
# =========================

def get_related(protocol, attr_name):
    try:
        return getattr(protocol, attr_name)
    except ObjectDoesNotExist:
        return None


def build_owner_info(protocol):
    parts = []

    if protocol.owner_name:
        parts.append(protocol.owner_name)

    if protocol.owner_address:
        parts.append(protocol.owner_address)

    if protocol.owner_phone:
        parts.append(f"тел.: {protocol.owner_phone}")

    if protocol.owner_document:
        parts.append(protocol.owner_document)

    return "\n".join(parts)


def build_owner_full_name(protocol):
    parts = [
        getattr(protocol, "owner_last_name", None),
        getattr(protocol, "owner_first_name", None),
        getattr(protocol, "owner_middle_name", None),
    ]

    return " ".join(
        str(value).strip()
        for value in parts
        if value
    )


def build_manufacturer_info(protocol):
    return fmt_text(getattr(protocol, "manufacturer_info", None))


def normalize_light_color(value):
    if not value:
        return ""

    value = str(value).strip()
    value_lower = value.lower().replace("ё", "е")

    if value_lower in ["желтый", "жёлтый"]:
        return "автожелтый"

    return value


def value_or_dash(value):
    """
    Для условных строк DOCX.

    Если значения нет, возвращаем "-".
    Используется там, где строка остаётся в шаблоне,
    но значение должно быть прочерком.
    """
    if value is None:
        return "-"

    value = str(value).strip()

    if value == "":
        return "-"

    return value


def is_positive_count(value):
    """
    Проверка наличия светового прибора по количеству.

    Правило:
    - пусто / None / "-" / "0" / 0 => прибора нет;
    - любая другая цифра/число => прибор есть.

    Например:
    1, 2, 3 => есть
    0, "-", "" => нет
    """
    if value is None:
        return False

    value = str(value).strip()

    if value == "" or value == "-":
        return False

    number = decimal_value(value)

    if number is None:
        return False

    return number != 0


def is_true(value):
    return value is True


def is_fuel_petrol_like(value):
    return value in ["petrol", "hybrid"]


def is_fuel_diesel(value):
    return value == "diesel"


def conclusion_text(*lines):
    return "\n".join(lines)


def get_tire_depth_value(protocol, value, active_season):
    if protocol.tire_season != active_season:
        return "-"

    return value_with_unit_or_dash(True, value, 1)


def get_tire_depth_uncertainty(protocol, value, active_season):
    if protocol.tire_season != active_season:
        return "-"

    return uncertainty_with_unit_or_dash(True, value, "0,05")


def value_if_applicable(is_applicable, value, decimals=2):
    if not is_applicable:
        return "-"

    formatted = fmt_num(value, decimals)

    if not formatted:
        return "-"

    return formatted


def uncertainty_if_applicable(is_applicable, value, uncertainty):
    if not is_applicable:
        return "-"

    if value is None or value == "":
        return "-"

    return uncertainty


def result_with_uncertainty_if_applicable(is_applicable, value, uncertainty, decimals=2, unit=""):
    if not is_applicable:
        return "-"

    formatted = fmt_num(value, decimals)

    if not formatted:
        return "-"

    if unit:
        return f"{formatted} {unit} ± {uncertainty} {unit}"

    return f"{formatted} ± {uncertainty}"


def value_with_unit_or_dash(is_applicable, value, decimals=2, unit=""):
    if not is_applicable:
        return "-"

    formatted = fmt_num(value, decimals)

    if not formatted:
        return "-"

    if unit:
        return f"{formatted} {unit}"

    return formatted


def uncertainty_with_unit_or_dash(is_applicable, value, uncertainty, unit=""):
    if not is_applicable:
        return "-"

    if value is None or value == "":
        return "-"

    if unit:
        return f"{uncertainty} {unit}"

    return uncertainty


def build_full_result_text(
    is_applicable,
    conclusion,
    requirement_text=None,
    result_text=None,
    not_applicable_text=None,
):
    if not is_applicable:
        return not_applicable_text or "-"

    parts = []

    if conclusion:
        parts.append(conclusion)

    if requirement_text:
        parts.append("Требование:")
        parts.append(requirement_text)

    if result_text:
        parts.append("Результат:")
        parts.append(result_text)

    return "\n".join(parts)


def build_tire_depth_result_text(
    is_applicable,
    conclusion,
    requirement_text,
    values,
    not_applicable_text=None,
):
    if not is_applicable:
        return not_applicable_text or "-"

    parts = []

    if conclusion:
        parts.append(conclusion)

    parts.append("Требование:")
    parts.append(requirement_text)

    parts.append("Результат:")

    for label_text, value, uncertainty in values:
        parts.append(f"{label_text}: {value} ± {uncertainty} мм")

    return "\n".join(parts)


# =========================
# Динамические результаты:
# статус + заключение
# =========================

NOT_APPLICABLE_MESSAGES = {
    "result_a_3_2": "не применяется (пункт Постановления Правительства)",
    "result_a_6_5": "не применяется (ТС не оснащено противоугонным устройством, блокирующим рулевое управление)",
    "result_a_8_7": "не применяется (в ТС отсутствует адаптивная система переднего освещения)",
    "result_a_8_10_3": "не применяется (в ТС отсутствуют передние противотуманные фары)",
    "result_a_8_20_3": "не применяется (ТС не оснащено устройствами фароочистки  и автоматическим корректирующим устройством угла наклона фар (не предусмотренно конструкцией))",
    "result_a_8_20_8": "не применяется (в ТС отсутствуют передние противотуманные фары)",
    "result_a_8_24_1": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "result_a_8_24_2": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "result_a_8_24_3": "не применяется (в ТС отсутствуют задние противотуманные фонари)",
    "result_a_8_25": "не применяется (в ТС отсутствуют стояночные огни)",
    "result_a_8_27": "не применяется (в ТС отсутствуют дневные ходовые огни)",
    "result_a_10_5": "не применяется (на ТС установлены летние шины)",
    "result_a_10_6": "не применяется (на ТС установлены шины без шипов)",
    "result_a_16_17": "не применяется (на ТС отсутствуют подножки и ступеньки)",
    "result_a_18_5": "не применяется (на ТС отсутствует складывающаяся крыша)",
    "result_a_26_12": "не применяется (на ТС отсутствует запасное колесо)",
}


def make_result(is_applicable, conclusion, not_applicable_message=None):
    """
    Общее правило для подсказок вида:
    "Соответствует/не применяется".

    Если элемент/условие есть:
        статус = соответствует
        заключение = полный текст требований

    Если элемента/условия нет:
        статус = не применяется
        заключение = "-"
    """
    if is_applicable:
        return "соответствует", conclusion

    return not_applicable_message or "не применяется", "-"


def add_result_pair(context, key_prefix, is_applicable, conclusion):
    not_applicable_message = NOT_APPLICABLE_MESSAGES.get(key_prefix)
    if key_prefix.startswith("result_a_22_5_"):
        not_applicable_message = "не применяется (ТС не оборудовано газобалонным оборудованием)"

    status, conclusion_value = make_result(
        is_applicable,
        conclusion,
        not_applicable_message,
    )

    context[f"{key_prefix}_status"] = status
    context[f"{key_prefix}_conclusion"] = conclusion_value


def add_direct_result_pair(context, key_prefix, status, conclusion):
    """
    Для случаев, где в статусной ячейке должен быть не просто текст
    "соответствует", а конкретное значение:
    - среднее значение дымности;
    - пробег более/менее 3000 км.
    """
    context[f"{key_prefix}_status"] = status

    if status.startswith("не применяется") or status.startswith("не указано"):
        context[f"{key_prefix}_conclusion"] = "-"
    else:
        context[f"{key_prefix}_conclusion"] = conclusion


CONCLUSIONS = {
    "a_3_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложение № 3 п. 16.1;",
        "Приложение №4 п.5.1",
    ),

    "a_6_5": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения №4 п.1.1.5",
    ),

    "a_8_1": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения №4 п. 1.3.1",
        "(таблица 1.3.1)",
    ),

    "a_8_7": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.1.3.7",
    ),

    "a_8_10_1": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.1.3.10.1",
    ),

    "a_8_10_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.1.3.10.2",
    ),

    "a_8_10_3": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.1.3.10.3",
    ),

    "a_8_13_1": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.1.3.13.1",
    ),

    "a_8_13_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.1.3.13.2",
    ),

    "a_8_20_3": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.8.3",
    ),

    "a_8_20_8": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.8.8",
    ),

    "a_8_24_1": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.12.1",
    ),

    "a_8_24_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.12.2",
    ),

    "a_8_24_3": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.12.3",
    ),

    "a_8_25": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.13",
    ),

    "a_8_27": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.3.15",
    ),

    "a_10_5": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.5.5",
    ),

    "a_10_6": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.5.4",
    ),

    "a_10_7_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.5.6.2",
    ),

    "a_10_7_3": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.5.6.3",
    ),

    "a_11_8_sun_strip": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.4.3",
    ),

    "a_16_17": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.3.6.17",
    ),

    "a_18_5": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 4 п.3.4.4.5",
    ),

    "a_21_7": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения №8 п.9.1",
    ),

    "a_21_8": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения №8 п.9.2",
    ),

    "a_21_9": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения №8 п.9.3",
    ),

    "a_22_5_1": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.1",
    ),

    "a_22_5_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.2",
    ),

    "a_22_5_3": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.3",
    ),

    "a_22_5_4": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.4",
    ),

    "a_22_5_5": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.5",
    ),

    "a_22_5_6_1": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.6.1",
    ),

    "a_22_5_6_2": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.6.2",
    ),

    "a_22_5_6_3": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.9.8.6.3",
    ),

    "a_26_12": conclusion_text(
        "Соответствует требованиям",
        "ТР ТС 018/2011",
        "Приложения N 8 п.10.12",
    ),
}


def build_dynamic_result_values(protocol, measurement, light):
    values = {}

    fuel_type = getattr(measurement, "fuel_type", None)
    tire_season = getattr(protocol, "tire_season", None)
    has_spikes = getattr(protocol, "has_spikes", None)

    front_fog_present = is_positive_count(getattr(light, "front_fog_count", None))
    rear_fog_count = getattr(light, "rear_fog_count", None)
    rear_fog_present = is_positive_count(rear_fog_count)
    daytime_running_present = is_positive_count(
        getattr(light, "daytime_running_light_count", None)
    )

    parking_light_present = (
            is_positive_count(getattr(light, "parking_light_count", None))
            or is_positive_count(getattr(light, "rear_parking_light_count", None))
    )

    adaptive_front_lighting_present = is_positive_count(
        getattr(light, "adaptive_front_lighting_count", None)
    )

    washer_present = is_true(getattr(light, "headlight_washer_present", None))

    # А.3.2 — кнопка вызова экстренных оперативных служб / ГЛОНАСС
    add_result_pair(
        values,
        "result_a_3_2",
        is_true(getattr(measurement, "glonass_button_present", None)),
        CONCLUSIONS["a_3_2"],
    )

    # А.6.5 — блокировка рулевого управления
    add_result_pair(
        values,
        "result_a_6_5",
        is_true(getattr(measurement, "steering_lock_present", None)),
        CONCLUSIONS["a_6_5"],
    )

    # А.8.7 — адаптивная система переднего освещения или омыватели фар
    add_result_pair(
        values,
        "result_a_8_7",
        adaptive_front_lighting_present or washer_present,
        CONCLUSIONS["a_8_7"],
    )

    # А.8.10.3 — передние ПТФ
    add_result_pair(
        values,
        "result_a_8_10_3",
        front_fog_present,
        CONCLUSIONS["a_8_10_3"],
    )

    # А.8.13.1 — задние ПТФ
    if rear_fog_count == 1:
        add_result_pair(
            values,
            "result_a_8_13_1",
            True,
            CONCLUSIONS["a_8_13_1"],
        )
    elif rear_fog_count is None:
        add_direct_result_pair(
            values,
            "result_a_8_13_1",
            "не указано",
            "-",
        )
    else:
        reason = (
            "в ТС отсутствуют задние противотуманные фонари"
            if rear_fog_count == 0
            else "в ТС имеется два задних противотуманных фонаря"
        )
        add_direct_result_pair(
            values,
            "result_a_8_13_1",
            f"не применяется ({reason})",
            "-",
        )

    # А.8.20.3 — омыватели фар
    add_result_pair(
        values,
        "result_a_8_20_3",
        washer_present,
        CONCLUSIONS["a_8_20_3"],
    )

    # А.8.20.8 — передние ПТФ
    add_result_pair(
        values,
        "result_a_8_20_8",
        front_fog_present,
        CONCLUSIONS["a_8_20_8"],
    )

    # А.8.24.1–А.8.24.3 — задние ПТФ
    add_result_pair(
        values,
        "result_a_8_24_1",
        rear_fog_present,
        CONCLUSIONS["a_8_24_1"],
    )
    add_result_pair(
        values,
        "result_a_8_24_2",
        rear_fog_present,
        CONCLUSIONS["a_8_24_2"],
    )
    add_result_pair(
        values,
        "result_a_8_24_3",
        rear_fog_present,
        CONCLUSIONS["a_8_24_3"],
    )

    # А.8.25 — стояночные огни
    add_result_pair(
        values,
        "result_a_8_25",
        parking_light_present,
        CONCLUSIONS["a_8_25"],
    )

    # А.8.27 — дневные ходовые огни
    add_result_pair(
        values,
        "result_a_8_27",
        daytime_running_present,
        CONCLUSIONS["a_8_27"],
    )

    # А.10.5 — зимние шины
    add_result_pair(
        values,
        "result_a_10_5",
        tire_season == "winter",
        CONCLUSIONS["a_10_5"],
    )

    # А.10.6 — шипы
    add_result_pair(
        values,
        "result_a_10_6",
        tire_season == "winter" and has_spikes is True,
        CONCLUSIONS["a_10_6"],
    )

    # А.16.17 — подножки
    add_result_pair(
        values,
        "result_a_16_17",
        is_true(getattr(measurement, "steps_present", None)),
        CONCLUSIONS["a_16_17"],
    )

    # А.18.5 — открывающаяся крыша
    add_result_pair(
        values,
        "result_a_18_5",
        is_true(getattr(measurement, "opening_roof_present", None)),
        CONCLUSIONS["a_18_5"],
    )

    # А.21.7–А.21.9 — сначала исключаем неподходящий тип двигателя,
    # затем проверяем минимальный пробег.
    mileage = decimal_value(getattr(measurement, "mileage_km", None))

    if fuel_type == "diesel":
        add_direct_result_pair(
            values,
            "result_a_21_7",
            "не применяется (ТС оборудовано дизельным двигателем)",
            "-",
        )
    elif fuel_type == "electric":
        add_direct_result_pair(
            values,
            "result_a_21_7",
            "не применяется (ТС оборудовано только электродвигателем)",
            "-",
        )
    elif mileage is None:
        add_direct_result_pair(values, "result_a_21_7", "не указано", "-")
    elif mileage < 3000:
        add_direct_result_pair(
            values,
            "result_a_21_7",
            "не применяется (пробег ТС менее 3000 км)",
            "-",
        )
    elif is_fuel_petrol_like(fuel_type):
        add_result_pair(
            values,
            "result_a_21_7",
            True,
            CONCLUSIONS["a_21_7"],
        )
    else:
        add_direct_result_pair(values, "result_a_21_7", "не указано", "-")

    if is_fuel_petrol_like(fuel_type):
        add_direct_result_pair(
            values,
            "result_a_21_8",
            "не применяется (ТС оборудовано бензиновым двигателем)",
            "-",
        )
    elif fuel_type == "electric":
        add_direct_result_pair(
            values,
            "result_a_21_8",
            "не применяется (ТС оборудовано только электродвигателем)",
            "-",
        )
    elif mileage is None:
        add_direct_result_pair(values, "result_a_21_8", "не указано", "-")
    elif mileage < 3000:
        add_direct_result_pair(
            values,
            "result_a_21_8",
            "не применяется (пробег ТС менее 3000 км)",
            "-",
        )
    elif is_fuel_diesel(fuel_type):
        add_result_pair(
            values,
            "result_a_21_8",
            True,
            CONCLUSIONS["a_21_8"],
        )
    else:
        add_direct_result_pair(values, "result_a_21_8", "не указано", "-")

    if fuel_type == "electric":
        add_direct_result_pair(
            values,
            "result_a_21_9",
            "не применяется (ТС оборудовано только электродвигателем)",
            "-",
        )
    elif mileage is None:
        add_direct_result_pair(
            values,
            "result_a_21_9",
            "не указано",
            "-",
        )

    elif mileage < 3000:
        add_direct_result_pair(
            values,
            "result_a_21_9",
            f"менее 3000 км. Пробег: {fmt_num(mileage, 0)} км",
            "-",
        )

    else:
        add_direct_result_pair(
            values,
            "result_a_21_9",
            f"не менее 3000 км. Пробег: {fmt_num(mileage, 0)} км",
            CONCLUSIONS["a_21_9"],
        )
        if is_fuel_diesel(fuel_type):
            average = calc_light_absorption_average(measurement)
            status = f"{fmt_num(average, 3)} м-1" if average is not None else "соответствует"
            add_direct_result_pair(
                values,
                "result_a_21_8",
                status,
                CONCLUSIONS["a_21_8"],
            )

    # А.22.5.* — газобаллонное оборудование.
    gas_equipment_present = is_true(
        getattr(measurement, "gas_equipment_present", None)
    )

    for suffix in [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6_1",
        "6_2",
        "6_3",
    ]:
        conclusion_key = f"a_22_5_{suffix}"
        result_key = f"result_a_22_5_{suffix}"

        add_result_pair(
            values,
            result_key,
            gas_equipment_present,
            CONCLUSIONS[conclusion_key],
        )

    # А.26.12 — запасное колесо
    add_result_pair(
        values,
        "result_a_26_12",
        is_true(getattr(measurement, "spare_wheel_present", None)),
        CONCLUSIONS["a_26_12"],
    )

    return values


# =========================
# Условные строки световых приборов
# =========================

def build_light_device_row_values(light):
    """
    Значения для условных строк световых приборов в таблице.

    Использование в DOCX:
    {%tr if parking_light_present %}
    строка с цветом и количеством
    {%tr endif %}

    {%tr if not parking_light_present %}
    строка "не применяется" / "-"
    {%tr endif %}

    Важно:
    Если count = None, "", "-", 0, то *_present = False.
    """

    return {
        # Общий текст заключения для строки, когда прибор есть
        "light_device_conclusion": CONCLUSIONS["a_8_1"],

        # Фары ближнего света
        "low_beam_present": is_positive_count(getattr(light, "low_beam_count", None)),
        "low_beam_color_value": normalize_light_color(
            getattr(light, "low_beam_color", None)
        ),
        "low_beam_count_value": value_or_dash(
            fmt_int(getattr(light, "low_beam_count", None))
        ),

        # Фары дальнего света
        "high_beam_present": is_positive_count(getattr(light, "high_beam_count", None)),
        "high_beam_color_value": normalize_light_color(
            getattr(light, "high_beam_color", None)
        ),
        "high_beam_count_value": value_or_dash(
            fmt_int(getattr(light, "high_beam_count", None))
        ),

        # Передние противотуманные фары
        "front_fog_present": is_positive_count(getattr(light, "front_fog_count", None)),
        "front_fog_color_value": normalize_light_color(
            getattr(light, "front_fog_color", None)
        ),
        "front_fog_count_value": value_or_dash(
            fmt_int(getattr(light, "front_fog_count", None))
        ),

        # Фонари заднего хода
        "reverse_light_present": is_positive_count(getattr(light, "reverse_light_count", None)),
        "reverse_light_color_value": normalize_light_color(
            getattr(light, "reverse_light_color", None)
        ),
        "reverse_light_count_value": value_or_dash(
            fmt_int(getattr(light, "reverse_light_count", None))
        ),

        # Указатели поворота
        "turn_signal_present": is_positive_count(getattr(light, "turn_signal_count", None)),
        "turn_signal_color_value": normalize_light_color(
            getattr(light, "turn_signal_color", None)
        ),
        "turn_signal_count_value": value_or_dash(
            fmt_int(getattr(light, "turn_signal_count", None))
        ),

        # Передние габаритные огни
        "front_position_light_present": is_positive_count(
            getattr(light, "front_position_light_count", None)
        ),
        "front_position_light_color_value": normalize_light_color(
            getattr(light, "front_position_light_color", None)
        ),
        "front_position_light_count_value": value_or_dash(
            fmt_int(getattr(light, "front_position_light_count", None))
        ),

        # Задние габаритные огни
        "rear_position_light_present": is_positive_count(
            getattr(light, "rear_position_light_count", None)
        ),
        "rear_position_light_color_value": normalize_light_color(
            getattr(light, "rear_position_light_color", None)
        ),
        "rear_position_light_count_value": value_or_dash(
            fmt_int(getattr(light, "rear_position_light_count", None))
        ),

        # Основной сигнал торможения
        "main_brake_signal_present": is_positive_count(
            getattr(light, "main_brake_signal_count", None)
        ),
        "main_brake_signal_color_value": normalize_light_color(
            getattr(light, "main_brake_signal_color", None)
        ),
        "main_brake_signal_count_value": value_or_dash(
            fmt_int(getattr(light, "main_brake_signal_count", None))
        ),

        # Дополнительный сигнал торможения
        "additional_brake_signal_present": is_positive_count(
            getattr(light, "additional_brake_signal_count", None)
        ),
        "additional_brake_signal_color_value": normalize_light_color(
            getattr(light, "additional_brake_signal_color", None)
        ),
        "additional_brake_signal_count_value": value_or_dash(
            fmt_int(getattr(light, "additional_brake_signal_count", None))
        ),

        # Задние противотуманные фонари
        "rear_fog_present": is_positive_count(getattr(light, "rear_fog_count", None)),
        "rear_fog_color_value": normalize_light_color(
            getattr(light, "rear_fog_color", None)
        ),
        "rear_fog_count_value": value_or_dash(
            fmt_int(getattr(light, "rear_fog_count", None))
        ),

        # Подсветка государственного номера
        "plate_light_present": is_positive_count(getattr(light, "plate_light_count", None)),
        "plate_light_color_value": normalize_light_color(
            getattr(light, "plate_light_color", None)
        ),
        "plate_light_count_value": value_or_dash(
            fmt_int(getattr(light, "plate_light_count", None))
        ),

        # Дневные ходовые огни
        "daytime_running_light_present": is_positive_count(
            getattr(light, "daytime_running_light_count", None)
        ),
        "daytime_running_light_color_value": normalize_light_color(
            getattr(light, "daytime_running_light_color", None)
        ),
        "daytime_running_light_count_value": value_or_dash(
            fmt_int(getattr(light, "daytime_running_light_count", None))
        ),

        # Передние стояночные огни
        "parking_light_present": is_positive_count(
            getattr(light, "parking_light_count", None)
        ),
        "parking_light_color_value": normalize_light_color(
            getattr(light, "parking_light_color", None)
        ),
        "parking_light_count_value": value_or_dash(
            fmt_int(getattr(light, "parking_light_count", None))
        ),

        # Задние стояночные огни
        "rear_parking_light_present": is_positive_count(
            getattr(light, "rear_parking_light_count", None)
        ),
        "rear_parking_light_color_value": normalize_light_color(
            getattr(light, "rear_parking_light_color", None)
        ),
        "rear_parking_light_count_value": value_or_dash(
            fmt_int(getattr(light, "rear_parking_light_count", None))
        ),

        # Адаптивная система переднего освещения
        "adaptive_front_lighting_present": is_positive_count(
            getattr(light, "adaptive_front_lighting_count", None)
        ),
        "adaptive_front_lighting_color_value": normalize_light_color(
            getattr(light, "adaptive_front_lighting_color", None)
        ),
        "adaptive_front_lighting_count_value": value_or_dash(
            fmt_int(getattr(light, "adaptive_front_lighting_count", None))
        ),
    }


# =========================
# Передние ПТФ: А.8.10.1–А.8.10.3
# =========================

def build_front_fog_values(light):
    front_fog_present = is_positive_count(
        getattr(light, "front_fog_count", None)
    )

    fog_light_left_distance = getattr(light, "fog_light_left_distance_mm", None)
    fog_light_right_distance = getattr(light, "fog_light_right_distance_mm", None)

    fog_light_upper_point = getattr(light, "fog_light_upper_point_mm", None)
    fog_light_lower_point = getattr(light, "fog_light_lower_point_mm", None)

    left_distance = value_with_unit_or_dash(
        front_fog_present,
        fog_light_left_distance,
        2,
        "мм",
    )
    right_distance = value_with_unit_or_dash(
        front_fog_present,
        fog_light_right_distance,
        2,
        "мм",
    )

    left_distance_u = uncertainty_with_unit_or_dash(
        front_fog_present,
        fog_light_left_distance,
        "0,29",
        "мм",
    )
    right_distance_u = uncertainty_with_unit_or_dash(
        front_fog_present,
        fog_light_right_distance,
        "0,29",
        "мм",
    )

    lower_point = value_with_unit_or_dash(
        front_fog_present,
        fog_light_lower_point,
        2,
        "мм",
    )
    upper_point = value_with_unit_or_dash(
        front_fog_present,
        fog_light_upper_point,
        2,
        "мм",
    )

    lower_point_u = uncertainty_with_unit_or_dash(
        front_fog_present,
        fog_light_lower_point,
        "0,29",
        "мм",
    )
    upper_point_u = uncertainty_with_unit_or_dash(
        front_fog_present,
        fog_light_upper_point,
        "0,29",
        "мм",
    )

    return {
        "fog_light_left_distance_8_10_1": left_distance,
        "fog_light_right_distance_8_10_1": right_distance,
        "u_fog_light_left_distance_8_10_1": left_distance_u,
        "u_fog_light_right_distance_8_10_1": right_distance_u,

        "fog_light_lower_point_8_10_2": lower_point,
        "fog_light_upper_point_8_10_2": upper_point,
        "u_fog_light_lower_point_8_10_2": lower_point_u,
        "u_fog_light_upper_point_8_10_2": upper_point_u,

        "full_result_a_8_10_1": build_full_result_text(
            front_fog_present,
            CONCLUSIONS["a_8_10_1"],
            "не более 400 мм",
            f"Левая {left_distance} ± {left_distance_u}\n"
            f"Правая {right_distance} ± {right_distance_u}",
              not_applicable_text="не применяется (в ТС отсутствуют передние противотуманные фары)",
        ),

        "full_result_a_8_10_2": build_full_result_text(
            front_fog_present,
            CONCLUSIONS["a_8_10_2"],
            "не менее 250 мм и не более 800 мм",
            f"Левая нижняя граница: {lower_point} ± {lower_point_u}\n"
            f"Левая верхняя граница: {upper_point} ± {upper_point_u}\n"
            f"Правая нижняя граница: {lower_point} ± {lower_point_u}\n"
            f"Правая верхняя граница: {upper_point} ± {upper_point_u}",
                not_applicable_text="не применяется (в ТС отсутствуют передние противотуманные фары)",
        ),

        "full_result_a_8_10_3": build_full_result_text(
            front_fog_present,
            CONCLUSIONS["a_8_10_3"],
                not_applicable_text="не применяется (в ТС отсутствуют передние противотуманные фары)",
        ),
    }


# =========================
# Задние ПТФ: А.8.13.2
# =========================

def build_rear_fog_values(light):
    rear_fog_present = is_positive_count(
        getattr(light, "rear_fog_count", None)
    )

    rear_fog_upper_point = getattr(light, "rear_fog_upper_point_mm", None)
    rear_fog_lower_point = getattr(light, "rear_fog_lower_point_mm", None)

    upper_point = value_with_unit_or_dash(
        rear_fog_present,
        rear_fog_upper_point,
        2,
        "мм",
    )

    lower_point = value_with_unit_or_dash(
        rear_fog_present,
        rear_fog_lower_point,
        2,
        "мм",
    )

    upper_point_u = uncertainty_with_unit_or_dash(
        rear_fog_present,
        rear_fog_upper_point,
        "0,29",
        "мм",
    )

    lower_point_u = uncertainty_with_unit_or_dash(
        rear_fog_present,
        rear_fog_lower_point,
        "0,29",
        "мм",
    )

    return {
        "rear_fog_upper_point_8_13_2": upper_point,
        "rear_fog_lower_point_8_13_2": lower_point,
        "u_rear_fog_upper_point_8_13_2": upper_point_u,
        "u_rear_fog_lower_point_8_13_2": lower_point_u,

        "full_result_a_8_13_2": build_full_result_text(
            rear_fog_present,
            CONCLUSIONS["a_8_13_2"],
            "не менее 250 мм и не более 1000 мм",
            f"Верхняя граница: {upper_point} ± {upper_point_u}\n"
            f"Нижняя граница: {lower_point} ± {lower_point_u}",
              not_applicable_text="не применяется (в ТС отсутствуют задние противотуманные фонари)",
        ),
    }


# =========================
# Сезонная глубина протектора
# =========================

def build_tire_depth_values(protocol, measurement):
    tire_depth_fl_mm = getattr(measurement, "tire_depth_fl_mm", None)
    tire_depth_fr_mm = getattr(measurement, "tire_depth_fr_mm", None)
    tire_depth_rl_mm = getattr(measurement, "tire_depth_rl_mm", None)
    tire_depth_rr_mm = getattr(measurement, "tire_depth_rr_mm", None)

    is_summer = protocol.tire_season == "summer"
    is_winter = protocol.tire_season == "winter"

    summer_fl = get_tire_depth_value(protocol, tire_depth_fl_mm, "summer")
    summer_fr = get_tire_depth_value(protocol, tire_depth_fr_mm, "summer")
    summer_rl = get_tire_depth_value(protocol, tire_depth_rl_mm, "summer")
    summer_rr = get_tire_depth_value(protocol, tire_depth_rr_mm, "summer")

    summer_u_fl = get_tire_depth_uncertainty(protocol, tire_depth_fl_mm, "summer")
    summer_u_fr = get_tire_depth_uncertainty(protocol, tire_depth_fr_mm, "summer")
    summer_u_rl = get_tire_depth_uncertainty(protocol, tire_depth_rl_mm, "summer")
    summer_u_rr = get_tire_depth_uncertainty(protocol, tire_depth_rr_mm, "summer")

    winter_fl = get_tire_depth_value(protocol, tire_depth_fl_mm, "winter")
    winter_fr = get_tire_depth_value(protocol, tire_depth_fr_mm, "winter")
    winter_rl = get_tire_depth_value(protocol, tire_depth_rl_mm, "winter")
    winter_rr = get_tire_depth_value(protocol, tire_depth_rr_mm, "winter")

    winter_u_fl = get_tire_depth_uncertainty(protocol, tire_depth_fl_mm, "winter")
    winter_u_fr = get_tire_depth_uncertainty(protocol, tire_depth_fr_mm, "winter")
    winter_u_rl = get_tire_depth_uncertainty(protocol, tire_depth_rl_mm, "winter")
    winter_u_rr = get_tire_depth_uncertainty(protocol, tire_depth_rr_mm, "winter")

    return {
        # А.10.7.2 — летние шины
        "tire_depth_fl_10_7_2": summer_fl,
        "tire_depth_fr_10_7_2": summer_fr,
        "tire_depth_rl_10_7_2": summer_rl,
        "tire_depth_rr_10_7_2": summer_rr,

        "u_tire_depth_fl_10_7_2": summer_u_fl,
        "u_tire_depth_fr_10_7_2": summer_u_fr,
        "u_tire_depth_rl_10_7_2": summer_u_rl,
        "u_tire_depth_rr_10_7_2": summer_u_rr,

        "full_result_a_10_7_2": build_tire_depth_result_text(
            is_summer,
            CONCLUSIONS["a_10_7_2"],
            "не менее 1,6 мм",
            [
                ("Переднее левое", summer_fl, summer_u_fl),
                ("Переднее правое", summer_fr, summer_u_fr),
                ("Заднее левое", summer_rl, summer_u_rl),
                ("Заднее правое", summer_rr, summer_u_rr),
            ],
        ),

        # А.10.7.3 — зимние шины
        "tire_depth_fl_10_7_3": winter_fl,
        "tire_depth_fr_10_7_3": winter_fr,
        "tire_depth_rl_10_7_3": winter_rl,
        "tire_depth_rr_10_7_3": winter_rr,

        "u_tire_depth_fl_10_7_3": winter_u_fl,
        "u_tire_depth_fr_10_7_3": winter_u_fr,
        "u_tire_depth_rl_10_7_3": winter_u_rl,
        "u_tire_depth_rr_10_7_3": winter_u_rr,

        "full_result_a_10_7_3": build_tire_depth_result_text(
            is_winter,
            CONCLUSIONS["a_10_7_3"],
            "не должно быть менее 4,0 мм",
            [
                ("Переднее левое", winter_fl, winter_u_fl),
                ("Переднее правое", winter_fr, winter_u_fr),
                ("Заднее левое", winter_rl, winter_u_rl),
                ("Заднее правое", winter_rr, winter_u_rr),
            ],
                not_applicable_text="не применяется (на ТС установлены летние шины)",
        ),
    }


# =========================
# Светозащитная полоса: А.11.8
# =========================

def build_sun_strip_values(measurement):
    sun_strip_width = getattr(measurement, "sun_strip_width_mm", None)
    sun_strip_present = is_positive_count(sun_strip_width)

    if sun_strip_present:
        sun_strip_value = f"{fmt_num(sun_strip_width, 2)} мм"
        sun_strip_uncertainty = "0,19 мм"
        full_result = build_full_result_text(
            True,
            CONCLUSIONS["a_11_8_sun_strip"],
            "не более 140,00 мм",
            f"{fmt_num(sun_strip_width, 2)} мм ± 0,19 мм",
        )
    else:
        sun_strip_value = "отсутствие"
        sun_strip_uncertainty = "-"
        full_result = "-"

    return {
        "sun_strip_width_11_8": sun_strip_value,
        "u_sun_strip_width_11_8": sun_strip_uncertainty,
        "full_result_a_11_8_sun_strip": full_result,
    }


# =========================
# Экология: А.21.7–А.21.9
# =========================

def build_eco_values(protocol, measurement):
    fuel_type = getattr(measurement, "fuel_type", None)
    mileage = decimal_value(getattr(measurement, "mileage_km", None))

    mileage_is_3000_or_more = mileage is not None and mileage >= 3000

    co_applicable = mileage_is_3000_or_more and is_fuel_petrol_like(fuel_type)
    diesel_applicable = mileage_is_3000_or_more and is_fuel_diesel(fuel_type)

    if fuel_type == "diesel":
        co_not_applicable_text = "не применяется (ТС оборудовано дизельным двигателем)"
    elif fuel_type == "electric":
        co_not_applicable_text = "не применяется (ТС оборудовано только электродвигателем)"
    elif mileage is not None and mileage < 3000:
        co_not_applicable_text = "не применяется (пробег ТС менее 3000 км)"
    else:
        co_not_applicable_text = None

    if is_fuel_petrol_like(fuel_type):
        diesel_not_applicable_text = "не применяется (ТС оборудовано бензиновым двигателем)"
    elif fuel_type == "electric":
        diesel_not_applicable_text = "не применяется (ТС оборудовано только электродвигателем)"
    elif mileage is not None and mileage < 3000:
        diesel_not_applicable_text = "не применяется (пробег ТС менее 3000 км)"
    else:
        diesel_not_applicable_text = None

    co_min = getattr(measurement, "co_min_pct", None)
    co_max = getattr(measurement, "co_max_pct", None)

    light_absorption_average = calc_light_absorption_average(measurement)

    if fuel_type == "electric":
        mileage_21_9 = "не применяется (ТС оборудовано только электродвигателем)"
    elif mileage is None:
        mileage_21_9 = "не указано"
    elif mileage >= 3000:
        mileage_21_9 = "не менее 3000 км"
    else:
        mileage_21_9 = "менее 3000 км"

    return {
        # А.21.7 — CO
        "co_min_21_7": value_if_applicable(co_applicable, co_min, 2),
        "co_max_21_7": value_if_applicable(co_applicable, co_max, 2),

        "co_min_21_7_with_unit": value_with_unit_or_dash(
            co_applicable,
            co_min,
            2,
            "%",
        ),
        "co_max_21_7_with_unit": value_with_unit_or_dash(
            co_applicable,
            co_max,
            2,
            "%",
        ),

        "u_co_min_21_7": uncertainty_if_applicable(
            co_applicable,
            co_min,
            "0,19",
        ),
        "u_co_max_21_7": uncertainty_if_applicable(
            co_applicable,
            co_max,
            "0,19",
        ),

        "co_min_result_21_7": result_with_uncertainty_if_applicable(
            co_applicable,
            co_min,
            "0,19",
            2,
            "%",
        ),
        "co_max_result_21_7": result_with_uncertainty_if_applicable(
            co_applicable,
            co_max,
            "0,19",
            2,
            "%",
        ),

        "full_result_a_21_7": build_full_result_text(
            co_applicable,
            CONCLUSIONS["a_21_7"],
            "Минимальная - не более 0,3 %\nПовышенная - не более 0,2 %",
            f"Минимальная - {result_with_uncertainty_if_applicable(co_applicable, co_min, '0,19', 2, '%')}\n"
            f"Повышенная - {result_with_uncertainty_if_applicable(co_applicable, co_max, '0,19', 2, '%')}",
            co_not_applicable_text,
        ),

        # А.21.8 — дымность дизеля
        "light_absorption_avg_21_8": value_if_applicable(
            diesel_applicable,
            light_absorption_average,
            3,
        ),
        "light_absorption_avg_21_8_with_unit": value_with_unit_or_dash(
            diesel_applicable,
            light_absorption_average,
            3,
            "м-1",
        ),
        "u_light_absorption_avg_21_8": uncertainty_if_applicable(
            diesel_applicable,
            light_absorption_average,
            "0,048",
        ),
        "light_absorption_result_21_8": result_with_uncertainty_if_applicable(
            diesel_applicable,
            light_absorption_average,
            "0,048",
            3,
            "м-1",
        ),

        "full_result_a_21_8": build_full_result_text(
            diesel_applicable,
            CONCLUSIONS["a_21_8"],
            "не более 1,5 м-1",
            result_with_uncertainty_if_applicable(
                diesel_applicable,
                light_absorption_average,
                "0,048",
                3,
                "м-1",
            ),
            diesel_not_applicable_text,
        ),

        # А.21.9 — пробег
        "mileage_21_9": mileage_21_9,
        "full_result_a_21_9": (
            CONCLUSIONS["a_21_9"]
            if fuel_type != "electric" and mileage is not None and mileage >= 3000
            else "не применяется (ТС оборудовано только электродвигателем)"
            if fuel_type == "electric"
            else "-"
        ),
    }


# =========================
# Фото
# =========================

def get_photo_path(protocol, photo_type):
    photo = protocol.photos.filter(photo_type=photo_type).order_by("sort_order", "id").first()

    if not photo or not photo.file_path:
        return ""

    raw_path = str(photo.file_path)

    if raw_path.startswith("http://") or raw_path.startswith("https://"):
        return ""

    path = Path(raw_path)

    if path.is_absolute() and path.exists():
        return str(path)

    media_path = Path(settings.MEDIA_ROOT) / raw_path

    if media_path.exists():
        return str(media_path)

    base_path = Path(settings.BASE_DIR) / raw_path

    if base_path.exists():
        return str(base_path)

    return ""


def build_photo_values(protocol):
    return {
        "photo_stand_test": get_photo_path(protocol, "stand_test_photo"),
        "photo_gas_test": get_photo_path(protocol, "gas_test_photo"),
        "photo_noise_test": get_photo_path(protocol, "noise_test_photo"),
    }


# =========================
# Главная сборка context для DOCX
# =========================

def build_protocol_docx_context(protocol):
    measurement = get_related(protocol, "measurement")
    brake = get_related(protocol, "brake")
    light = get_related(protocol, "light")
    test_conditions = get_related(protocol, "test_conditions")
    road_conditions = get_related(protocol, "road_conditions")
    power_supply = get_related(protocol, "power_supply")

    context = {
        # =========================
        # Общие данные
        # =========================
        "protocol_number": fmt_text(protocol.protocol_number),
        "protocol_date": fmt_date(protocol.protocol_date),
        "protocol_page_count": "",

        # =========================
        # Таблица 1.1
        # =========================
        "brand_name": fmt_text(protocol.brand_name).upper(),
        "commercial_name": fmt_text(protocol.commercial_name).upper(),
        "body_type": fmt_text(protocol.body_type),
        "vin": fmt_text(protocol.vin),
        "registration_number": fmt_text(protocol.registration_number, "отсутствует"),
        "vehicle_category": fmt_text(protocol.vehicle_category),
        "owner_info": build_owner_info(protocol),
        "owner_name": fmt_text(protocol.owner_name),

        "owner_last_name": fmt_text(getattr(protocol, "owner_last_name", None)),
        "owner_first_name": fmt_text(getattr(protocol, "owner_first_name", None)),
        "owner_middle_name": fmt_text(getattr(protocol, "owner_middle_name", None)),
        "owner_full_name": fmt_text(build_owner_full_name(protocol)),

        "owner_address": fmt_text(protocol.owner_address),
        "owner_phone": fmt_text(protocol.owner_phone),
        "manufacturer_info": build_manufacturer_info(protocol),
        "inspection_place": fmt_text(protocol.inspection_place, DEFAULT_INSPECTION_PLACE),

        # =========================
        # Условия испытаний
        # =========================
        "ambient_temperature_c": fmt_num(
            getattr(test_conditions, "ambient_temperature_c", None),
            1,
        ),
        "relative_humidity_pct": fmt_num(
            getattr(test_conditions, "relative_humidity_pct", None),
            1,
        ),
        "atmospheric_pressure_kpa": fmt_num(
            getattr(test_conditions, "atmospheric_pressure_kpa", None),
            2,
        ),

        "road_ambient_temperature_c": fmt_num(
            getattr(road_conditions, "road_ambient_temperature_c", None),
            1,
        ),
        "road_relative_humidity_pct": fmt_num(
            getattr(road_conditions, "road_relative_humidity_pct", None),
            1,
        ),

        "frequency_hz": fmt_num(getattr(power_supply, "frequency_hz", None), 1),
        "phase_a_n_voltage_v": fmt_num(getattr(power_supply, "phase_a_n_voltage_v", None), 1),
        "phase_b_n_voltage_v": fmt_num(getattr(power_supply, "phase_b_n_voltage_v", None), 1),
        "phase_c_n_voltage_v": fmt_num(getattr(power_supply, "phase_c_n_voltage_v", None), 1),
        "phase_ab_voltage_v": fmt_num(getattr(power_supply, "phase_ab_voltage_v", None), 1),
        "phase_bc_voltage_v": fmt_num(getattr(power_supply, "phase_bc_voltage_v", None), 1),
        "phase_ac_voltage_v": fmt_num(getattr(power_supply, "phase_ac_voltage_v", None), 1),

        # =========================
        # Автомобиль
        # =========================
        "wheel_marking_front": fmt_text(protocol.wheel_marking_front),
        "wheel_marking_rear": fmt_text(protocol.wheel_marking_rear),
        "tire_season_label": label(TIRE_SEASON_LABELS, protocol.tire_season),
        "has_spikes_label": fmt_bool(protocol.has_spikes),
        "manufacture_year": fmt_int(protocol.manufacture_year),
        "color": fmt_text(protocol.color),

        # =========================
        # Measurement
        # =========================
        "wheel_formula_label": label(
            WHEEL_FORMULA_LABELS,
            getattr(measurement, "wheel_formula", None),
        ),
        "mufflers_count": fmt_int(getattr(measurement, "mufflers_count", None)),
        "seats_count": fmt_text(getattr(measurement, "seats_count", None)),
        "steps_present_label": fmt_bool(
            getattr(measurement, "steps_present", None),
            "Наличие",
            "Отсутствие",
        ),

        "engine_model": fmt_text(getattr(measurement, "engine_model", None)),
        "engine_power_kw": fmt_num(getattr(measurement, "engine_power_kw", None), 0),
        "engine_layout_label": label(
            ENGINE_LAYOUT_LABELS,
            getattr(measurement, "engine_layout", None),
        ),
        "cylinder_layout_label": label(
            CYLINDER_LAYOUT_LABELS,
            getattr(measurement, "cylinder_layout", None),
        ),
        "cylinders_count": fmt_int(getattr(measurement, "cylinders_count", None)),
        "fuel_type_label": label(
            FUEL_TYPE_LABELS,
            getattr(measurement, "fuel_type", None),
        ),
        "turbo_present_label": fmt_bool(
            getattr(measurement, "turbo_present", None),
            "Наличие",
            "Отсутствие",
        ),

        "steering_booster_type_label": label(
            STEERING_BOOSTER_LABELS,
            getattr(measurement, "steering_booster_type", None),
        ),
        "transmission_type_label": label(
            TRANSMISSION_LABELS,
            getattr(measurement, "transmission_type", None),
        ),

        "tire_depth_fl_mm": fmt_num(getattr(measurement, "tire_depth_fl_mm", None), 1),
        "tire_depth_fr_mm": fmt_num(getattr(measurement, "tire_depth_fr_mm", None), 1),
        "tire_depth_rl_mm": fmt_num(getattr(measurement, "tire_depth_rl_mm", None), 1),
        "tire_depth_rr_mm": fmt_num(getattr(measurement, "tire_depth_rr_mm", None), 1),

        "bumper_bends_to_body_label": fmt_bool(
            getattr(measurement, "bumper_bends_to_body", None)
        ),
        "bumper_to_body_distance_mm": fmt_num(
            getattr(measurement, "bumper_to_body_distance_mm", None),
            2,
        ),
        "opening_roof_present_label": fmt_bool(
            getattr(measurement, "opening_roof_present", None)
        ),

        "protruding_elements_doors_mm": fmt_num(
            getattr(measurement, "protruding_elements_doors_mm", None),
            2,
        ),
        "protruding_elements_other_mm": fmt_num(
            getattr(measurement, "protruding_elements_other_mm", None),
            2,
        ),

        "glass_transparency_right_pct": fmt_num(
            getattr(measurement, "glass_transparency_right_pct", None),
            1,
        ),
        "glass_transparency_left_pct": fmt_num(
            getattr(measurement, "glass_transparency_left_pct", None),
            1,
        ),
        "glass_transparency_windshield_pct": fmt_num(
            getattr(measurement, "glass_transparency_windshield_pct", None),
            1,
        ),
        "sun_strip_width_mm": fmt_num(
            getattr(measurement, "sun_strip_width_mm", None),
            2,
        ),

        "steering_backlash_deg": fmt_num(
            getattr(measurement, "steering_backlash_deg", None),
            1,
        ),

        "speed_by_speedometer_kmh": fmt_num(
            getattr(measurement, "speed_by_speedometer_kmh", None),
            1,
        ),
        "actual_speed_kmh": fmt_num(
            getattr(measurement, "actual_speed_kmh", None),
            1,
        ),

        "exhaust_noise_constant_db": fmt_num(
            getattr(measurement, "exhaust_noise_constant_db", None),
            1,
        ),
        "exhaust_noise_deceleration_db": fmt_num(
            getattr(measurement, "exhaust_noise_deceleration_db", None),
            1,
        ),

        "co_min_pct": fmt_num(getattr(measurement, "co_min_pct", None), 2),
        "co_max_pct": fmt_num(getattr(measurement, "co_max_pct", None), 2),

        "light_absorption_1": fmt_num(getattr(measurement, "light_absorption_1", None), 2),
        "light_absorption_2": fmt_num(getattr(measurement, "light_absorption_2", None), 2),
        "light_absorption_3": fmt_num(getattr(measurement, "light_absorption_3", None), 2),
        "light_absorption_4": fmt_num(getattr(measurement, "light_absorption_4", None), 2),
        "light_absorption_5": fmt_num(getattr(measurement, "light_absorption_5", None), 2),
        "light_absorption_6": fmt_num(getattr(measurement, "light_absorption_6", None), 2),

        "vehicle_length_mm": fmt_num(getattr(measurement, "vehicle_length_mm", None), 1),
        "vehicle_width_mm": fmt_num(getattr(measurement, "vehicle_width_mm", None), 1),
        "vehicle_height_mm": fmt_num(getattr(measurement, "vehicle_height_mm", None), 1),
        "vehicle_weight_kg": fmt_num(getattr(measurement, "vehicle_weight_kg", None), 0),
        "axle1_load_kg": fmt_num(getattr(measurement, "axle1_load_kg", None), 0),
        "axle2_load_kg": fmt_num(getattr(measurement, "axle2_load_kg", None), 0),
        "stand_axle1_load_kg": fmt_num(getattr(measurement, "stand_axle1_load_kg", None), 0),
        "stand_axle2_load_kg": fmt_num(getattr(measurement, "stand_axle2_load_kg", None), 0),

        "mileage_km": fmt_num(getattr(measurement, "mileage_km", None), 0),
        "spare_wheel_present_label": fmt_bool(
            getattr(measurement, "spare_wheel_present", None),
            "Наличие",
            "Отсутствие",
        ),
        "steering_lock_present_label": fmt_bool(
            getattr(measurement, "steering_lock_present", None),
            "Наличие",
            "Отсутствие",
        ),
        "gas_equipment_present_label": fmt_bool(
            getattr(measurement, "gas_equipment_present", None),
            "Наличие",
            "Отсутствие",
        ),
        "glonass_button_present_label": fmt_bool(
            getattr(measurement, "glonass_button_present", None),
            "соответствует",
            "не применяется",
        ),

        # =========================
        # Brake
        # =========================
        "service_brake_type_label": label(
            SERVICE_BRAKE_LABELS,
            getattr(brake, "service_brake_type", None),
        ),
        "parking_brake_type_label": label(
            PARKING_BRAKE_LABELS,
            getattr(brake, "parking_brake_type", None),
        ),

        "service_brake_control_force_axle1_n": fmt_num(
            getattr(brake, "service_brake_control_force_axle1_n", None),
            1,
        ),
        "service_brake_control_force_axle2_n": fmt_num(
            getattr(brake, "service_brake_control_force_axle2_n", None),
            1,
        ),
        "parking_brake_control_force_n": fmt_num(
            getattr(brake, "parking_brake_control_force_n", None),
            1,
        ),

        "axle_1_brake_difference_pct": fmt_num(
            getattr(brake, "axle_1_brake_difference_pct", None),
            1,
        ),
        "axle_2_brake_difference_pct": fmt_num(
            getattr(brake, "axle_2_brake_difference_pct", None),
            1,
        ),

        "service_brake_front_left_kn": fmt_num(
            getattr(brake, "service_brake_front_left_kn", None),
            2,
        ),
        "service_brake_front_right_kn": fmt_num(
            getattr(brake, "service_brake_front_right_kn", None),
            2,
        ),
        "service_brake_rear_left_kn": fmt_num(
            getattr(brake, "service_brake_rear_left_kn", None),
            2,
        ),
        "service_brake_rear_right_kn": fmt_num(
            getattr(brake, "service_brake_rear_right_kn", None),
            2,
        ),

        "parking_brake_left_kn": fmt_num(getattr(brake, "parking_brake_left_kn", None), 2),
        "parking_brake_right_kn": fmt_num(getattr(brake, "parking_brake_right_kn", None), 2),

        # =========================
        # Light
        # =========================
        "low_beam_count": fmt_int(getattr(light, "low_beam_count", None)),
        "low_beam_color": normalize_light_color(getattr(light, "low_beam_color", None)),

        "high_beam_count": fmt_int(getattr(light, "high_beam_count", None)),
        "high_beam_color": normalize_light_color(getattr(light, "high_beam_color", None)),

        "front_fog_count": fmt_int(getattr(light, "front_fog_count", None)),
        "front_fog_color": normalize_light_color(getattr(light, "front_fog_color", None)),

        "reverse_light_count": fmt_int(getattr(light, "reverse_light_count", None)),
        "reverse_light_color": normalize_light_color(getattr(light, "reverse_light_color", None)),

        "turn_signal_count": fmt_int(getattr(light, "turn_signal_count", None)),
        "turn_signal_color": normalize_light_color(getattr(light, "turn_signal_color", None)),

        "front_position_light_count": fmt_int(
            getattr(light, "front_position_light_count", None)
        ),
        "front_position_light_color": normalize_light_color(
            getattr(light, "front_position_light_color", None)
        ),

        "rear_position_light_count": fmt_int(
            getattr(light, "rear_position_light_count", None)
        ),
        "rear_position_light_color": normalize_light_color(
            getattr(light, "rear_position_light_color", None)
        ),

        "main_brake_signal_count": fmt_int(
            getattr(light, "main_brake_signal_count", None)
        ),
        "main_brake_signal_color": normalize_light_color(
            getattr(light, "main_brake_signal_color", None)
        ),

        "additional_brake_signal_count": fmt_int(
            getattr(light, "additional_brake_signal_count", None)
        ),
        "additional_brake_signal_color": normalize_light_color(
            getattr(light, "additional_brake_signal_color", None)
        ),

        "rear_fog_count": fmt_int(getattr(light, "rear_fog_count", None)),
        "rear_fog_color": normalize_light_color(getattr(light, "rear_fog_color", None)),

        "plate_light_count": fmt_int(getattr(light, "plate_light_count", None)),
        "plate_light_color": normalize_light_color(getattr(light, "plate_light_color", None)),

        "daytime_running_light_count": fmt_int(
            getattr(light, "daytime_running_light_count", None)
        ),
        "daytime_running_light_color": normalize_light_color(
            getattr(light, "daytime_running_light_color", None)
        ),

        "parking_light_count": fmt_int(getattr(light, "parking_light_count", None)),
        "parking_light_color": normalize_light_color(
            getattr(light, "parking_light_color", None)
        ),

        "rear_parking_light_count": fmt_int(
            getattr(light, "rear_parking_light_count", None)
        ),
        "rear_parking_light_color": normalize_light_color(
            getattr(light, "rear_parking_light_color", None)
        ),

        "adaptive_front_lighting_count": fmt_int(
            getattr(light, "adaptive_front_lighting_count", None)
        ),
        "adaptive_front_lighting_color": normalize_light_color(
            getattr(light, "adaptive_front_lighting_color", None)
        ),

        "headlight_washer_present_label": fmt_bool(
            getattr(light, "headlight_washer_present", None),
            "Наличие",
            "Отсутствие",
        ),

        "left_34v_cd": fmt_num(getattr(light, "left_34v_cd", None), 1),
        "left_52h_cd": fmt_num(getattr(light, "left_52h_cd", None), 1),
        "left_high_beam_cd": fmt_num(getattr(light, "left_high_beam_cd", None), 1),
        "right_34v_cd": fmt_num(getattr(light, "right_34v_cd", None), 1),
        "right_52h_cd": fmt_num(getattr(light, "right_52h_cd", None), 1),
        "right_high_beam_cd": fmt_num(getattr(light, "right_high_beam_cd", None), 1),

        "turn_signal_frequency_per_min": fmt_num(
            getattr(light, "turn_signal_frequency_per_min", None),
            1,
        ),
        "turn_signal_frequency_hz": fmt_num(
            getattr(light, "turn_signal_frequency_hz", None),
            1,
        ),

        "low_beam_upper_point_mm": fmt_num(
            getattr(light, "low_beam_upper_point_mm", None),
            2,
        ),
        "low_beam_lower_point_mm": fmt_num(
            getattr(light, "low_beam_lower_point_mm", None),
            2,
        ),

        "fog_light_upper_point_mm": fmt_num(
            getattr(light, "fog_light_upper_point_mm", None),
            2,
        ),
        "fog_light_lower_point_mm": fmt_num(
            getattr(light, "fog_light_lower_point_mm", None),
            2,
        ),
        "fog_light_left_distance_mm": fmt_num(
            getattr(light, "fog_light_left_distance_mm", None),
            2,
        ),
        "fog_light_right_distance_mm": fmt_num(
            getattr(light, "fog_light_right_distance_mm", None),
            2,
        ),

        "brake_signal_upper_point_mm": fmt_num(
            getattr(light, "brake_signal_upper_point_mm", None),
            2,
        ),
        "brake_signal_lower_point_mm": fmt_num(
            getattr(light, "brake_signal_lower_point_mm", None),
            2,
        ),
        "brake_signal_left_distance_mm": fmt_num(
            getattr(light, "brake_signal_left_distance_mm", None),
            2,
        ),
        "brake_signal_right_distance_mm": fmt_num(
            getattr(light, "brake_signal_right_distance_mm", None),
            2,
        ),

        "additional_brake_signal_from_glass_edge_mm": fmt_num(
            getattr(light, "additional_brake_signal_from_glass_edge_mm", None),
            2,
        ),
        "additional_brake_signal_from_support_surface_mm": fmt_num(
            getattr(light, "additional_brake_signal_from_support_surface_mm", None),
            2,
        ),
        "additional_brake_signal_optical_center_shift_mm": fmt_num(
            getattr(light, "additional_brake_signal_optical_center_shift_mm", None),
            2,
        ),

        "rear_fog_upper_point_mm": fmt_num(
            getattr(light, "rear_fog_upper_point_mm", None),
            2,
        ),
        "rear_fog_lower_point_mm": fmt_num(
            getattr(light, "rear_fog_lower_point_mm", None),
            2,
        ),
    }

    context.update(build_tire_depth_values(protocol, measurement))
    context.update(build_eco_values(protocol, measurement))
    context.update(build_front_fog_values(light))
    context.update(build_rear_fog_values(light))
    context.update(build_sun_strip_values(measurement))
    dynamic_result_values = build_dynamic_result_values(protocol, measurement, light)
    context.update(dynamic_result_values)
    context.update(build_light_device_row_values(light))
    context.update(build_calculated_values(protocol))
    context.update(build_uncertainty_values(protocol))
    context.update(build_photo_values(protocol))
    context.update(
        build_applicability_values(
            protocol,
            measurement,
            light,
            context,
        )
    )

    return context
