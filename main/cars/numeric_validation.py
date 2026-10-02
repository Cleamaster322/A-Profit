from decimal import Decimal, InvalidOperation

from rest_framework import serializers


CONDITION_RANGES = {
    "ambient_temperature_c": ("18", "22", "Температура окружающей среды", "°C"),
    "relative_humidity_pct": ("45", "69", "Относительная влажность", "%"),
    "atmospheric_pressure_kpa": ("92", "105", "Атмосферное давление", "кПа"),
    "road_ambient_temperature_c": ("-25", "40", "Температура окружающей среды на дороге", "°C"),
    "road_relative_humidity_pct": ("15", "95", "Относительная влажность на дороге", "%"),
}

POWER_SUPPLY_RANGES = {
    "frequency_hz": ("50", "50", "Частота электрической сети", "Гц"),
    "phase_a_n_voltage_v": ("187", "242", "Фаза A–N", "В"),
    "phase_b_n_voltage_v": ("187", "242", "Фаза B–N", "В"),
    "phase_c_n_voltage_v": ("187", "242", "Фаза C–N", "В"),
    "phase_ab_voltage_v": ("332", "418", "Фаза A–B", "В"),
    "phase_bc_voltage_v": ("332", "418", "Фаза B–C", "В"),
    "phase_ac_voltage_v": ("332", "418", "Фаза A–C", "В"),
}

MEASUREMENT_RANGES = {
    "bumper_to_body_distance_mm": ("0", "20", "Расстояние от края бампера до кузова", "мм"),
    "sun_strip_width_mm": ("0", "140", "Ширина светозащитной полосы", "мм"),
    "speed_by_speedometer_kmh": ("21", "21", "Скорость по спидометру", "км/ч"),
    "actual_speed_kmh": ("20", "20", "Фактическая скорость", "км/ч"),
    "exhaust_noise_constant_db": ("0", "96", "Шум на постоянных оборотах", "дБА"),
    "exhaust_noise_deceleration_db": ("0", "96", "Шум при замедлении", "дБА"),
    "co_min_pct": ("0", "0.3", "CO на минимальных оборотах", "%"),
    "co_max_pct": ("0", "0.2", "CO на повышенных оборотах", "%"),
    "light_absorption_1": ("0", "1.5", "Дымность, замер 1", "м⁻¹"),
    "light_absorption_2": ("0", "1.5", "Дымность, замер 2", "м⁻¹"),
    "light_absorption_3": ("0", "1.5", "Дымность, замер 3", "м⁻¹"),
    "light_absorption_4": ("0", "1.5", "Дымность, замер 4", "м⁻¹"),
    "light_absorption_5": ("0", "1.5", "Дымность, замер 5", "м⁻¹"),
    "light_absorption_6": ("0", "1.5", "Дымность, замер 6", "м⁻¹"),
    "protruding_elements_doors_mm": ("0", "40", "Выступание ручек дверей и багажника", "мм"),
    "protruding_elements_other_mm": ("0", "30", "Выступание остальных элементов", "мм"),
    "vehicle_length_mm": ("0", "8150", "Длина транспортного средства", "мм"),
    "vehicle_width_mm": ("0", "4500", "Ширина транспортного средства", "мм"),
    "vehicle_height_mm": ("0", "2800", "Высота транспортного средства", "мм"),
    "vehicle_weight_kg": ("200", "3500", "Масса при взвешивании на весах", "кг"),
    "axle1_load_kg": ("200", "3500", "Нагрузка на ось 1 при взвешивании на весах", "кг"),
    "axle2_load_kg": ("200", "3500", "Нагрузка на ось 2 при взвешивании на весах", "кг"),
    "stand_axle1_load_kg": ("0", "3500", "Нагрузка на ось 1 на тормозном стенде", "кг"),
    "stand_axle2_load_kg": ("0", "3500", "Нагрузка на ось 2 на тормозном стенде", "кг"),
}

BRAKE_RANGES = {
    "service_brake_control_force_axle1_n": ("0", "490", "Усилие на органе управления рабочей тормозной системы, ось 1", "Н"),
    "service_brake_control_force_axle2_n": ("0", "490", "Усилие на органе управления рабочей тормозной системы, ось 2", "Н"),
    "service_brake_front_left_kn": ("0", "30", "Тормозная сила переднего левого колеса", "кН"),
    "service_brake_front_right_kn": ("0", "30", "Тормозная сила переднего правого колеса", "кН"),
    "service_brake_rear_left_kn": ("0", "30", "Тормозная сила заднего левого колеса", "кН"),
    "service_brake_rear_right_kn": ("0", "30", "Тормозная сила заднего правого колеса", "кН"),
    "parking_brake_left_kn": ("0", "30", "Тормозная сила стояночной системы, левое колесо", "кН"),
    "parking_brake_right_kn": ("0", "30", "Тормозная сила стояночной системы, правое колесо", "кН"),
    "stand_axle1_load_kg": ("0", "3500", "Нагрузка на ось 1 при взвешивании на стенде", "кг"),
    "stand_axle2_load_kg": ("0", "3500", "Нагрузка на ось 2 при взвешивании на стенде", "кг"),
}

NON_HEADLIGHT_LIGHT_COUNT_RANGES = {
    "reverse_light_count": ("1", "2", "Фонарь заднего хода", "шт.", ("1", "2")),
    "turn_signal_count": ("2", "2", "Указатели поворота", "шт.", ("2",)),
    "front_position_light_count": ("2", "2", "Передние габаритные огни", "шт.", ("2",)),
    "rear_position_light_count": ("2", "2", "Задние габаритные огни", "шт.", ("2",)),
    "main_brake_signal_count": ("2", "2", "Основной сигнал торможения", "шт.", ("2",)),
    "additional_brake_signal_count": ("1", "2", "Дополнительный сигнал торможения", "шт.", ("1", "2")),
    "rear_fog_count": ("0", "2", "Задние противотуманные фонари", "шт.", ("0", "1", "2")),
    "plate_light_count": ("1", "2", "Фонарь освещения заднего номера", "шт.", ("1", "2")),
    "daytime_running_light_count": ("0", "2", "Дневные ходовые огни", "шт.", ("0", "2")),
    "parking_light_count": ("0", "2", "Передние стояночные огни", "шт.", ("0", "2")),
    "rear_parking_light_count": ("0", "2", "Задние стояночные огни", "шт.", ("0", "2")),
}

NON_HEADLIGHT_LIGHT_RANGES = {
    "brake_signal_left_distance_mm": ("0", "400", "Основной сигнал торможения, левый по ширине", "мм"),
    "brake_signal_right_distance_mm": ("0", "400", "Основной сигнал торможения, правый по ширине", "мм"),
    "brake_signal_upper_point_mm": ("350", "1500", "Основной сигнал торможения, верхняя точка", "мм"),
    "brake_signal_lower_point_mm": ("350", "1500", "Основной сигнал торможения, нижняя точка", "мм"),
    "additional_brake_signal_from_support_surface_mm": ("850", "2800", "Дополнительный сигнал торможения от опорной поверхности", "мм"),
    "additional_brake_signal_from_glass_edge_mm": ("0", "150", "Дополнительный сигнал торможения от края стекла", "мм"),
    "additional_brake_signal_optical_center_shift_mm": ("0", "150", "Смещение центра дополнительного сигнала торможения", "мм"),
    "rear_fog_upper_point_mm": ("250", "1000", "Задние противотуманные фонари, верхняя точка", "мм"),
    "rear_fog_lower_point_mm": ("250", "1000", "Задние противотуманные фонари, нижняя точка", "мм"),
    "turn_signal_frequency_hz": ("1.4", "1.6", "Частота указателей поворота", "Гц", ("1.4", "1.6")),
    "turn_signal_frequency_per_min": ("84", "96", "Частота указателей поворота", "проблесков/мин", ("84", "96")),
}


def format_bound(value):
    return str(value).replace(".", ",")


def validate_numeric_ranges(serializer, attrs, rules):
    errors = {}
    dash_fields = set(attrs.get("dash_fields") or [])

    for field_name, rule in rules.items():
        minimum, maximum, label, unit = rule[:4]
        allowed_values = rule[4] if len(rule) > 4 else None
        value = attrs.get(field_name, getattr(serializer.instance, field_name, None))
        if value is None or field_name in dash_fields:
            continue

        try:
            numeric_value = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            continue

        lower_bound = Decimal(minimum)
        upper_bound = Decimal(maximum)
        if lower_bound <= numeric_value <= upper_bound:
            if not allowed_values or any(
                numeric_value == Decimal(str(allowed)) for allowed in allowed_values
            ):
                continue

        if allowed_values:
            allowed_text = " или ".join(format_bound(allowed) for allowed in allowed_values)
            errors[field_name] = (
                f"{label}: введено {value} {unit}; допустимые значения: "
                f"{allowed_text} {unit} (границы от {format_bound(minimum)} "
                f"до {format_bound(maximum)} {unit})."
            )
        else:
            errors[field_name] = (
                f"{label}: введено {value} {unit}; допустимое значение "
                f"от {format_bound(minimum)} до {format_bound(maximum)} {unit}."
            )

    if errors:
        raise serializers.ValidationError(errors)


def tire_depth_rule(field_name, season):
    if season == "summer":
        return ("1.6", "10", "Глубина протектора летней шины", "мм")
    if season == "winter":
        return ("4", "10", "Глубина протектора зимней шины", "мм")
    return None
