from decimal import Decimal, InvalidOperation

from rest_framework import serializers


CONDITION_RANGES = {
    "ambient_temperature_c": ("19", "21", "Температура окружающей среды", "°C"),
    "relative_humidity_pct": ("48", "66", "Относительная влажность", "%"),
    "atmospheric_pressure_kpa": ("93", "104", "Атмосферное давление", "кПа"),
    "road_ambient_temperature_c": ("-25", "40", "Температура окружающей среды на дороге", "°C"),
    "road_relative_humidity_pct": ("15", "95", "Относительная влажность на дороге", "%"),
}

POWER_SUPPLY_RANGES = {
    "phase_a_n_voltage_v": ("187", "242", "Фаза A–N", "В"),
    "phase_b_n_voltage_v": ("187", "242", "Фаза B–N", "В"),
    "phase_c_n_voltage_v": ("187", "242", "Фаза C–N", "В"),
    "phase_ab_voltage_v": ("332", "418", "Фаза A–B", "В"),
    "phase_bc_voltage_v": ("332", "418", "Фаза B–C", "В"),
    "phase_ac_voltage_v": ("332", "418", "Фаза A–C", "В"),
}

MEASUREMENT_RANGES = {
    "bumper_to_body_distance_mm": ("0", "19", "Расстояние от края бампера до кузова", "мм"),
    "sun_strip_width_mm": ("0", "139", "Ширина светозащитной полосы", "мм"),
    "speed_by_speedometer_kmh": ("20", "25", "Скорость по спидометру", "км/ч", ("20", "25")),
    "exhaust_noise_constant_db": ("0", "94", "Шум на постоянных оборотах", "дБА"),
    "exhaust_noise_deceleration_db": ("0", "94", "Шум при замедлении", "дБА"),
    "co_min_pct": ("0", "0.29", "CO на минимальных оборотах", "%"),
    "co_max_pct": ("0", "0.19", "CO на повышенных оборотах", "%"),
    "light_absorption_1": ("0", "1.5", "Дымность, замер 1", "м⁻¹"),
    "light_absorption_2": ("0", "1.5", "Дымность, замер 2", "м⁻¹"),
    "light_absorption_3": ("0", "1.5", "Дымность, замер 3", "м⁻¹"),
    "light_absorption_4": ("0", "1.5", "Дымность, замер 4", "м⁻¹"),
    "light_absorption_5": ("0", "1.5", "Дымность, замер 5", "м⁻¹"),
    "light_absorption_6": ("0", "1.5", "Дымность, замер 6", "м⁻¹"),
    "protruding_elements_doors_mm": ("0", "39", "Выступание ручек дверей и багажника", "мм"),
    "protruding_elements_other_mm": ("0", "29", "Выступание остальных элементов", "мм"),
    "vehicle_length_mm": ("0", "8148", "Длина транспортного средства", "мм"),
    "vehicle_width_mm": ("0", "4499", "Ширина транспортного средства", "мм"),
    "vehicle_height_mm": ("0", "2799", "Высота транспортного средства", "мм"),
    "axle1_load_kg": ("0", "3500", "Нагрузка на ось 1 при взвешивании на весах", "кг"),
    "axle2_load_kg": ("0", "3500", "Нагрузка на ось 2 при взвешивании на весах", "кг"),
    "steering_backlash_deg": ("0", "9.5", "Люфт в рулевом управлении", "°"),
    "glass_transparency_right_pct": ("72", "95", "Светопропускание правого стекла", "%"),
    "glass_transparency_left_pct": ("72", "95", "Светопропускание левого стекла", "%"),
    "glass_transparency_windshield_pct": ("72", "95", "Светопропускание ветрового стекла", "%"),
}

BRAKE_RANGES = {
    "service_brake_control_force_axle1_n": ("0", "465", "Усилие на органе управления рабочей тормозной системы, ось 1", "Н"),
    "service_brake_control_force_axle2_n": ("0", "465", "Усилие на органе управления рабочей тормозной системы, ось 2", "Н"),
    "service_brake_front_left_kn": ("0", "30", "Тормозная сила переднего левого колеса", "кН"),
    "service_brake_front_right_kn": ("0", "30", "Тормозная сила переднего правого колеса", "кН"),
    "service_brake_rear_left_kn": ("0", "30", "Тормозная сила заднего левого колеса", "кН"),
    "service_brake_rear_right_kn": ("0", "30", "Тормозная сила заднего правого колеса", "кН"),
    "parking_brake_left_kn": ("0", "30", "Тормозная сила стояночной системы, левое колесо", "кН"),
    "parking_brake_right_kn": ("0", "30", "Тормозная сила стояночной системы, правое колесо", "кН"),
}

# Количество приборов, которое в протоколе записано статично (ближний свет, указатели
# поворота, габариты, основной стоп-сигнал), не проверяем.
NON_HEADLIGHT_LIGHT_COUNT_RANGES = {
    "high_beam_count": ("2", "4", "Фара дальнего света", "шт.", ("2", "4")),
    "front_fog_count": ("0", "2", "Передние противотуманные фары", "шт.", ("0", "2")),
    "adaptive_front_lighting_count": ("0", "2", "Адаптивная система переднего освещения", "шт.", ("0", "2")),
    "reverse_light_count": ("1", "2", "Фонарь заднего хода", "шт.", ("1", "2")),
    "additional_brake_signal_count": ("1", "2", "Дополнительный сигнал торможения", "шт.", ("1", "2")),
    "rear_fog_count": ("0", "2", "Задние противотуманные фонари", "шт.", ("0", "1", "2")),
    "plate_light_count": ("1", "2", "Фонарь освещения заднего номера", "шт.", ("1", "2")),
    "daytime_running_light_count": ("0", "2", "Дневные ходовые огни", "шт.", ("0", "2")),
    "parking_light_count": ("0", "2", "Передние стояночные огни", "шт.", ("0", "2")),
    "rear_parking_light_count": ("0", "2", "Задние стояночные огни", "шт.", ("0", "2")),
}

NON_HEADLIGHT_LIGHT_RANGES = {
    "low_beam_upper_point_mm": ("501", "1199", "Фара ближнего света по высоте вверх", "мм"),
    "low_beam_lower_point_mm": ("501", "1199", "Фара ближнего света по высоте вниз", "мм"),
    "fog_light_left_distance_mm": ("0", "399", "Передние противотуманные фары по ширине, левая", "мм"),
    "fog_light_right_distance_mm": ("0", "399", "Передние противотуманные фары по ширине, правая", "мм"),
    "fog_light_upper_point_mm": ("251", "799", "Передние противотуманные фары по высоте вверх", "мм"),
    "fog_light_lower_point_mm": ("251", "799", "Передние противотуманные фары по высоте вниз", "мм"),
    "left_34v_cd": ("100", "642", "Сила света фар 34′, левая", "кд"),
    "right_34v_cd": ("100", "642", "Сила света фар 34′, правая", "кд"),
    "left_52h_cd": ("1900", "110000", "Сила света фар 52′, левая", "кд"),
    "right_52h_cd": ("1900", "110000", "Сила света фар 52′, правая", "кд"),
    "left_high_beam_cd": ("5000", "112000", "Сила света фары дальнего света, левая", "кд"),
    "right_high_beam_cd": ("5000", "112000", "Сила света фары дальнего света, правая", "кд"),
    "brake_signal_left_distance_mm": ("0", "399", "Основной сигнал торможения, левый по ширине", "мм"),
    "brake_signal_right_distance_mm": ("0", "399", "Основной сигнал торможения, правый по ширине", "мм"),
    "brake_signal_upper_point_mm": ("351", "1499", "Основной сигнал торможения, верхняя точка", "мм"),
    "brake_signal_lower_point_mm": ("351", "1499", "Основной сигнал торможения, нижняя точка", "мм"),
    "additional_brake_signal_from_support_surface_mm": ("851", "2799", "Дополнительный сигнал торможения от опорной поверхности", "мм"),
    "additional_brake_signal_from_glass_edge_mm": ("0", "149", "Дополнительный сигнал торможения от края стекла", "мм"),
    "additional_brake_signal_optical_center_shift_mm": ("0", "149", "Смещение центра дополнительного сигнала торможения", "мм"),
    "rear_fog_upper_point_mm": ("251", "999", "Задние противотуманные фонари, верхняя точка", "мм"),
    "rear_fog_lower_point_mm": ("251", "999", "Задние противотуманные фонари, нижняя точка", "мм"),
    "turn_signal_frequency_hz": ("1.4", "1.6", "Частота указателей поворота", "Гц", ("1.4", "1.5", "1.6")),
    "turn_signal_frequency_per_min": ("84", "96", "Частота указателей поворота", "проблесков/мин", ("84", "90", "96")),
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
        return ("1.7", "10", "Глубина протектора летней шины", "мм")
    if season == "winter":
        return ("4.1", "10", "Глубина протектора зимней шины", "мм")
    return None
